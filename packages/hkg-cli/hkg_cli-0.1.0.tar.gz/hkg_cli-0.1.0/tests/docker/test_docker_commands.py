from unittest.mock import patch, call
import pytest
from subprocess import CalledProcessError
import typer

from hkg_cli.docker import commands as docker_cmd


@patch("hkg_cli.docker.commands.check_call")
def test_get_command_podman_compose(mock_check_call):
    """Test that _get_command returns ['podman', 'compose'] when it is available."""
    mock_check_call.side_effect = [None]  # podman compose version succeeds
    command = docker_cmd._get_command()
    assert command == ["podman", "compose"]
    mock_check_call.assert_called_once_with(["podman", "compose", "version"])


@patch("hkg_cli.docker.commands.check_call")
def test_get_command_docker_compose(mock_check_call):
    """Test that _get_command returns ['docker', 'compose'] when podman fails."""
    mock_check_call.side_effect = [
        CalledProcessError(1, "podman compose version"),  # podman compose version fails
        None,  # docker compose version succeeds
    ]
    command = docker_cmd._get_command()
    assert command == ["docker", "compose"]
    assert mock_check_call.call_count == 2
    mock_check_call.assert_has_calls(
        [
            call(["podman", "compose", "version"]),
            call(["docker", "compose", "version"]),
        ]
    )


@patch("hkg_cli.docker.commands.check_call")
def test_get_command_docker_compose_legacy(mock_check_call):
    """Test that _get_command returns ['docker-compose'] when podman and docker compose fail."""
    mock_check_call.side_effect = [
        CalledProcessError(1, "podman compose version"),  # podman compose version fails
        CalledProcessError(1, "docker compose version"),  # docker compose version fails
        None,  # docker-compose version succeeds
    ]
    command = docker_cmd._get_command()
    assert command == ["docker-compose"]
    assert mock_check_call.call_count == 3
    mock_check_call.assert_has_calls(
        [
            call(["podman", "compose", "version"]),
            call(["docker", "compose", "version"]),
            call(["docker-compose", "version"]),
        ]
    )


@patch("hkg_cli.docker.commands.check_call")
def test_get_command_none_available(mock_check_call):
    """Test that _get_command raises CalledProcessError when no command is available."""
    mock_check_call.side_effect = [
        CalledProcessError(1, "podman compose version"),
        CalledProcessError(1, "docker compose version"),
        CalledProcessError(1, "docker-compose version"),
    ]
    with pytest.raises(CalledProcessError):
        docker_cmd._get_command()
    assert mock_check_call.call_count == 3


@patch("hkg_cli.docker.commands.check_call")
def test_get_command_podman_missing_file_not_found(mock_check_call):
    """Test that _get_command falls back to docker compose if podman binary is missing (FileNotFoundError)."""
    mock_check_call.side_effect = [
        FileNotFoundError(),  # podman missing
        None,  # docker compose available
    ]
    command = docker_cmd._get_command()
    assert command == ["docker", "compose"]
    assert mock_check_call.call_count == 2
    mock_check_call.assert_has_calls(
        [
            call(["podman", "compose", "version"]),
            call(["docker", "compose", "version"]),
        ]
    )


@patch("hkg_cli.docker.commands.check_call")
def test_get_command_podman_and_docker_missing_file_not_found(mock_check_call):
    """Test that _get_command falls back to docker-compose if podman and docker binaries are missing (FileNotFoundError)."""
    mock_check_call.side_effect = [
        FileNotFoundError(),  # podman missing
        FileNotFoundError(),  # docker missing
        None,  # docker-compose available
    ]
    command = docker_cmd._get_command()
    assert command == ["docker-compose"]
    assert mock_check_call.call_count == 3
    mock_check_call.assert_has_calls(
        [
            call(["podman", "compose", "version"]),
            call(["docker", "compose", "version"]),
            call(["docker-compose", "version"]),
        ]
    )


@patch("hkg_cli.docker.commands.check_call")
def test_get_command_all_missing_file_not_found(mock_check_call):
    """Test that _get_command raises CalledProcessError if all binaries are missing (FileNotFoundError)."""
    mock_check_call.side_effect = [
        FileNotFoundError(),
        FileNotFoundError(),
        FileNotFoundError(),
    ]
    with pytest.raises(CalledProcessError):
        docker_cmd._get_command()
    assert mock_check_call.call_count == 3


