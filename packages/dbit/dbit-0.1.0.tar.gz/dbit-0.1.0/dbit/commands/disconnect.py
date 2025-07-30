"""
Schema disconnection command for dbit CLI.

This module handles disconnecting from the current database:
- Removes database connection from configuration
- Preserves other repository settings
- Provides feedback on successful disconnection

Author: Navaneet
License: MIT
"""

from pathlib import Path

import click
import yaml

# Path to the schema configuration file
SCHEMA_PATH = Path(".dbit/schema.yaml")


@click.command(name="disconnect")
def command():
    """
    Disconnect the current database connection.

    Removes the database connection string from the repository configuration
    while preserving all other settings like migrations and current version.
    After disconnecting, you can use 'dbit connect' to establish a new connection.

    This is useful when:
    - Switching between different databases
    - Clearing sensitive connection information
    - Preparing repository for sharing/version control

    Example:
        dbit disconnect
    """
    # Check if dbit repository exists
    if not SCHEMA_PATH.exists():
        click.echo("No dbit schema found. Please run 'dbit init' first.")
        return

    # Load current configuration
    with SCHEMA_PATH.open("r") as f:
        config = yaml.safe_load(f)

    # Check if there's a connection to disconnect
    if config.get("db") is None:
        click.echo(
            "No database connection configured. Please run 'dbit connect' first."
        )
        return

    # Remove the database connection
    config["db"] = None

    # Save the updated configuration
    with SCHEMA_PATH.open("w") as f:
        yaml.safe_dump(config, f)

    click.secho(
        "Disconnected from the database. You can reconnect using 'dbit connect'.",
        fg="green",
    )
