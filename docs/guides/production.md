# Production Checklist

Before going to production with plyra-memory-server.

## Security

- [ ] `PLYRA_ADMIN_API_KEY` changed from default
- [ ] Admin key stored in secrets manager (Azure Key Vault, etc.)
- [ ] HTTPS enforced (Azure Container Apps handles this automatically)
- [ ] CORS origins restricted if server is public-facing
- [ ] No API keys committed to git

## Storage

- [ ] Persistent volume mounted at `/data`
- [ ] Volume backed up regularly (Azure File Share snapshots)
- [ ] If running multiple replicas: Postgres configured

## Monitoring

- [ ] `/health` endpoint monitored (Azure health probe configured)
- [ ] Container logs routed to Log Analytics or similar
- [ ] Alert on 5xx error rate

## Performance

- [ ] `PLYRA_RATE_LIMIT_RPM` tuned for expected load
- [ ] Min replicas set to 1 if cold start latency is unacceptable
- [ ] `ANTHROPIC_API_KEY` set if LLM extraction is needed

## Verification

```bash
# Health check
curl https://your-server/health

# Create a test key
curl -X POST https://your-server/admin/keys \
  -H "Authorization: Bearer $ADMIN_KEY" \
  -d '{"workspace_id":"smoke-test","env":"test"}'

# Write and read
curl -X POST https://your-server/v1/remember \
  -H "Authorization: Bearer $TEST_KEY" \
  -d '{"content":"production smoke test"}'

curl -X POST https://your-server/v1/context \
  -H "Authorization: Bearer $TEST_KEY" \
  -d '{"query":"smoke test","token_budget":128}'

# Revoke test key
curl -X DELETE https://your-server/admin/keys/{key_id} \
  -H "Authorization: Bearer $ADMIN_KEY"
```

---

← [LLM extraction](llm-extraction.md) · [Home →](../index.md)
