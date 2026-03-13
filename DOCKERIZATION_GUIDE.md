# AI Employee System - Dockerization Guide

**Date:** 2026-03-04
**Goal:** Containerize the entire AI Employee system for local testing and easy cloud deployment
**Estimated Time:** 6-8 hours

---

## 🎯 Why Dockerize First?

**Benefits:**
1. ✅ **Test locally** - Verify everything works before cloud deployment
2. ✅ **Easier debugging** - Separate app issues from cloud issues
3. ✅ **Reproducible** - Same environment everywhere
4. ✅ **Fast deployment** - `docker compose up` on any machine
5. ✅ **No vendor lock-in** - Works on Oracle, AWS, local, anywhere

---

## 📦 What We'll Containerize

### Current System Components

**Python Services:**
- Watchers (Gmail, WhatsApp, Filesystem)
- Orchestrator
- Workflows (CEO Briefing, etc.)
- MCP Servers

**External Services:**
- Odoo Community (accounting)
- PostgreSQL (for Odoo)

**Data:**
- Obsidian Vault (mounted as volume)
- Logs
- Configuration files

---

## 🏗️ Docker Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  Watchers        │  │  Odoo Community  │                 │
│  │  Container       │  │  Container       │                 │
│  │                  │  │                  │                 │
│  │  - Gmail Watcher │  │  - Odoo 19       │                 │
│  │  - WhatsApp      │  │  - Port 8069     │                 │
│  │  - Filesystem    │  │                  │                 │
│  │  - Orchestrator  │  └────────┬─────────┘                 │
│  │  - MCP Servers   │           │                           │
│  └────────┬─────────┘           │                           │
│           │                     │                           │
│           │         ┌───────────▼─────────┐                 │
│           │         │  PostgreSQL         │                 │
│           │         │  Container          │                 │
│           │         │                     │                 │
│           │         │  - Odoo Database    │                 │
│           │         └─────────────────────┘                 │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────────┐                │
│  │         Mounted Volumes                 │                │
│  │                                         │                │
│  │  - AI_Employee_Vault/ (read/write)     │                │
│  │  - logs/ (read/write)                  │                │
│  │  - config/ (read-only)                 │                │
│  └─────────────────────────────────────────┘                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Steps

### Step 1: Create Project Structure (15 minutes)

Create Docker-specific directories:

```bash
cd /mnt/d/AI/Personal-AI-Employee

# Create Docker directories
mkdir -p docker/watchers
mkdir -p docker/odoo
mkdir -p docker/config
mkdir -p docker/scripts

# Create placeholder files
touch docker/watchers/Dockerfile
touch docker/odoo/docker-compose.odoo.yml
touch docker-compose.yml
touch .dockerignore
```

---

### Step 2: Create .dockerignore (5 minutes)

Create `.dockerignore` to exclude unnecessary files:

```bash
cat > .dockerignore << 'EOF'
# Git
.git
.gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Logs
logs/
*.log

# Secrets (NEVER include in Docker images)
.env
.env.*
*.key
*.pem
token.pickle
credentials.json
whatsapp_session/

# Obsidian
.obsidian/

# Documentation (not needed in container)
*.md
!README.md

# Test files
test_*.py
*_test.py

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
tmp/
temp/
*.tmp
EOF
```

---

### Step 3: Create Watchers Dockerfile (30 minutes)

Create `docker/watchers/Dockerfile`:

```dockerfile
# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy requirements first (for layer caching)
COPY watchers/pyproject.toml watchers/uv.lock* ./

# Install Python dependencies
RUN uv pip install --system -r pyproject.toml

# Install additional dependencies for watchers
RUN uv pip install --system \
    google-auth-oauthlib \
    google-auth-httplib2 \
    google-api-python-client \
    playwright \
    watchdog \
    schedule

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY watchers/ ./watchers/
COPY workflows/ ./workflows/
COPY .claude/ ./.claude/

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV VAULT_PATH=/vault

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (can be overridden in docker-compose)
CMD ["python", "watchers/main.py"]
```

---

