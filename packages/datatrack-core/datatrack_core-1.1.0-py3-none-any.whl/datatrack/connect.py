"""
Database Connection Management Module

This module handles database connections for the Datatrack tool, providing
comprehensive utilities to establish, test, and manage connections to various
database systems including SQLite, MySQL, PostgreSQL, and others supported by SQLAlchemy.

Key Features:
- Database connection establishment and validation
- Connection string parsing and sanitization
- Database name extraction for file naming conventions
- Connection persistence and configuration management
- Support for multiple database backends

Supported Database Systems:
- SQLite (local file-based databases)
- MySQL/MariaDB (with pymysql driver)
- PostgreSQL (with psycopg2 driver)
- Any SQLAlchemy-compatible database

Author: Navaneet
"""

import re
from pathlib import Path
from urllib.parse import urlparse

import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ArgumentError, OperationalError, SQLAlchemyError

# Configuration paths for connection management
CONFIG_DIR = Path(".datatrack")
DB_LINK_FILE = CONFIG_DIR / "db_link.yaml"


def get_connected_db_name():
    """
    Extract a filesystem-safe database name from the current connection.

    This function retrieves the connected database name and sanitizes it
    for use in file paths and directory names.

    Returns:
        str: Sanitized database name suitable for filesystem use

    Raises:
        ValueError: If no connection exists or database name cannot be extracted

    Note:
        - SQLite databases use the filename without extension
        - Other databases use the database name from the connection URI
    """
    if not DB_LINK_FILE.exists():
        raise ValueError(
            "No database connection found. Please run `datatrack connect` first."
        )

    with open(DB_LINK_FILE) as f:
        uri = yaml.safe_load(f).get("link", "")
        parsed = urlparse(uri)

        # Handle SQLite database files specially
        if parsed.scheme.startswith("sqlite"):
            db_path = Path(parsed.path).name
            db_name = db_path.replace(".db", "")
        else:
            # Extract database name from URI path
            db_name = parsed.path.lstrip("/")

        # Sanitize the name for filesystem compatibility
        safe_name = re.sub(r"[^\w\-]", "_", db_name)
        if not safe_name:
            raise ValueError("Could not extract a valid database name from URI.")
        return safe_name


def save_connection(link: str):
    """
    Establish and validate a database connection, then persist it for future use.

    This function performs comprehensive connection validation including authentication,
    network connectivity, and basic query execution before saving the connection
    configuration to the local datatrack configuration directory.

    Args:
        link (str): Database connection URI in SQLAlchemy format
                   Examples:
                   - MySQL: mysql+pymysql://user:pass@host:port/database
                   - PostgreSQL: postgresql://user:pass@host:port/database
                   - SQLite: sqlite:///path/to/database.db

    Returns:
        None: Prints status messages and saves connection if successful

    Raises:
        Various database-specific exceptions are caught and converted to
        user-friendly error messages with troubleshooting guidance.

    Note:
        - Only one database connection can be active at a time
        - Connection validation includes a test query execution
        - Saved connections are stored in .datatrack/db_link.yaml
    """
    if DB_LINK_FILE.exists():
        print("A database is already connected.")
        print("   Disconnect first using: `datatrack disconnect`\n")
        return

    try:
        # Attempt connection establishment and validation
        engine = create_engine(link)
        with engine.connect() as conn:
            # Execute test query to verify database accessibility
            conn.execute(text("SELECT 1"))
    except OperationalError as e:
        # Handle database operational errors with specific guidance
        msg = str(e).lower()
        if "access denied" in msg:
            print("Access denied. Please check your DB username/password.")
        elif "can't connect" in msg or "could not connect" in msg:
            print("Could not connect to server. Is the DB server running?")
        elif "does not exist" in msg:
            print("Database not found. Please create it first or check the name.")
        else:
            print(f"Operational error: {e}")
        return
    except ArgumentError:
        # Handle malformed connection string errors
        print("Invalid connection string. Please verify format.")
        print("Example (MySQL): mysql+pymysql://root:pass@localhost:3306/dbname")
        print("Example (SQLite): sqlite:///path/to/file.db")
        return
    except ModuleNotFoundError:
        # Handle missing database driver dependencies
        print("Missing driver. Please install required DB driver packages.")
        print("  - MySQL: `pip install pymysql`")
        print("  - PostgreSQL: `pip install psycopg2-binary`")
        return
    except SQLAlchemyError as e:
        # Handle SQLAlchemy-specific errors
        print(f"SQLAlchemy error: {e}")
        return
    except Exception as e:
        # Handle any unexpected errors gracefully
        print(f"Unexpected error: {e}")
        return

    # Persist validated connection configuration
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(DB_LINK_FILE, "w") as f:
        yaml.dump({"link": link}, f)
    print(f"Successfully connected and saved link:\n   {link}")


def get_saved_connection():
    """
    Retrieve the saved database connection URI from configuration.

    Returns:
        str or None: Database connection URI if saved, None otherwise
    """
    if DB_LINK_FILE.exists():
        with open(DB_LINK_FILE) as f:
            return yaml.safe_load(f).get("link")
    return None


def remove_connection():
    """
    Remove the saved database connection configuration file.

    This function safely deletes the connection configuration,
    allowing users to connect to a different database.
    """
    if DB_LINK_FILE.exists():
        DB_LINK_FILE.unlink()
        print("Disconnected and removed saved DB link.")
    else:
        print("No active database connection found.")
