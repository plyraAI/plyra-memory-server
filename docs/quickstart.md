# Quickstart

## Option A: Use the hosted server (fastest)

No setup required. Get a free API key at [plyra-keys.vercel.app](https://plyra-keys.vercel.app) — enter your email, get a key instantly.

```bash
export PLYRA_SERVER_URL=https://plyra-memory-server.politedesert-a99b9eaf.centralindia.azurecontainerapps.io
export PLYRA_API_KEY=plm_live_...  # from plyra-keys.vercel.app
```

Then use [plyra-memory](https://plyraai.github.io/plyra-memory) normally — it auto-detects the server URL.

---

## Option B: Self-host with Docker

Server running and accepting memory in 3 commands.

## Prerequisites

- Docker + Docker Compose
- [plyra-memory](https://plyraai.github.io/plyra-memory) installed in your agent

## 1. Clone and configure

```bash
git clone https://github.com/plyraAI/plyra-memory-server
cd plyra-memory-server
cp .env.example .env
```

Open `.env` and set a strong admin key:

```bash
PLYRA_ADMIN_API_KEY=plm_admin_your_strong_key_here
```

!!! warning "Change the admin key"
    The default `plm_admin_changeme` is insecure.
    Set a strong random value before exposing the server to any network.

## 2. Start the server

```bash
docker compose up -d
```

Verify it's running:

```bash
curl http://localhost:7700/health
# {"status":"ok","version":"0.1.0","uptime_seconds":1.2,...}
```

## 3. Create your first API key

```bash
curl -X POST http://localhost:7700/admin/keys \
  -H "Authorization: Bearer your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "my-workspace",
    "label": "dev",
    "env": "live"
  }'
```

Response:

```json
{
  "key": "plm_live_a1b2c3d4e5f6g7h8i9j0...",
  "key_id": "abc123",
  "workspace_id": "my-workspace",
  "env": "live"
}
```

!!! warning "Save this key"
    The plaintext key is shown exactly once and never stored.
    Copy it now.

## 4. Connect your agent

Set two environment variables in your agent's environment:

```bash
export PLYRA_SERVER_URL=http://localhost:7700
export PLYRA_API_KEY=plm_live_a1b2c3d4e5f6...
```

Your agent code is **unchanged**:

```python
from plyra_memory import Memory

async with Memory(agent_id="my-agent") as memory:
    await memory.remember("user prefers Python async frameworks")
    ctx = await memory.context_for("what stack does the user use?")
    print(ctx.content)
```

plyra-memory detects `PLYRA_SERVER_URL` and routes all operations to
the server automatically. Local storage is not used.

## Verify end-to-end

```bash
# Write memory via curl
curl -X POST http://localhost:7700/v1/remember \
  -H "Authorization: Bearer plm_live_..." \
  -H "Content-Type: application/json" \
  -d '{"content": "user prefers TypeScript", "agent_id": "test-agent"}'

# Read context via curl
curl -X POST http://localhost:7700/v1/context \
  -H "Authorization: Bearer plm_live_..." \
  -H "Content-Type: application/json" \
  -d '{"query": "what does the user prefer?", "agent_id": "test-agent"}'
```

## Next steps

- [Configuration →](configuration.md) — all env vars
- [API reference →](api/index.md) — full route documentation
- [Azure deployment →](deploy/azure.md) — production hosting

---

**Next:** [Configuration →](configuration.md)
