# Server-Side LLM Extraction

Configure the server to use LLM-powered fact extraction for all agents.

## How it works

When `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` is set on the server,
all `remember()` calls use `LLMExtractor` instead of the default regex.
This applies to every agent connecting to this server.

## Configure

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
```

Or for OpenAI:
```bash
OPENAI_API_KEY=sk-...
```

Restart the server after changing:
```bash
docker compose up -d --force-recreate
```

## Verify extraction is running

```bash
# Write a message with implicit preferences
curl -X POST http://localhost:7700/v1/remember \
  -H "Authorization: Bearer plm_live_..." \
  -d '{"content": "I mostly reach for TypeScript these days"}'

# Wait ~1 second for background extraction, then recall
curl -X POST http://localhost:7700/v1/context \
  -H "Authorization: Bearer plm_live_..." \
  -d '{"query": "what language does the user prefer?"}'
# → context should mention TypeScript
```

## Client vs server extraction

| | Client-side | Server-side |
|---|---|---|
| Config | `Memory.with_anthropic(api_key=...)` | `ANTHROPIC_API_KEY` on server |
| Applies to | that agent only | all agents on this server |
| API key | in agent environment | in server environment only |

Server-side is simpler for multi-agent setups — one API key to manage.

→ [LLM extraction docs](https://plyraai.github.io/plyra-memory/extraction/llm/)

---

← [Postgres migration](postgres.md) · [Production checklist →](production.md)
