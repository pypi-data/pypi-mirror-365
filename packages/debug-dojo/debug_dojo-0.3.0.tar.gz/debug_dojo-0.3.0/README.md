<p align="center">
  <img src="https://github.com/bwrob/debug-dojo/blob/main/logo/logo_white.png?raw=true" alt="debug dojo" style="width:50%; max-width:400px;"/>
</p>

<p align="center">
    <em>debug dojo, a place for zen debugging</em>
</p>

[![PyPi Version](https://img.shields.io/pypi/v/debug-dojo.svg?style=flat-square)](https://pypi.org/project/debug-dojo)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/debug-dojo.svg?style=flat-square)](https://pypi.org/pypi/debug-dojo/)

**debug-dojo** is a Python package providing utilities for enhanced debugging and inspection in the terminal. It leverages [`rich`](https://github.com/Textualize/rich) for beautiful output and offers helpers for side-by-side object comparison, improved tracebacks from `rich`, and easy integration with PuDB. All tools can be installed at once or individually, allowing for flexible debugging setups.

## Features

- **Convenient CLI** Quickly run your code with debugging tools enabled.
- **Simple API:** Install all tools or only what you need.
- **PuDB integration:** Quickly enable the PuDB TUI debugger.
- **Rich tracebacks:** Get readable, colorized tracebacks for easier debugging.
- **Side-by-side object inspection:** Visually compare Python objects, their attributes, and methods in the terminal.

## Usage

### CLI

Run your Python script with debugging tools enabled using the `debug-dojo` command:

```console
dojo my_script.py
```

### Install all debugging tools

In the `PuDB` style, you can install all debugging tools and enter the debugging mode with a single command:

```python
import debug_dojo.all; b()

p(object_1)  # Pretty print an object with Rich
i(object_1)  # Inspect an object
c(object_1, object_2)  # Compare two objects side-by-side
```

Where:

- `b()` is a builtin-injected function that sets a breakpoint using PuDB's `set_trace()`.
- `p(object_1)` is pretty printing of an object using Rich.
- `i(object_1)` to inspect an object using Rich.
- `c(object_1, object_2)` to compare two objects side-by-side.

### Use individual tools

```python
from debug_dojo import install_inspect, use_pudb, use_rich_traceback

install_inspect()         # Enable object inspection helpers
use_pudb()                # Set up PuDB as the debugger
use_rich_traceback()      # Enable Rich tracebacks
```

### Compare objects side-by-side

```python
from debug_dojo.compareres import inspect_objects_side_by_side

a = {"foo": 1, "bar": 2}
b = [1, 2, 3]
inspect_objects_side_by_side(a, b)
```


## Installation

The package is available on PyPI and can be installed using standard Python package management tools.

```console
pip install debug-dojo
```

You can also use `poetry` or `uv` to add it to your project:

```console
poetry add debug-dojo
```

```console
uv add debug-dojo
```

Note that dojo most likely will not work when installed via `pipx` or `uvx`, as it relies on the current Python environment dependencies.

## Development

### Lint and type check

```console
ruff check src/debug_dojo --fix
basedpyright src/debug_dojo
```
