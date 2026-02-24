# POST /v1/remember

Write content to all memory layers for a workspace/user/agent.

## Request

```
POST /v1/remember
Authorization: Bearer plm_live_...
Content-Type: application/json
```

```json
{
  "content":    "user prefers Python async frameworks",
  "user_id":    "user_xyz",
  "agent_id":   "support-agent",
  "importance": 0.8,
  "source":     "user_message",
  "metadata":   {}
}
```

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `content` | string | yes | — | Content to store. Max 32,000 chars. |
| `user_id` | string | no | null | User namespace within workspace. |
| `agent_id` | string | no | null | Agent namespace within user. |
| `importance` | float | no | `0.6` | Priority 0.0–1.0. Affects working memory eviction. |
| `source` | string | no | null | Content origin. Maps to EpisodeEvent. |
| `metadata` | object | no | `{}` | Arbitrary key-value metadata. |

### Source values

| Value | Maps to |
|-------|---------|
| `user_message` | `USER_MESSAGE` |
| `agent_response` | `AGENT_RESPONSE` |
| `tool_output` | `TOOL_RESULT` |
| `tool_call` | `TOOL_CALL` |
| null | `AGENT_RESPONSE` |

## Response

```json
{
  "working_entry_id": "a1b2c3d4...",
  "episode_id":       "e5f6g7h8...",
  "facts_queued":     true,
  "latency_ms":       8.3
}
```

`facts_queued: true` means fact extraction is running as a background task.
Facts appear in semantic memory within ~500ms.

## Example

```bash
curl -X POST http://localhost:7700/v1/remember \
  -H "Authorization: Bearer plm_live_..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "my name is Alex, I prefer TypeScript",
    "agent_id": "support-agent",
    "source": "user_message",
    "importance": 0.9
  }'
```

---

← [API overview](index.md) · [/v1/recall →](recall.md)
