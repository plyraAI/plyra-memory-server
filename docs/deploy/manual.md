# Manual Deployment

If you cannot use Docker or Azure, you can run the server directly on
any machine with Python 3.11+.

## Prerequisites

- Python 3.11, 3.12, or 3.13
- A supervisor like `systemd` or `pm2`

## 1. Install

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the server
pip install plyra-memory-server
```

## 2. Configure

Set environment variables in your environment or via a `.env` file
in the working directory.

```bash
export PLYRA_ADMIN_API_KEY=plm_admin_your_strong_key_here
export PLYRA_STORE_URL=/path/to/persistent/memory.db
export PLYRA_VECTORS_URL=/path/to/persistent/memory.index
export PLYRA_KEY_STORE_URL=/path/to/persistent/keys.db
export PLYRA_ENV=production
```

## 3. Run

The server includes a built-in CLI powered by Uvicorn.

```bash
plyra-server
```

To bind to all interfaces on port 80:

```bash
PLYRA_HOST=0.0.0.0 PLYRA_PORT=80 plyra-server
```

## 4. systemd service (Linux)

Create `/etc/systemd/system/plyra-server.service`:

```ini
[Unit]
Description=plyra-memory-server
After=network.target

[Service]
User=plyra
Group=plyra
WorkingDirectory=/opt/plyra
EnvironmentFile=/opt/plyra/.env
ExecStart=/opt/plyra/.venv/bin/plyra-server
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable plyra-server
sudo systemctl start plyra-server
```

---

← [Azure](azure.md)
