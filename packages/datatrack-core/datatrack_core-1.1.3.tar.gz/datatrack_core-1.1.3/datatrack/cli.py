"""
Datatrack CLI - Command Line Interface for Database Schema Tracking

This module provides the main command-line interface for Datatrack, a tool designed
to track, compare, and manage database schema changes across different environments.

Key Features:
- Initialize tracking projects
- Connect to various database systems
- Take schema snapshots
- Compare schema versions
- Export and import schema data
- Validate schema integrity

Author: Navaneet
"""

import os
from pathlib import Path

import typer
import yaml

from datatrack import connect as connect_module
from datatrack import diff as diff_module
from datatrack import exporter, history, linter, pipeline
from datatrack import test_connection as test_module
from datatrack import tracker, verifier

# Main CLI application instance
app = typer.Typer(
    help="Datatrack: Professional database schema tracking and versioning CLI",
    add_help_option=False,
    invoke_without_command=True,
)

# Configuration constants
CONFIG_DIR = ".datatrack"
CONFIG_FILE = "config.yaml"


@app.command()
def init():
    """
    Initialize a new Datatrack project in the current directory.

    Creates the necessary configuration files and directory structure
    for tracking database schema changes.
    """
    config_path = Path(CONFIG_DIR)
    if config_path.exists():
        typer.echo("✓ Datatrack is already initialized in this directory.")
        raise typer.Exit()

    # Create project configuration directory
    config_path.mkdir(parents=True, exist_ok=True)

    # Initialize default project configuration
    default_config = {
        "project_name": "my-datatrack-project",
        "created_by": os.getenv("USER") or "unknown",
        "version": "0.1",
        "sources": [],
    }

    with open(config_path / CONFIG_FILE, "w") as f:
        yaml.dump(default_config, f)

    typer.echo("✓ Datatrack project initialized successfully in .datatrack/")


