FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for graph databases
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src/
#COPY .env .env

# Create internal storage directories
RUN mkdir -p /app/internal_storage/kuzu /app/internal_storage/qdrant

# Set essential runtime environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV SSE_HOST=0.0.0.0
ENV SSE_PORT=8766
ENV KUZU_DB_PATH=/app/internal_storage/kuzu/memory_db
ENV QDRANT_STORAGE_PATH=/app/internal_storage/qdrant

# Default configuration - Override these at runtime with --env-file or -e flags
# See .env.example for complete configuration options
ENV MEMORY_SYSTEM_MCP_PORT=8787
ENV MEMORY_SYSTEM_MCP_HOST=0.0.0.0
ENV MEMORY_SYSTEM_LOG_LEVEL=INFO
ENV MEMG_VECTOR_DIMENSION=768
ENV EMBEDDING_DIMENSION_LEN=768
ENV GEMINI_MODEL=gemini-2.0-flash

# SECURITY: API keys MUST be provided at runtime
# Example: docker run --env-file .env your-image
ENV GOOGLE_API_KEY=""











# Expose port
EXPOSE 8766

# Run the production MCP server
WORKDIR /app/src
CMD ["python", "-m", "memory_system.mcp_server"]
