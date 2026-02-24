# Admin — API Keys

Create, list, and revoke API keys. Requires `PLYRA_ADMIN_API_KEY`.

## POST /admin/keys — Create key

```bash
curl -X POST http://localhost:7700/admin/keys \
  -H "Authorization: Bearer plm_admin_..." \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id":   "acme-corp",
    "label":          "production agent",
    "env":            "live",
    "rate_limit_rpm": 600
  }'
```

### Request fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workspace_id` | string | yes | Workspace this key belongs to |
| `label` | string | no | Human-readable label |
| `env` | string | no | `live` or `test` (default: `live`) |
| `rate_limit_rpm` | int | no | Override default rate limit |

### Response

```json
{
  "key":          "plm_live_a1b2c3...",
  "key_id":       "abc123def456",
  "workspace_id": "acme-corp",
  "label":        "production agent",
  "env":          "live",
  "created_at":   "2025-11-01T09:00:00Z",
  "is_active":    true
}
```

!!! warning
    `key` is the plaintext value — shown once, never stored.
    Copy it immediately.

---

## GET /admin/keys/{workspace_id} — List keys

```bash
curl http://localhost:7700/admin/keys/acme-corp \
  -H "Authorization: Bearer plm_admin_..."
```

Returns list of `APIKeyInfo` objects. Plaintext key values are never
included — only the first 16 characters as `key_prefix`.

```json
[
  {
    "key_id":       "abc123",
    "workspace_id": "acme-corp",
    "key_prefix":   "plm_live_a1b2c3...",
    "label":        "production agent",
    "env":          "live",
    "created_at":   "2025-11-01T09:00:00Z",
    "last_used_at": "2025-11-15T14:23:00Z",
    "is_active":    true
  }
]
```

---

## DELETE /admin/keys/{key_id} — Revoke key

```bash
curl -X DELETE http://localhost:7700/admin/keys/abc123 \
  -H "Authorization: Bearer plm_admin_..."
```

```json
{"revoked": true, "key_id": "abc123"}
```

Revoked keys return `401` immediately on next use.
Revocation is instant — no propagation delay.

→ [Key management guide](../guides/api-keys.md)

---

← [/v1/stats](stats.md) · [Deployment →](../deploy/index.md)
