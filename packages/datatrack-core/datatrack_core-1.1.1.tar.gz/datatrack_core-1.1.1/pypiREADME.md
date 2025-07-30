# Datatrack - Version Control for Database Schemas

A high-performance CLI tool that brings Git-like version control to your database schemas with intelligent processing optimizations. Built for Data Engineers, Analytics Engineers, and Platform Teams.

## Key Features

- **High Performance**: 70-75% faster schema introspection for large databases
- **Intelligent Processing**: Auto-selects optimal strategy based on schema size
- **Multi-Database Support**: PostgreSQL, MySQL, SQLite, SQL Server
- **Schema Comparison**: Generate detailed diffs between versions
- **Quality Linting**: Enforce naming conventions and best practices
- **Multiple Export Formats**: JSON, YAML, Markdown, HTML

## Performance Improvements

| Schema Size   | Processing Method    | Performance Gain |
|---------------|----------------------|------------------|
| 1-49 tables   | Standard | Baseline  |                  |
| 50-199 tables | Parallel (4 workers) | 65-70% faster    |
| 200+ tables   | Parallel + Batched   | 70-75% faster    |

## Installation

```bash
pip install datatrack-core
```
pip install -e .
```
This method is ideal if you want to contribute or modify the tool.

## Helpful Commands

Datatrack comes with built-in help and guidance for every command. Use this to quickly learn syntax and options:
```bash
datatrack --help
or
datatrack -h
```

##  How to Use

### 1. Initialize Tracking

```bash
datatrack init
```

Creates `.datatrack/`, `.databases/`, and optional initial files.


### 2. Connect to a Database

Save your DB connection for future use:

### MySQL

```bash
datatrack connect mysql+pymysql://root:<password>@localhost:3306/<database-name>
```

### PostgreSQL

```bash
datatrack connect postgresql+psycopg2://postgres:<password>@localhost:5432/<database-name>
```

### SQLite

```bash
datatrack connect sqlite:///.databases/<database-name>
```

## 3. Take a Schema Snapshot

```bash
# Standard snapshot
datatrack snapshot

# High-performance snapshot with parallel processing
datatrack snapshot --parallel

# Custom performance configuration
datatrack snapshot --parallel --max-workers 8 --batch-size 50

# For large schemas (200+ tables) - automatically optimized
datatrack snapshot  # Auto-enables parallel + batched processing
```

Saves the current schema to `.databases/exports/<db_name>/snapshots/`.

## 4. Lint the Schema

```bash
datatrack lint
```

Detects issues in naming and structure.

## 5. Verify Schema Rules

```bash
datatrack verify
```

Validates schema against `schema_rules.yaml`.

## 6. View Schema Differences

```bash
datatrack diff
```

Shows table and column changes between the latest two snapshots.

## 7. Export Snapshots or Diffs

Export latest snapshot as YAML (default)
```bash
datatrack export
```

Explicitly export snapshot as YAML
```bash
datatrack export --type snapshot --format yaml
```
Export latest diff as JSON
```bash
datatrack export --type diff --format json
```

Output is saved in `.databases/exports/<db_name>/`.

## 8. View Snapshot History

```bash
datatrack history
```

Displays all snapshot timestamps and table counts.

## 9. Run the Full Pipeline

```bash
datatrack pipeline run
```

Runs `lint`, `snapshot`, `verify`, `diff`, and `export` together.

For advanced use cases and integration into CI/CD, visit:

**https://github.com/nrnavaneet/datatrack**
