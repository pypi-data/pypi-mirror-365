import os
import sqlite3

import click
import pytest
from click.testing import CliRunner

from dbit.commands import verify


def test_verify_schema_pass(tmp_path, capsys):
    db_file = tmp_path / "good.db"
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """
    )
    conn.execute("CREATE INDEX idx_users_email ON users(email)")
    conn.execute("CREATE INDEX idx_users_status ON users(status)")
    conn.execute(
        "INSERT INTO users VALUES "
        "(1, 'EXT001', 'Alice', 'alice@test.com', 'active', CURRENT_TIMESTAMP)"
    )
    conn.commit()
    conn.close()

    verify.verify_schema_and_quality(f"sqlite:///{db_file}")
    captured = capsys.readouterr()
    assert "Schema and data quality verification passed" in captured.out


def test_verify_schema_missing(tmp_path, capsys):
    db_file = tmp_path / "missing.db"
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE users (
            name TEXT,
            email VARCHAR
        )
    """
    )
    conn.commit()
    conn.close()

    with pytest.raises(click.ClickException) as exc_info:
        verify.verify_schema_and_quality(f"sqlite:///{db_file}")
    assert "Schema validation failed" in str(exc_info.value)


def test_verify_schema_type(tmp_path, capsys):
    # Create a test database with type issues
    db_file = tmp_path / "types.db"
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            status TEXT NULL,
            type VARCHAR
        )
    """
    )
    conn.commit()
    conn.close()

    verify.verify_schema_and_quality(f"sqlite:///{db_file}")
    captured = capsys.readouterr()
    assert (
        "Column 'status' in table 'users' is nullable but probably shouldn't be"
        in captured.out
    )
    assert "uses unbounded VARCHAR" in captured.out


def test_verify_shows_analysis(tmp_path, capsys):
    # Test that verification shows detailed analysis
    db_file = tmp_path / "analysis.db"
    conn = sqlite3.connect(db_file)
    conn.execute("CREATE TABLE empty (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

    verify.verify_schema_and_quality(f"sqlite:///{db_file}")
    captured = capsys.readouterr()
    assert "Table empty is empty" in captured.out
    assert (
        "verification completed" in captured.out.lower()
        and "warnings" in captured.out.lower()
    )


def test_verify_quality_pass(tmp_path, capsys):
    # Test passing quality checks - all fields properly constrained
    db_file = tmp_path / "quality.db"
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL CHECK (price > 0),
            status TEXT NOT NULL,
            type TEXT NOT NULL
        )
    """
    )
    conn.execute("CREATE INDEX idx_products_status ON products(status)")
    conn.execute("CREATE INDEX idx_products_type ON products(type)")
    conn.execute("CREATE INDEX idx_products_product_id ON products(product_id)")
    conn.execute(
        "INSERT INTO products VALUES (1, 'PRD001', 'Test', 10.0, 'active', 'physical')"
    )
    conn.commit()
    conn.close()

    verify.verify_schema_and_quality(f"sqlite:///{db_file}")
    captured = capsys.readouterr()
    assert "Schema and data quality verification passed" in captured.out


def test_verify_quality_fail(tmp_path, capsys):
    # Test failing quality checks
    db_file = tmp_path / "bad_quality.db"
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE orders (
            id INTEGER,
            user_id INTEGER REFERENCES users(id),
            status VARCHAR,
            amount REAL
        )
    """
    )
    conn.commit()
    conn.close()

    with pytest.raises(click.ClickException) as exc_info:
        verify.verify_schema_and_quality(f"sqlite:///{db_file}")
    assert "Schema validation failed" in str(exc_info.value)


def test_verify_cli_pass(tmp_path):
    # Test CLI command success with a clean schema
    runner = CliRunner()
    db_file = tmp_path / "cli_test.db"
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE test (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """
    )
    conn.execute("CREATE INDEX idx_test_status ON test(status)")
    conn.execute("CREATE INDEX idx_test_code ON test(code)")
    conn.execute("INSERT INTO test VALUES (1, 'TST001', 'Test', 'active')")
    conn.commit()
    conn.close()

    with runner.isolated_filesystem():
        os.makedirs(".dbit")
        with open(".dbit/schema.yaml", "w") as f:
            f.write(f"db: sqlite:///{db_file}\n")
        result = runner.invoke(verify.command)
        assert result.exit_code == 0
        assert "Schema and data quality verification passed" in result.output


def test_verify_cli_fail(tmp_path):
    # Test CLI command failure
    runner = CliRunner()
    db_file = tmp_path / "cli_fail.db"
    conn = sqlite3.connect(db_file)
    conn.execute("CREATE TABLE test (name TEXT)")  # No primary key
    conn.commit()
    conn.close()

    with runner.isolated_filesystem():
        os.makedirs(".dbit")
        with open(".dbit/schema.yaml", "w") as f:
            f.write(f"db: sqlite:///{db_file}\n")
        result = runner.invoke(verify.command)
        assert result.exit_code != 0
        assert "does not have a primary key" in result.output
