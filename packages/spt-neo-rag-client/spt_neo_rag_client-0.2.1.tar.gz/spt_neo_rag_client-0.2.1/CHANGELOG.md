# Changelog

All notable changes to the SPT Neo RAG Python Client SDK will be documented in this file.

## [0.2.0] - 2025-01-03

### Added

#### New BM25 Endpoints Module (`client.bm25`)
- **`get_bm25_index_status(knowledge_base_id)`**: Get BM25 index status and metadata for a knowledge base
- **`build_bm25_index(knowledge_base_id, k1=1.2, b=0.75)`**: Build or rebuild BM25 index with custom parameters
- **`delete_bm25_index(knowledge_base_id)`**: Delete BM25 index for a knowledge base
- **`check_bm25_availability(knowledge_base_id)`**: Check if BM25 enhancement is available
- All methods include both async and sync versions (`*_sync`)

#### Enhanced Admin Endpoints (`client.admin`)
**Backup Management:**
- **`list_backups()`**: List all available database backups
- **`create_backup()`**: Initiate a database backup
- **`restore_backup(backup_filename)`**: Restore database from a backup
- **`delete_backup(backup_filename)`**: Delete a specific backup file
- **`download_backup(backup_filename)`**: Download a backup file

**System Monitoring:**
- **`get_rate_limit_stats()`**: Get current rate limiting statistics
- **`get_system_metrics()`**: Get comprehensive system metrics
- **`clear_rate_limit_cache()`**: Clear rate limiting cache for debugging

#### Enhanced Models Endpoints (`client.models`)
- **`get_model_names(provider, model_type=None)`**: Get available model names for a provider
- **`get_providers()`**: Get list of available providers

### Updated
- **Version bumped from 0.1.0 to 0.2.0**
- **README.md**: Added comprehensive documentation for BM25 endpoints with examples
- **Client Documentation**: Updated endpoint list to include BM25 operations

### Technical Improvements
- All new endpoints follow the established pattern of async/sync method pairs
- Comprehensive error handling with `NeoRagApiError` exceptions
- Consistent parameter validation and response handling
- Type hints throughout all new modules

### Compatibility
- **Backwards Compatible**: All existing functionality remains unchanged
- **API Compatibility**: Compatible with SPT Neo RAG API v1
- **Python Support**: Python 3.7+

### Example Usage

```python
# BM25 Operations
kb_id = "your-knowledge-base-id"

# Check availability and build index
availability = await client.bm25.check_bm25_availability(kb_id)
if availability['available']:
    build_result = await client.bm25.build_bm25_index(kb_id, k1=1.2, b=0.75)
    print(f"Build task: {build_result['task_id']}")

# Admin backup operations
backups = await client.admin.list_backups()
backup_task = await client.admin.create_backup()

# Enhanced model queries
providers = await client.models.get_providers()
openai_models = await client.models.get_model_names("openai")
```

## [0.1.0] - 2024-12-XX

### Added
- Initial release of SPT Neo RAG Python Client SDK
- Authentication support (API key and username/password)
- Core endpoint modules:
  - Admin operations
  - API key management
  - Content operations
  - Document management
  - Health checks
  - Knowledge base management
  - Knowledge graph operations
  - Query execution
  - Structured schema management
  - Task management
  - Team management
  - User management
  - Webhook configuration
- Async and sync method support for all operations
- Comprehensive error handling and exception classes
- Type hints and Pydantic model integration 