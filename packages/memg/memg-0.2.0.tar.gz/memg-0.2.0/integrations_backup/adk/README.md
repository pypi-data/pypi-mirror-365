# 🤖 MEMG Integrations

Two simple examples showing how to integrate MEMG with AI frameworks.

## 🚀 Quick Start

```bash
# Install MEMG
pip install memg

# Run the setup
./setup.sh

# Choose your integration:
python agent.py    # Google ADK integration
python chat.py     # Anthropic Claude integration
```

## 📁 Files

- `setup.sh` - Installs dependencies for both integrations
- `agent.py` - Google ADK + MEMG (proper ADK agent with tools)
- `chat.py` - Anthropic Claude + MEMG (direct API integration)
- `claude_memory.py` - Claude integration logic

## 🤖 Google ADK Integration (`agent.py`)

Uses Google's Agent Development Kit with proper ADK patterns:
- `LlmAgent` with Gemini models
- `FunctionTool` classes for memory operations
- `InMemoryRunner` for execution
- Proper ADK architecture

**Memory Tools:**
- `add_memory(content)` - Store information
- `search_memories(query)` - Find relevant memories

## 🧠 Claude Integration (`chat.py`)

Direct Anthropic API integration:
- Claude 3.5 Sonnet with tools
- Tool calling for memory operations
- Simple CLI chat interface

## 🔧 Setup

**For Google ADK:**
1. Set up Google Cloud authentication
2. Or add `GOOGLE_API_KEY` to `.env`

**For Claude:**
1. Get Anthropic API key
2. Add `ANTHROPIC_API_KEY` to `.env`

Both show the same core pattern: **pip install memg** + expose memory as AI tools. 