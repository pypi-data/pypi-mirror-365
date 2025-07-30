"""
Schema log command for dbit CLI.

This module handles viewing the history of schema snapshots:
- Lists all snapshots with timestamps
- Displays version numbers, names, and descriptions
- Provides schema change analysis between snapshots
- Offers git-like commit history view

Author: Navaneet
License: MIT
"""

import os

import click
import yaml


def compare_schemas(old_schema, new_schema):
    """
    Compare two schema snapshots and return a description of changes.

    Analyzes the differences between two database schema snapshots and
    generates human-readable descriptions of what changed.

    Args:
        old_schema (dict): Previous schema snapshot
        new_schema (dict): Current schema snapshot

    Returns:
        list: List of change descriptions

    Example:
        changes = compare_schemas(old_snap, new_snap)
        for change in changes:
            print(change)  # "Added new table 'users'"
    """
    changes = []

    # Compare tables
    old_tables = set(old_schema.keys())
    new_tables = set(new_schema.keys())

    # Check for added/removed tables
    added_tables = new_tables - old_tables
    removed_tables = old_tables - new_tables

    for table in added_tables:
        changes.append(f"Added new table '{table}'")

    for table in removed_tables:
        changes.append(f"Removed table '{table}'")

    # Check for changes in existing tables
    for table in old_tables & new_tables:
        old_cols = {col["name"]: col for col in old_schema[table]["columns"]}
        new_cols = {col["name"]: col for col in new_schema[table]["columns"]}

        # Check for added/modified/removed columns
        for col_name, col_info in new_cols.items():
            if col_name not in old_cols:
                changes.append(
                    f"Added column '{col_name}' ({col_info['type']}) to table '{table}'"
                )
            elif old_cols[col_name] != col_info:
                changes.append(f"Modified column '{col_name}' in table '{table}'")

        for col_name in old_cols:
            if col_name not in new_cols:
                changes.append(f"Removed column '{col_name}' from table '{table}'")

    return changes


@click.command(name="log")
def command():
    """
    Show the log of database schema changes from migration history.

    Displays a chronological history of all database schema changes,
    including migrations that have been applied. Shows version numbers,
    migration names, and descriptions in a git-like log format.

    The log shows:
    - Migration version numbers
    - Migration names and descriptions
    - Chronological order of changes

    Example:
        dbit log

    Output example:
        Migration History:
        Version: 3: add_indexes - Added indexes for performance
        Version: 2: alter_users - Added email column to users table
        Version: 1: init - Initial schema setup
    """
    # Check if dbit repository exists
    schema_path = ".dbit/schema.yaml"
    if not os.path.exists(schema_path):
        click.echo("No schema found. Please run 'dbit init' first.")
        return

    # Load schema configuration
    with open(schema_path, "r") as f:
        schema_data = yaml.safe_load(f)

    # Check if migrations exist
    if "migrations" not in schema_data or not schema_data["migrations"]:
        click.echo("No migrations found in schema history.")
        return

    # Display migration history from schema.yaml
    click.echo("\nMigration History:")
    for migration in schema_data["migrations"]:
        version = migration["version"]
        name = migration["name"]
        description = migration["description"]
        click.echo(f"Version: {version}: {name} - {description}")
