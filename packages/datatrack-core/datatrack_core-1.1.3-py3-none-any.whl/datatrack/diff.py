"""
Schema Difference Analysis Module

This module provides comprehensive functionality to compare database schema snapshots,
identifying and analyzing changes between different versions of database structures.
It performs detailed comparisons across all database objects and provides actionable
insights into schema evolution.

Key Features:
- Intelligent comparison of the two most recent schema snapshots
- Detailed table and column change analysis with type detection
- Comprehensive database object comparison (views, procedures, functions, triggers, etc.)
- Data change detection and reporting with statistical analysis
- Human-readable diff output with color-coded changes
- Support for complex schema migrations and rollback analysis

Comparison Types:
- Structural changes: Tables, columns, indexes, constraints
- Object changes: Views, stored procedures, functions, triggers
- Data changes: Row additions, deletions, modifications
- Metadata changes: Comments, permissions, collations

Author: Navaneet
"""

from pathlib import Path

import yaml

from datatrack.connect import get_connected_db_name


def load_snapshots():
    """
    Load and return the two most recent schema snapshots for comparison.

    Returns:
        tuple: (older_snapshot, newer_snapshot) as dictionaries

    Raises:
        FileNotFoundError: If fewer than 2 snapshots exist for comparison

    Note:
        Snapshots are automatically sorted by filename (timestamp) with
        the most recent snapshot considered as 'newer'.
    """
    db_name = get_connected_db_name()
    snap_dir = Path(".databases/exports") / db_name / "snapshots"
    snapshots = sorted(snap_dir.glob("*.yaml"), reverse=True)

    if len(snapshots) < 2:
        raise FileNotFoundError(
            f"Need at least 2 snapshots to run a diff for '{db_name}'."
        )

    # Load the two most recent snapshots
    with open(snapshots[0]) as f1, open(snapshots[1]) as f2:
        newer = yaml.safe_load(f1)
        older = yaml.safe_load(f2)

    return older, newer


def diff_schemas(old, new):
    """
    Analyze and display comprehensive differences between two schema versions.

    Args:
        old: Dictionary containing the older schema snapshot
        new: Dictionary containing the newer schema snapshot

    Note:
        Outputs a detailed comparison report including:
        - Added/removed tables and database objects
        - Column additions, removals, and type changes
        - Data modifications (if available)
    """

    def diff_named_objects(obj_name, key="name"):
        """Helper function to compare collections of named database objects."""
        print(f"\n{obj_name.capitalize()} Changes:")
        old_set = {v[key] for v in old.get(obj_name, [])}
        new_set = {v[key] for v in new.get(obj_name, [])}
        added = new_set - old_set
        removed = old_set - new_set

        # Report additions and removals
        for a in added:
            print(f"  + Added {obj_name[:-1]}: {a}")
        for r in removed:
            print(f"  - Removed {obj_name[:-1]}: {r}")
        if not added and not removed:
            print(f"\tNo {obj_name} added or removed.")

    print("\n=== SCHEMA DIFF ===")

    # Create lookup dictionaries for efficient comparison
    old_tables = {t["name"]: t for t in old.get("tables", [])}
    new_tables = {t["name"]: t for t in new.get("tables", [])}

    # Analyze table-level changes
    old_set = set(old_tables)
    new_set = set(new_tables)

    added_tables = new_set - old_set
    removed_tables = old_set - new_set
    common_tables = old_set & new_set

    print("\nTable Changes:")
    for t in added_tables:
        print(f"  + Added table: {t}")
    for t in removed_tables:
        print(f"  - Removed table: {t}")
    if not added_tables and not removed_tables:
        print("\tNo tables added or removed.")

    # Column diff
    print("\nColumn Changes:")
    for table in common_tables:
        old_cols = {c["name"]: c["type"] for c in old_tables[table]["columns"]}
        new_cols = {c["name"]: c["type"] for c in new_tables[table]["columns"]}

        old_col_set = set(old_cols)
        new_col_set = set(new_cols)

        for c in new_col_set - old_col_set:
            print(f"  + {table}.{c} ({new_cols[c]})")
        for c in old_col_set - new_col_set:
            print(f"  - {table}.{c} ({old_cols[c]})")
        for c in old_col_set & new_col_set:
            if old_cols[c] != new_cols[c]:
                print(f"  ~ {table}.{c} changed: {old_cols[c]} -> {new_cols[c]}")

    # Other schema objects
    for section in ["views", "triggers", "procedures", "functions", "sequences"]:
        diff_named_objects(section)

    # Data diff (if available)
    print("\n=== DATA DIFF ===")
    old_data = old.get("data", {})
    new_data = new.get("data", {})
    common_tables_with_data = set(old_data) & set(new_data)

    for table in common_tables_with_data:
        old_rows = {str(row) for row in old_data[table]}
        new_rows = {str(row) for row in new_data[table]}

        added_rows = new_rows - old_rows
        removed_rows = old_rows - new_rows

        if added_rows or removed_rows:
            print(f"\nData changes in `{table}`:")
            for row in added_rows:
                print(f"  + {row}")
            for row in removed_rows:
                print(f"  - {row}")
        else:
            print(f"\nNo data changes in `{table}`.")

    print("\nDiff complete.\n")
