"""
dbit CLI Entry Point

This module provides the main command-line interface for dbit, a Git-like tool
for managing database schemas with version control capabilities.

The CLI supports commands for:
- Initializing repositories
- Connecting to databases
- Creating schema snapshots
- Checking status and differences
- Viewing change logs
- Verifying schema quality
- Managing database connections

Author: Navaneet
License: MIT
"""


import click
from dbit.commands import connect, disconnect, init, log, snapshot, status, verify
from dbit.cli_help import HELP_BANNER, HELP_USAGE



@click.group(context_settings={"help_option_names": ["--help", "-h"]})
@click.pass_context
def cli(ctx):
    """
    dbit - Git-like CLI tool for managing database schemas.
    (Run 'dbit help' or 'dbit --help' for full usage)
    """
    if ctx.invoked_subcommand is None and (ctx.args and ctx.args[0] in ["help", "--help", "-h"]):
        click.echo(HELP_BANNER)
        click.echo(HELP_USAGE)
        ctx.exit()


cli.add_command(init.command)  # Initialize repository
cli.add_command(connect.command)  # Connect to database
cli.add_command(snapshot.command)  # Create schema snapshots
cli.add_command(status.command)  # Show status and changes
cli.add_command(log.command)  # Show change history
cli.add_command(verify.command)  # Verify schema quality
cli.add_command(disconnect.command)  # Disconnect from database

@cli.command("help", short_help="Show help message and usage.")
@click.pass_context
def help_cmd(ctx):
    """Show this help message and exit."""
    click.echo(HELP_BANNER)
    click.echo(HELP_USAGE)
