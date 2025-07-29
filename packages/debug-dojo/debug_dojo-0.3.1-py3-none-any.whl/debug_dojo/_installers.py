"""Debugging tools for Python.

This module provides functions to set up debugging tools like PuDB and Rich Traceback.
It checks for the availability of these tools and configures them accordingly.
"""

from __future__ import annotations

import builtins
import json
import os
import sys

from rich import print as rich_print

from ._compareres import inspect_objects_side_by_side
from ._config import DebugDojoConfig, DebuggerType, Features

BREAKPOINT_ENV_VAR = "PYTHONBREAKPOINT"


def _use_pdb() -> None:
    """Set PDB as the default debugger."""
    import pdb

    os.environ[BREAKPOINT_ENV_VAR] = "pdb.set_trace"
    sys.breakpointhook = pdb.set_trace


def _use_pudb() -> None:
    """Check if PuDB is available and set it as the default debugger."""
    import pudb  # pyright: ignore[reportMissingTypeStubs]

    os.environ[BREAKPOINT_ENV_VAR] = "pudb.set_trace"
    sys.breakpointhook = pudb.set_trace


def _use_ipdb() -> None:
    """Set IPDB as the default debugger."""
    import ipdb  # pyright: ignore[reportMissingTypeStubs]

    os.environ[BREAKPOINT_ENV_VAR] = "ipdb.set_trace"
    os.environ["IPDB_CONTEXT_SIZE"] = "20"
    sys.breakpointhook = ipdb.set_trace  # pyright: ignore[reportUnknownMemberType]


def _use_debugpy() -> None:
    """Check if IPDB is available and set it as the default debugger."""
    import debugpy  # pyright: ignore[reportMissingTypeStubs]

    os.environ[BREAKPOINT_ENV_VAR] = "debugpy.breakpoint"
    sys.breakpointhook = debugpy.breakpoint

    port = 6969
    _ = debugpy.listen(("localhost", port))

    config = {
        "name": "debug-dojo",
        "type": "debugpy",
        "request": "attach",
        "connect": {"port": port},
    }
    rich_print(
        f"[blue]Debugging via Debugpy. Connect your VSC debugger to port {port}.[/blue]"
    )
    rich_print("[blue]Configuration:[/blue]")
    rich_print(json.dumps(config, indent=4))

    debugpy.wait_for_client()


def _rich_traceback() -> None:
    """Check if Rich Traceback is available and set it as the default."""
    from rich import traceback

    _ = traceback.install(show_locals=True)


def _inspect() -> None:
    """Print the object using a custom inspect function."""
    from rich import inspect

    def inspect_with_defaults(obj: object, **kwargs: object) -> None:
        """Inspect an object using Rich's inspect function."""
        if not kwargs:
            kwargs = {"methods": True, "private": True}
        return inspect(obj, **kwargs)  # pyright: ignore[reportArgumentType]

    builtins.i = inspect_with_defaults  # pyright: ignore[reportAttributeAccessIssue]


def _compare() -> None:
    """Print the object using a custom inspect function."""
    builtins.c = inspect_objects_side_by_side  # pyright: ignore[reportAttributeAccessIssue]


def _breakpoint() -> None:
    """Install the breakpoint function."""
    builtins.b = breakpoint  # pyright: ignore[reportAttributeAccessIssue]


def _rich_print() -> None:
    """Install the print from rich."""
    from rich import print as rich_print

    builtins.p = rich_print  # pyright: ignore[reportAttributeAccessIssue]


def _install_features(features: Features) -> None:
    """Install the specified debugging features."""
    if features.rich_inspect:
        _inspect()
    if features.rich_print:
        _rich_print()
    if features.rich_traceback:
        _rich_traceback()
    if features.comparer:
        _compare()
    if features.breakpoint:
        _breakpoint()


def _set_debugger(debugger: DebuggerType) -> None:  # noqa: RET503
    """Set the debugger based on the configuration."""
    if debugger == DebuggerType.PDB:
        return _use_pdb()
    if debugger == DebuggerType.PUDB:
        return _use_pudb()
    if debugger == DebuggerType.IPDB:
        return _use_ipdb()
    if debugger == DebuggerType.DEBUGPY:
        return _use_debugpy()


def install_by_config(config: DebugDojoConfig) -> None:
    """Install debugging tools."""
    _set_debugger(config.debugger)
    _install_features(config.features)