### Step 4: Create Docker Compose File (45 minutes)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL for Odoo
  postgres:
    image: postgres:15
    container_name: ai-employee-postgres
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo_password_change_me
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ai-employee-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Odoo Community Edition
  odoo:
    image: odoo:19
    container_name: ai-employee-odoo
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8069:8069"
    environment:
      HOST: postgres
      USER: odoo
      PASSWORD: odoo_password_change_me
    volumes:
      - odoo_data:/var/lib/odoo
      - ./docker/odoo/addons:/mnt/extra-addons
      - ./docker/odoo/config:/etc/odoo
    networks:
      - ai-employee-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Watchers and Orchestrator
  watchers:
    build:
      context: .
      dockerfile: docker/watchers/Dockerfile
    container_name: ai-employee-watchers
    depends_on:
      - odoo
    environment:
      # Vault path
      VAULT_PATH: /vault

      # Odoo connection
      ODOO_URL: http://odoo:8069
      ODOO_DB: postgres
      ODOO_USERNAME: admin
      ODOO_PASSWORD: admin

      # Gmail (mount credentials as secrets)
      GMAIL_CREDENTIALS_PATH: /secrets/credentials.json
      GMAIL_TOKEN_PATH: /secrets/token.pickle

      # WhatsApp (mount session as secret)
      WHATSAPP_SESSION_PATH: /secrets/whatsapp_session

      # Logging
      LOG_LEVEL: INFO
      LOG_PATH: /app/logs

      # Python
      PYTHONUNBUFFERED: 1
    volumes:
      # Mount vault (read/write)
      - ./AI_Employee_Vault:/vault

      # Mount logs (read/write)
      - ./logs:/app/logs

      # Mount secrets (read-only)
      - ./secrets:/secrets:ro

      # Mount config (read-only)
      - ./docker/config:/config:ro
    networks:
      - ai-employee-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Health Monitor (optional)
  health-monitor:
    build:
      context: .
      dockerfile: docker/watchers/Dockerfile
    container_name: ai-employee-health-monitor
    depends_on:
      - watchers
      - odoo
    command: ["python", "watchers/health_monitor.py"]
    environment:
      VAULT_PATH: /vault
      LOG_PATH: /app/logs
      CHECK_INTERVAL: 60
    volumes:
      - ./AI_Employee_Vault:/vault
      - ./logs:/app/logs
    networks:
      - ai-employee-network
    restart: unless-stopped

networks:
  ai-employee-network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
  odoo_data:
    driver: local
```

---

### Step 5: Create Secrets Directory (10 minutes)

Create a secrets directory for sensitive files:

```bash
# Create secrets directory
mkdir -p secrets

# Move sensitive files to secrets (if they exist)
# Gmail credentials
if [ -f "watchers/credentials.json" ]; then
    cp watchers/credentials.json secrets/
fi

if [ -f "watchers/token.pickle" ]; then
    cp watchers/token.pickle secrets/
fi

# WhatsApp session
if [ -d "watchers/whatsapp_session" ]; then
    cp -r watchers/whatsapp_session secrets/
fi

# Create .gitignore for secrets
cat > secrets/.gitignore << 'EOF'
# Ignore all files in secrets directory
*

# Except this .gitignore
!.gitignore

# And the README
!README.md
EOF

# Create README for secrets
cat > secrets/README.md << 'EOF'
# Secrets Directory

This directory contains sensitive files that should NEVER be committed to Git.

## Files that go here:
- credentials.json (Gmail OAuth)
- token.pickle (Gmail token)
- whatsapp_session/ (WhatsApp session data)
- .env files with API keys

## Security:
- All files in this directory are git-ignored
- Docker mounts this as read-only volume
- Never commit secrets to version control
EOF
```

---

### Step 6: Create Environment File Template (10 minutes)

Create `.env.template` (for documentation):

```bash
cat > .env.template << 'EOF'
# AI Employee Docker Environment Variables
# Copy this to .env and fill in your values
# NEVER commit .env to Git!

# Odoo Configuration
ODOO_URL=http://odoo:8069
ODOO_DB=postgres
ODOO_USERNAME=admin
ODOO_PASSWORD=change_me_in_production

# PostgreSQL Configuration
POSTGRES_DB=postgres
POSTGRES_USER=odoo
POSTGRES_PASSWORD=change_me_in_production

# Gmail API (paths to mounted secrets)
GMAIL_CREDENTIALS_PATH=/secrets/credentials.json
GMAIL_TOKEN_PATH=/secrets/token.pickle

# WhatsApp
WHATSAPP_SESSION_PATH=/secrets/whatsapp_session

# Anthropic API (for Claude Code)
ANTHROPIC_API_KEY=your_api_key_here

# Logging
LOG_LEVEL=INFO
LOG_PATH=/app/logs

# Vault
VAULT_PATH=/vault
EOF
```

Create actual `.env` file:

```bash
cp .env.template .env
echo "✅ Created .env file - EDIT THIS FILE with your actual values"
```

---

### Step 7: Create Docker Helper Scripts (20 minutes)

Create `docker/scripts/start.sh`:

```bash
cat > docker/scripts/start.sh << 'EOF'
#!/bin/bash
# Start AI Employee Docker Stack

set -e

echo "🚀 Starting AI Employee Docker Stack..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "📝 Copy .env.template to .env and fill in your values"
    exit 1
