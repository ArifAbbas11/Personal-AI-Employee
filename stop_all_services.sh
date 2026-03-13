#!/bin/bash
# Stop All Services Script
# This script stops all Platinum Tier services

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.env.production"

echo "Stopping Platinum Tier Services..."
echo "=================================="

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file=$2

    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Stopping $service_name (PID: $PID)..."
            kill "$PID"

            # Wait for process to stop
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    echo "✓ $service_name stopped"
                    rm -f "$pid_file"
                    return 0
                fi
                sleep 1
            done

            # Force kill if still running
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "Force stopping $service_name..."
                kill -9 "$PID"
                rm -f "$pid_file"
                echo "✓ $service_name force stopped"
            fi
        else
            echo "✓ $service_name not running"
            rm -f "$pid_file"
        fi
    else
        echo "✓ $service_name not running (no PID file)"
    fi
}

# Stop all services
stop_service "Automation MCP Server" "$LOG_PATH/automation_mcp_server.pid"
stop_service "Multi-Agent MCP Server" "$LOG_PATH/multi_agent_mcp_server.pid"
stop_service "Health Monitor" "$LOG_PATH/health_monitor.pid"

echo ""
echo "=================================="
echo "All services stopped"
