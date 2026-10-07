"""
Voltacent Triad API — v1 product server.
Serves the production triad (direction classifier + magnitude regressor +
volatility forecaster) over HTTP with API-key auth and rate limits.

Deployment: runs ON the inference VPS, alongside the shuck-engine checkout,
so it imports the real inference modules (same models, same ClickHouse,
same feature code). It does not reimplement anything.

    /home/ubuntu/shuck-engine          <- existing engine checkout
    /home/ubuntu/voltacent-api         <- this server (this directory)

Endpoints:
    GET /v1/health               service + model status (no auth)
    GET /v1/signals/latest       direction + probability per instrument
    GET /v1/magnitude/forecast   expected move (pips) + hurdle pass/fail
    GET /v1/volatility/forecast  expected volatility + regime
    POST /admin/keys             issue a key (localhost only)
"""

import hashlib
import hmac
import os
import secrets
import sqlite3
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from triad import TriadEngine, TriadError
from keys import KeyStore

BASE_DIR = Path(__file__).resolve().parent

# Key database location. On Render this must live on the persistent disk
# (/var/data); everywhere else it sits next to the app. Override with KEYS_DB_PATH.
def _default_db_path() -> Path:
    if os.environ.get("KEYS_DB_PATH"):
        return Path(os.environ["KEYS_DB_PATH"])
    if Path("/var/data").is_dir():
        return Path("/var/data/keys.db")
    return BASE_DIR / "keys.db"


DB_PATH = _default_db_path()

# Rate limits: requests per minute, per key, per endpoint group
RATE_LIMITS = {
    "sandbox": 60,
    "live": 600,
}

_key_store: KeyStore | None = None
_engine: TriadEngine | None = None
_hits: dict[str, list[float]] = defaultdict(list)


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rate_limit_ok(key_id: str, tier: str) -> bool:
    now = time.monotonic()
    window = _hits[key_id]
    while window and window[0] <= now - 60:
        window.pop(0)
    if len(window) >= RATE_LIMITS.get(tier, 60):
        return False
    window.append(now)
    return True


async def require_key(x_api_key: str | None = Header(default=None)) -> dict:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header.")
    rec = _key_store.verify(x_api_key)
    if not rec:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    if rec["revoked"]:
        raise HTTPException(status_code=403, detail="API key revoked.")
    if not _rate_limit_ok(rec["key_id"], rec["tier"]):
        raise HTTPException(
            status_code=429, detail="Rate limit exceeded. Slow down."
        )
    _key_store.touch(rec["key_id"])
    return rec


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _key_store, _engine
    _key_store = KeyStore(DB_PATH)
    _engine = TriadEngine()  # loads models at startup; fail-closed
    yield


app = FastAPI(title="Voltacent Triad API", version="1.0.0", lifespan=lifespan)


@app.exception_handler(TriadError)
async def triad_error_handler(request: Request, exc: TriadError):
    return JSONResponse(
        status_code=503,
        content={"error": "inference_unavailable", "detail": str(exc)},
    )


@app.get("/v1/health")
def health():
    status = _engine.health()
    status["server_time_utc"] = utcnow_iso()
    return status


@app.get("/v1/signals/latest")
def signals_latest(
    instruments: str | None = Query(
        default=None,
        description="Comma-separated, e.g. EUR_USD,GBP_USD. Defaults to the traded universe.",
    ),
    key: dict = Depends(require_key),
):
    insts = [s.strip() for s in instruments.split(",")] if instruments else None
    if key["tier"] == "sandbox":
        # Sandbox serves the dated canary snapshot, never live inference.
        return {
            "tier": "sandbox",
            "as_of": "2026-09-16T08:45:00Z",
            "note": "Sandbox serves a recorded snapshot, not live inference.",
            "signals": [],
        }
    try:
        return {"tier": "live", "as_of": utcnow_iso(), "signals": _engine.signals(insts)}
    except TriadError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@app.get("/v1/magnitude/forecast")
def magnitude_forecast(
    instruments: str | None = Query(default=None),
    key: dict = Depends(require_key),
):
    insts = [s.strip() for s in instruments.split(",")] if instruments else None
    if key["tier"] == "sandbox":
        return {"tier": "sandbox", "note": "Sandbox serves a recorded snapshot, not live inference.", "forecasts": []}
    try:
        return {"tier": "live", "as_of": utcnow_iso(), "forecasts": _engine.magnitude(insts)}
    except TriadError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@app.get("/v1/volatility/forecast")
def volatility_forecast(
    instruments: str | None = Query(default=None),
    key: dict = Depends(require_key),
):
    insts = [s.strip() for s in instruments.split(",")] if instruments else None
    if key["tier"] == "sandbox":
        return {"tier": "sandbox", "note": "Sandbox serves a recorded snapshot, not live inference.", "forecasts": []}
    try:
        return {"tier": "live", "as_of": utcnow_iso(), "forecasts": _engine.volatility(insts)}
    except TriadError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@app.post("/admin/keys")
def issue_key(
    request: Request,
    name: str = Query(description="Human label for the key"),
    tier: str = Query(default="sandbox", description="sandbox or live"),
    scopes: str = Query(default="signals:read,magnitude:read,volatility:read"),
):
    # Admin issuance is localhost-only. No remote key minting.
    if request.client.host not in ("127.0.0.1", "::1"):
        raise HTTPException(status_code=403, detail="Admin endpoint is localhost-only.")
    if tier not in RATE_LIMITS:
        raise HTTPException(status_code=400, detail="tier must be sandbox or live")
    raw = "vc_" + secrets.token_urlsafe(32)
    key_id = _key_store.issue(
        name=name, tier=tier, scopes=[s.strip() for s in scopes.split(",")], raw_key=raw
    )
    # The raw key is shown ONCE, at creation. Only the hash is stored.
    return {"key_id": key_id, "api_key": raw, "tier": tier,
            "warning": "Store this key now. It cannot be retrieved again."}
