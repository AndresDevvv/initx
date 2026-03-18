# Development

Status: alpha.

## Local Test Run

```bash
python3 -m unittest discover -s tests
```

## Package Entry Point

The console command is defined in `pyproject.toml`:

```toml
[project.scripts]
initx = "init_cli.cli:main"
```

## Current Scope

Implemented templates:

- `initx python <name>`
- `initx python .`
- `initx node <name>`
- `initx node .`

Planned ideas live in the roadmap and are not implemented unless they are listed above.

## Test Coverage

Current tests cover:

- Python project generation
- Node.js project generation
- current-directory initialization with `.`
- refusal to overwrite existing or non-empty directories
