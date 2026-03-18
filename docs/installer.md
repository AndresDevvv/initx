# Installer

Status: alpha.

The recommended hosted installer is:

```bash
curl -fsSL https://raw.githubusercontent.com/AndresDevvv/initx/main/scripts/install.sh | bash
```

What it does:

- clones or updates the repo into `~/Init`
- creates a virtual environment in `~/Init/venv`
- installs the package into that virtual environment
- writes a global launcher to `~/.local/bin/initx`
- adds `~/.local/bin` to your shell `PATH` if needed

Prerequisites:

- `git`
- `python3` or `python`
- `bash`

Manual local install:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Hosted script path:

```text
https://raw.githubusercontent.com/AndresDevvv/initx/main/scripts/install.sh
```

Update behavior:

- the installed `initx` launcher runs `git fetch` before execution
- if the local checkout is behind `origin/main`, it fast-forwards
- after pulling, it refreshes the package inside `~/Init/venv`

Supported templates after install:

- `initx python <name>`
- `initx python .`
- `initx node <name>`
- `initx node .`

Template-specific prerequisites:

- Python templates require `python` or `python3`
- Node templates require both `node` and `npm`

Optional auto-update:

- auto-update is disabled by default
- enable it during install with `INIT_AUTO_UPDATE=1`
- example:

```bash
curl -fsSL https://raw.githubusercontent.com/AndresDevvv/initx/main/scripts/install.sh | INIT_AUTO_UPDATE=1 bash
```
