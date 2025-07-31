#!/bin/bash
# Memory System Startup Script
# Automatically sets environment variables and starts the MCP server

# Set required environment variables
export KUZU_DB_PATH="$HOME/.local/share/memory_system/kuzu/memory_db"
export QDRANT_PATH="$HOME/.local/share/memory_system/qdrant"
export MEMORY_SYSTEM_MCP_PORT=8787

# Create directories if they don't exist
mkdir -p "$(dirname "$KUZU_DB_PATH")"
mkdir -p "$QDRANT_PATH"

echo "🚀 Starting Memory System MCP Server..."
echo "📂 Kuzu DB: $KUZU_DB_PATH"
echo "📂 Qdrant: $QDRANT_PATH"
echo "🌐 Port: $MEMORY_SYSTEM_MCP_PORT"
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not detected. Activating venv..."
    source venv/bin/activate
fi

# Start the server
python -m src.memory_system.mcp_server
