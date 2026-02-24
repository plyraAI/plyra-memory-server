# POST /v1/recall

Search memory by semantic similarity. Returns ranked results from all layers.

## Request

```
POST /v1/recall
Authorization: Bearer plm_live_...
Content-Type: application/json
```

```json
{
  "query":    "what does the user prefer?",
  "user_id":  "user_xyz",
  "agent_id": "support-agent",
  "top_k":    10,
  "layers":   ["working", "episodic", "semantic"]
}
```

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | yes | — | Semantic search query |
| `user_id` | string | no | null | Filter to this user namespace |
| `agent_id` | string | no | null | Filter to this agent namespace |
| `top_k` | int | no | `10` | Max results. Range: 1–100. |
| `layers` | array | no | all | Layers to search: `working`, `episodic`, `semantic` |

## Response

```json
{
  "query":       "what does the user prefer?",
  "results":     [...],
  "total_found": 5,
  "cache_hit":   false,
  "latency_ms":  14.2
}
```

Each result in `results` is a ranked memory entry with `score`, `content`,
`layer`, `created_at`, and any stored metadata.

## Example

```bash
curl -X POST http://localhost:7700/v1/recall \
  -H "Authorization: Bearer plm_live_..." \
  -H "Content-Type: application/json" \
  -d '{"query": "what does the user prefer?", "top_k": 5}'
```

---

← [/v1/remember](remember.md) · [/v1/context →](context.md)
