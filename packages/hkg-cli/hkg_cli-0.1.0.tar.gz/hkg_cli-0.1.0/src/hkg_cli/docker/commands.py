"""Common commands for Docker Compose."""

import logging
from pathlib import Path

import typer
from subprocess import check_call, CalledProcessError

logger = logging.getLogger("hkg_cli")
logger.setLevel(logging.INFO)


def _get_command() -> list[str]:
    """Determine the container compose command to use.

    This function attempts to run commands in the following order:
    1. `podman compose version`
    2. `docker compose version`
    3. `docker-compose version`

    If none of these commands are available, it logs a critical error and exits the application.

    Returns:
        list[str]: The container compose command to use in a form of list so it can be used with subprocess.

    Raises:
        SystemExit: If no container compose command is available.
    """
    # Try podman compose first
    try:
        logger.debug("Checking if 'podman compose' is available...")
        check_call(["podman", "compose", "version"])
        logger.debug("'podman compose' command found.")
        return ["podman", "compose"]
    except (CalledProcessError, FileNotFoundError):
        logger.debug("'podman compose' not found, attempting 'docker compose'...")

    # Try docker compose next
    try:
        check_call(["docker", "compose", "version"])
        logger.debug("'docker compose' command found.")
        return ["docker", "compose"]
    except (CalledProcessError, FileNotFoundError):
        logger.debug("'docker compose' not found, attempting 'docker-compose'...")

    # Finally try docker-compose
    try:
        check_call(["docker-compose", "version"])
        logger.debug("'docker-compose' command found.")
        return ["docker-compose"]
    except (CalledProcessError, FileNotFoundError) as e:
        if isinstance(e, CalledProcessError):
            returncode = e.returncode
            cmd = e.cmd
        else:  # FileNotFoundError
            returncode = 127  # Standard for command not found
            cmd = getattr(e, "filename", "unknown")
        raise CalledProcessError(
            returncode,
            cmd,
            "No container compose command is available. Please ensure:\n"
            "1. Either Podman or Docker is installed and running\n"
            "2. The compose plugin is installed\n"
            "3. The 'podman' or 'docker' command is in your system PATH\n"
            "For installation instructions, visit:\n"
            "- Podman: https://podman.io/getting-started/installation\n"
            "- Docker: https://docs.docker.com/compose/install/",
        ) from e


def _check_compose_file() -> None:
    """Check if a compose file exists in the current directory."""
    if not Path("docker-compose.yml").exists():
        logger.error("No docker-compose.yml file found in the current directory.")
        raise typer.Exit(1)


def _run(additional_commands: list[str]) -> None:
    """Run a given docker compose command with the previously determined command."""
    _check_compose_file()
    commands = _get_command()
    full_cmd = commands + additional_commands
    logger.debug("Running command: %s", " ".join(full_cmd))
    try:
        check_call(full_cmd)
    except CalledProcessError as e:
        logger.error(
            "Command %s failed with exit code %d", " ".join(full_cmd), e.returncode
        )
        raise typer.Exit(e.returncode) from e


def start() -> None:
    """Start the Docker Compose services."""
    logger.info("Starting Docker Compose services...")
    _run(["up", "-d"])
    logger.info("Docker Compose services have started successfully.")


def stop() -> None:
    """Stop the Docker Compose services."""
    logger.info("Stopping Docker Compose services...")
    _run(["down"])
    logger.info("Docker Compose services have been stopped.")


def nuke() -> None:
    """Completely remove all Docker Compose services, including images, volumes and networks."""
    logger.info(
        "Removing all Docker Compose services, images, volumes, and networks..."
    )
    _run(["down", "--rmi", "all", "--volumes", "--remove-orphans"])
    logger.info(
        "All Docker Compose services, images, volumes, and networks have been removed."
    )