fi

# Check if secrets directory exists
if [ ! -d secrets ]; then
    echo "❌ Error: secrets/ directory not found"
    echo "📝 Create secrets/ directory and add credentials"
    exit 1
fi

# Build images
echo "🔨 Building Docker images..."
docker compose build

# Start services
echo "▶️  Starting services..."
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check status
echo "📊 Service Status:"
docker compose ps

echo ""
echo "✅ AI Employee Stack Started!"
echo ""
echo "📍 Access Points:"
echo "   - Odoo: http://localhost:8069"
echo "   - Logs: ./logs/"
echo "   - Vault: ./AI_Employee_Vault/"
echo ""
echo "📝 Useful Commands:"
echo "   - View logs: docker compose logs -f"
echo "   - Stop stack: docker compose down"
echo "   - Restart: docker compose restart"
echo "   - Status: docker compose ps"
EOF

chmod +x docker/scripts/start.sh
```

Create `docker/scripts/stop.sh`:

```bash
cat > docker/scripts/stop.sh << 'EOF'
#!/bin/bash
# Stop AI Employee Docker Stack

set -e

echo "🛑 Stopping AI Employee Docker Stack..."

docker compose down

echo "✅ Stack stopped"
EOF

chmod +x docker/scripts/stop.sh
```

Create `docker/scripts/logs.sh`:

```bash
cat > docker/scripts/logs.sh << 'EOF'
#!/bin/bash
# View AI Employee Docker Logs

# Default to all services
SERVICE=${1:-}

if [ -z "$SERVICE" ]; then
    echo "📋 Viewing logs for all services..."
    docker compose logs -f
else
    echo "📋 Viewing logs for $SERVICE..."
    docker compose logs -f $SERVICE
fi
EOF

chmod +x docker/scripts/logs.sh
```

Create `docker/scripts/shell.sh`:

```bash
cat > docker/scripts/shell.sh << 'EOF'
#!/bin/bash
# Open shell in container

SERVICE=${1:-watchers}

echo "🐚 Opening shell in $SERVICE container..."
docker compose exec $SERVICE /bin/bash
EOF

chmod +x docker/scripts/shell.sh
```

---

### Step 8: Update Watchers for Docker (30 minutes)

Create `watchers/main.py` (orchestrator entry point):

```python
#!/usr/bin/env python3
"""
AI Employee Watchers - Main Orchestrator
Runs all watchers in Docker container
"""

import os
import sys
import time
import logging
import signal
from pathlib import Path
from threading import Thread

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import watchers
from watchers.gmail_watcher import GmailWatcher
from watchers.filesystem_watcher import FilesystemWatcher
# from watchers.whatsapp_watcher import WhatsAppWatcher  # Uncomment when ready

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.getenv('LOG_PATH', '/app/logs') + '/orchestrator.log')
    ]
)

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global shutdown_flag
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_flag = True

def run_watcher(watcher_class, *args, **kwargs):
    """Run a watcher in a thread"""
    try:
        watcher = watcher_class(*args, **kwargs)
        logger.info(f"Starting {watcher_class.__name__}...")

        while not shutdown_flag:
            try:
                watcher.run_once()  # Run one iteration
                time.sleep(watcher.check_interval)
            except Exception as e:
                logger.error(f"Error in {watcher_class.__name__}: {e}")
                time.sleep(60)  # Wait before retry

    except Exception as e:
        logger.error(f"Fatal error in {watcher_class.__name__}: {e}")

def main():
    """Main orchestrator"""
    logger.info("🚀 AI Employee Watchers Starting...")

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Get configuration from environment
    vault_path = os.getenv('VAULT_PATH', '/vault')
    gmail_creds = os.getenv('GMAIL_CREDENTIALS_PATH')

    # Verify vault exists
    if not Path(vault_path).exists():
        logger.error(f"Vault not found at {vault_path}")
        sys.exit(1)

    logger.info(f"Using vault at: {vault_path}")

    # Start watchers in threads
    threads = []

    # Filesystem Watcher
    thread = Thread(
        target=run_watcher,
        args=(FilesystemWatcher, vault_path),
        daemon=True
    )
    thread.start()
    threads.append(thread)
    logger.info("✅ Filesystem Watcher started")

    # Gmail Watcher (if credentials available)
    if gmail_creds and Path(gmail_creds).exists():
        thread = Thread(
            target=run_watcher,
            args=(GmailWatcher, vault_path, gmail_creds),
            daemon=True
        )
        thread.start()
        threads.append(thread)
        logger.info("✅ Gmail Watcher started")
    else:
        logger.warning("⚠️  Gmail credentials not found, skipping Gmail Watcher")

    # WhatsApp Watcher (uncomment when ready)
    # whatsapp_session = os.getenv('WHATSAPP_SESSION_PATH')
    # if whatsapp_session and Path(whatsapp_session).exists():
    #     thread = Thread(
    #         target=run_watcher,
    #         args=(WhatsAppWatcher, vault_path, whatsapp_session),
    #         daemon=True
    #     )
    #     thread.start()
    #     threads.append(thread)
    #     logger.info("✅ WhatsApp Watcher started")

    logger.info(f"🎯 All watchers started ({len(threads)} active)")

    # Keep main thread alive
    try:
        while not shutdown_flag:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")

    # Graceful shutdown
    logger.info("🛑 Shutting down watchers...")
    for thread in threads:
        thread.join(timeout=5)

    logger.info("✅ Shutdown complete")

