# CLI Parameters

Status: alpha.

## Basic Usage

```bash
initx python myapp
initx node myapp
```

This creates:

- `myapp/`
- `myapp/venv/`
- `myapp/main.py`
- `myapp/requirements.txt`
- `myapp/.gitignore`
- `myapp/README.md`

For Node.js this creates:

- `myapp/`
- `myapp/package.json`
- `myapp/index.js`
- `myapp/.gitignore`
- `myapp/README.md`

## Command Shape

```bash
initx python <name> [--path <directory>] [--no-venv]
initx node <name> [--path <directory>]
```

## Parameters

- `python`: selects the Python project template
- `node`: selects the Node.js project template
- `<name>`: the directory name for the generated project
- `--path`: sets the parent directory where the project will be created
- `--no-venv`: skips `python -m venv venv`

## Prerequisites

- `initx python ...` requires `python` or `python3`
- `initx node ...` requires both `node` and `npm`

For Python projects, Init prefers `python3` when both `python3` and `python` exist, and falls back to `python` only when `python3` is unavailable.

## Current Directory Mode

Using `.` instead of a project name tells Init to use the current target directory directly.

Examples:

```bash
initx python .
initx node .
initx python . --path ~/empty-folder
```

Rules:

- the target directory must already exist or be resolvable by `--path`
- the target directory must be empty
- Init will refuse to write into a non-empty directory

## Examples

```bash
initx python myapp
initx python myapp --path ~/code
initx python myapp --no-venv
initx python .
initx node myapp
initx node myapp --path ~/code
initx node .
```

`initx <platform> .` initializes the current directory, but only if it is empty.
