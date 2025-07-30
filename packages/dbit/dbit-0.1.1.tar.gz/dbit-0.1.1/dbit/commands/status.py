"""
Database Schema Status Command

This module provides the 'status' command for dbit, which shows the current
state of the database schema compared to the last snapshot. It highlights
changes that have been made since the last recorded version.

The status command:
- Compares current schema with latest snapshot
- Shows added/removed/modified tables and columns
- Optionally compares data changes
- Provides git-like status output

Author: Navaneet
License: MIT
"""

import json
import os

import click
import yaml

from dbit.database import get_schema_snapshot, load_connection
from dbit.utils.diff import diff_schemas


@click.command(name="status")
@click.option(
    "--content",
    default=0,
    help="Include row comparison in status (default: 0, no data)",
)
def command(content):
    """
    Show uncommitted database schema changes.

    Displays the differences between the current database schema and the
    last captured snapshot, similar to 'git status'. Shows what has changed
    since the last snapshot was taken.

    Args:
        content (int): Number of rows to compare for data changes.
                      If 0 (default), only schema changes are shown.
                      If > 0, includes data comparison up to that many rows.

    Examples:
        dbit status                      # Schema changes only
        dbit status --content 5          # Schema + data changes (5 rows)
    """
    # Check if dbit repository is initialized
    if not os.path.exists(".dbit/schema.yaml"):
        click.echo(".dbit repository not initialized. Please run 'dbit init' first.")
        return

    # Load repository configuration
    with open(".dbit/schema.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Check if database is connected
    if not config.get("db"):
        click.echo(
            "No database connection configured. Please run 'dbit connect' first."
        )
        return

    # Check if any snapshots exist
    current_version = config.get("current_version")
    if not current_version:
        click.echo(
            "No snapshots found. Please take a snapshot first using 'dbit snapshot'."
        )
        return

    # Check if snapshot file exists
    snap_path = os.path.join(".dbit/snapshots", current_version)
    if not os.path.exists(snap_path):
        click.echo(f"Snapshot file {current_version} not found in .dbit/snapshots.")
        return

    # Load the last snapshot
    with open(snap_path, "r") as f:
        snapshot = json.load(f)

    # Get current database schema
    conn = load_connection(config["db"])
    current = get_schema_snapshot(conn, include_rows=content)

    # Compare current state with snapshot
    diffs = diff_schemas(current, snapshot, row_limit=content)
    if diffs:
        click.echo("Changes since last snapshot:")
        for line in diffs:
            click.echo("  " + line)
    else:
        click.echo("No changes detected since last snapshot.")
