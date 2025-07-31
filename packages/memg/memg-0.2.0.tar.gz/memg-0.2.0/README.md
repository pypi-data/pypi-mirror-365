# MEMG - Memory Management System

A lightweight, local-first memory system for developers and applications. Built with Qdrant vector database and Kuzu graph database for efficient memory storage and retrieval.

## Project Status

**Current Phase**: Foundation Complete (Planning & Architecture Complete)
**Next Phase**: Phase 1 - Minimum Viable Memory (Implementation)

- Enterprise system archived
- Architecture documented 
- Smart prompts implemented for memory extraction
- Core database interfaces implemented (Qdrant + Kuzu)
- Environment configuration centralized
- Memory processing pipeline in development

## What This Will Be

A personal memory system that:
- **Stores coding knowledge** without cloud dependencies
- **Connects related memories** automatically
- **Provides fast, relevant search** with local embeddings
- **Integrates with development workflow** through APIs and CLI
- **Respects privacy** with local-first architecture

## Architecture Overview

### Target Stack (Local-First)
- **Storage**: SQLite → SQLite+vectors → SQLite+vectors+Kuzu
- **Embeddings**: FastEmbed (384-dim, 200MB footprint)
- **API**: FastAPI + FastMCP servers
- **Deployment**: Single Docker container

### Current Assets
- **Smart Prompts**: Context-aware memory extraction (in `src/memory_system/prompts/`)
- **Architecture**: Complete technical specifications
- **Data Organization**: Structured folders for memories and conversations

## Development Roadmap

**Phase 1 (2-3 weeks)**: Basic local memory with SQLite + text search
**Phase 2 (2-3 weeks)**: Add semantic search with FastEmbed
**Phase 3 (2-3 weeks)**: Graph relationships with Kuzu
**Phase 4 (1-2 weeks)**: Developer integration and polish

See `DEVELOPMENT_ROADMAP.md` for detailed implementation plan.

## Use Cases

1. **Smart Development Database** ⭐⭐⭐⭐⭐ - Perfect fit
2. **AI Coder Documentation** ⭐⭐⭐⭐ - Leverages technical prompts
3. **Personal Memory System** ⭐⭐⭐ - Original vision
4. **Note Taking** ⭐⭐ - Underutilizes architecture
5. **Todo Lists** ⭐ - Wrong tool for the job

## Current Files

```
├── PERSONAL_MEMORY_SYSTEM.md # Vision and architecture
├── TECHNICAL_SPEC.md # Detailed technical specs
├── CURRENT_STATUS.md # Implementation assessment
├── DEVELOPMENT_ROADMAP.md # Phase-by-phase plan
├── src/memory_system/prompts/ # Smart memory extraction prompts
├── legacy_memory_enterprise_system.zip # Archived working system
└── [data folders] # Ready for implementation
```

## Getting Started

### Quick Start

**Easy startup with the provided script:**
```bash
# Clone and setup
git clone https://github.com/genovo-ai/memg.git
cd memg
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Start the system (recommended)
./start_memory_server.sh
```

**Manual startup:**
```bash
export KUZU_DB_PATH="$HOME/.local/share/memory_system/kuzu/memory_db"
export QDRANT_PATH="$HOME/.local/share/memory_system/qdrant"
export GOOGLE_API_KEY="your-api-key" # Optional
python -m src.memory_system.mcp_server
```

**Verify system:**
```bash
curl http://localhost:8787/
```

### Configuration (Alternative)

Create a `.env` file with the required configuration:

```bash
GOOGLE_API_KEY=your_api_key_here
KUZU_DB_PATH=$HOME/.local/share/memory_system/kuzu/memory_db
QDRANT_PATH=$HOME/.local/share/memory_system/qdrant
MEMORY_SYSTEM_MCP_PORT=8787
```

### Interface Status 

- **QdrantInterface**: Cloud-ready with .env configuration
- **KuzuInterface**: Single database path from .env
- **All tests passing**: Core database operations verified
- **No hardcoded values**: Configuration centralized

**Next Steps**:
1. Add embeddings service (Google AI or FastEmbed)
2. Implement memory processing pipeline
3. Build FastAPI endpoints

## Why This Approach

The archived enterprise system (Memory + Neo4j + cloud services) works but is overkill for personal use:
- 4GB+ RAM requirements
- Cloud dependencies and costs
- Complex deployment
- Poor response quality (JSON dumps)

This rebuild prioritizes:
- **Local-first**: Your data stays yours
- **Lightweight**: <500MB footprint
- **Fast**: Sub-second responses
- **Clean**: Useful answers, not JSON vomit
- **Simple**: Single container deployment

---

*From planning to daily-use tool in 8-10 weeks.*
