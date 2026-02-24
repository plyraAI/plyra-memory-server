"""SQLite-backed key store. Default for self-hosted deployments."""

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import aiosqlite

from ..models import APIKeyInfo, AuthContext
from .base import KeyStore


class SQLiteKeyStore(KeyStore):
    def __init__(self, db_path: str, default_rate_limit: int = 600):
        self._db_path = Path(db_path).expanduser()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: aiosqlite.Connection | None = None
        self._default_rate_limit = default_rate_limit

    async def initialize(self) -> None:
        self._conn = await aiosqlite.connect(str(self._db_path))
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id          TEXT PRIMARY KEY,
                key_hash    TEXT NOT NULL UNIQUE,
                key_prefix  TEXT NOT NULL,
                workspace_id TEXT NOT NULL,
                label       TEXT,
                env         TEXT NOT NULL DEFAULT 'live',
                rate_limit_rpm INTEGER NOT NULL DEFAULT 600,
                created_at  TEXT NOT NULL,
                last_used_at TEXT,
                is_active   INTEGER NOT NULL DEFAULT 1
            )
        """)
        await self._conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_keys_hash ON api_keys(key_hash)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_keys_workspace ON api_keys(workspace_id)"
        )
        await self._conn.commit()

    async def create_key(
        self,
        key_hash: str,
        key_prefix: str,
        workspace_id: str,
        label: str | None,
        env: str,
        rate_limit_rpm: int,
    ) -> APIKeyInfo:
        key_id = uuid4().hex
        now = datetime.now(UTC).isoformat()
        await self._conn.execute(
            """
            INSERT INTO api_keys
              (id, key_hash, key_prefix, workspace_id, label, env,
               rate_limit_rpm, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
            (
                key_id,
                key_hash,
                key_prefix,
                workspace_id,
                label,
                env,
                rate_limit_rpm,
                now,
            ),
        )
        await self._conn.commit()
        return APIKeyInfo(
            key_id=key_id,
            workspace_id=workspace_id,
            key_prefix=key_prefix,
            label=label,
            env=env,
            created_at=datetime.fromisoformat(now),
            is_active=True,
        )

    async def validate_key(self, key_hash: str) -> AuthContext | None:
        async with self._conn.execute(
            "SELECT * FROM api_keys WHERE key_hash = ? AND is_active = 1", (key_hash,)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        # Update last_used_at
        now = datetime.now(UTC).isoformat()
        await self._conn.execute(
            "UPDATE api_keys SET last_used_at = ? WHERE id = ?", (now, row["id"])
        )
        await self._conn.commit()
        return AuthContext(
            workspace_id=row["workspace_id"],
            key_id=row["id"],
            env=row["env"],
            api_key_prefix=row["key_prefix"],
        )

    async def list_keys(self, workspace_id: str) -> list[APIKeyInfo]:
        async with self._conn.execute(
            "SELECT * FROM api_keys WHERE workspace_id = ? ORDER BY created_at DESC",
            (workspace_id,),
        ) as cur:
            rows = await cur.fetchall()
        return [
            APIKeyInfo(
                key_id=r["id"],
                workspace_id=r["workspace_id"],
                key_prefix=r["key_prefix"],
                label=r["label"],
                env=r["env"],
                created_at=datetime.fromisoformat(r["created_at"]),
                last_used_at=datetime.fromisoformat(r["last_used_at"])
                if r["last_used_at"]
                else None,
                is_active=bool(r["is_active"]),
            )
            for r in rows
        ]

    async def revoke_key(self, key_id: str) -> bool:
        await self._conn.execute(
            "UPDATE api_keys SET is_active = 0 WHERE id = ?", (key_id,)
        )
        await self._conn.commit()
        return True

    async def get_key_info(self, key_id: str) -> APIKeyInfo | None:
        async with self._conn.execute(
            "SELECT * FROM api_keys WHERE id = ?", (key_id,)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        return APIKeyInfo(
            key_id=row["id"],
            workspace_id=row["workspace_id"],
            key_prefix=row["key_prefix"],
            label=row["label"],
            env=row["env"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_used_at=datetime.fromisoformat(row["last_used_at"])
            if row["last_used_at"]
            else None,
            is_active=bool(row["is_active"]),
        )

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
