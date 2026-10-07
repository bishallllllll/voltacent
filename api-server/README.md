# Voltacent Triad API — v1 product server

Serves the production triad as a real product: API-key auth, rate limits,
four endpoints. Runs on the inference VPS next to the shuck-engine checkout
and imports its real inference modules — no reimplementation.

## Layout on the VPS

```
/home/ubuntu/shuck-engine   <- existing engine checkout (untouched)
/home/ubuntu/voltacent-api  <- this directory
    app.py
    triad.py
    keys.py
    keys.db                 <- created at runtime (API key hashes)
    requirements.txt
    systemd/voltacent-api.service
```

## Deploy (run on the VPS)

```bash
# 1. Copy the files
scp -r api-server ubuntu:<vps>:/home/ubuntu/voltacent-api

# 2. On the VPS
cd /home/ubuntu/voltacent-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# shuck-engine deps (xgboost, pandas, clickhouse-connect, pyyaml) must already
# be installed for the engine user — reuse that environment if simpler.

# 3. Smoke test (imports the real triad; fail-closed if models missing)
SHUCK_ENGINE_DIR=/home/ubuntu/shuck-engine python3 -c "from triad import TriadEngine; e=TriadEngine(); print(e.health())"

# 4. Install the service
sudo cp systemd/voltacent-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now voltacent-api.service

# 5. Issue the first key (localhost only)
curl -X POST "http://127.0.0.1:18900/admin/keys?name=founder&tier=live"
# -> returns {"key_id": ..., "api_key": "vc_..."} — store the key NOW, it is shown once.

# 6. Test authed
curl -H "X-API-Key: vc_..." "http://127.0.0.1:18900/v1/signals/latest?instruments=EUR_USD,GBP_USD"
```

## Public exposure

The service binds to 127.0.0.1. Put nginx/Caddy in front with TLS and
proxy `https://api.voltacent.<domain>/` → `127.0.0.1:18900`. Keep
`/admin/*` blocked at the proxy — key issuance stays localhost-only.

## Endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | /v1/health | no | model versions, status |
| GET | /v1/signals/latest | key | direction + probability per instrument |
| GET | /v1/magnitude/forecast | key | expected pips + hurdle verdict |
| GET | /v1/volatility/forecast | key | expected vol + regime |
| POST | /admin/keys | localhost | issue key (shown once) |

Tiers: `sandbox` (60 req/min, serves the dated snapshot — never live inference),
`live` (600 req/min, real triad). Scopes are recorded per key; enforcement
per endpoint is a one-line addition in `require_key` when you need it.

## What this does NOT do yet (later stages)

- Key management UI (Stage 4 console: create/revoke in the dashboard)
- Usage metering dashboard (log to a table; the console reads it)
- Billing/Stripe (Stage 5)
- The Lovable site's Supabase auth is separate; key issuance here is
  operator-run until the console wires it up.
