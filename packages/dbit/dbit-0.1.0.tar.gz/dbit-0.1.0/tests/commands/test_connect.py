import os
import shutil

import pytest
import yaml
from click.testing import CliRunner

from dbit.commands import connect


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def setup_dbit_folder():
    """Create fake .dbit folder with empty schema.yaml."""
    if os.path.exists(".dbit"):
        shutil.rmtree(".dbit")
    os.makedirs(".dbit")
    with open(".dbit/schema.yaml", "w") as f:
        yaml.dump({"db": None, "migrations": [], "current_version": None}, f)
    yield
    shutil.rmtree(".dbit")


def test_connect_command_postgres_connection_string(monkeypatch, runner):
    def mock_test_connection(url):
        assert "postgres://" in url
        return True  # Simulate successful connection

    monkeypatch.setattr("dbit.commands.connect.test_connection", mock_test_connection)

    result = runner.invoke(
        connect.command, input="postgres://user:pass@localhost:5432/testdb\n"
    )

    assert result.exit_code == 0
    assert "Enter database connection string" in result.output
    assert "Connected to database successfully!" in result.output

    with open(".dbit/schema.yaml", "r") as f:
        config = yaml.safe_load(f)
        assert config["db"] == "postgres://user:pass@localhost:5432/testdb"


def test_connect_command_mysql_connection_string(monkeypatch, runner):
    def mock_test_connection(url):
        assert "mysql://" in url
        return True

    monkeypatch.setattr("dbit.commands.connect.test_connection", mock_test_connection)

    result = runner.invoke(
        connect.command, input="mysql://user:pass@localhost:3306/testdb\n"
    )

    assert result.exit_code == 0
    assert "Enter database connection string" in result.output
    assert "Connected to database successfully!" in result.output

    with open(".dbit/schema.yaml", "r") as f:
        config = yaml.safe_load(f)
        assert config["db"] == "mysql://user:pass@localhost:3306/testdb"


def test_connect_command_sqlite_connection_string(monkeypatch, runner):
    def mock_test_connection(url):
        assert "sqlite://" in url
        return True  # Simulate successful connection

    monkeypatch.setattr("dbit.commands.connect.test_connection", mock_test_connection)

    result = runner.invoke(connect.command, input="sqlite:///test.db\n")

    assert result.exit_code == 0
    assert "Enter database connection string" in result.output
    assert "Connected to database successfully!" in result.output

    with open(".dbit/schema.yaml", "r") as f:
        config = yaml.safe_load(f)
        assert config["db"] == "sqlite:///test.db"
