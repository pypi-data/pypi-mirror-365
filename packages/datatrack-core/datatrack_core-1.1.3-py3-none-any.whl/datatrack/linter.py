"""
Database Schema Linting and Code Quality Module

This module provides automated code quality analysis and linting capabilities
for database schemas, helping maintain consistent, readable, and maintainable
database designs across development teams.

Key Features:
- Schema naming convention analysis and enforcement
- Code quality metrics and recommendations
- Best practice validation for database design
- Automated suggestions for schema improvements
- Performance optimization recommendations
- Documentation completeness checks

Linting Categories:
- Naming: Consistent naming patterns and conventions
- Structure: Table and column organization best practices
- Performance: Index usage and query optimization hints
- Maintainability: Clear, descriptive naming and documentation
- Standards: Industry best practices and team guidelines

Quality Checks:
- Maximum name length validation
- Ambiguous naming detection
- Generic type usage warnings
- Reserved keyword conflicts
- Relationship clarity and documentation

Author: Navaneet
"""

import re
from pathlib import Path
from typing import Dict, List

import yaml

from datatrack.connect import get_connected_db_name

# Constants
MAX_NAME_LENGTH = 30

AMBIGUOUS_NAMES = {
    "data",
    "value",
    "info",
    "details",
    "record",
    "item",
    "object",
    "entity",
    "metadata",
    "input",
    "output",
}

GENERIC_TYPES = {
    "string",
    "integer",
    "float",
    "boolean",
    "date",
    "datetime",
    "text",
    "json",
    "number",
}

RESERVED_KEYWORDS = {
    "select",
    "from",
    "table",
    "drop",
    "insert",
    "update",
    "delete",
    "create",
    "alter",
    "rename",
    "join",
    "where",
    "group",
    "by",
    "having",
    "order",
    "limit",
    "offset",
    "union",
    "intersect",
    "except",
    "as",
    "on",
    "in",
    "not",
    "is",
    "null",
    "and",
    "or",
    "like",
    "between",
    "exists",
}


def is_snake_case(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z][a-z0-9_]*", name))


def load_latest_snapshot():
    """
    Load the most recent YAML schema snapshot from exports.
    """
    db_name = get_connected_db_name()
    snap_dir = Path(".databases/exports") / db_name / "snapshots"
    snapshots = sorted(snap_dir.glob("*.yaml"), reverse=True)

    if not snapshots:
        raise ValueError(f"No snapshots found for database '{db_name}'.")

    with open(snapshots[0]) as f:
        return yaml.safe_load(f)


def lint_schema(schema: Dict) -> List[str]:
    """
    Perform comprehensive linting analysis on database schema structure.

    Analyzes naming conventions, reserved keyword usage, length limits,
    and best practices for tables and columns.

    Args:
        schema (Dict): Complete schema dictionary from snapshot

    Returns:
        List[str]: List of warning messages for schema improvements
    """
    warnings = []

    for table in schema.get("tables", []):
        table_name = table["name"]

        # Table name validation checks
        if len(table_name) > MAX_NAME_LENGTH:
            warnings.append(
                f"Table name '{table_name}' exceeds max length of {MAX_NAME_LENGTH} characters."
                "Consider shortening it (e.g., 'user_activity_log' -> 'activity_log')."
            )

        if not is_snake_case(table_name):
            warnings.append(
                f"Table name '{table_name}' is not in snake_case."
                "Avoid using keywords like 'select', 'table', 'order'."
            )

        if table_name.lower() in RESERVED_KEYWORDS:
            warnings.append(
                f"Table name '{table_name}' is a reserved SQL keyword."
                "Use more descriptive names like 'user_logs' or 'product_metrics'."
            )

        if table_name.lower() in AMBIGUOUS_NAMES:
            warnings.append(
                f"Table name '{table_name}' is too ambiguous."
                "Use more descriptive names like 'user_logs' or 'product_metrics'."
            )

        # --- Column checks ---
        for col in table.get("columns", []):
            col_name = col["name"]
            col_type = str(col.get("type", "")).lower()

            if len(col_name) > MAX_NAME_LENGTH:
                warnings.append(
                    f"Column '{col_name}' in table '{table_name}' exceeds max name length."
                    "Use concise names like 'created_at', 'order_total'."
                )

            if not is_snake_case(col_name):
                warnings.append(
                    f"Column '{col_name}' in table '{table_name}' is not in snake_case."
                    "Example: rename 'UserID' to 'user_id'."
                )

            if col_name.lower() in RESERVED_KEYWORDS:
                warnings.append(
                    f"Column '{col_name}' in table '{table_name}' is a reserved SQL keyword."
                    "Avoid column names like 'from', 'order', 'select'."
                )

            if col_name.lower() in AMBIGUOUS_NAMES:
                warnings.append(
                    f"Column '{col_name}' in table '{table_name}' has an ambiguous name."
                )

            normalized_type = re.sub(r"\(.*\)", "", col_type).strip().lower()
            if normalized_type in GENERIC_TYPES:
                warnings.append(
                    f"Column '{col_name}' in table '{table_name}' uses a generic type: {col_type}."
                    "Consider using domain-specific types like 'decimal(10,2)', 'varchar(255)', or 'timestamp with time zone'."
                )

    return warnings
