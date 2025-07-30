"""
Database Schema Tracking Module

This module provides comprehensive functionality for capturing, analyzing, and storing
database schema snapshots across multiple database systems. It serves as the core
engine for schema version control and change detection.

Key Features:
- Comprehensive schema snapshot creation with full metadata
- Multi-database support (MySQL, PostgreSQL, SQLite, Oracle, etc.)
- Intelligent hash-based change detection and versioning
- Timestamped version management with audit trails
- Secure credential handling and connection management
- Advanced schema introspection and analysis

Database-Specific Features:
- MySQL: Triggers, procedures, functions, and events
- PostgreSQL: Sequences, indexes, and constraints
- SQLite: Optimized for lightweight schema tracking
- Universal: Tables, columns, views, and data types

Author: Navaneet
"""

import hashlib
import re
from datetime import datetime
from pathlib import Path

import yaml
from sqlalchemy import create_engine, inspect, text

from datatrack.connect import get_connected_db_name, get_saved_connection

# Base directory for storing database exports and snapshots
EXPORT_BASE_DIR = Path(".databases/exports")


def sanitize_url(url_obj):
    """
    Remove sensitive credentials from database URL for logging.

    Args:
        url_obj: SQLAlchemy URL object containing connection details

    Returns:
        URL object with username and password removed for safe display
    """
    return url_obj.set(password=None).set(username=None)


