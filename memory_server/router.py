"""
plyra-memory-server HTTP routes.

Memory routes use workspace isolation from auth context.
Every request is namespaced to: workspace_id / user_id / agent_id

Routes:
  GET  /                        service info
  GET  /health                  health check
  GET  /stats                   memory counts for workspace

  POST /v1/remember             write to memory
  POST /v1/recall               search memory
  POST /v1/context              get prompt-ready context
  DELETE /v1/memory             clear memory (scoped)

  POST /admin/keys              create API key (admin only)
  GET  /admin/keys/{workspace}  list keys for workspace (admin only)
  DELETE /admin/keys/{key_id}   revoke key (admin only)
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .auth import require_admin, require_auth
from .config import ServerConfig
from .keys import generate_api_key
from .keys import key_prefix as fmt_key_prefix
from .models import (
    APIKeyInfo,
    APIKeyResponse,
    ContextRequest,
    ContextResponse,
    CreateKeyRequest,
    DeleteMemoryRequest,
    DeleteMemoryResponse,
    RecallRequest,
    RecallResponse,
    RememberRequest,
    RememberResponse,
    StatsResponse,
)
from .storage.sqlite import SQLiteKeyStore

logger = logging.getLogger(__name__)


def build_app(config: ServerConfig | None = None) -> FastAPI:
    config = config or ServerConfig.default()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Key store
        key_store = SQLiteKeyStore(
            config.key_store_url,
            config.rate_limit_rpm,
        )
        await key_store.initialize()
        app.state.key_store = key_store
        app.state.config = config
        app.state.start_time = time.monotonic()

        # Memory pool — one Memory instance per (workspace, agent) pair
        # In v0.3 we keep it simple: one global Memory instance namespaced
        # by passing workspace/user/agent as agent_id to plyra-memory
        from plyra_memory import MemoryConfig

        mem_config = MemoryConfig(
            store_url=config.store_url,
            vectors_url=config.vectors_url,
            embed_model=config.embed_model,
            cache_enabled=True,
        )

        # Wire LLM extractor if API key provided
        extractor = None
        llm_client = None

        if config.groq_api_key:
            try:
                from openai import OpenAI
                from plyra_memory.extraction.llm import LLMExtractor
                llm_client = OpenAI(
                    api_key=config.groq_api_key,
                    base_url="https://api.groq.com/openai/v1",
                )
                extractor = LLMExtractor(llm_client, model="llama-3.1-8b-instant")
                logger.info("LLM extraction: Groq llama-3.1-8b-instant")
            except ImportError:
                logger.warning("GROQ_API_KEY set but openai package not installed")

        elif config.anthropic_api_key:
            try:
                import anthropic
                from plyra_memory.extraction.llm import LLMExtractor
                llm_client = anthropic.Anthropic(api_key=config.anthropic_api_key)
                extractor = LLMExtractor(llm_client)
                logger.info("LLM extraction: Anthropic claude-haiku")
            except ImportError:
                logger.warning(
                    "ANTHROPIC_API_KEY set but anthropic package not installed"
                )

        elif config.openai_api_key:
            try:
                from openai import OpenAI
                from plyra_memory.extraction.llm import LLMExtractor
                llm_client = OpenAI(api_key=config.openai_api_key)
                extractor = LLMExtractor(llm_client)
                logger.info("LLM extraction: OpenAI gpt-4o-mini")
            except ImportError:
                logger.warning("OPENAI_API_KEY set but openai package not installed")

        else:
            logger.info(
                "LLM extraction: disabled (regex fallback). Set GROQ_API_KEY to enable."
            )

        app.state.mem_config = mem_config
        app.state.extractor = extractor
        app.state.llm_client = llm_client

        yield

        await key_store.close()

    app = FastAPI(
        title="plyra-memory-server",
        version="0.1.0",
        description="Self-hosted memory server for agentic AI",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Middleware: latency header ────────────────────────────────────────────

    @app.middleware("http")
    async def add_latency_header(request: Request, call_next):
        t0 = time.monotonic()
        response = await call_next(request)
        ms = round((time.monotonic() - t0) * 1000, 2)
        response.headers["X-Latency-Ms"] = str(ms)
        return response

    # ── Helper: get or create Memory instance for namespace ──────────────────

    async def get_memory(request: Request, user_id: str | None, agent_id: str | None):
        """
        Returns a Memory instance scoped to workspace/user/agent.
        For v0.3 self-hosted: uses compound agent_id as namespace key.
        e.g. "ws_acme:user_xyz:agent_support1"

        Uses a deterministic session_id derived from the namespaced_id so that
        episodic recall (which filters by session_id) finds memories written by
        previous requests for the same agent — not just the current request's session.
        """
        import hashlib

        auth = request.state.auth
        # Build namespaced agent_id
        parts = [f"ws_{auth.workspace_id}"]
        if user_id:
            parts.append(f"u_{user_id}")
        if agent_id:
            parts.append(f"a_{agent_id}")
        namespaced_id = ":".join(parts)

        # Stable session_id: same agent always gets the same session so
        # episodic memories from past requests are visible on recall.
        stable_session_id = hashlib.md5(namespaced_id.encode()).hexdigest()

        from plyra_memory import Memory

        memory = Memory(
            config=request.app.state.mem_config,
            agent_id=namespaced_id,
            session_id=stable_session_id,
            extractor=request.app.state.extractor,
            llm_client=request.app.state.llm_client,
        )
        await memory._ensure_initialized()
        return memory

    # ── Service routes ────────────────────────────────────────────────────────

    @app.get("/")
    async def root():
        return {
            "service": "plyra-memory-server",
            "version": "0.1.0",
            "status": "ok",
            "docs": "https://plyraai.github.io/plyra-memory",
        }

    @app.get("/health")
    async def health(request: Request):
        uptime = time.monotonic() - request.app.state.start_time
        return {
            "status": "ok",
            "version": "0.1.0",
            "uptime_seconds": round(uptime, 1),
            "env": config.env,
            "store": config.store_url,
            "vectors": config.vectors_url,
        }

    # ── Memory routes (require auth) ──────────────────────────────────────────

    @app.post(
        "/v1/remember",
        response_model=RememberResponse,
        dependencies=[Depends(require_auth)],
    )
    async def remember(request: Request, body: RememberRequest):
        t0 = time.monotonic()
        memory = await get_memory(request, body.user_id, body.agent_id)
        result = await memory.remember(
            content=body.content,
            importance=body.importance,
            source=body.source,
            metadata=body.metadata,
        )
        await memory.close()
        return RememberResponse(
            working_entry_id=result["working_entry"].id
            if result["working_entry"]
            else None,
            episode_id=result["episode"].id if result["episode"] else None,
            facts_queued=True,
            latency_ms=round((time.monotonic() - t0) * 1000, 2),
        )

    @app.post(
        "/v1/recall",
        response_model=RecallResponse,
        dependencies=[Depends(require_auth)],
    )
    async def recall(request: Request, body: RecallRequest):
        t0 = time.monotonic()
        from plyra_memory.schema import MemoryLayer

        layers = None
        if body.layers:
            try:
                layers = [MemoryLayer(layer) for layer in body.layers]
            except ValueError:
                raise HTTPException(
                    400, "Invalid layer. Use: working, episodic, semantic"
                )

        memory = await get_memory(request, body.user_id, body.agent_id)
        result = await memory.recall(
            query=body.query,
            top_k=body.top_k,
            layers=layers,
        )
        await memory.close()
        return RecallResponse(
            query=result.query,
            results=[r.model_dump() for r in result.results],
            total_found=result.total_found,
            cache_hit=result.cache_hit,
            latency_ms=round((time.monotonic() - t0) * 1000, 2),
        )

    @app.post(
        "/v1/context",
        response_model=ContextResponse,
        dependencies=[Depends(require_auth)],
    )
    async def context(request: Request, body: ContextRequest):
        t0 = time.monotonic()
        memory = await get_memory(request, body.user_id, body.agent_id)
        result = await memory.context_for(
            query=body.query,
            token_budget=body.token_budget,
        )
        await memory.close()
        return ContextResponse(
            query=result.query,
            content=result.content,
            token_count=result.token_count,
            token_budget=result.token_budget,
            memories_used=result.memories_used,
            cache_hit=result.cache_hit,
            latency_ms=round((time.monotonic() - t0) * 1000, 2),
        )

    @app.get(
        "/v1/stats", response_model=StatsResponse, dependencies=[Depends(require_auth)]
    )
    async def stats(
        request: Request,
        user_id: str | None = None,
        agent_id: str | None = None,
    ):
        auth = request.state.auth
        memory = await get_memory(request, user_id, agent_id)
        counts = await memory._store.count_memories()
        cache_size = memory._cache.size if memory._cache else 0
        uptime = time.monotonic() - request.app.state.start_time
        await memory.close()
        return StatsResponse(
            workspace_id=auth.workspace_id,
            working=counts.get("working", 0),
            episodic=counts.get("episodic", 0),
            semantic=counts.get("semantic", 0),
            cache_size=cache_size,
            uptime_seconds=round(uptime, 1),
        )

    @app.delete(
        "/v1/memory",
        response_model=DeleteMemoryResponse,
        dependencies=[Depends(require_auth)],
    )
    async def delete_memory(request: Request, body: DeleteMemoryRequest):
        memory = await get_memory(request, body.user_id, body.agent_id)
        layer = body.layer
        if layer == "working" or layer is None:
            await memory.working.clear(memory.session_id)
        # Episodic and semantic delete not exposed in v0.3 — too destructive
        # Future: add scoped delete by session_id or agent_id
        await memory.close()
        return DeleteMemoryResponse(
            deleted=True,
            message=f"Cleared {layer or 'working'} memory for agent {body.agent_id}",
        )

    # ── Admin routes ──────────────────────────────────────────────────────────

    @app.post(
        "/admin/keys",
        response_model=APIKeyResponse,
        dependencies=[Depends(require_admin)],
    )
    async def create_key(request: Request, body: CreateKeyRequest):
        plaintext_key, key_hash = generate_api_key(body.env)
        prefix = fmt_key_prefix(plaintext_key)
        rate_limit = body.rate_limit_rpm or config.rate_limit_rpm

        key_info = await request.app.state.key_store.create_key(
            key_hash=key_hash,
            key_prefix=prefix,
            workspace_id=body.workspace_id,
            label=body.label,
            env=body.env,
            rate_limit_rpm=rate_limit,
        )
        return APIKeyResponse(
            key=plaintext_key,  # only time plaintext is returned
            key_id=key_info.key_id,
            workspace_id=key_info.workspace_id,
            label=key_info.label,
            env=key_info.env,
            created_at=key_info.created_at,
            is_active=True,
        )

    @app.get(
        "/admin/keys/{workspace_id}",
        response_model=list[APIKeyInfo],
        dependencies=[Depends(require_admin)],
    )
    async def list_keys(request: Request, workspace_id: str):
        return await request.app.state.key_store.list_keys(workspace_id)

    @app.delete("/admin/keys/{key_id}", dependencies=[Depends(require_admin)])
    async def revoke_key(request: Request, key_id: str):
        ok = await request.app.state.key_store.revoke_key(key_id)
        if not ok:
            raise HTTPException(404, f"Key {key_id} not found")
        return {"revoked": True, "key_id": key_id}

    return app
