#!/bin/bash
# Open shell in container

SERVICE=${1:-watchers}

echo "🐚 Opening shell in $SERVICE container..."
docker compose exec $SERVICE /bin/bash
