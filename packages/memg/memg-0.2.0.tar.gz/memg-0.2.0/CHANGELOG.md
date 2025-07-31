# Changelog

## [0.2.1] - 2025-01-28

### 🧹 Major Cleanup & Modernization

#### **Repository Structure Cleanup**
- **Removed duplicate directories**: Eliminated duplicate copies of `models/`, `processing/`, `qdrant/`, `utils/`, `validation/`, `memcpv2/`, `kuzu_graph/`, `api/`, `prompts/`, `memg_data/`, `local_storage/` from `src/` root
- **Removed duplicate files**: Deleted duplicate copies of `mcp_server.py`, `exceptions.py`, `logging_config.py`, `sync_wrapper.py`, `config.py`, `version.py`
- **Single source of truth**: All code now lives in `src/memory_system/` directory
- **Cleaner structure**: Reduced confusion and potential import conflicts

#### **Database Modernization**
- **Upgraded Kuzu**: Updated from 0.8.0 (directory-based format) to 0.11.1 (modern single-file format)
- **Fresh start**: Removed old incompatible database directory to start with modern format
- **Breaking change resolved**: Fixed "Database path cannot be a directory" error

#### **Code Quality Improvements**
- **Applied black formatting**: 46 files reformatted for consistent code style
- **Applied isort**: All imports properly organized
- **Pylint compliance**: Addressed code quality issues

#### **Dependencies Verification**
- **google-genai**: 1.27.0 (modern package, not deprecated google-generativeai)
- **fastmcp**: 2.10.6 (correct version maintained)
- **kuzu**: 0.11.1 (modernized to latest stable version)

#### **Deployment Improvements**
- **Added startup script**: `start_memory_server.sh` automatically sets environment variables and starts server
- **Environment handling**: Proper environment variable configuration for database paths
- **Documentation**: Clear setup and usage instructions

### Technical Details

#### **Database Format Migration**
- **Old format** (Kuzu 0.8.0): Directory-based with multiple files (`catalog.kz`, `data.kz`, `metadata.kz`, etc.)
- **New format** (Kuzu 0.11.1): Single file database (~4KB initial size)

#### **File Structure After Cleanup**
```
src/
├── __init__.py
└── memory_system/ # Single source of truth
 ├── mcp_server.py # Main MCP server
 ├── sync_wrapper.py # Memory system interface
 ├── models/ # Data models
 ├── processing/ # Memory processing
 ├── qdrant/ # Vector database interface
 ├── kuzu_graph/ # Graph database interface
 ├── utils/ # Utilities
 ├── validation/ # Validation pipeline
 └── memcpv2/ # Memory system v2 components
```

### Breaking Changes
- **Database incompatibility**: Old Kuzu 0.8.0 databases are not compatible with 0.11.1
- **Import paths unchanged**: All import paths remain the same despite cleanup
- **Environment variables**: `KUZU_DB_PATH` must be set for database location

### Migration Guide
1. **Old database**: Will be automatically recreated in new format on first run
2. **No code changes required**: All APIs and interfaces remain the same
3. **Use startup script**: `./start_memory_server.sh` for easy deployment

### Verification
- **System startup**: MCP server starts successfully with Kuzu 0.11.1
- **Database creation**: New single-file format database created automatically
- **Code quality**: All files pass black, isort, and basic pylint checks
- **Duplicate removal**: No duplicate code or directories remain
