from rich.logging import RichHandler
import logging
import typer
from typing import Optional

from hkg_cli import __version__
from hkg_cli.subcommands import setup
from hkg_cli.docker.commands import start, stop, nuke
from hkg_cli.subcommands.utils import wrap_exceptions

# git main app
app = typer.Typer()

logger = logging.getLogger("hkg_cli")


@app.callback()
def version(value: bool):
    """Show the version of hkg-cli."""
    if value:
        typer.echo(f"hkg-cli version: v{__version__}")
        raise typer.Exit()


@app.callback()
def common(
    ctx: typer.Context,
    version: bool = typer.Option(
        None, "--version", "-v", help=version.__doc__, callback=version
    ),
    debug: bool = typer.Option(
        None,
        "--debug",
        "-d",
        help="Enable debug logging.",
    ),
):
    """Common functionality."""
    # Set RichHandler with user-defined configurations
    rich_handler = RichHandler(
        show_time=False,
        rich_tracebacks=True,
        show_level=debug,  # Configured per user's request
        show_path=debug,  # Configured per user's request
        tracebacks_show_locals=debug,
        markup=True,
    )

    # Set logging level and handler
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level, handlers=[rich_handler])


@app.command()
@wrap_exceptions
def run():
    """Start project by running docker compose file."""
    start()


@app.command("stop")
@wrap_exceptions
def stop_project(
    clear: Optional[bool] = typer.Option(
        False, "--clear", "-c", help="Clear all volumes and networks in docker.ß"
    ),
):
    """Stop docker containers."""
    if clear:
        nuke()
    else:
        stop()


# Add subcommands
app.add_typer(setup.app, name="setup")
