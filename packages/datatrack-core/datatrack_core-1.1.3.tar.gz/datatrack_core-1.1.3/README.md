# Datatrack

**Version Control for Database Schemas**

[![PyPI version](https://img.shields.io/pypi/v/datatrack-core?color=blue&label=PyPI)](https://pypi.org/project/datatrack-core/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/datatrack-core?color=blue)](https://pypi.org/project/datatrack-core/)

A high-performance CLI tool for tracking database schema changes with intelligent processing optimizations. Track, compare, and validate database schemas across PostgreSQL, MySQL, SQLite, and SQL Server.

## Features

- **Fast Schema Introspection**: 70-75% performance improvement for large databases
- **Intelligent Processing**: Auto-selects optimal strategy based on schema size
- **Schema Comparison**: Generate detailed diffs between schema versions
- **Best Practice Linting**: Enforce naming conventions and design patterns
- **Multiple Export Formats**: JSON, YAML, Markdown, HTML reports
- **Multi-Database Support**: PostgreSQL, MySQL, SQLite, SQL Server

## Installation

```bash
pip install datatrack-core
```

## Quick Start

```bash
# Initialize tracking for your database
datatrack init

# Connect to your database
datatrack connect postgresql://user:pass@localhost/mydb

# Take a schema snapshot
datatrack snapshot

# Compare changes
datatrack diff snapshot1 snapshot2

# Check schema quality
datatrack lint
```

## Performance Features

Datatrack automatically optimizes processing based on your schema size:

- **Small schemas (1-49 tables)**: Standard sequential processing
- **Medium schemas (50-199 tables)**: Parallel processing (65-70% faster)
- **Large schemas (200+ tables)**: Parallel + batched processing (70-75% faster)

```bash
# Manual performance tuning
datatrack snapshot --parallel --max-workers 8 --batch-size 50
```

## Performance Benchmarks

| Schema Size | Processing Method | Performance Improvement |
|-------------|------------------|-------------------------|
| 1-49 tables | Standard Sequential | Baseline |
| 50-199 tables | Parallel (4 workers) | **65-70% faster** |
| 200+ tables | Parallel + Batched | **70-75% faster** |

*Benchmarks run on standard hardware with PostgreSQL. Results may vary.*
## Examples

### Real-World Scenarios

**Data Engineering Pipeline**
```bash
# Before deploying pipeline changes
datatrack snapshot --name "pre-pipeline-v2.1"
datatrack lint --strict

# After deployment
datatrack snapshot --name "post-pipeline-v2.1"
datatrack diff pre-pipeline-v2.1 post-pipeline-v2.1
```

**Schema Migration Validation**
```bash
# Snapshot before migration
datatrack snapshot --name "before-migration"

# Run your migration scripts
# ...

# Validate changes
datatrack snapshot --name "after-migration"
datatrack diff before-migration after-migration --format markdown > migration-report.md
```

**Enterprise Database Monitoring**
```bash
# Daily schema monitoring (large database)
datatrack snapshot --parallel --max-workers 8 --batch-size 100

# Weekly quality checks
datatrack lint --export-report schema-quality-$(date +%Y%m%d).json
```

## Database Support

| Database | Connection String Example |
|----------|---------------------------|
| PostgreSQL | `postgresql://user:pass@localhost:5432/dbname` |
| MySQL | `mysql+pymysql://user:pass@localhost:3306/dbname` |
| SQLite | `sqlite:///path/to/database.db` |
| SQL Server | `mssql+pyodbc://user:pass@server/database` |

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Setup and requirements
- [Usage Guide](docs/USAGE.md) - Complete feature reference
- [Development Guide](docs/DEVELOPMENT.md) - Contributing guidelines
- [Architecture Overview](ARCHITECTURE_DIAGRAMS.md) - System design

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contribute/CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/nrnavaneet/datatrack.git
cd datatrack
pip install -e ".[dev]"
pytest tests/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- [GitHub Issues](https://github.com/nrnavaneet/datatrack/issues) - Bug reports and feature requests
- [GitHub Discussions](https://github.com/nrnavaneet/datatrack/discussions) - Questions and community
- 💡 **Suggest features** - [Start a discussion](https://github.com/nrnavaneet/datatrack/discussions)
- 📝 **Improve docs** - Documentation PRs are always welcome
- 🔧 **Write code** - Check out [good first issues](https://github.com/nrnavaneet/datatrack/labels/good%20first%20issue)

### Development Setup
```bash
git clone https://github.com/nrnavaneet/datatrack.git
cd datatrack
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

See our [Contributing Guide](docs/contribute/CONTRIBUTING.md) for detailed instructions.

## Community & Support

- [GitHub Discussions](https://github.com/nrnavaneet/datatrack/discussions) - Questions and community
- [Issue Tracker](https://github.com/nrnavaneet/datatrack/issues) - Bug reports and feature requests
- [Documentation](docs/) - Comprehensive guides and references

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with ❤️ by N R Navaneet. Special thanks to:
- [SQLAlchemy](https://www.sqlalchemy.org/) for database introspection
- [Typer](https://typer.tiangolo.com/) for the CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Assisted by [GitHub Copilot](https://github.com/features/copilot)
