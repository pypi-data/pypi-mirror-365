# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-01-29

### Added
- Initial release of dbit
- Database schema version control functionality
- Support for PostgreSQL, MySQL, and SQLite
- Core commands: init, connect, disconnect, snapshot, status, log, verify
- Schema quality validation
- Change detection and comparison
- Docker support
- Comprehensive documentation
- Initial release of dbit
- Git-like CLI interface for database schema management
- Multi-database support (PostgreSQL, MySQL, SQLite)
- Schema snapshot functionality
- Database connection management
- Schema comparison and diff tools
- Quality verification rules
- Migration history tracking
- Basic Airflow integration
- Docker containerization
- Comprehensive test suite

### Core Commands
- `dbit init` - Initialize repository
- `dbit connect` - Connect to database
- `dbit disconnect` - Disconnect from database
- `dbit snapshot` - Create schema snapshots
- `dbit status` - Show schema changes
- `dbit log` - View change history
- `dbit verify` - Verify schema quality

### Database Support
- PostgreSQL 9.6+ with psycopg2
- MySQL 5.7+ with mysql-connector-python
- SQLite 3.8+ with built-in support

### Features
- Schema versioning with JSON snapshots
- Optional data inclusion in snapshots
- Quality rules for schema validation
- Team collaboration support
- Environment variable configuration
- Comprehensive error handling
- Cross-platform compatibility (Linux, macOS, Windows)

### Documentation
- Installation guide
- Usage examples
- Contributing guidelines
- API documentation
- Docker usage instructions
- Airflow integration guide

[Unreleased]: https://github.com/navaneetnr/dbit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/navaneetnr/dbit/releases/tag/v0.1.0
