# Azure Container Apps

Production deployment on Azure. Managed HTTPS, persistent storage,
scales to zero when idle.

## Prerequisites

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login
az extension add --name containerapp --upgrade
```

## Step 1 — Resource group and environment

```bash
az group create \
  --name plyra-rg \
  --location eastus

az containerapp env create \
  --name plyra-env \
  --resource-group plyra-rg \
  --location eastus
```

## Step 2 — Persistent storage

```bash
# Storage account for SQLite persistence
az storage account create \
  --name plyrastorage$RANDOM \
  --resource-group plyra-rg \
  --sku Standard_LRS \
  --location eastus

# File share (mounted at /data in container)
STORAGE_ACCOUNT=$(az storage account list \
  --resource-group plyra-rg \
  --query "[0].name" -o tsv)

az storage share create \
  --name plyra-data \
  --account-name $STORAGE_ACCOUNT

STORAGE_KEY=$(az storage account keys list \
  --resource-group plyra-rg \
  --account-name $STORAGE_ACCOUNT \
  --query "[0].value" -o tsv)
```

## Step 3 — Admin key secret

```bash
az containerapp env secret set \
  --name plyra-env \
  --resource-group plyra-rg \
  --secrets admin-key="plm_admin_your_strong_key_here"
```

## Step 4 — Deploy

```bash
az containerapp create \
  --name plyra-memory-server \
  --resource-group plyra-rg \
  --environment plyra-env \
  --image ghcr.io/plyraai/plyra-memory-server:latest \
  --target-port 7700 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars \
    PLYRA_ADMIN_API_KEY=secretref:admin-key \
    PLYRA_STORE_URL=/data/memory.db \
    PLYRA_VECTORS_URL=/data/memory.index \
    PLYRA_KEY_STORE_URL=/data/keys.db \
    PLYRA_ENV=production
```

## Step 5 — Get your URL

```bash
az containerapp show \
  --name plyra-memory-server \
  --resource-group plyra-rg \
  --query properties.configuration.ingress.fqdn \
  --output tsv
# → plyra-memory-server.eastus.azurecontainerapps.io
```

## Step 6 — Verify

```bash
SERVER=https://plyra-memory-server.eastus.azurecontainerapps.io

curl $SERVER/health
# {"status":"ok",...}

curl -X POST $SERVER/admin/keys \
  -H "Authorization: Bearer plm_admin_your_strong_key_here" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id":"test","env":"live"}'
```

## Step 7 — Connect your agent

```bash
export PLYRA_SERVER_URL=https://plyra-memory-server.eastus.azurecontainerapps.io
export PLYRA_API_KEY=plm_live_...
```

```python
from plyra_memory import Memory

async with Memory(agent_id="my-agent") as memory:
    await memory.remember("deployed to Azure")
```

## Scaling

```bash
# Adjust min/max replicas
az containerapp update \
  --name plyra-memory-server \
  --resource-group plyra-rg \
  --min-replicas 1 \   # keep warm, no cold start
  --max-replicas 10
```

!!! note "SQLite and multiple replicas"
    SQLite supports only one writer at a time. If you scale beyond
    one replica, migrate to Postgres first.
    → [Postgres migration](../guides/postgres.md)

## Cost estimate

| Component | Free tier | Paid |
|-----------|-----------|------|
| Container Apps | 180,000 vCPU-s/month free | ~$0.000024/vCPU-s |
| Storage account | 5GB free | $0.02/GB |
| File share | included | — |

At low traffic (scales to zero): **~$0–5/month**.

---

← [Docker](docker.md) · [Manual →](manual.md)
