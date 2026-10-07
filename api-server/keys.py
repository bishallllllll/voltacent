"""API key issuance, hashing, and verification. SQLite-backed, stdlib only."""

import hashlib
import hmac
import secrets
import sqlite3
import time
from pathlib import Path


def _hash(raw_key: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", raw_key.encode(), salt.encode(), 200_000).hex()


class KeyStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS api_keys (
                key_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                tier TEXT NOT NULL,
                scopes TEXT NOT NULL,
                salt TEXT NOT NULL,
                key_hash TEXT NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0,
                created_at REAL NOT NULL,
                last_used_at REAL
            )"""
        )
        self._conn.commit()

    def issue(self, name: str, tier: str, scopes: list, raw_key: str) -> str:
        key_id = "key_" + secrets.token_hex(8)
        salt = secrets.token_hex(16)
        self._conn.execute(
            "INSERT INTO api_keys (key_id, name, tier, scopes, salt, key_hash, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (key_id, name, tier, ",".join(scopes), salt, _hash(raw_key, salt), time.time()),
        )
        self._conn.commit()
        return key_id

    def verify(self, raw_key: str) -> dict | None:
        # Compare against each stored hash with hmac.compare_digest.
        # Key count is small (per-customer keys); full scan is fine.
        for row in self._conn.execute(
            "SELECT key_id, name, tier, scopes, salt, key_hash, revoked FROM api_keys"
        ):
            key_id, name, tier, scopes, salt, key_hash, revoked = row
            if hmac.compare_digest(_hash(raw_key, salt), key_hash):
                return {
                    "key_id": key_id, "name": name, "tier": tier,
                    "scopes": scopes.split(","), "revoked": bool(revoked),
                }
        return None

    def touch(self, key_id: str) -> None:
        self._conn.execute(
            "UPDATE api_keys SET last_used_at = ? WHERE key_id = ?", (time.time(), key_id)
        )
        self._conn.commit()

    def revoke(self, key_id: str) -> None:
        self._conn.execute("UPDATE api_keys SET revoked = 1 WHERE key_id = ?", (key_id,))
        self._conn.commit()
