#!/bin/bash

echo "🤖 Setting up MEMG + Google ADK Integration..."

# Check if MEMG is installed
if ! python -c "import memg" 2>/dev/null; then
    echo "📦 Installing MEMG..."
    pip install memg
fi

# Install Google ADK and dependencies
echo "📦 Installing Google ADK and dependencies..."
pip install google-adk python-dotenv

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Setting up configuration..."
    cat > .env << EOF
# Google Cloud Configuration (optional - ADK can use default credentials)
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional: Specific API key for Gemini
GOOGLE_API_KEY=your_api_key_here
EOF
    echo ""
    echo "⚠️  Configuration created in .env file"
    echo "   - For Google Cloud: Set up Application Default Credentials"
    echo "   - Or add your GOOGLE_API_KEY to .env"
    echo "   - Get API key at: https://ai.google.dev/"
    echo ""
    read -p "Press Enter after you've configured authentication..."
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 Run with ADK: python agent.py"
echo "🚀 Run with Claude: python chat.py" 