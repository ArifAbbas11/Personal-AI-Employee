#!/bin/bash
# System Status Check Script
# Displays current status of all Platinum Tier services

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.env.production"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "PLATINUM TIER SYSTEM STATUS"
echo "=========================================="
echo ""

# Function to check service status
check_service() {
    local service_name=$1
    local pid_file=$2
    local port=$3

    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $service_name${NC}"
            echo "  PID: $PID"
            if [ -n "$port" ]; then
                echo "  Port: $port"
            fi

            # Check CPU and memory usage
            CPU=$(ps -p "$PID" -o %cpu --no-headers | xargs)
            MEM=$(ps -p "$PID" -o %mem --no-headers | xargs)
            echo "  CPU: ${CPU}%"
            echo "  Memory: ${MEM}%"

            # Check uptime
            START_TIME=$(ps -p "$PID" -o lstart --no-headers)
            echo "  Started: $START_TIME"
            return 0
        else
            echo -e "${RED}✗ $service_name${NC}"
            echo "  Status: Not running (stale PID file)"
            return 1
        fi
    else
        echo -e "${RED}✗ $service_name${NC}"
        echo "  Status: Not running (no PID file)"
        return 1
    fi
    echo ""
}

# Check all services
SERVICES_OK=true

echo "Services:"
echo "----------------------------------------"
check_service "Automation MCP Server" \
    "$LOG_PATH/automation_mcp_server.pid" \
    "$AUTOMATION_MCP_PORT" || SERVICES_OK=false
echo ""

check_service "Multi-Agent MCP Server" \
    "$LOG_PATH/multi_agent_mcp_server.pid" \
    "$MULTI_AGENT_MCP_PORT" || SERVICES_OK=false
echo ""

check_service "Health Monitor" \
    "$LOG_PATH/health_monitor.pid" \
    "" || echo -e "${YELLOW}  (Optional service)${NC}"
echo ""

# System resources
echo "System Resources:"
echo "----------------------------------------"
echo "CPU Cores: $(nproc)"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')"
echo "Memory: $(free -h | grep Mem | awk '{print $3 " / " $2 " (" $3/$2*100 "%)"}')"
echo "Disk: $(df -h /mnt/d/AI/Personal-AI-Employee | tail -1 | awk '{print $3 " / " $2 " (" $5 " used)"}')"
echo ""

# Log files
echo "Recent Logs:"
echo "----------------------------------------"
if [ -d "$LOG_PATH" ]; then
    echo "Log directory: $LOG_PATH"
    ls -lh "$LOG_PATH"/*.log 2>/dev/null | tail -5 || echo "No log files found"
else
    echo "Log directory not found"
fi
echo ""

# Data directories
echo "Data Directories:"
echo "----------------------------------------"
if [ -d "$VAULT_PATH" ]; then
    echo "Vault: $VAULT_PATH"
    du -sh "$VAULT_PATH"/* 2>/dev/null || echo "Empty"
else
    echo "Vault directory not found"
fi
echo ""

# Summary
echo "=========================================="
if [ "$SERVICES_OK" = true ]; then
    echo -e "${GREEN}✓ All services operational${NC}"
else
    echo -e "${YELLOW}⚠ Some services are down${NC}"
    echo ""
    echo "To restart services:"
    echo "  ./deploy_platinum_tier.sh"
fi
echo "=========================================="
