"""
Database Connection Management

This module handles database connections and operations for multiple database types.
It provides a unified interface for connecting to PostgreSQL, MySQL, and SQLite
databases, along with utilities for schema introspection and data extraction.

Supported databases:
- PostgreSQL (using psycopg2)
- MySQL (using mysql-connector-python)
- SQLite (using sqlite3)

Functions:
- test_connection: Validate database connection strings
- load_connection: Create database connections
- get_schema_snapshot: Extract schema and data from databases

Author: Navaneet
License: MIT
"""

import sqlite3
from urllib.parse import urlparse

import mysql.connector
import psycopg2


def test_connection(db_url):
    """
    Test database connection using the provided connection string.

    This function validates that the database connection string is correct
    and that the database is accessible. It supports PostgreSQL, MySQL,
    and SQLite databases.

    Args:
        db_url (str): Database connection string in URL format
                     Examples:
                     - postgresql://user:pass@host:port/dbname
                     - mysql://user:pass@host:port/dbname
                     - sqlite:///path/to/database.db

    Raises:
        ValueError: If the database type is not supported
        Exception: If connection fails (network, auth, etc.)

    Example:
        test_connection("postgresql://user:pass@localhost/mydb")
    """
    parsed = urlparse(db_url)

    # Test PostgreSQL connection
    if parsed.scheme.startswith("postgres"):
        conn = psycopg2.connect(db_url)
        conn.close()

    # Test MySQL connection
    elif parsed.scheme.startswith("mysql"):
        conn = mysql.connector.connect(
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 3306,
            database=parsed.path.lstrip("/"),
        )
        conn.close()

    # Test SQLite connection
    elif parsed.scheme.startswith("sqlite"):
        path = parsed.path
        conn = sqlite3.connect(path)
        conn.close()

    else:
        raise ValueError(
            f"Unsupported database type: {parsed.scheme}. "
            f"Supported types: postgresql, mysql, sqlite"
        )


def load_connection(db_url):
    """
    Create and return a database connection object.

    This function creates an actual database connection that can be used
    for queries and operations. The connection type is determined by the
    URL scheme.

    Args:
        db_url (str): Database connection string in URL format

    Returns:
        Connection object specific to the database type:
        - psycopg2.connection for PostgreSQL
        - mysql.connector.connection for MySQL
        - sqlite3.connection for SQLite

    Raises:
        ValueError: If the database type is not supported
        Exception: If connection fails

    Example:
        conn = load_connection("sqlite:///mydb.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        conn.close()
    """
    parsed = urlparse(db_url)

    # Create PostgreSQL connection
    if parsed.scheme.startswith("postgres"):
        return psycopg2.connect(db_url)

    # Create MySQL connection
    elif parsed.scheme.startswith("mysql"):
        return mysql.connector.connect(
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 3306,
            database=parsed.path.lstrip("/"),
        )

    # Create SQLite connection
    elif parsed.scheme.startswith("sqlite"):
        return sqlite3.connect(parsed.path)

    else:
        raise ValueError(
            f"Unsupported database type: {parsed.scheme}. "
            f"Supported types: postgresql, mysql, sqlite"
        )


def get_schema_snapshot(conn, include_rows=0):
    """
    Extract schema information and optionally data from the database.

    This function introspects the database to extract table schemas including
    column names and types. It can optionally include a limited number of rows
    of actual data from each table.

    Args:
        conn: Database connection object (sqlite3, psycopg2, or mysql.connector)
        include_rows (int): Number of rows to include per table (default: 0)
                           If 0, no data is included, only schema

    Returns:
        dict: Schema information in the format:
              {
                  'table_name': {
                      'columns': [{'name': str, 'type': str}, ...],
                      'rows': [[row_data], ...] or []
                  }
              }

    Example:
        conn = load_connection("sqlite:///mydb.db")
        schema = get_schema_snapshot(conn, include_rows=5)
        print(schema['users']['columns'])  # Column info
        print(schema['users']['rows'])     # First 5 rows
    """
    cursor = conn.cursor()
    schema = {}

    # Handle SQLite databases
    if isinstance(conn, sqlite3.Connection):
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall()]

        for table in tables:
            schema[table] = {"columns": [], "rows": []}

            # Get column information using PRAGMA
            cursor.execute(f"PRAGMA table_info({table})")
            schema[table]["columns"] = [
                {"name": c[1], "type": c[2]} for c in cursor.fetchall()
            ]

            # Get sample data if requested
            if include_rows:
                cursor.execute(f"SELECT * FROM {table} LIMIT {include_rows}")
                schema[table]["rows"] = cursor.fetchall()

    # Handle PostgreSQL databases
    elif isinstance(conn, psycopg2.extensions.connection):
        # Get all table names from public schema
        cursor.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='public'
        """
        )
        tables = [r[0] for r in cursor.fetchall()]

        for table in tables:
            schema[table] = {"columns": [], "rows": []}

            # Get column information from information_schema
            cursor.execute(
                f"""
                SELECT column_name, data_type FROM information_schema.columns
                WHERE table_name = '{table}'
            """
            )
            schema[table]["columns"] = [
                {"name": c[0], "type": c[1]} for c in cursor.fetchall()
            ]

            # Get sample data if requested
            if include_rows:
                cursor.execute(f"SELECT * FROM {table} LIMIT {include_rows}")
                schema[table]["rows"] = cursor.fetchall()

    # Handle MySQL databases
    elif isinstance(conn, mysql.connector.connection.MySQLConnection):
        # Get all table names
        cursor.execute("SHOW TABLES")
        tables = [r[0] for r in cursor.fetchall()]

        for table in tables:
            schema[table] = {"columns": [], "rows": []}

            # Get column information using DESCRIBE
            cursor.execute(f"DESCRIBE {table}")
            schema[table]["columns"] = [
                {"name": c[0], "type": c[1]} for c in cursor.fetchall()
            ]

            # Get sample data if requested
            if include_rows:
                cursor.execute(f"SELECT * FROM {table} LIMIT {include_rows}")
                schema[table]["rows"] = cursor.fetchall()

    cursor.close()
    conn.close()
    return schema
