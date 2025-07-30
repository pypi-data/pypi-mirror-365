"""
Schema Difference Utility

This module provides utilities for comparing database schemas and identifying
differences between snapshots. It generates human-readable descriptions of
schema changes for status reporting and migration planning.

Functions:
- diff_schemas: Compare two schema snapshots and return change descriptions

Author: Navaneet
License: MIT
"""


def diff_schemas(current, snapshot, row_limit=0):
    """
    Compare two database schema snapshots and identify differences.

    Analyzes two schema snapshots to find structural differences including
    added/removed tables, column changes, and optionally data differences.

    Args:
        current (dict): Current database schema snapshot
        snapshot (dict): Previous schema snapshot to compare against
        row_limit (int): Number of rows to compare for data changes (default: 0)

    Returns:
        list: List of change descriptions in human-readable format
              Each item describes a specific change (e.g., "[+] New table: users")

    Change notation:
        [+] - Added (new tables, columns)
        [-] - Removed (deleted tables, columns)
        [~] - Modified (changed types, data)

    Example:
        changes = diff_schemas(current_schema, old_schema, row_limit=5)
        for change in changes:
            print(change)  # "[+] New table: products"
    """
    changes = []

    # Get table names from both schemas
    current_tables = set(current.keys())
    snapshot_tables = set(snapshot.keys())

    # Find added and removed tables
    added_tables = current_tables - snapshot_tables
    removed_tables = snapshot_tables - current_tables

    # Report new tables
    for t in added_tables:
        changes.append(f"[+] New table: {t}")

    # Report removed tables
    for t in removed_tables:
        changes.append(f"[-] Removed table: {t}")

    # Compare existing tables for column changes
    common_tables = current_tables & snapshot_tables
    for table in common_tables:
        # Get column information for comparison
        curr_cols = {col["name"]: col["type"] for col in current[table]["columns"]}
        snap_cols = {col["name"]: col["type"] for col in snapshot[table]["columns"]}

        # Find column differences
        added_cols = set(curr_cols) - set(snap_cols)
        removed_cols = set(snap_cols) - set(curr_cols)
        common_cols = set(curr_cols) & set(snap_cols)

        # Report new columns
        for c in added_cols:
            changes.append(f"[+] New column in {table}: {c} ({curr_cols[c]})")

        # Report removed columns
        for c in removed_cols:
            changes.append(f"[-] Removed column from {table}: {c} ({snap_cols[c]})")

        # Report column type changes
        for c in common_cols:
            if curr_cols[c] != snap_cols[c]:
                old_type = snap_cols[c]
                new_type = curr_cols[c]
                changes.append(
                    f"[~] Column {c} in {table} changed type: {old_type} -> {new_type}"
                )

        # Compare data if row limit is specified
        if row_limit > 0:
            current_rows = current[table].get("rows", [])[:row_limit]
            snapshot_rows = snapshot[table].get("rows", [])[:row_limit]
            if current_rows != snapshot_rows:
                changes.append(
                    f"[~] Data changed in {table} (showing up to {row_limit} rows):"
                )

    return changes