if __name__ == '__main__':
    main()
```

Make it executable:
```bash
chmod +x watchers/main.py
```

---

### Step 9: Test Docker Build (15 minutes)

Test building the Docker images:

```bash
# Build watchers image
docker compose build watchers

# Check image was created
docker images | grep ai-employee

# Test running container (dry run)
docker compose run --rm watchers python --version
# Should output: Python 3.13.x
```

---

### Step 10: Start Docker Stack (15 minutes)

Start the complete stack:

```bash
# Start all services
./docker/scripts/start.sh

# Or manually:
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Check specific service
docker compose logs -f watchers
```

Expected output:
```
✅ AI Employee Stack Started!

📍 Access Points:
   - Odoo: http://localhost:8069
   - Logs: ./logs/
   - Vault: ./AI_Employee_Vault/
```

---

## 📋 Verification Checklist

After completing all steps:

- [ ] Docker Compose file created
- [ ] Dockerfiles created
- [ ] .dockerignore configured
- [ ] secrets/ directory created
- [ ] .env file created and configured
- [ ] Helper scripts created and executable
- [ ] watchers/main.py orchestrator created
- [ ] Docker images build successfully
- [ ] Containers start without errors
- [ ] Odoo accessible at http://localhost:8069
- [ ] Watchers running (check logs)
- [ ] Vault mounted correctly
- [ ] Logs being written

---

## 🧪 Testing the Docker Stack

### Test 1: Verify Containers Running

```bash
docker compose ps

# Expected output:
# NAME                        STATUS
# ai-employee-postgres        Up (healthy)
# ai-employee-odoo            Up (healthy)
# ai-employee-watchers        Up
# ai-employee-health-monitor  Up
```

### Test 2: Test Filesystem Watcher

```bash
# Drop a test file in Inbox
echo "Test expense: $50 for office supplies" > AI_Employee_Vault/Inbox/test_expense.txt

# Check watcher logs
docker compose logs watchers | grep -i "test_expense"

# Check action item created
ls AI_Employee_Vault/Needs_Action/
```

### Test 3: Test Odoo Access

```bash
# Open browser to http://localhost:8069
# Should see Odoo login page
# Default credentials: admin / admin
```

### Test 4: Test Vault Mounting

```bash
# Exec into container
docker compose exec watchers /bin/bash

# Inside container, check vault
ls -la /vault
cat /vault/Dashboard.md

# Exit
exit
```

---

## 🐛 Troubleshooting

### Issue: Containers won't start

```bash
# Check logs
docker compose logs

# Check specific service
docker compose logs watchers

# Rebuild images
docker compose build --no-cache
docker compose up -d
```

### Issue: Permission denied on vault

```bash
# Fix permissions
chmod -R 755 AI_Employee_Vault/
docker compose restart watchers
```

### Issue: Odoo database error

```bash
# Reset Odoo database
docker compose down -v  # WARNING: Deletes all data
docker compose up -d
```

### Issue: Port already in use

```bash
# Check what's using port 8069
lsof -i :8069

# Kill the process or change port in docker-compose.yml
```

---

## 🚀 Next Steps

Once Docker stack is working locally:

1. **Test all features** - Verify watchers, Odoo, workflows
2. **Document any issues** - Note what works and what doesn't
3. **Optimize configuration** - Tune resource limits, intervals
4. **Prepare for cloud** - Docker stack can be deployed anywhere

---

## 📚 Docker Commands Reference

```bash
# Start stack
docker compose up -d

# Stop stack
docker compose down

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f watchers

# Restart service
docker compose restart watchers

# Rebuild and restart
docker compose up -d --build

# Execute command in container
docker compose exec watchers python --version

# Open shell in container
docker compose exec watchers /bin/bash

# Check resource usage
docker stats

# Remove everything (including volumes)
docker compose down -v
```

---

*Dockerization guide created: 2026-03-04*
*Ready to containerize AI Employee system*
