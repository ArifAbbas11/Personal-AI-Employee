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
