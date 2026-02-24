<div align="center">

<img src="docs/assets/logo.png" width="48" height="48" alt="Plyra" />

# plyra-memory-server

**Self-hosted memory infrastructure for agentic AI.**  
Multi-tenant. API key auth. Workspace isolation.  
Drop-in backend for [plyra-memory](https://github.com/plyraAI/plyra-memory).

[![License](https://img.shields.io/badge/license-Apache%202.0-2dd4bf?labelColor=0d1117)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20|%203.12%20|%203.13-2dd4bf?labelColor=0d1117)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-21%20passing-2dd4bf?labelColor=0d1117)](tests/)
[![Docker](https://img.shields.io/badge/docker-ready-2dd4bf?labelColor=0d1117)](Dockerfile)
[![Docs](https://img.shields.io/badge/docs-plyraai.github.io-818cf8?labelColor=0d1117)](https://plyraai.github.io/plyra-memory-server)

</div>

---

## The problem

You have multiple agents running across multiple services.
Each one has its own memory — or none at all.

There is no shared layer. No persistence across restarts.
No way to say: every agent working for this user should know what that user told us last week.

plyra-memory-server solves this. One server. All your agents connect to it.
Memory persists, is isolated by workspace, and survives restarts.

```
Agent A (LangGraph)  ─┐
Agent B (AutoGen)    ──┤── plyra-memory-server ── ~/.plyra/memory.db
Agent C (plain Python)─┘         ↑
                           plm_live_abc123
                         Authorization: Bearer
```

---

## Quickstart

```bash
# 1. Clone and configure
git clone https://github.com/plyraAI/plyra-memory-server
cd plyra-memory-server
cp .env.example .env
# Edit .env — set PLYRA_ADMIN_API_KEY to something strong

# 2. Start the server
docker compose up -d

# 3. Create your first API key
curl -X POST http://localhost:7700/admin/keys \
  -H "Authorization: Bearer your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id": "my-workspace", "label": "dev", "env": "live"}'
```

Response:
```json
{
  "key": "plm_live_a1b2c3d4e5f6...",
  "workspace_id": "my-workspace",
  "env": "live"
}
```

Save that key. It is shown only once.

---

## Connect your agent

Set two environment variables — your agent connects automatically:

```bash
export PLYRA_SERVER_URL=http://localhost:7700
export PLYRA_API_KEY=plm_live_a1b2c3d4e5f6...
```

```python
from plyra_memory import Memory

# Identical API — local or server mode
async with Memory(agent_id="support-agent") as memory:
    await memory.remember("user prefers Python async frameworks")
    ctx = await memory.context_for("what stack does the user use?")
    print(ctx.content)
```

No code changes. No new imports. The library detects `PLYRA_SERVER_URL`
and routes all operations to the server automatically.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  plyra-memory-server                                │
│                                                     │
│  FastAPI                    :7700                   │
│  ├── Auth middleware        API key → workspace     │
│  ├── POST /v1/remember      write to memory         │
│  ├── POST /v1/recall        search memory           │
│  ├── POST /v1/context       get prompt context      │
│  ├── GET  /v1/stats         memory counts           │
│  └── POST /admin/keys       create / revoke keys    │
│                                                     │
│  plyra-memory (library)                             │
│  ├── Working memory         current session         │
│  ├── Episodic memory        all sessions, vector    │
│  └── Semantic memory        facts, decay, dedup     │
│                                                     │
│  Storage                                            │
│  ├── SQLite  (default)      ~/.plyra/memory.db      │
│  └── Postgres (optional)    PLYRA_DATABASE_URL      │
└─────────────────────────────────────────────────────┘
```

---

## Multi-tenant isolation

Every API key belongs to a workspace.
Memory is fully isolated between workspaces — no cross-contamination.

```python
# Agent A — workspace "acme"
memory_a = Memory(agent_id="agent-1")   # key: plm_live_acme...
await memory_a.remember("acme internal data")

# Agent B — workspace "other"
memory_b = Memory(agent_id="agent-1")   # key: plm_live_other...
ctx = await memory_b.context_for("acme internal data")
# → returns nothing. Workspace isolation enforced server-side.
```

Within a workspace, memory is further namespaced by `user_id` and `agent_id`:

```python
await memory.remember(
    "user prefers dark mode",
    metadata={"user_id": "user_xyz", "agent_id": "support-agent"}
)
```

---

## API reference

### Authentication

All memory routes require:
```
Authorization: Bearer plm_live_<key>
```

Admin routes require `PLYRA_ADMIN_API_KEY`.

### Memory routes

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/v1/remember` | Write content to all memory layers |
| POST | `/v1/recall` | Search memory by semantic similarity |
| POST | `/v1/context` | Get prompt-ready context string |
| GET | `/v1/stats` | Memory counts for workspace |
| DELETE | `/v1/memory` | Clear working memory |

### Admin routes

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/admin/keys` | Create API key |
| GET | `/admin/keys/{workspace_id}` | List keys for workspace |
| DELETE | `/admin/keys/{key_id}` | Revoke key |

Full API reference: [plyraai.github.io/plyra-memory-server](https://plyraai.github.io/plyra-memory-server)

---

## Configuration

All config via environment variables. See `.env.example` for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `PLYRA_ADMIN_API_KEY` | `plm_admin_changeme` | Admin key — **change this** |
| `PLYRA_HOST` | `0.0.0.0` | Bind address |
| `PLYRA_PORT` | `7700` | Port |
| `PLYRA_ENV` | `local` | Environment tag |
| `PLYRA_STORE_URL` | `~/.plyra/memory.db` | SQLite path |
| `PLYRA_VECTORS_URL` | `~/.plyra/memory.index` | ChromaDB path |
| `PLYRA_KEY_STORE_URL` | `~/.plyra/keys.db` | Key store path |
| `ANTHROPIC_API_KEY` | — | Enables LLM fact extraction |
| `OPENAI_API_KEY` | — | Alternative LLM for extraction |

---

## Deployment

### Docker (recommended)

```bash
# SQLite — zero dependencies
docker compose up -d

# Postgres — production multi-node
POSTGRES_PASSWORD=strong_password docker compose \
  -f docker-compose.postgres.yml up -d
```

### Azure Container Apps

```bash
# Build and push image
az acr build --registry plyraregistry \
  --image plyra-memory-server:latest .

# Deploy
az containerapp create \
  --name plyra-memory-server \
  --resource-group plyra-rg \
  --image plyraregistry.azurecr.io/plyra-memory-server:latest \
  --env-vars PLYRA_ADMIN_API_KEY=secretref:admin-key \
  --target-port 7700 \
  --ingress external
```

Full Azure deployment guide:
[plyraai.github.io/plyra-memory-server/deploy/azure](https://plyraai.github.io/plyra-memory-server/deploy/azure)

### Manual

```bash
pip install plyra-memory-server
PLYRA_ADMIN_API_KEY=your-key plyra-server
```

---

## Works with plyra-memory

plyra-memory-server is the server component of the plyra-memory stack.
The library handles local mode. The server handles multi-agent, multi-tenant.

| | Local | Server |
|---|---|---|
| Install | `pip install plyra-memory` | `docker compose up` |
| Config | zero | two env vars |
| Agents | one process | unlimited |
| Persistence | `~/.plyra/` | mounted volume or Postgres |
| Isolation | by `agent_id` | by workspace + user + agent |
| Scale | single node | multi-instance with Postgres |

---

## Framework support

plyra-memory (the library) works with all major agent frameworks.
When `PLYRA_SERVER_URL` is set, all framework adapters route to the server automatically.

| Framework | Adapter | Mode |
|-----------|---------|------|
| LangGraph | `create_memory_nodes(memory)` | auto |
| AutoGen | `MemoryHook(memory)` | auto |
| LangChain | `PlyraMemory(memory)` | auto |
| CrewAI | `MemoryTool(memory)` | auto |
| OpenAI Agents SDK | `create_memory_tools(memory)` | auto |
| Plain Python | `Memory()` | auto |

---

## Related

- [plyra-memory](https://github.com/plyraAI/plyra-memory) — the library (PyPI)
- [plyra-guard](https://github.com/plyraAI/plyra-guard) — action middleware for agents
- [plyraai.github.io](https://plyraai.github.io) — full documentation

---

## License

Apache 2.0 — see [LICENSE](LICENSE)

Built by [Plyra](https://plyraai.github.io) —
open-source infrastructure for agentic AI.
