# Changelog

## v0.1.0

- FastAPI server on port 7700
- API key authentication (SHA-256 hashed, SQLite key store)
- Workspace → user → agent isolation
- Routes: `/v1/remember`, `/v1/recall`, `/v1/context`, `/v1/stats`
- Admin routes: `/admin/keys` (create, list, revoke)
- Docker image with pre-baked sentence-transformers model
- `docker-compose.yml` (SQLite) and `docker-compose.postgres.yml`
- HTTP backend in plyra-memory library (auto-detect via env vars)
- 21 tests passing on Python 3.11, 3.12, 3.13

---

[GitHub releases](https://github.com/plyraAI/plyra-memory-server/releases)
