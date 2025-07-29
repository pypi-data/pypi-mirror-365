"""Command-line interface for running Python scripts or modules with debugging tools."""

import os
import runpy
import sys
from bdb import BdbQuit
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rich_print

from .installers import install_all

cli = typer.Typer(
    name="debug_dojo",
    help="Run a Python script or module with debugging tools installed.",
    no_args_is_help=True,
)


def execute_with_debug(target_name: str, args_for_target: list[str]) -> None:
    """Execute a target script or module with installation of debugging tools."""
    sys.argv = [target_name, *args_for_target]

    install_all()

    if (
        Path(target_name).exists()
        or target_name.endswith(".py")
        or os.sep in target_name
    ):
        if not Path(target_name).exists():
            sys.exit(1)
        runner = runpy.run_path
    else:
        runner = runpy.run_module

    _ = runner(target_name, run_name="__main__")


@cli.command(
    name="",
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    },
)
def main(
    ctx: typer.Context,
    target_name: Annotated[
        str,
        typer.Argument(
            ...,
            help="The target script or module to debug. Provide the path or module name.",
        ),
    ],
) -> None:
    """Run the command-line interface."""
    args_for_target = ctx.args
    try:
        execute_with_debug(target_name, args_for_target)
    except BdbQuit:
        rich_print("[red]Debugging session terminated by user.[/red]")
        sys.exit(0)


@cli.command("config")
def config() -> None:
    """Display the configuration for the debug dojo."""
    rich_print("[green]Debug Dojo Configuration:[/green]")
    rich_print("This tool installs debugging tools and runs Python scripts or modules.")
    rich_print(
        "You can specify a target script or module to debug, along with any arguments."
    )
    rich_print("Example usage: `debug_dojo target_to_debug.py --some-input-to-target`")
