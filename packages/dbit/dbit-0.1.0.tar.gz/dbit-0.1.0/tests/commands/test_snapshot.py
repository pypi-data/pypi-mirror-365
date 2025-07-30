import json
import os
import shutil

import pytest
import yaml
from click.testing import CliRunner

from dbit.commands import snapshot


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def setup_schema_yaml(tmp_path):
    if os.path.exists(".dbit"):
        shutil.rmtree(".dbit")
    os.makedirs(".dbit/snapshots", exist_ok=True)
    with open(".dbit/schema.yaml", "w") as f:
        yaml.dump(
            {"db": "sqlite:///test.db", "migrations": [], "current_version": None}, f
        )
    yield
    shutil.rmtree(".dbit")


def test_snapshot_creates_json_snapshot_file(runner, monkeypatch):
    def fake_load_connection(db_url):
        import sqlite3

        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        cur.execute("INSERT INTO test (name) VALUES ('Alice'),('Bob')")
        conn.commit()
        return conn

    monkeypatch.setattr("dbit.commands.snapshot.load_connection", fake_load_connection)

    result = runner.invoke(snapshot.command, ["--content", "2"])
    assert result.exit_code == 0
    assert "Snapshot saved as v1.json in .dbit/snapshots" in result.output

    path = ".dbit/snapshots/v1.json"
    assert os.path.exists(path)

    with open(path, "r") as f:
        data = json.load(f)
        assert "test" in data
        assert "columns" in data["test"]
        assert "rows" in data["test"]
        assert len(data["test"]["rows"]) == 2
    assert "Snapshot saved as v1.json in .dbit/snapshots" in result.output

    path = ".dbit/snapshots/v1.json"
    assert os.path.exists(path)

    with open(path, "r") as f:
        data = json.load(f)
        assert "test" in data
        assert "columns" in data["test"]
        assert "rows" in data["test"]
        assert len(data["test"]["rows"]) == 2