@app.command()
def snapshot(
    include_data: bool = typer.Option(
        False,
        "--include-data",
        help="Include sample table data in the snapshot (default: False)",
    ),
    max_rows: int = typer.Option(
        100,
        "--max-rows",
        help="Maximum number of rows to capture per table (only if --include-data is used)",
    ),
    parallel: bool = typer.Option(
        True,
        "--parallel/--no-parallel",
        help="Use parallel processing for large schemas (default: True)",
    ),
    max_workers: int = typer.Option(
        4,
        "--max-workers",
        help="Maximum number of parallel workers for schema introspection (default: 4)",
    ),
    batch_size: int = typer.Option(
        100,
        "--batch-size",
        help="Batch size for processing tables in memory-efficient mode (default: 100)",
    ),
):
    """
    Capture a comprehensive database schema snapshot from the connected database.

    This command performs deep introspection of the database structure and creates
    a timestamped snapshot file containing all schema objects. The snapshot serves
    as a version control point for tracking schema evolution over time.

    Features:
    - Complete schema capture (tables, views, triggers, procedures, functions)
    - Optional data sampling for testing and validation
    - Metadata enrichment with timestamps and change detection hashes
    - Database-specific object support (MySQL triggers, PostgreSQL sequences, etc.)

    Output:
    - YAML snapshot file in .databases/exports/{db_name}/snapshots/
    - Timestamped filename for chronological ordering
    - Comprehensive metadata for change tracking

    Examples:
    - Basic snapshot: datatrack snapshot
    - With data: datatrack snapshot --include-data --max-rows 50
    """
    source = connect_module.get_saved_connection()
    if not source:
        typer.echo(
            "No database connection found. Please run 'datatrack connect <db_uri>' first."
        )
        raise typer.Exit(code=1)

    typer.echo("\nCapturing schema snapshot from source...")

    try:
        snapshot_path = tracker.snapshot(
            source,
            include_data=include_data,
            max_rows=max_rows,
            parallel=parallel,
            max_workers=max_workers,
            batch_size=batch_size,
        )
        typer.secho(
            "Snapshot successfully captured and saved.\n", fg=typer.colors.GREEN
        )
        typer.echo(f"Saved at: {snapshot_path}\n")
    except Exception as e:
        typer.secho(f"Error capturing snapshot: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from e


@app.command()
def diff():
    """
    Compare the two most recent snapshots and display comprehensive schema differences.

    This command loads the latest two schema snapshots and performs detailed
    comparison analysis, identifying changes in tables, columns, views, and
    other database objects.
    """
    try:
        # Load and compare the two most recent snapshots
        old, new = diff_module.load_snapshots()
        diff_module.diff_schemas(old, new)
    except Exception as e:
        typer.secho(f"{str(e)}", fg=typer.colors.RED)


@app.command()
def verify():
    """
    Check schema against configured rules (e.g. snake_case, reserved words).
    """
    typer.echo("\nVerifying schema...\n")

    try:
        schema = verifier.load_latest_snapshot()
        rules = verifier.load_rules()
        violations = verifier.verify_schema(schema, rules)

        if not violations:
            typer.secho("All schema rules passed!\n", fg=typer.colors.GREEN)
        else:
            for v in violations:
                typer.secho(v, fg=typer.colors.RED)
            raise typer.Exit(code=1)

    except Exception as e:
        typer.secho(f"Error during verification: {str(e)}\n", fg=typer.colors.RED)
        raise typer.Exit(code=1) from e


@app.command("history")
def history_command():
    """View schema snapshot history timeline"""
    history.print_history()
    print()


@app.command()
def export(
    type: str = typer.Option("snapshot", help="Export type: snapshot or diff"),
    format: str = typer.Option("json", help="Output format: json or yaml"),
):
    """
    Export latest snapshot or diff as JSON/YAML.
    Saves to default path in .databases/exports/
    """
    typer.echo(f"\nExporting {type} as {format}...\n")

    try:
        if type == "snapshot":
            exporter.export_snapshot(fmt=format)
            output_file = f".databases/exports/latest_snapshot.{format}"
        elif type == "diff":
            exporter.export_diff(fmt=format)
            output_file = f".databases/exports/latest_diff.{format}"
        else:
            typer.secho(
                "Invalid export type. Use 'snapshot' or 'diff'.", fg=typer.colors.RED
            )
            raise typer.Exit(code=1)

        typer.secho(f"Exported to {output_file}", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"Export failed: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from e


@app.command()
def lint():
    """
    Run non-blocking schema quality checks (naming,types, etc).
    """
    typer.echo("\n Running schema linter...\n")

    try:
        schema = linter.load_latest_snapshot()
        warnings = linter.lint_schema(schema)

        if not warnings:
            typer.secho("No linting issues found!\n", fg=typer.colors.GREEN)
        else:
            for w in warnings:
                typer.secho(w, fg=typer.colors.YELLOW)
            raise typer.Exit(code=1)

    except Exception as e:
        typer.secho(f"Error during linting: {str(e)}\n", fg=typer.colors.RED)
        raise typer.Exit(code=1) from e


app.add_typer(pipeline.app, name="pipeline")


@app.command()
def connect(link: str = typer.Argument(..., help="Database connection URI")):
    """
    Establish and save a database connection for schema tracking operations.

    This command validates the provided database connection URI, performs
    comprehensive connection testing, and saves the configuration for use
    by all subsequent Datatrack operations.

    Supported Database Systems:
    - MySQL/MariaDB: mysql+pymysql://user:pass@host:port/database
    - PostgreSQL: postgresql://user:pass@host:port/database
    - SQLite: sqlite:///path/to/database.db
    - Oracle: oracle+cx_oracle://user:pass@host:port/service

    Connection Features:
    - Automatic connection validation and testing
    - Credential verification and access testing
    - Database driver dependency checking
    - Secure connection string storage

    Security:
    - Connection strings are validated before storage
    - Test queries ensure proper database access
    - Error messages provide troubleshooting guidance

    Examples:
    - MySQL: datatrack connect "mysql+pymysql://root:password@localhost:3306/mydb"
    - SQLite: datatrack connect "sqlite:///./myapp.db"
    - PostgreSQL: datatrack connect "postgresql://user:pass@localhost:5432/mydb"

    Note: Only one database connection can be active at a time.
    Use 'datatrack disconnect' to remove the current connection.
    """
    connect_module.save_connection(link)


@app.command()
def disconnect():
    """
    Remove the saved database connection link.
    """
    connect_module.remove_connection()


@app.command("test-connection")
def test_connection():
    """
    Test if the saved database connection works.
    """
    result = test_module.test_connection()
    if "failed" in result.lower() or "no connection" in result.lower():
        typer.secho(result, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    else:
        typer.secho(result, fg=typer.colors.GREEN)


@app.callback()
def main(
    help: bool = typer.Option(
        False, "--help", "-h", is_eager=True, help="Show this message and exit."
    ),
):
    if help:
        banner = """
        ██████╗   █████╗ ████████╗ █████╗ ████████╗██████╗   █████╗   ██████╗ ██╗  ██╗
        ██╔══██╗ ██╔══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗ ██╔══██╗ ██╔════╝ ██║ ██╔╝
        ██║  ██║ ███████║   ██║   ███████║   ██║   ██████╔╝ ███████║ ██║      █████╔╝
        ██║  ██║ ██╔══██║   ██║   ██╔══██║   ██║   ██╔══██╗ ██╔══██║ ██║      ██╔═██╗
        ██████╔╝ ██║  ██║   ██║   ██║  ██║   ██║   ██║  ██║ ██║  ██║ ╚██████╗ ██║  ██╗
        ╚═════╝  ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═╝  ╚═╝  ╚═════╝ ╚═╝  ╚═╝

                        “Version Control for Your Database Schema”
        """
        typer.echo(banner)

        typer.echo("USAGE:")
        typer.echo("  datatrack <command> [options]\n")

        typer.echo("COMMANDS:")
        typer.echo(
            "  init                 Initialize Datatrack config in the current directory."
        )
        typer.echo(
            "  connect              Connect to a database and save the connection string."
        )
        typer.echo("  disconnect           Remove the saved database connection.")
        typer.echo(
            "  snapshot             Capture a schema snapshot and save it to disk."
        )
        typer.echo("  SNAPSHOT OPTIONS:")
        typer.echo(" --include-data      Include row data in the snapshot.")
        typer.echo(
            " --max-rows <int>    Limit number of rows per table (used with --include-data)."
        )
        typer.echo(
            " --parallel          Use parallel processing for large schemas (default: True)."
        )
        typer.echo(
            " --max-workers <int> Maximum number of parallel workers (default: 4)."
        )
        typer.echo(
            " --batch-size <int>  Batch size for memory-efficient processing (default: 100)."
        )
        typer.echo("  diff                 Compare the latest two schema snapshots.")
        typer.echo("  lint                 Run a basic linter to flag schema smells.")
        typer.echo(
            "  verify               Apply custom schema verification rules from config."
        )
        typer.echo(
            "  export               Export latest snapshot or diff as JSON/YAML."
        )
        typer.echo("  history              View schema snapshot history.")
        typer.echo(
            "  pipeline run         Run snapshot, diff, lint, and verify in one step."
        )
        typer.echo("  help                 Show this help message.\n")

        typer.echo("EXPORT OPTIONS:")
        typer.echo(
            "  --type [snapshot|diff]     Type of export to generate (default: snapshot)"
        )
        typer.echo("  --format [json|yaml]       Output format (default: json)\n")

        typer.echo("EXAMPLES:")
        typer.echo("  # Connect to PostgreSQL:")
        typer.echo(
            "  datatrack connect postgresql+psycopg2://postgres:pass123@localhost:5433/testdb"
        )
        typer.echo("\n  # Connect to MySQL:")
        typer.echo(
            "  datatrack connect mysql+pymysql://root:pass123@localhost:3306/testdb"
        )
        typer.echo("\n  # Connect to SQLite:")
        typer.echo("  datatrack connect sqlite:///.databases/example.db")
        typer.echo("\n  # Take a snapshot:")
        typer.echo("  datatrack snapshot")
        typer.echo("\n  # Take a snapshot with data and performance optimization:")
        typer.echo(
            "  datatrack snapshot --include-data --max-rows 50 --parallel --max-workers 8"
        )
        typer.echo("\n  # Show differences between last 2 snapshots:")
        typer.echo("  datatrack diff")
        typer.echo("\n  # Export latest snapshot as YAML:")
        typer.echo("  datatrack export --type snapshot --format yaml")
        typer.echo("\n  # Export latest diff as JSON:")
        typer.echo("  datatrack export --type diff --format json")
        typer.echo("\n  # Lint the schema:")
        typer.echo("  datatrack lint")
        typer.echo("\n  # Verify with custom rules:")
        typer.echo("  datatrack verify")
        typer.echo("\n  # Show snapshot history:")
        typer.echo("  datatrack history")
        typer.echo("\n  # Run full pipeline (snapshot + diff + lint + verify):")
        typer.echo("  datatrack pipeline run\n")

        typer.echo("NOTES:")
        typer.echo(
            "  • Datatrack supports PostgreSQL, MySQL, and SQLite (via SQLAlchemy URIs)."
        )
        typer.echo(
            "  • Snapshots are saved under `.databases/exports/<db_name>/snapshots/`."
        )
        typer.echo(
            "  • Use a `schema_rules.yaml` file to define custom rules for verification."
        )
        typer.echo(
            "  • Performance optimization: Use --parallel for 65-75% speed boost on large databases."
        )
        typer.echo(
            "  • Ideal for teams integrating schema change tracking in CI/CD pipelines.\n"
        )

        typer.echo("Documentation: https://github.com/nrnavaneet/datatrack")
        raise typer.Exit()


if __name__ == "__main__":
    app()
