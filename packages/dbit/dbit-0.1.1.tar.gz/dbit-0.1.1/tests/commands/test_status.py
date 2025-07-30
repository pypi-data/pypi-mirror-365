import json
import os
import shutil

import pytest
import yaml
from click.testing import CliRunner

from dbit.commands import status


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def setup_snapshot(tmp_path):
    if os.path.exists(".dbit"):
        shutil.rmtree(".dbit")
    os.makedirs(".dbit/snapshots")

    snapshot_data = {
        "test": {"columns": [{"name": "id", "type": "INTEGER"}], "rows": [[1]]}
    }

    with open(".dbit/snapshots/v1.json", "w") as f:
        json.dump(snapshot_data, f)

    with open(".dbit/schema.yaml", "w") as f:
        yaml.dump(
            {"db": "sqlite:///test.db", "migrations": [], "current_version": "v1.json"},
            f,
        )
    yield
    shutil.rmtree(".dbit")


@pytest.fixture
def monkey_patch_live_db(monkeypatch):
    def fake_load_connection(db_url):
        import sqlite3

        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        cur.execute("INSERT INTO test (name) VALUES ('Alice'),('Bob')")
        conn.commit()
        return conn

    monkeypatch.setattr("dbit.commands.status.load_connection", fake_load_connection)


def test_status_with_diff(runner, monkey_patch_live_db):
    result = runner.invoke(status.command, ["--content", "2"])
    assert result.exit_code == 0
    assert "Changes since last snapshot:" in result.output
    assert "[~] Data changed in test (showing up to 2 rows):" in result.output
