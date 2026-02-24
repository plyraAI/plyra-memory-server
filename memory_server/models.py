from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def _new_id() -> str:
    return uuid4().hex


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ── API Key models ─────────────────────────────────────────────────────────────


class CreateKeyRequest(BaseModel):
    workspace_id: str = Field(..., min_length=1, max_length=64)
    label: str | None = None  # human-readable label
    env: str = "live"  # "live" or "test"
    rate_limit_rpm: int | None = None  # override default rate limit


class APIKeyResponse(BaseModel):
    key: str  # plm_live_... (shown only on creation)
    key_id: str
    workspace_id: str
    label: str | None
    env: str
    created_at: datetime
    last_used_at: datetime | None = None
    is_active: bool = True


class APIKeyInfo(BaseModel):
    """Returned by GET /admin/keys — key value never included."""

    key_id: str
    workspace_id: str
    key_prefix: str  # first 12 chars e.g. "plm_live_abc"
    label: str | None
    env: str
    created_at: datetime
    last_used_at: datetime | None = None
    is_active: bool


class RevokeKeyRequest(BaseModel):
    key_id: str


# ── Memory operation models ────────────────────────────────────────────────────


class RememberRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=32_000)
    user_id: str | None = None
    agent_id: str | None = None
    importance: float = Field(0.6, ge=0.0, le=1.0)
    source: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RememberResponse(BaseModel):
    working_entry_id: str | None
    episode_id: str | None
    facts_queued: bool  # True — extraction runs in background
    latency_ms: float


class RecallRequest(BaseModel):
    query: str = Field(..., min_length=1)
    user_id: str | None = None
    agent_id: str | None = None
    top_k: int = Field(10, ge=1, le=100)
    token_budget: int | None = None
    layers: list[str] | None = None  # ["working", "episodic", "semantic"]


class RecallResponse(BaseModel):
    query: str
    results: list[dict[str, Any]]
    total_found: int
    cache_hit: bool
    latency_ms: float


class ContextRequest(BaseModel):
    query: str = Field(..., min_length=1)
    user_id: str | None = None
    agent_id: str | None = None
    token_budget: int = Field(2_048, ge=64, le=32_000)


class ContextResponse(BaseModel):
    query: str
    content: str
    token_count: int
    token_budget: int
    memories_used: int
    cache_hit: bool
    latency_ms: float


class StatsResponse(BaseModel):
    workspace_id: str
    working: int
    episodic: int
    semantic: int
    cache_size: int
    uptime_seconds: float


class DeleteMemoryRequest(BaseModel):
    user_id: str | None = None
    agent_id: str | None = None
    layer: str | None = None  # "working" | "episodic" | "semantic" | None=all


class DeleteMemoryResponse(BaseModel):
    deleted: bool
    message: str


# ── Auth models ────────────────────────────────────────────────────────────────


class AuthContext(BaseModel):
    """Injected into every request by auth middleware."""

    workspace_id: str
    key_id: str
    env: str
    api_key_prefix: str
