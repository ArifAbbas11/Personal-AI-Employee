#!/bin/bash
# Automated Odoo Deployment Script
# Deploys Odoo ERP with Accounting module for AI Employee integration

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ODOO_VERSION="${ODOO_VERSION:-14}"
ODOO_PORT="${ODOO_PORT:-8069}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
ODOO_DB="${ODOO_DB:-odoo_db}"
ODOO_USER="${ODOO_USER:-admin}"
ODOO_PASSWORD="${ODOO_PASSWORD:-admin}"
CONFIG_FILE="AI_Employee_Vault/Config/odoo_config.json"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Odoo Automated Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Docker is running
docker_running() {
    docker info >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local max_attempts=30
    local attempt=0

    echo -e "${YELLOW}Waiting for service at $host:$port...${NC}"

    while [ $attempt -lt $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            echo -e "${GREEN}✓ Service is ready${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    echo -e "${RED}✗ Service failed to start${NC}"
    return 1
}

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites${NC}"
echo "-----------------------------------"

if ! command_exists docker; then
    echo -e "${RED}✗ Docker not found${NC}"
    echo ""
    echo "Please install Docker first:"
    echo "  Ubuntu/Debian: sudo apt-get install docker.io"
    echo "  macOS: brew install docker"
    echo "  Or visit: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

if ! docker_running; then
    echo -e "${RED}✗ Docker daemon not running${NC}"
    echo ""
    echo "Please start Docker:"
    echo "  sudo systemctl start docker"
    exit 1
fi
echo -e "${GREEN}✓ Docker daemon running${NC}"

if ! command_exists nc; then
    echo -e "${YELLOW}⚠ netcat not found (optional for connection testing)${NC}"
fi

echo ""

# Step 2: Check for existing Odoo installation
echo -e "${BLUE}Step 2: Checking for existing installation${NC}"
echo "-----------------------------------"

if docker ps -a | grep -q "odoo"; then
    echo -e "${YELLOW}⚠ Existing Odoo container found${NC}"
    read -p "Remove existing container? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker stop odoo 2>/dev/null || true
        docker rm odoo 2>/dev/null || true
        echo -e "${GREEN}✓ Removed existing Odoo container${NC}"
    else
        echo -e "${YELLOW}Keeping existing container${NC}"
    fi
fi

if docker ps -a | grep -q "odoo-db"; then
    echo -e "${YELLOW}⚠ Existing PostgreSQL container found${NC}"
    read -p "Remove existing database container? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker stop odoo-db 2>/dev/null || true
        docker rm odoo-db 2>/dev/null || true
        echo -e "${GREEN}✓ Removed existing database container${NC}"
    else
        echo -e "${YELLOW}Keeping existing database container${NC}"
    fi
fi

echo ""

# Step 3: Deploy PostgreSQL
echo -e "${BLUE}Step 3: Deploying PostgreSQL database${NC}"
echo "-----------------------------------"

if ! docker ps | grep -q "odoo-db"; then
    echo "Starting PostgreSQL container..."
    docker run -d \
        --name odoo-db \
        -e POSTGRES_USER=odoo \
        -e POSTGRES_PASSWORD=odoo \
        -e POSTGRES_DB=postgres \
        -p ${POSTGRES_PORT}:5432 \
        postgres:13

    echo -e "${GREEN}✓ PostgreSQL container started${NC}"

    # Wait for PostgreSQL to be ready
    sleep 5
else
    echo -e "${GREEN}✓ PostgreSQL already running${NC}"
fi

echo ""

# Step 4: Deploy Odoo
echo -e "${BLUE}Step 4: Deploying Odoo${NC}"
echo "-----------------------------------"

if ! docker ps | grep -q "odoo"; then
    echo "Starting Odoo container..."
    docker run -d \
        --name odoo \
        --link odoo-db:db \
        -p ${ODOO_PORT}:8069 \
        -e HOST=db \
        -e USER=odoo \
        -e PASSWORD=odoo \
        odoo:${ODOO_VERSION}

    echo -e "${GREEN}✓ Odoo container started${NC}"

    # Wait for Odoo to be ready
    echo "Waiting for Odoo to initialize (this may take 1-2 minutes)..."
    sleep 30

    if command_exists nc; then
        wait_for_service localhost ${ODOO_PORT}
    else
        echo -e "${YELLOW}⚠ Waiting 30 more seconds for Odoo to start...${NC}"
        sleep 30
    fi
else
    echo -e "${GREEN}✓ Odoo already running${NC}"
fi

echo ""

# Step 5: Create database and install Accounting module
echo -e "${BLUE}Step 5: Setting up Odoo database${NC}"
echo "-----------------------------------"

echo "Odoo is now accessible at: http://localhost:${ODOO_PORT}"
echo ""
echo -e "${YELLOW}Manual steps required:${NC}"
echo "1. Open http://localhost:${ODOO_PORT} in your browser"
echo "2. Create a new database:"
echo "   - Master Password: admin"
echo "   - Database Name: ${ODOO_DB}"
echo "   - Email: admin@example.com"
echo "   - Password: ${ODOO_PASSWORD}"
echo "   - Language: English"
echo "   - Country: Your country"
echo "3. After database creation, install the 'Accounting' module"
echo "4. Go to Settings > Users & Companies > Users"
echo "5. Create an API user with Accounting permissions"
echo ""
read -p "Press Enter when you've completed these steps..."

echo ""

# Step 6: Create configuration file
echo -e "${BLUE}Step 6: Creating configuration file${NC}"
echo "-----------------------------------"

# Ensure config directory exists
mkdir -p "$(dirname "$CONFIG_FILE")"

# Check if config file already exists
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}⚠ Configuration file already exists${NC}"
    read -p "Overwrite? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Keeping existing configuration${NC}"
        echo ""
        echo -e "${BLUE}Step 7: Testing connection${NC}"
        echo "-----------------------------------"
        python3 watchers/odoo_mcp_server.py --test
        exit 0
    fi
