#!/usr/bin/env python3
"""
Production Memory System MCP Server
Clean implementation using sync wrapper - like Mem0 pattern
"""

from fastmcp import FastMCP

from memory_system.exceptions import (
    ConfigurationError,
    MCPError,
    ProcessingError,
    ValidationError,
    wrap_exception,
)
from memory_system.logging_config import get_logger, log_error, log_operation
from memory_system.sync_wrapper import SyncMemorySystem

# Environment loading handled by individual interfaces

# Set up logging
logger = get_logger("mcp_server")

# Initialize memory system - like Mem0
try:
    memory = SyncMemorySystem()
    logger.info("Memory system initialized successfully")
except (ConfigurationError, FileNotFoundError, PermissionError) as e:
    log_error("mcp_server", "system_initialization", e)
    memory = None
    raise MCPError(
        "Configuration error during memory system initialization",
        operation="system_initialization",
        original_error=e,
    )
except Exception as e:
    log_error("mcp_server", "system_initialization", e)
    memory = None
    raise MCPError(
        "Failed to initialize memory system",
        operation="system_initialization",
        original_error=e,
    )

# Initialize MCP server - EXACT legacy pattern
app = FastMCP()


# Add health check endpoints for Docker health checks
@app.custom_route("/", methods=["GET"])
async def root_health_check(request):
    """Root endpoint for basic health check"""
    from starlette.responses import JSONResponse

    return JSONResponse({"status": "healthy", "service": "g^mem v0.2 MCP Server"})


@app.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Detailed health check endpoint"""
    from starlette.responses import JSONResponse

    health_status = {
        "status": "healthy",
        "service": "g^mem v0.2 MCP Server",
        "version": "v0.2",
        "memory_system_initialized": memory is not None,
    }

    if memory:
        try:
            stats = memory.get_stats()
            health_status.update(
                {
                    "components": {
                        "processor": stats.get("processor_initialized", False),
                        "retriever": stats.get("retriever_initialized", False),
                        "qdrant": stats.get("qdrant_available", False),
                        "kuzu": stats.get("kuzu_available", False),
                    }
                }
            )
        except (ConfigurationError, ProcessingError) as e:
            health_status["status"] = "degraded"
            health_status["error"] = f"Configuration/processing error: {str(e)}"
            log_error("mcp_server", "health_check", e)
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["error"] = f"Unexpected error: {str(e)}"
            log_error("mcp_server", "health_check", e)
    else:
        health_status["status"] = "unhealthy"
        health_status["error"] = "Memory system not initialized"

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(health_status, status_code=status_code)


@app.tool("add_memory")
def add_memory(
    content: str,
    memory_type: str = None,
    source: str = "mcp_api",
    title: str = None,
    tags: str = None,
):
    """
    Add a memory to the g^mem system with optional type specification.

    Args:
        content: The memory content to store
        memory_type: Optional memory type - 'document', 'note', or 'conversation'.
                    If not specified, AI will auto-detect based on content.
        source: Source identifier for the memory (default: 'mcp_api')
        title: Optional title for the memory
        tags: Optional comma-separated tags for the memory

    Returns:
        Success/failure message with processing details
    """
    try:
        if not memory:
            return {"result": "❌ Memory system not initialized"}

        # Parse memory_type
        from memory_system.models.core import MemoryType

        parsed_memory_type = None
        if memory_type:
            try:
                if memory_type.upper() == "DOCUMENT":
                    parsed_memory_type = MemoryType.DOCUMENT
                elif memory_type.upper() == "NOTE":
                    parsed_memory_type = MemoryType.NOTE
                elif memory_type.upper() == "CONVERSATION":
                    parsed_memory_type = MemoryType.CONVERSATION
                else:
                    return {
                        "result": f"❌ Invalid memory_type: {memory_type}. Use 'document', 'note', or 'conversation'"
                    }
            except Exception:
                return {"result": f"❌ Invalid memory_type: {memory_type}"}

        # Parse tags
        parsed_tags = []
        if tags:
            parsed_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # Use the full API
        response = memory.add(
            content=content,
            memory_type=parsed_memory_type,
            title=title,
            source=source,
            tags=parsed_tags,
        )

        # Return detailed response
        if response.success:
            result = {
                "result": "✅ Memory added successfully",
                "memory_id": response.memory_id,
                "final_type": response.final_type.value,
                "ai_verified": response.ai_verified,
                "summary_generated": response.summary_generated,
                "type_changed": response.type_changed,
                "processing_time_ms": response.processing_time_ms,
                "word_count": response.word_count,
            }
            return result
        else:
            return {"result": "❌ Failed to add memory"}

    except (ConfigurationError, ValidationError) as e:
        log_error("mcp_server", "add_memory", e, content_length=len(content))
        return {"result": f"❌ Configuration/validation error: {str(e)}"}
    except Exception as e:
        log_error("mcp_server", "add_memory", e, content_length=len(content))
        return {"result": f"❌ Failed to add memory: {str(e)}"}


@app.tool("search_memories")
def search_memories(query: str, limit: int = 5):
    """Search memories in the system"""
    try:
        if not memory:
            return {"result": "❌ Memory system not initialized"}

        # Direct sync call - like Mem0
        results = memory.search(query, limit=limit)

        return {"result": results}

    except (ValidationError, ProcessingError) as e:
        log_error("mcp_server", "search_memories", e, query=query, limit=limit)
        return {"result": f"❌ Search error: {str(e)}"}
    except Exception as e:
        log_error("mcp_server", "search_memories", e, query=query, limit=limit)
        return {"result": f"❌ Failed to search memories: {str(e)}"}


@app.tool("get_system_info")
def get_system_info(random_string: str = "dummy"):
    """Get information about the memory system configuration"""
    try:
        if not memory:
            return {
                "result": {"components_initialized": False, "status": "Not initialized"}
            }

        # Direct sync call - let memory system report its own storage info
        stats = memory.get_stats()

        # Only add MCP server specific info
        stats.update({"transport": "SSE", "port": 8787})

        return {"result": stats}

    except (ConfigurationError, ProcessingError) as e:
        log_error("mcp_server", "get_system_info", e)
        return {"result": f"❌ System info error: {str(e)}"}
    except Exception as e:
        log_error("mcp_server", "get_system_info", e)
        return {"result": f"❌ Failed to get system info: {str(e)}"}


if __name__ == "__main__":
    # Get port from environment variable, default to 8787 for backward compatibility
    import os

    port = int(os.getenv("MEMORY_SYSTEM_MCP_PORT", "8787"))

    # EXACT legacy pattern - clean and simple
    # nosec B104: Server needs to bind to 0.0.0.0 for containerized deployments
    app.run(transport="sse", host="0.0.0.0", port=port)  # nosec
