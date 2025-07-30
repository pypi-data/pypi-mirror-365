import os
import shutil

import pytest
import yaml
from click.testing import CliRunner

from dbit.commands import init


@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup the .dbit directory after each test."""
    if os.path.exists(".dbit"):
        shutil.rmtree(".dbit")
    yield
    if os.path.exists(".dbit"):
        shutil.rmtree(".dbit")


def test_dbit_init_creates_folder():
    runner = CliRunner()
    result = runner.invoke(init.command)

    assert result.exit_code == 0
    assert os.path.exists(".dbit/schema.yaml")
    assert "Initialized dbit repository." in result.output

    with open(".dbit/schema.yaml", "r") as f:
        data = yaml.safe_load(f)
        assert data["db"] is None
        assert data["migrations"] == []
        assert data["current_version"] is None