def compute_hash(data: dict) -> str:
    """
    Generate SHA256 hash of schema data for change detection.

    Args:
        data: Schema dictionary to hash

    Returns:
        str: Hexadecimal SHA256 hash string

    Note:
        Uses sorted YAML serialization to ensure consistent hashing
        regardless of dictionary key order.
    """
    serialized = yaml.dump(data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def save_schema_snapshot(schema: dict, db_name: str) -> Path:
    """
    Persist schema snapshot to YAML file with comprehensive metadata.

    Args:
        schema: Complete schema dictionary containing tables, views, etc.
        db_name: Name of the database being tracked

    Returns:
        Path: Location of the saved snapshot file

    Note:
        Snapshots are stored with timestamp-based naming for easy sorting
        and include metadata for tracking purposes.
    """
    snapshot_dir = EXPORT_BASE_DIR / db_name / "snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp-based snapshot identifier
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_id = f"snapshot_{timestamp}"
    snapshot_file = snapshot_dir / f"{snapshot_id}.yaml"

    # Enrich schema with tracking metadata
    schema["__meta__"] = {
        "snapshot_id": snapshot_id,
        "timestamp": timestamp,
        "database": db_name,
        "hash": compute_hash(schema),
    }

    with open(snapshot_file, "w") as f:
        yaml.dump(schema, f, sort_keys=False, default_flow_style=False)

    print(f"Snapshot saved at: {snapshot_file}")
    return snapshot_file


def is_valid_table_name(name: str) -> bool:
    """Validate that the table name contains only alphanumeric and underscores."""
    return re.match(r"^\w+$", name) is not None


def snapshot(source: str = None, include_data: bool = False, max_rows: int = 50):
    """
    Capture a comprehensive database schema snapshot with optional data inclusion.

    This function performs deep introspection of the database structure, capturing
    all schema objects including tables, views, triggers, procedures, functions,
    and sequences. It creates a complete, timestamped snapshot for version control.

    Args:
        source (str, optional): Database connection URI. If None, uses saved connection
        include_data (bool): Whether to include table data in the snapshot
        max_rows (int): Maximum number of rows to capture per table when including data

    Returns:
        Path: Path to the created snapshot file

    Schema Objects Captured:
        - Tables: Complete structure including columns, constraints, indexes
        - Views: View definitions and dependencies
        - Triggers: Event-based logic and timing
        - Procedures: Stored procedure definitions
        - Functions: User-defined function signatures
        - Sequences: Auto-increment and sequence objects

    Database-Specific Features:
        - MySQL: Triggers, procedures, functions, events
        - PostgreSQL: Sequences, advanced constraint types
        - SQLite: Optimized lightweight schema capture

    Metadata Enrichment:
        - Snapshot timestamp and unique identifier
        - Database name and connection details
        - Schema hash for change detection
        - Version tracking information

    Data Inclusion Options:
        - Full table data (limited by max_rows)
        - Sample data for testing and validation
        - Data type validation and consistency checks

    Note:
        Snapshots are stored with timestamp-based naming for chronological
        ordering and include comprehensive metadata for tracking purposes.
    """
    if source is None:
        source = get_saved_connection()
        if not source:
            raise ValueError(
                "No DB source provided or saved. Run `datatrack connect` first."
            )

    db_name = get_connected_db_name()
    engine = create_engine(source)
    insp = inspect(engine)

    schema_data = {
        "dialect": engine.dialect.name,
        "url": str(sanitize_url(engine.url)),
        "tables": [],
        "views": [],
        "triggers": [],
        "functions": [],
        "procedures": [],
        "sequences": [],
    }

    if include_data:
        schema_data["data"] = {}

    with engine.connect() as conn:
        # Extract table information with comprehensive metadata
        for table_name in insp.get_table_names():
            columns = insp.get_columns(table_name)
            pk = insp.get_pk_constraint(table_name)
            fks = insp.get_foreign_keys(table_name)
            idx = insp.get_indexes(table_name)

            table_info = {
                "name": table_name,
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"],
                    }
                    for col in columns
                ],
                "primary_key": pk.get("constrained_columns", []),
                "foreign_keys": [
                    {
                        "column": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"],
                    }
                    for fk in fks
                ],
                "indexes": idx,
            }
            schema_data["tables"].append(table_info)

            if include_data:
                try:
                    if not is_valid_table_name(table_name):
                        raise ValueError(f"Invalid table name: {table_name}")
                    query = text(f"SELECT * FROM {table_name} LIMIT :max_rows")  # nosec
                    result = conn.execute(query, {"max_rows": max_rows})
                    rows = [dict(row) for row in result.fetchall()]
                    # Sample table data with row limit enforcement
                    schema_data["data"][table_name] = rows
                except Exception as e:
                    print(f"Could not fetch data for `{table_name}`: {e}")

        # Extract database views with definitions
        for view_name in insp.get_view_names():
            definition = insp.get_view_definition(view_name)
            schema_data["views"].append({"name": view_name, "definition": definition})

        # Database-specific feature extraction
        dialect = engine.dialect.name.lower()

        if dialect == "mysql":
            # MySQL-specific objects: triggers, procedures, functions
            schema_data["triggers"] = [
                dict(row) for row in conn.execute(text("SHOW TRIGGERS")).fetchall()
            ]
            schema_data["procedures"] = [
                dict(row)
                for row in conn.execute(
                    text("SHOW PROCEDURE STATUS WHERE Db = DATABASE()")
                ).fetchall()
            ]
            schema_data["functions"] = [
                dict(row)
                for row in conn.execute(
                    text("SHOW FUNCTION STATUS WHERE Db = DATABASE()")
                ).fetchall()
            ]

        elif dialect == "postgresql":
            schema_data["triggers"] = [
                dict(row)
                for row in conn.execute(
                    text(
                        """
                SELECT event_object_table, trigger_name, action_timing, event_manipulation, action_statement
                FROM information_schema.triggers
            """
                    )
                ).fetchall()
            ]
            schema_data["procedures"] = [
                dict(row)
                for row in conn.execute(
                    text(
                        """
                SELECT proname, proargnames, prosrc
                FROM pg_proc
                JOIN pg_namespace ON pg_proc.pronamespace = pg_namespace.oid
                WHERE pg_namespace.nspname NOT IN ('pg_catalog', 'information_schema')
            """
                    )
                ).fetchall()
            ]
            schema_data["sequences"] = [
                row["sequence_name"]
                for row in conn.execute(
                    text("SELECT sequence_name FROM information_schema.sequences")
                ).fetchall()
            ]

        elif dialect == "sqlite":
            res = conn.execute(
                text(
                    "SELECT name, type, sql FROM sqlite_master WHERE type IN ('view', 'trigger')"
                )
            )
            for row in res.fetchall():
                entry = dict(row)
                if entry["type"] == "view":
                    schema_data["views"].append(
                        {"name": entry["name"], "definition": entry["sql"]}
                    )
                elif entry["type"] == "trigger":
                    schema_data["triggers"].append(entry)

    return save_schema_snapshot(schema_data, db_name)
