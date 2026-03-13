#!/bin/bash
# Stop AI Employee Docker Stack

set -e

echo "🛑 Stopping AI Employee Docker Stack..."

docker compose down

echo "✅ Stack stopped"
