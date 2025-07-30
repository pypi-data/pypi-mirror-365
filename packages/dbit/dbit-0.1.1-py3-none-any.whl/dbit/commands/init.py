"""
dbit Repository Initialization Command

This module provides the 'init' command for dbit, which initializes a new
repository for database schema version control. It creates the necessary
directory structure and configuration files.

The init command:
- Creates .dbit directory
- Initializes schema.yaml configuration file
- Sets up the basic repository structure for version control

Author: Navaneet
License: MIT
"""

import os

import click
import yaml


@click.command(name="init")
def command():
    """
    Initialize a dbit schema repository.

    Creates a new dbit repository in the current directory by setting up
    the .dbit folder and configuration files. This is similar to 'git init'
    but for database schema version control.

    Creates:
    - .dbit/ directory for repository data
    - .dbit/schema.yaml for configuration
    - Placeholder for migrations and snapshots

    Example:
        dbit init
    """
    # Check if repository already exists
    if not os.path.exists(".dbit"):
        # Create the .dbit directory
        os.makedirs(".dbit")

        # Initialize the schema configuration file
        schema_file = {
            "db": None,  # Database connection string
            "migrations": [],  # List of applied migrations
            "current_version": None,  # Current schema version
        }

        # Write the configuration to schema.yaml
        with open(".dbit/schema.yaml", "w") as f:
            yaml.dump(schema_file, f)

        click.echo("Initialized dbit repository.")
    else:
        click.echo("dbit repository already exists.")
