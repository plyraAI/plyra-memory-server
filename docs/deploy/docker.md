# Docker Deployment

## SQLite (default — zero dependencies)

```bash
git clone https://github.com/plyraAI/plyra-memory-server
cd plyra-memory-server
cp .env.example .env
# Edit .env — set PLYRA_ADMIN_API_KEY

docker compose up -d
```

Data persists in a named Docker volume (`plyra_data`).

```bash
# Check status
docker compose ps
docker compose logs memory-server --tail 20

# Stop
docker compose down

# Stop and delete data
docker compose down -v
```

## Postgres (multi-instance)

```bash
# Set a strong Postgres password
echo "POSTGRES_PASSWORD=strong_password" >> .env

docker compose -f docker-compose.postgres.yml up -d
```

Postgres data persists in `postgres_data` volume.
Memory server connects automatically on startup.

## Update to new version

```bash
docker compose pull
docker compose up -d
```

## Persistent volume location

```bash
# Find volume mount on host
docker volume inspect plyra_data
```

Default: `/var/lib/docker/volumes/plyra_data/_data/`

→ [Postgres migration guide](../guides/postgres.md)

---

← [Deploy overview](index.md) · [Azure →](azure.md)
