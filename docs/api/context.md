# POST /v1/context

Get a prompt-ready context string. Call this before every LLM invocation.

## Request

```
POST /v1/context
Authorization: Bearer plm_live_...
Content-Type: application/json
```

```json
{
  "query":        "what is the user working on?",
  "user_id":      "user_xyz",
  "agent_id":     "support-agent",
  "token_budget": 2048
}
```

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | yes | — | What to retrieve. Usually the user's message. |
| `user_id` | string | no | null | Namespace filter |
| `agent_id` | string | no | null | Namespace filter |
| `token_budget` | int | no | `2048` | Max tokens in returned context. Range: 64–32,000. |

## Response

```json
{
  "query":         "what is the user working on?",
  "content":       "[WORKING MEMORY]\nuser asked about deployment...\n\n[SEMANTIC]\nuser WORKS_ON LangGraph agent",
  "token_count":   142,
  "token_budget":  2048,
  "memories_used": 4,
  "cache_hit":     false,
  "latency_ms":    11.7
}
```

Inject `content` into your LLM system prompt:

```python
ctx = await client.post("/v1/context", json={"query": user_message}).json()

prompt = f"""You are a helpful assistant.

{ctx['content']}

User: {user_message}"""
```

## Example

```bash
curl -X POST http://localhost:7700/v1/context \
  -H "Authorization: Bearer plm_live_..." \
  -H "Content-Type: application/json" \
  -d '{"query": "what is the user building?", "token_budget": 1024}'
```

---

← [/v1/recall](recall.md) · [/v1/stats →](stats.md)
