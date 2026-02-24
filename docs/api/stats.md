# GET /v1/stats

Get summary statistics for memory usage across layers.

## Request

```
GET /v1/stats
Authorization: Bearer plm_live_...
```

To filter by user or agent, pass query parameters:

```
GET /v1/stats?user_id=user_xyz&agent_id=support-agent
```

## Response

```json
{
  "total_memories": 125,
  "by_layer": {
    "working": 15,
    "episodic": 80,
    "semantic": 30
  },
  "namespace": {
    "workspace_id": "acme-corp",
    "user_id":      "user_xyz",
    "agent_id":     "support-agent"
  }
}
```

---

← [/v1/context](context.md) · [Admin keys →](admin.md)
