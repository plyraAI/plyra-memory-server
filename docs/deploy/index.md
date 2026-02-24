# Deployment

plyra-memory-server ships as a Docker image. Three deployment paths:

| Path | Use case | Complexity |
|------|----------|------------|
| [Docker Compose](docker.md) | Local, single server, dev | Low |
| [Azure Container Apps](azure.md) | Production, scalable, managed | Medium |
| [Manual](manual.md) | Custom environments, no Docker | Low |

## Which to choose

**Docker Compose** — start here. Works on any machine with Docker.
SQLite for storage, zero external dependencies.
Upgrade to Postgres when you need multi-instance.

**Azure Container Apps** — production deployment. Managed HTTPS,
persistent volume, scales to zero when idle, ~$5–15/month at low traffic.

**Manual** — for environments where Docker isn't available.
`pip install plyra-memory-server` then `plyra-server`.

---

[Docker →](docker.md) · [Azure →](azure.md) · [Manual →](manual.md)
