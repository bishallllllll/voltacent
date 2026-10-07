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

SHUCK_ENGINE_DIR = Path(os.environ.get("SHUCK_ENGINE_DIR", "/home/ubuntu/shuck-engine"))
if str(SHUCK_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(SHUCK_ENGINE_DIR))


class TriadError(RuntimeError):
    """Raised when any leg of the triad cannot produce a forecast. Fail-closed."""


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TriadEngine:
    def __init__(self) -> None:
        try:
            from inference.predict import predict_latest_bar, load_model
            from inference.regression import build_live_reg_provider
            from inference.volatility import build_live_vol_provider
        except Exception as exc:
            raise TriadError(f"Cannot import shuck-engine inference modules: {exc}")

        self._predict_latest_bar = predict_latest_bar
        try:
            load_model(verify_manifest=True)  # sha-pinned, fail-closed on tamper
        except Exception as exc:
            raise TriadError(f"Classifier failed to load: {exc}")

        try:
            self._reg = build_live_reg_provider()
        except Exception as exc:
            raise TriadError(f"Regression gate failed to load: {exc}")
        try:
            self._vol = build_live_vol_provider()
        except Exception as exc:
            raise TriadError(f"Volatility gate failed to load: {exc}")

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
        return {
            "status": "ok",
            "models": self.model_versions,
            "threshold": 0.62,
        }
