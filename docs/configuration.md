# Configuration

All configuration via environment variables. Set in `.env` or pass directly to Docker.

## Full reference

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PLYRA_ADMIN_API_KEY` | `plm_admin_changeme` | **yes** | Admin key for `/admin/keys` routes. Change before production. |
| `PLYRA_HOST` | `0.0.0.0` | no | Bind address |
| `PLYRA_PORT` | `7700` | no | HTTP port |
| `PLYRA_ENV` | `local` | no | Environment tag (`local`, `staging`, `production`) |
| `PLYRA_DEBUG` | `false` | no | Enable debug logging |
| `PLYRA_STORE_URL` | `~/.plyra/memory.db` | no | SQLite path for memory storage |
| `PLYRA_VECTORS_URL` | `~/.plyra/memory.index` | no | ChromaDB path for vector index |
| `PLYRA_KEY_STORE_URL` | `~/.plyra/keys.db` | no | SQLite path for API key storage |
| `PLYRA_RATE_LIMIT_RPM` | `600` | no | Requests per minute per API key |
| `PLYRA_CORS_ORIGINS` | `["*"]` | no | Allowed CORS origins |
| `ANTHROPIC_API_KEY` | — | no | Enables server-side LLM fact extraction via Anthropic |
| `OPENAI_API_KEY` | — | no | Enables server-side LLM fact extraction via OpenAI |

## Minimal production .env

```bash
# Required
PLYRA_ADMIN_API_KEY=plm_admin_<strong_random_value>

# Storage paths (Docker volume mounted at /data)
PLYRA_STORE_URL=/data/memory.db
PLYRA_VECTORS_URL=/data/memory.index
PLYRA_KEY_STORE_URL=/data/keys.db

# Environment tag
PLYRA_ENV=production

# Optional: LLM for server-side fact extraction
ANTHROPIC_API_KEY=sk-ant-...
```

## Docker environment

Pass env vars to Docker Compose via `.env` file (auto-loaded)
or inline:

```bash
PLYRA_ADMIN_API_KEY=strong_key \
ANTHROPIC_API_KEY=sk-ant-... \
docker compose up -d
```

## Azure environment

Set via Container Apps secrets and env vars:

```bash
# Create secret
az containerapp secret set \
  --name plyra-memory-server \
  --resource-group plyra-rg \
  --secrets admin-key="plm_admin_strong_key"

# Reference in env vars
az containerapp update \
  --name plyra-memory-server \
  --resource-group plyra-rg \
  --set-env-vars \
    PLYRA_ADMIN_API_KEY=secretref:admin-key \
    PLYRA_ENV=production
```

→ [Full Azure guide](deploy/azure.md)

## LLM extraction

Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` to enable server-side fact extraction.
When set, all `remember()` calls use LLM extraction regardless of client configuration.

→ [LLM extraction guide](guides/llm-extraction.md)

---

← [Quickstart](quickstart.md) · [API reference →](api/index.md)
