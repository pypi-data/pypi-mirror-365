"""Utility functions for cli subcommands."""

import logging
import traceback

import typer
import wrapt
from rich.markup import escape

logger = logging.getLogger("hgk_cli")


@wrapt.decorator
def wrap_exceptions(wrapped, instance, args, kwargs):
    """Format and log exceptions for cli commands."""
    try:
        return wrapped(*args, **kwargs)

    except Exception as e:
        # Escape the error message to prevent Rich from misinterpreting it
        escaped_error_message = escape(str(e))
        escaped_traceback = escape(traceback.format_exc())

        logger.error("[bold red]Error: %s[/bold red]", escaped_error_message)
        logger.debug("[red]%s[/red]", escaped_traceback)
        raise typer.Exit(code=1) from e
