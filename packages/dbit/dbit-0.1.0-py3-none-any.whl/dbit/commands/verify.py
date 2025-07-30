"""
Database Schema Verification Command

This module provides the 'verify' command for dbit, which performs quality
checks and validation on database schemas. It applies configurable rules
to ensure schema best practices and data quality standards.

The verify command:
- Validates schema structure and design
- Checks for common database issues
- Applies configurable quality rules
- Reports violations and suggestions

Verification rules include:
- Primary key requirements
- Nullable field analysis
- Data type validation
- Naming convention checks
- Index recommendations

Author: Navaneet
License: MIT
"""

import os

import click
import yaml
from sqlalchemy import create_engine, inspect

from dbit.utils.rules import DataTypeRule, NullableRule, TableEmptyRule, get_all_rules


def get_db_url(schema_file=".dbit/schema.yaml"):
    """
    Get database URL from schema configuration file.

    Reads the dbit configuration file and extracts the database connection
    string for verification operations.

    Args:
        schema_file (str): Path to schema configuration file

    Returns:
        str: Database connection URL

    Raises:
        click.ClickException: If repository not initialized or no connection configured
    """
    if not os.path.exists(schema_file):
        raise click.ClickException(
            ".dbit repository not initialized. Please run 'dbit init' first."
        )

    with open(schema_file, "r") as f:
        config = yaml.safe_load(f)

    if not config.get("db"):
        raise click.ClickException(
            "No database connection configured. Please run 'dbit connect' first."
        )

    return config["db"]


def verify_schema_and_quality(db_url):
    """
    Verify database schema and data quality using defined rules.

    Performs comprehensive validation of the database schema by applying
    a set of quality rules. Rules check for common issues like missing
    primary keys, inappropriate nullable fields, and data type problems.

    Args:
        db_url (str): Database connection string

    Raises:
        click.ClickException: If verification fails due to rule violations

    Example:
        verify_schema_and_quality("sqlite:///mydb.db")
    """
    try:
        # Create database engine and inspector
        engine = create_engine(db_url)
        inspector = inspect(engine)

        # Get all verification rules
        rules = get_all_rules()
        failures = []
        warnings = []

        # Run verification rules against database
        with engine.connect() as conn:
            for rule in rules:
                if not rule.check(inspector, conn):
                    message = rule.get_message()
                    # Categorize as warning or error based on rule type
                    if isinstance(rule, (TableEmptyRule, DataTypeRule, NullableRule)):
                        warnings.append(message)
                    else:
                        failures.append(message)

        # Report failures (critical issues)
        if failures:
            click.secho("\nSchema validation failed!", fg="red", bold=True)
            for failure in failures:
                click.secho("ERROR: ", fg="red", bold=True, nl=False)
                click.secho(failure, fg="red")

        # Report warnings (potential issues)
        if warnings:
            click.secho("\nWarnings found:", fg="yellow", bold=True)
            for warning in warnings:
                click.secho("WARN:  ", fg="yellow", bold=True, nl=False)
                click.secho(warning, fg="yellow")

        # Provide final verification status
        if not failures and not warnings:
            click.secho(
                "\nSUCCESS: Schema and data quality verification passed",
                fg="green",
                bold=True,
            )
        elif not failures:
            click.secho(
                "\nSUCCESS: Schema and data quality verification completed",
                fg="green",
                bold=True,
            )
            click.secho(
                "         (with warnings - review and fix if needed)", fg="yellow"
            )
        else:
            raise click.ClickException(
                "Schema validation failed. Please fix the issues above."
            )

    except Exception as e:
        raise click.ClickException(f"Error during verification: {str(e)}")


@click.command(name="verify")
@click.option("--fix", is_flag=True, help="Attempt to fix common issues automatically")
def command(fix):
    """
    Verify database schema and quality checks.

    Performs comprehensive validation of the database schema to ensure
    it follows best practices and quality standards. Checks for common
    issues and provides actionable feedback.

    Args:
        fix (bool): Whether to attempt automatic fixes for common issues
                   (Currently not implemented, reserved for future use)

    The verification includes:
    - Primary key validation
    - Nullable field analysis
    - Data type appropriateness
    - Table structure validation
    - Data quality checks

    Examples:
        dbit verify                    # Run verification
        dbit verify --fix              # Run with auto-fix (future feature)
    """
    db_url = get_db_url()
    verify_schema_and_quality(db_url)
