#!/bin/bash

# 🚀 Start MCP Server with google-genai
# This script ensures the virtual environment is activated and the server runs correctly

echo "🚀 Starting MemG MCP Server with lovely google-genai..."
echo "📦 Using google-genai (NOT the deprecated google-generativeai)"

# Activate virtual environment
source .venv/bin/activate

# Configure local storage to avoid conflicts
export QDRANT_STORAGE_PATH="./memg_data/qdrant"
export KUZU_DB_PATH="./memg_data/kuzu"
export LOG_FILE_PATH="./memg_data/logs/memg.log"

# Create storage directories
mkdir -p memg_data/{qdrant,kuzu,logs}

# Kill any conflicting processes (optional cleanup)
echo "🧹 Cleaning up any conflicting processes..."
pkill -f "mcp_server.py" 2>/dev/null || true
sleep 1

# Check dependencies
echo "🔍 Checking google-genai..."
python -c "from google import genai; print('✅ google-genai working!')" || {
    echo "❌ google-genai not working. Run: pip install -r requirements.txt"
    exit 1
}

# Check environment
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
google_key = os.getenv('GOOGLE_API_KEY')
if google_key:
    print('✅ GOOGLE_API_KEY configured')
else:
    print('❌ GOOGLE_API_KEY missing in .env file')
    exit(1)
"

echo "📁 Using local storage: ./memg_data/"
echo "🎯 Starting MCP server on port 8787..."
echo "📖 Visit http://localhost:8787/health for health check"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Start the server
cd src && python mcp_server.py
