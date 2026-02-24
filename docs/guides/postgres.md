# Postgres Migration

Migrate from SQLite to Postgres for multi-instance deployments.

## When to migrate

Migrate when you need:
- More than one server replica (SQLite allows one writer)
- Managed database backups and point-in-time recovery
- Larger memory datasets (SQLite practical limit ~1GB)

## Setup

```bash
# docker-compose.postgres.yml is included in the repo
POSTGRES_PASSWORD=strong_password \
  docker compose -f docker-compose.postgres.yml up -d
```

The server connects to Postgres automatically when `PLYRA_DATABASE_URL`
is set:

```bash
PLYRA_DATABASE_URL=postgresql://plyra:password@postgres:5432/plyra_memory
```

## Migrate existing data

Automated migration script (coming in v0.2.0):

```bash
# Export from SQLite
plyra-server export --format json > memory_export.json

# Import to Postgres
PLYRA_DATABASE_URL=postgres://... \
  plyra-server import --file memory_export.json
```

For v0.1.0: start fresh with Postgres. SQLite data cannot be migrated automatically yet.

## Azure Postgres

```bash
az postgres flexible-server create \
  --resource-group plyra-rg \
  --name plyra-db \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --admin-user plyra \
  --admin-password $POSTGRES_PASSWORD \
  --database-name plyra_memory
```

---

← [API key management](api-keys.md) · [LLM extraction →](llm-extraction.md)
