from typer.testing import CliRunner
from unittest.mock import patch
from hkg_cli.main import app

runner = CliRunner()


def test_app_version():
    """Test the --version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "hkg-cli version: v" in result.stdout


@patch("hkg_cli.main.start")
def test_run_command(mock_start):
    """Test the 'run' command."""
    result = runner.invoke(app, ["run"])
    assert result.exit_code == 0
    mock_start.assert_called_once()


@patch("hkg_cli.main.stop")
def test_stop_command(mock_stop):
    """Test the 'stop' command without clearing."""
    result = runner.invoke(app, ["stop"])
    assert result.exit_code == 0
    mock_stop.assert_called_once()


@patch("hkg_cli.main.nuke")
def test_stop_command_with_clear(mock_nuke):
    """Test the 'stop' command with the --clear flag."""
    result = runner.invoke(app, ["stop", "--clear"])
    assert result.exit_code == 0
    mock_nuke.assert_called_once()
