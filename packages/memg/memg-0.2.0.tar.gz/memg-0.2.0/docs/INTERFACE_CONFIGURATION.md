# Database Interface Configuration

## Overview

All database interfaces use centralized configuration through `.env` file to eliminate hardcoded values and enable cloud deployment.

## Configuration File (.env)

```bash
# Google AI API
GOOGLE_API_KEY=your_api_key_here

# Kuzu Graph Database
KUZU_DB_PATH=~/.memory_databases/kuzu/memory_db

# Qdrant Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=memory_collection
```

## Interface Usage

### QdrantInterface

```python
from src.memory_system.qdrant.interface import QdrantInterface

# Uses .env configuration automatically
qdrant = QdrantInterface()

# Or override specific values
qdrant = QdrantInterface(host="qdrant.cloud", port=443, collection_name="prod_memories")

# Default collection operations
qdrant.add_point(vector, payload)
qdrant.search_points(vector, limit=10)
qdrant.get_stats()

# Custom collection operations
qdrant.add_point(vector, payload, collection="custom_collection")
```

### KuzuInterface

```python
from src.memory_system.kuzu.interface import KuzuInterface

# Uses .env configuration automatically
kuzu = KuzuInterface()

# Or override database path
kuzu = KuzuInterface(db_path="/custom/path/to/db")

# Standard operations
kuzu.add_node("Person", {"name": "Alice"})
kuzu.add_relationship("Alice", "KNOWS", "Bob", {"since": "2023"})
kuzu.query("MATCH (p:Person) RETURN p.name")
```

## Cloud Deployment

For cloud deployment, simply update the `.env` file:

```bash
# Qdrant Cloud
QDRANT_HOST=your-cluster.qdrant.cloud
QDRANT_PORT=6333
QDRANT_COLLECTION=memory_collection

# Or local Qdrant service
QDRANT_HOST=qdrant.service.local
QDRANT_PORT=6333
QDRANT_COLLECTION=memory_collection
```

## Benefits

- **Single source of truth**: No multiple collection/database names
- **Cloud-ready**: Easy to switch between local and cloud services
- **No hardcoded values**: All configuration externalized
- **Environment-specific**: Different configs for dev/staging/prod
- **Docker-friendly**: Environment variables pass through containers

## Testing

Core interfaces tested and verified:

```bash
pytest tests/test_interfaces.py::TestQdrantInterface::test_connection
pytest tests/test_interfaces.py::TestKuzuInterface -v
```

All database operations work with .env configuration.
