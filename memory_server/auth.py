"""
API key authentication middleware.

Clients send:
  Authorization: Bearer plm_live_abc123...

Middleware:
  1. Extracts key from header
  2. Hashes it (SHA-256)
  3. Looks up hash in KeyStore
  4. Injects AuthContext into request.state
  5. Returns 401 if invalid
"""

from __future__ import annotations

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer

from .keys import hash_key
from .storage.base import KeyStore

security = HTTPBearer(auto_error=False)


async def require_auth(request: Request) -> None:
    """
    FastAPI dependency. Injects AuthContext into request.state.auth.
    Raises 401 if key is missing or invalid.
    """
    key_store: KeyStore = request.app.state.key_store

    # Extract key from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Missing Authorization header. Use: Authorization: Bearer plm_live_..."
            ),
        )

    raw_key = auth_header[len("Bearer ") :]
    if not raw_key.startswith("plm_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format. Keys must start with plm_",
        )

    key_hash = hash_key(raw_key)
    auth_ctx = await key_store.validate_key(key_hash)

    if auth_ctx is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key.",
        )

    request.state.auth = auth_ctx


async def require_admin(request: Request) -> None:
    """
    Stricter dependency for admin routes (/admin/keys).
    Validates against PLYRA_ADMIN_API_KEY env var.
    """
    config = request.app.state.config
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    provided_key = auth_header[len("Bearer ") :]
    if provided_key != config.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")
