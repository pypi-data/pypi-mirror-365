import os

import yaml
from click.testing import CliRunner

from dbit.commands import log


def test_log_shows_migrations(tmp_path):
    os.chdir(tmp_path)

    schema_data = {
        "db": None,
        "current_version": 3,
        "migrations": [
            {"version": 1, "name": "init", "description": "Added users table"},
            {"version": 2, "name": "alter_users", "description": "Added email"},
            {"version": 3, "name": "drop_temp", "description": "Dropped temp table"},
        ],
    }

    os.mkdir(".dbit")
    with open(".dbit/schema.yaml", "w") as f:
        yaml.safe_dump(schema_data, f)

    runner = CliRunner()
    result = runner.invoke(log.command)

    assert result.exit_code == 0
    assert "Version: 1: init - Added users table" in result.output
    assert "Version: 2: alter_users - Added email" in result.output
    assert "Version: 3: drop_temp - Dropped temp table" in result.output
