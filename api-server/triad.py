"""
Adapter between the Voltacent API and the real shuck-engine inference code.

Runs on the VPS with the shuck-engine checkout importable, e.g.::

    /home/ubuntu/shuck-engine/inference/predict.py
    /home/ubuntu/shuck-engine/inference/regression.py
    /home/ubuntu/shuck-engine/inference/volatility.py

Set SHUCK_ENGINE_DIR if the checkout lives elsewhere.
"""

import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

SHUCK_ENGINE_DIR = Path(os.environ.get("SHUCK_ENGINE_DIR")
                       or (Path(__file__).parent / "shuck-engine"))
if str(SHUCK_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(SHUCK_ENGINE_DIR))


class TriadError(RuntimeError):
    """Raised when any leg of the triad cannot produce a forecast. Fail-closed."""


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TriadEngine:
    def __init__(self) -> None:
        # Every leg is optional: the service starts degraded with zero models
        # and legs are added later. Nothing here raises at startup.
        self._predict_latest_bar = None
        self._reg = None
        self._vol = None
        self.legs = {"direction": False, "magnitude": False, "volatility": False}
        self.errors = {}

        try:
            from inference.predict import predict_latest_bar, load_model
            load_model(verify_manifest=True)  # sha-pinned, fail-closed on tamper
            self._predict_latest_bar = predict_latest_bar
            self.legs["direction"] = True
        except Exception as exc:
            self.errors["direction"] = f"{type(exc).__name__}: {exc}"
            print(f"WARNING: direction leg unavailable: {exc}", flush=True)

        try:
            from inference.regression import build_live_reg_provider
            self._reg = build_live_reg_provider()
            self.legs["magnitude"] = True
        except Exception as exc:
            self.errors["magnitude"] = f"{type(exc).__name__}: {exc}"
            print(f"WARNING: magnitude leg unavailable: {exc}", flush=True)

        try:
            from inference.volatility import build_live_vol_provider
            self._vol = build_live_vol_provider()
            self.legs["volatility"] = True
        except Exception as exc:
            self.errors["volatility"] = f"{type(exc).__name__}: {exc}"
            print(f"WARNING: volatility leg unavailable: {exc}", flush=True)

        # Model identity for /v1/health (keep in sync with deployment manifest)
        self.model_versions = {
            "direction": "xgboost_fold11_20260904_094734",
            "magnitude": "gen1-xgboost-regressor",
            "volatility": "gen1-xgboost-volatility",
        }

    # -- helpers ---------------------------------------------------------

    def _frame(self, instruments):
        try:
            df = self._predict_latest_bar(target_instruments=instruments)
        except Exception as exc:
            raise TriadError(f"Classifier inference failed: {exc}")
        if df is None or getattr(df, "empty", True):
            raise TriadError("Classifier returned no predictions.")
        return df

    @staticmethod
    def _col(df, *names):
        for n in names:
            if n in df.columns:
                return n
        raise TriadError(f"Expected one of columns {names}, got {list(df.columns)}")

    # -- public legs -----------------------------------------------------

    def signals(self, instruments=None):
        """Direction + probability per instrument, latest closed bar."""
        if not self.legs["direction"]:
            raise TriadError("Direction model not deployed yet.")
        df = self._frame(instruments)
        inst_col = self._col(df, "instrument", "symbol", "pair")
        prob_col = self._col(df, "probability", "prob", "p_long", "pred_proba")
        out = []
        for _, row in df.iterrows():
            p = float(row[prob_col])
            direction = "long" if p >= 0.62 else ("short" if p <= 0.38 else "flat")
            out.append({
                "instrument": str(row[inst_col]),
                "probability": round(p, 4),
                "direction": direction,
                "threshold": 0.62,
                "dead_zone": [0.38, 0.62],
            })
        return out

    def magnitude(self, instruments=None):
        """Expected move in pips + hurdle verdict per instrument."""
        if not self.legs["magnitude"]:
            raise TriadError("Magnitude model not deployed yet.")
        df = self._frame(instruments)
        inst_col = self._col(df, "instrument", "symbol", "pair")
        out = []
        for _, row in df.iterrows():
            inst = str(row[inst_col])
            try:
                pips = self._reg.predict_pips(inst, row)
            except Exception as exc:
                raise TriadError(f"Regression gate failed for {inst}: {exc}")
            pips = float(pips)
            out.append({
                "instrument": inst,
                "expected_pips": round(pips, 2),
                "hurdle_pips": 0.6,
                "passes_hurdle": abs(pips) >= 0.6,
            })
        return out

    def volatility(self, instruments=None):
        """Expected volatility + regime per instrument."""
        if not self.legs["volatility"]:
            raise TriadError("Volatility model not deployed yet.")
        df = self._frame(instruments)
        inst_col = self._col(df, "instrument", "symbol", "pair")
        out = []
        for _, row in df.iterrows():
            inst = str(row[inst_col])
            try:
                vol = self._vol.forecast(inst, row)
            except Exception as exc:
                raise TriadError(f"Volatility gate failed for {inst}: {exc}")
            out.append({
                "instrument": inst,
                "expected_volatility": float(vol),
                "gate": "enabled",
            })
        return out

    def health(self):
        live = [k for k, v in self.legs.items() if v]
        return {
            "status": "ok" if len(live) == 3 else ("degraded" if live else "no_models"),
            "legs": self.legs,
            "models": self.model_versions,
            "threshold": 0.62,
            "errors": self.errors,
        }
