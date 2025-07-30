"""
Database Connection Command

This module provides the 'connect' command for dbit, which establishes
and configures database connections. It supports PostgreSQL, MySQL,
and SQLite databases through connection strings.

The connect command:
- Tests database connectivity
- Stores connection information in repository config
- Supports both command-line and interactive input

Supported URL formats:
- postgresql://user:password@host:port/database
- mysql://user:password@host:port/database
- sqlite:///path/to/database.db

Author: Navaneet
License: MIT
"""

import os

import click
import yaml

from dbit.database import test_connection


@click.command(name="connect")
@click.option("--db-url", envvar="DB_URL", help="Database connection string")
def command(db_url):
    """
    Connect to a database and save the connection string in config.

    Establishes a connection to a database and stores the connection
    information for future use. The connection is tested before saving.

    Args:
        db_url (str): Database connection string. If not provided,
                     user will be prompted interactively.

    Environment Variables:
        DB_URL: Can be set to provide the connection string

    Examples:
        dbit connect --db postgresql://user:pass@localhost/mydb
        dbit connect --db sqlite:///./myproject.db
        dbit connect  # Interactive prompt
    """
    # Get database URL from option or prompt user
    if db_url:
        db = db_url
    else:
        db = click.prompt(
            "Enter database connection string "
            "(e.g., postgresql://user:password@localhost/dbname)",
            type=str,
        )

    # Test the connection before saving
    try:
        test_connection(db)
    except Exception as e:
        click.echo(f"Connection failed: {e}")
        return

    # Check if dbit repository exists
    config_path = ".dbit/schema.yaml"
    if not os.path.exists(config_path):
        click.echo(".dbit repository not found. Run 'dbit init' first.")
        return

    # Load existing configuration
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    # Update with new database connection
    config["db"] = db

    # Save updated configuration
    with open(config_path, "w") as file:
        yaml.safe_dump(config, file)

    click.echo("Connected to database successfully!")
