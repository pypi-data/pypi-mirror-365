# dbit - Database Schema Version Control

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Git-like CLI tool for managing database schemas with version control capabilities.

## Features

- Git-like interface for database schema management
- Support for PostgreSQL, MySQL, and SQLite
- Schema snapshots and version tracking
- Schema quality validation
- Change detection and comparison


## Installation

### Using PyPI (Recommended)
```bash
pip install dbit
```

### Using GitHub (Latest)
```bash
pip install git+https://github.com/navaneetnr/dbit.git
```

### From Source (Development)
```bash
git clone https://github.com/navaneetnr/dbit.git
cd dbit
python -m venv venv
source venv/bin/activate
pip install -e .
```

### With Docker
```bash
docker pull ghcr.io/navaneetnr/dbit:latest
# Or build locally for development:
docker build --target development -t dbit:dev .
```


## Usage Example

For a full list of commands and options, run:

```bash
dbit help
# or
dbit --help
# or
dbit -h
```

Common usage:

```bash
# Initialize a dbit repository in your project
dbit init

# Connect to your database
dbit connect --db-url postgresql://user:password@localhost/dbname

# Take a schema snapshot
dbit snapshot

# See changes since last snapshot
dbit status

# View schema change history
dbit log

# Run schema quality checks
dbit verify
```

## Commands
---------------------------------------------------------------------
|           Command              |           Description            |
|--------------------------------|----------------------------------|
| `dbit --help`                  | For full list of commands        |
| `dbit init`                    | Initialize a new dbit repository |
| `dbit connect --db-url <url>`  | Connect to a database            |
| `dbit disconnect`              | Disconnect from current database |
| `dbit snapshot [--content N]`  | Create schema snapshot           |
| `dbit status [--content N]`.   | Show changes since last snapshot |
| `dbit log`                     | Show change history              |
| `dbit verify`                  | Verify schema quality            |
---------------------------------------------------------------------
## Connection Strings

```bash
# PostgreSQL
postgresql://user:password@host:port/database

# MySQL
mysql://user:password@host:port/database

# SQLite
sqlite:///path/to/database.db
```

## Configuration

dbit stores configuration in `.dbit/schema.yaml`:

```yaml
db: postgresql://user:password@localhost/dbname
migrations: []
current_version: v1.json
```


## Documentation

- [Contributing Guide](docs/CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## Contributing

If you want to contribute to dbit, follow these steps:

### Quick Developer Setup

Use the provided script to set up your environment:

```bash
./scripts/setup-dev.sh
```

This will:
- Check your Python version (3.8+ required)
- Create and activate a virtual environment (`venv`)
- Upgrade pip
- Install all development dependencies
- Install pre-commit hooks
- Run pre-commit on all files

After setup, activate your environment with:
```bash
source venv/bin/activate
```

Run tests with:
```bash
pytest
```

Run all pre-commit checks manually with:
```bash
pre-commit run --all-files
```

### Manual Setup (Alternative)
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/dbit.git`
3. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```
6. Create a feature branch, make your changes, run tests (`pytest`), and submit a pull request.

### Development with Docker

```bash
# Build development image
docker build --target development -t dbit:dev .

# Run development container
# Mount your code for live editing
# (from project root)
docker run -it --rm -v $(pwd):/app dbit:dev
```


## License

MIT License - see [LICENSE](LICENSE) file for details.


## Support

- Issues: [GitHub Issues](https://github.com/navaneetnr/dbit/issues)
- Discussions: [GitHub Discussions](https://github.com/navaneetnr/dbit/discussions)

## Author
N R Navaneet