@patch("hkg_cli.docker.commands.check_call")
def test_get_command_mixed_errors(mock_check_call):
    """Test that _get_command handles a mix of CalledProcessError and FileNotFoundError."""
    mock_check_call.side_effect = [
        CalledProcessError(1, "podman compose version"),  # podman fails
        FileNotFoundError(),  # docker missing
        None,  # docker-compose available
    ]
    command = docker_cmd._get_command()
    assert command == ["docker-compose"]
    assert mock_check_call.call_count == 3
    mock_check_call.assert_has_calls(
        [
            call(["podman", "compose", "version"]),
            call(["docker", "compose", "version"]),
            call(["docker-compose", "version"]),
        ]
    )


@patch("hkg_cli.docker.commands.Path.exists", return_value=True)
@patch("hkg_cli.docker.commands._get_command")
@patch("hkg_cli.docker.commands.check_call")
def test_run_success(mock_check_call, mock_get_command, mock_exists):
    """Test that _run executes the command successfully."""
    mock_get_command.return_value = ["docker", "compose"]
    docker_cmd._run(["up", "-d"])
    mock_check_call.assert_called_once_with(["docker", "compose", "up", "-d"])


@patch("hkg_cli.docker.commands.Path.exists", return_value=True)
@patch("hkg_cli.docker.commands._get_command")
@patch("hkg_cli.docker.commands.check_call")
def test_run_failure(mock_check_call, mock_get_command, mock_exists):
    """Test that _run raises typer.Exit on command failure."""
    mock_get_command.return_value = ["docker", "compose"]
    mock_check_call.side_effect = CalledProcessError(1, "docker compose up -d")
    with pytest.raises(typer.Exit):
        docker_cmd._run(["up", "-d"])
    mock_check_call.assert_called_once_with(["docker", "compose", "up", "-d"])


@patch("hkg_cli.docker.commands.Path.exists", return_value=False)
def test_run_missing_compose_file(mock_exists):
    """Test that _run raises typer.Exit if docker-compose.yml is missing."""
    with pytest.raises(typer.Exit):
        docker_cmd._run(["up", "-d"])
    mock_exists.assert_called_once()


@patch("hkg_cli.docker.commands.Path.exists", return_value=True)
@patch("hkg_cli.docker.commands._get_command", return_value=["docker", "compose"])
@patch("hkg_cli.docker.commands.check_call")
def test_run_with_compose_file(mock_check_call, mock_get_command, mock_exists):
    """Test that _run proceeds if docker-compose.yml exists."""
    docker_cmd._run(["up", "-d"])
    mock_exists.assert_called_once()
    mock_get_command.assert_called_once()
    mock_check_call.assert_called_once_with(["docker", "compose", "up", "-d"])


# Public command tests


@patch("hkg_cli.docker.commands._run")
def test_start(mock_run):
    """Test that start calls _run with the correct arguments."""
    docker_cmd.start()
    mock_run.assert_called_once_with(["up", "-d"])


@patch("hkg_cli.docker.commands._run")
def test_stop(mock_run):
    """Test that stop calls _run with the correct arguments."""
    docker_cmd.stop()
    mock_run.assert_called_once_with(["down"])


@patch("hkg_cli.docker.commands._run")
def test_nuke(mock_run):
    """Test that nuke calls _run with the correct arguments."""
    docker_cmd.nuke()
    mock_run.assert_called_once_with(
        ["down", "--rmi", "all", "--volumes", "--remove-orphans"]
    )


@patch("hkg_cli.docker.commands.Path.exists", return_value=False)
def test_start_missing_compose_file(mock_exists):
    """Test that start raises typer.Exit if docker-compose.yml is missing."""
    with pytest.raises(typer.Exit):
        docker_cmd.start()
    mock_exists.assert_called_once()


@patch("hkg_cli.docker.commands.Path.exists", return_value=False)
def test_stop_missing_compose_file(mock_exists):
    """Test that stop raises typer.Exit if docker-compose.yml is missing."""
    with pytest.raises(typer.Exit):
        docker_cmd.stop()
    mock_exists.assert_called_once()


@patch("hkg_cli.docker.commands.Path.exists", return_value=False)
def test_nuke_missing_compose_file(mock_exists):
    """Test that nuke raises typer.Exit if docker-compose.yml is missing."""
    with pytest.raises(typer.Exit):
        docker_cmd.nuke()
    mock_exists.assert_called_once()
