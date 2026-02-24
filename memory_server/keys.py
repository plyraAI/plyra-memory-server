"""
API key management for plyra-memory-server.

Key format:
  plm_live_<32 random hex chars>    production
  plm_test_<32 random hex chars>    test/dev

Key storage: SQLite (default) or Postgres (PLYRA_KEY_STORE_URL=postgres://...)
Keys are stored as SHA-256 hashes — plaintext never persisted after generation.
"""

from __future__ import annotations

import hashlib
import secrets


def generate_api_key(env: str = "live") -> tuple[str, str]:
    """
    Generate a new API key.
    Returns (plaintext_key, key_hash).
    Only plaintext_key is shown to the user — never stored.
    key_hash is stored in the database.
    """
    env = "live" if env not in ("live", "test") else env
    random_part = secrets.token_hex(24)  # 48 chars
    key = f"plm_{env}_{random_part}"
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return key, key_hash


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def key_prefix(key: str) -> str:
    """Return first 16 chars for display (safe — not enough to brute force)."""
    return key[:16] + "..."