fi

# Prompt for configuration details
echo "Enter Odoo configuration details:"
read -p "Odoo URL [http://localhost:${ODOO_PORT}]: " ODOO_URL
ODOO_URL=${ODOO_URL:-http://localhost:${ODOO_PORT}}

read -p "Database name [${ODOO_DB}]: " DB_NAME
DB_NAME=${DB_NAME:-${ODOO_DB}}

read -p "Username [${ODOO_USER}]: " USERNAME
USERNAME=${USERNAME:-${ODOO_USER}}

read -sp "Password [${ODOO_PASSWORD}]: " PASSWORD
PASSWORD=${PASSWORD:-${ODOO_PASSWORD}}
echo ""

# Create configuration file
cat > "$CONFIG_FILE" << EOF
{
  "url": "${ODOO_URL}",
  "db": "${DB_NAME}",
  "username": "${USERNAME}",
  "password": "${PASSWORD}",
  "api_key": ""
}
EOF

chmod 600 "$CONFIG_FILE"
echo -e "${GREEN}✓ Configuration file created: $CONFIG_FILE${NC}"

echo ""

# Step 7: Test connection
echo -e "${BLUE}Step 7: Testing connection${NC}"
echo "-----------------------------------"

if python3 watchers/odoo_mcp_server.py --test 2>/dev/null; then
    echo -e "${GREEN}✓ Connection test successful${NC}"
else
    echo -e "${RED}✗ Connection test failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Verify Odoo is running: docker ps | grep odoo"
    echo "2. Check Odoo logs: docker logs odoo"
    echo "3. Verify database was created in Odoo web interface"
    echo "4. Verify credentials in $CONFIG_FILE"
    exit 1
fi

echo ""

# Step 8: Run test suite
echo -e "${BLUE}Step 8: Running test suite${NC}"
echo "-----------------------------------"

if [ -f "test_odoo_integration.sh" ]; then
    bash test_odoo_integration.sh
else
    echo -e "${YELLOW}⚠ Test suite not found (test_odoo_integration.sh)${NC}"
fi

echo ""

# Step 9: Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Odoo Deployment Complete${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Odoo is now running and configured!"
echo ""
echo "Access Odoo:"
echo "  URL: http://localhost:${ODOO_PORT}"
echo "  Database: ${DB_NAME}"
echo "  Username: ${USERNAME}"
echo ""
echo "Configuration:"
echo "  File: $CONFIG_FILE"
echo ""
echo "Docker containers:"
echo "  Odoo: docker logs odoo"
echo "  PostgreSQL: docker logs odoo-db"
echo ""
echo "To stop Odoo:"
echo "  docker stop odoo odoo-db"
echo ""
echo "To start Odoo:"
echo "  docker start odoo-db odoo"
echo ""
echo "To remove Odoo:"
echo "  docker stop odoo odoo-db"
echo "  docker rm odoo odoo-db"
echo ""
echo "Next steps:"
echo "1. Generate CEO Briefing with financial data:"
echo "   python3 watchers/simple_ceo_briefing.py"
echo ""
echo "2. Create test invoice:"
echo "   python3 -c 'from watchers.odoo_mcp_server import OdooMCPServer; server = OdooMCPServer(); print(server.create_invoice(partner_id=1, amount=100.00, description=\"Test\"))'"
echo ""
echo "3. Get financial report:"
echo "   python3 -c 'from watchers.odoo_mcp_server import OdooMCPServer; server = OdooMCPServer(); print(server.get_financial_report(\"2026-02-01\", \"2026-02-28\"))'"
echo ""
