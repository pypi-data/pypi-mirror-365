"""
Database Schema Snapshot Command

This module provides the 'snapshot' command for dbit, which captures
the current state of database schema and optionally data. Snapshots
are stored as JSON files and used for version control and comparison.

The snapshot command:
- Captures complete schema information (tables, columns, types)
- Optionally includes sample data from tables
- Stores snapshots in versioned JSON files
- Updates repository configuration with current version

Author: Navaneet
License: MIT
"""

import json
import os

import click
import yaml

from dbit.database import get_schema_snapshot, load_connection


@click.command(name="snapshot")
@click.option(
    "--content",
    default=0,
    help="Number of rows of data to include (default: 0, no data)",
)
def command(content):
    """
    Take a snapshot of the current database schema (and optionally data).

    Creates a versioned snapshot of the database schema, including table
    structures, column definitions, and optionally sample data. Snapshots
    are stored as JSON files in .dbit/snapshots/ and used for tracking
    changes over time.

    Args:
        content (int): Number of rows to include from each table.
                      If 0 (default), only schema is captured.
                      If > 0, includes up to that many rows per table.

    Examples:
        dbit snapshot                    # Schema only
        dbit snapshot --content 10       # Schema + 10 rows per table
    """

    # Check if dbit repository is initialized
    config_path = ".dbit/schema.yaml"
    if not os.path.exists(config_path):
        click.echo(".dbit repository not initialized. Please run 'dbit init' first.")
        return

    # Load repository configuration
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Check if database is connected
    if not config.get("db"):
        click.echo(
            "No database connection configured. Please run 'dbit connect' first."
        )
        return

    # Connect to database and capture schema
    conn = load_connection(config["db"])
    snapshot = get_schema_snapshot(conn, include_rows=content)

    # Ensure snapshots directory exists
    snap_directory = ".dbit/snapshots"
    os.makedirs(snap_directory, exist_ok=True)

    # Calculate next version number
    existing = sorted(
        f
        for f in os.listdir(snap_directory)
        if f.startswith("v") and f.endswith(".json")
    )
    version_num = len(existing) + 1
    file_name = f"v{version_num}.json"

    # Save snapshot to JSON file
    with open(os.path.join(snap_directory, file_name), "w") as f:
        json.dump(snapshot, f, indent=2)

    # Update configuration with current version
    config["current_version"] = file_name
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f)

    click.echo(f"Snapshot saved as {file_name} in .dbit/snapshots")
