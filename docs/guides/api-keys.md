# API Key Management

Key lifecycle, rotation, and security best practices.

## Key format

```
plm_live_<48 hex chars>    production
plm_test_<48 hex chars>    development / testing
```

`plm` = plyra memory. `live` vs `test` is informational — the server
does not enforce different behaviour based on env, but it helps you
track which keys belong to which environment.

## Creating keys

```bash
curl -X POST http://localhost:7700/admin/keys \
  -H "Authorization: Bearer $PLYRA_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "acme-corp",
    "label": "production — support agent",
    "env": "live"
  }'
```

Create one key per:
- Agent (tightest isolation)
- Environment (dev key, staging key, production key)
- Team or workspace (customer-level isolation)

## Revoking keys

```bash
# List keys for a workspace to get key_id
curl http://localhost:7700/admin/keys/acme-corp \
  -H "Authorization: Bearer $PLYRA_ADMIN_KEY"

# Revoke by key_id
curl -X DELETE http://localhost:7700/admin/keys/{key_id} \
  -H "Authorization: Bearer $PLYRA_ADMIN_KEY"
```

Revocation is instant. The revoked key returns `401` on next use.

## Key rotation

Rotate production keys periodically or after any suspected compromise:

```bash
# 1. Create new key
NEW_KEY=$(curl -X POST http://localhost:7700/admin/keys \
  -H "Authorization: Bearer $PLYRA_ADMIN_KEY" \
  -d '{"workspace_id":"acme","label":"rotated key"}' | jq -r .key)

# 2. Update env var in your agent deployment
# 3. Redeploy agents with new key
# 4. Verify agents are using new key
# 5. Revoke old key
curl -X DELETE http://localhost:7700/admin/keys/{old_key_id} \
  -H "Authorization: Bearer $PLYRA_ADMIN_KEY"
```

## Security checklist

- Never commit API keys to git
- Use environment variables or secrets managers (Azure Key Vault, etc.)
- Set `PLYRA_ADMIN_API_KEY` to a strong random value before deployment
- Use separate keys for dev, staging, production
- Revoke unused keys

---

← [Workspace isolation](isolation.md) · [Postgres migration →](postgres.md)
