"""
Database Schema Validation Rules

This module provides a collection of validation rules for checking database
schema quality and best practices. Rules are used by the verify command to
ensure databases follow proper design principles.

The rule system includes:
- Base SchemaRule class for custom rules
- Built-in rules for common validations
- Extensible architecture for adding new rules

Built-in rules:
- TableEmptyRule: Checks for empty tables
- PrimaryKeyRule: Ensures all tables have primary keys
- IndexRule: Validates foreign key indexing
- DataTypeRule: Checks for appropriate data types
- NullableRule: Analyzes nullable field usage

Author: Navaneet
License: MIT
"""

import sqlalchemy as sa


class SchemaRule:
    """
    Base class for schema validation rules.

    All schema validation rules inherit from this class and must implement
    the check() and get_message() methods. Rules are applied during the
    verify command to validate database schema quality.

    Methods:
        check(): Perform the validation check
        get_message(): Return a description of any violations found
    """

    def check(self, inspector, connection):
        """
        Perform the validation check.

        Args:
            inspector: SQLAlchemy inspector for schema introspection
            connection: Database connection for queries

        Returns:
            bool: True if validation passes, False if violations found
        """
        raise NotImplementedError

    def get_message(self):
        """
        Get a human-readable message describing any violations.

        Returns:
            str: Description of the validation violation
        """
        raise NotImplementedError


class TableEmptyRule(SchemaRule):
    """
    Check if any tables are empty.

    This rule identifies tables that contain no data, which might indicate
    unused tables or missing data population. Empty tables are reported
    as warnings rather than errors.
    """

    def __init__(self):
        self.empty_tables = []

    def check(self, inspector, connection):
        """Check each table for row count."""
        for table_name in inspector.get_table_names():
            count = connection.execute(
                sa.text(f"SELECT COUNT(*) FROM {table_name}")
            ).scalar()
            if count == 0:
                self.empty_tables.append(table_name)
        return len(self.empty_tables) == 0

    def get_message(self):
        """Return message about empty tables."""
        tables = ", ".join(self.empty_tables)
        plural = "s" if len(self.empty_tables) > 1 else ""
        verb = "are" if len(self.empty_tables) > 1 else "is"
        return f"Table{plural} {tables} {verb} empty."


class PrimaryKeyRule(SchemaRule):
    """
    Check if all tables have primary keys.

    This rule ensures that every table has a primary key defined, which is
    essential for data integrity, replication, and many database operations.
    Tables without primary keys are reported as critical errors.
    """

    def __init__(self):
        self.tables_without_pk = []

    def check(self, inspector, connection):
        """Check each table for primary key constraint."""
        for table_name in inspector.get_table_names():
            pk = inspector.get_pk_constraint(table_name)
            if not pk["constrained_columns"]:
                self.tables_without_pk.append(table_name)
        return len(self.tables_without_pk) == 0

    def get_message(self):
        """Return message about missing primary keys."""
        tables = ", ".join(self.tables_without_pk)
        plural = "s" if len(self.tables_without_pk) > 1 else ""
        verb = "do" if len(self.tables_without_pk) > 1 else "does"
        return f"Table{plural} {tables} {verb} not have a primary key."


class IndexRule(SchemaRule):
    """
    Check if foreign key columns have indexes.

    This rule ensures that foreign key columns are properly indexed, which
    is important for query performance and referential integrity operations.
    Missing indexes on foreign keys can cause performance issues.
    """

    def __init__(self):
        self.missing_indexes = []

    def check(self, inspector, connection):
        """Check foreign key columns for indexes."""
        for table_name in inspector.get_table_names():
            # Get all indexed columns
            indexes = {
                col
                for idx in inspector.get_indexes(table_name)
                for col in idx["column_names"]
            }
            # Check each foreign key
            for fk in inspector.get_foreign_keys(table_name):
                for col in fk["constrained_columns"]:
                    if col not in indexes:
                        self.missing_indexes.append((table_name, col))
        return len(self.missing_indexes) == 0

    def get_message(self):
        return "\n".join(
            f"Foreign key column '{col}' in table '{table}' has no index."
            for table, col in self.missing_indexes
        )


class DataTypeRule(SchemaRule):
    """Check for recommended data types (e.g., TEXT vs VARCHAR)."""

    def __init__(self):
        self.issues = []

    def check(self, inspector, connection):
        for table_name in inspector.get_table_names():
            for column in inspector.get_columns(table_name):
                col_type = str(column["type"]).lower()
                if "varchar" in col_type and not column.get("length"):
                    self.issues.append(
                        (table_name, column["name"], "unbounded VARCHAR")
                    )
        return len(self.issues) == 0

    def get_message(self):
        return "\n".join(
            f"Column '{col}' in table '{table}' uses {issue}."
            for table, col, issue in self.issues
        )


class NullableRule(SchemaRule):
    """Check for columns that should probably not be nullable."""

    def __init__(self):
        self.nullable_columns = []

    def check(self, inspector, connection):
        for table_name in inspector.get_table_names():
            pk = inspector.get_pk_constraint(table_name)
            pk_columns = set(pk["constrained_columns"])

            for column in inspector.get_columns(table_name):
                # Skip PRIMARY KEY columns as they are implicitly NOT NULL
                if (
                    column["name"] in pk_columns
                    and "INTEGER" in str(column["type"]).upper()
                ):
                    continue

                if column["nullable"] and any(
                    key in column["name"].lower()
                    for key in ["id", "code", "type", "status"]
                ):
                    self.nullable_columns.append((table_name, column["name"]))
        return len(self.nullable_columns) == 0

    def get_message(self):
        return "\n".join(
            f"Column '{col}' in table '{table}' is nullable but probably shouldn't be."
            for table, col in self.nullable_columns
        )


def get_all_rules():
    """Return a list of all schema validation rules."""
    return [
        TableEmptyRule(),
        PrimaryKeyRule(),
        IndexRule(),
        DataTypeRule(),
        NullableRule(),
    ]
