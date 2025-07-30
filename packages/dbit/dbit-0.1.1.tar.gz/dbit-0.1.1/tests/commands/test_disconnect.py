import os
import shutil
import tempfile

import pytest
import yaml
from click.testing import CliRunner

from dbit.commands import connect, disconnect, init


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def clean_dbit():
    if os.path.exists(".dbit"):
        shutil.rmtree(".dbit")
    yield
    if os.path.exists(".dbit"):
        shutil.rmtree(".dbit")


def test_disconnect_removes_db_key(runner):
    runner.invoke(init.command)

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        temp_db_path = tmp_db.name

    try:
        result = runner.invoke(connect.command, input=f"sqlite:///{temp_db_path}\n")
        assert result.exit_code == 0

        with open(".dbit/schema.yaml", "r") as f:
            before = yaml.safe_load(f)
        assert before["db"] is not None

        result = runner.invoke(disconnect.command)
        assert result.exit_code == 0
        assert "Disconnected from the database." in result.output

        with open(".dbit/schema.yaml", "r") as f:
            after = yaml.safe_load(f)
        assert after["db"] is None

    finally:

        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)
