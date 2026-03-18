#!/usr/bin/env bash

set -euo pipefail

REPO_URL="${INIT_REPO_URL:-https://github.com/AndresDevvv/initx.git}"
REPO_BRANCH="${INIT_REPO_BRANCH:-main}"
INSTALL_DIR="${INIT_INSTALL_DIR:-$HOME/Init}"
VENV_DIR="$INSTALL_DIR/venv"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
LAUNCHER_PATH="$BIN_DIR/initx"
AUTO_UPDATE="${INIT_AUTO_UPDATE:-0}"

log() {
  printf '[init-installer] %s\n' "$1"
}

ensure_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    exit 1
  fi
}

resolve_python() {
  if command -v python3 >/dev/null 2>&1; then
    printf '%s' "python3"
    return
  fi

  if command -v python >/dev/null 2>&1; then
    printf '%s' "python"
    return
  fi

  printf 'Missing required command: python3 or python\n' >&2
  exit 1
}

ensure_line_in_file() {
  local file="$1"
  local line="$2"

  touch "$file"
  if ! grep -Fqx "$line" "$file"; then
    printf '\n%s\n' "$line" >>"$file"
  fi
}

choose_shell_rc() {
  if [ -n "${ZSH_VERSION:-}" ] || [ "${SHELL:-}" = "$(command -v zsh 2>/dev/null || true)" ]; then
    printf '%s' "$HOME/.zshrc"
    return
  fi

  printf '%s' "$HOME/.bashrc"
}

install_repo() {
  if [ -d "$INSTALL_DIR/.git" ]; then
    log "Updating existing checkout in $INSTALL_DIR"
    git -C "$INSTALL_DIR" fetch origin "$REPO_BRANCH"
    git -C "$INSTALL_DIR" checkout "$REPO_BRANCH"
    git -C "$INSTALL_DIR" pull --ff-only origin "$REPO_BRANCH"
    return
  fi

  if [ -e "$INSTALL_DIR" ] && [ ! -d "$INSTALL_DIR/.git" ]; then
    printf 'Install directory exists but is not a git repository: %s\n' "$INSTALL_DIR" >&2
    exit 1
  fi

  log "Cloning $REPO_URL into $INSTALL_DIR"
  git clone --branch "$REPO_BRANCH" "$REPO_URL" "$INSTALL_DIR"
}

setup_venv() {
  local python_cmd
  python_cmd="$(resolve_python)"

  log "Creating virtual environment in $VENV_DIR"
  "$python_cmd" -m venv "$VENV_DIR"

  log "Installing package dependencies"
  "$VENV_DIR/bin/pip" install --upgrade pip setuptools
  if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
  fi
  "$VENV_DIR/bin/pip" install -e "$INSTALL_DIR"
}

write_launcher() {
  mkdir -p "$BIN_DIR"

  cat >"$LAUNCHER_PATH" <<EOF
#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$INSTALL_DIR"
BRANCH="$REPO_BRANCH"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"
AUTO_UPDATE="$AUTO_UPDATE"

if [ "\$AUTO_UPDATE" = "1" ] && [ -d "\$REPO_DIR/.git" ] && command -v git >/dev/null 2>&1; then
  git -C "\$REPO_DIR" fetch --quiet origin "\$BRANCH" || true
  local_head="\$(git -C "\$REPO_DIR" rev-parse HEAD 2>/dev/null || true)"
  remote_head="\$(git -C "\$REPO_DIR" rev-parse "origin/\$BRANCH" 2>/dev/null || true)"

  if [ -n "\$local_head" ] && [ -n "\$remote_head" ] && [ "\$local_head" != "\$remote_head" ]; then
    printf '[init] Updating local checkout from origin/%s\n' "\$BRANCH" >&2
    git -C "\$REPO_DIR" pull --ff-only origin "\$BRANCH"
    "\$VENV_PIP" install -e "\$REPO_DIR" >/dev/null
  fi
fi

exec "\$VENV_PYTHON" -m init_cli.cli "\$@"
EOF

  chmod +x "$LAUNCHER_PATH"
}

ensure_path() {
  local shell_rc
  shell_rc="$(choose_shell_rc)"
  local export_line='export PATH="$HOME/.local/bin:$PATH"'

  if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    log "Adding $BIN_DIR to PATH in $shell_rc"
    ensure_line_in_file "$shell_rc" "$export_line"
    log "Open a new shell or run: source $shell_rc"
  fi
}

main() {
  ensure_command git
  resolve_python >/dev/null

  install_repo
  setup_venv
  write_launcher
  ensure_path

  log "Installation complete"
  if [ "$AUTO_UPDATE" = "1" ]; then
    log "Optional auto-update is enabled"
  else
    log "Optional auto-update is disabled by default"
    log "Re-run with INIT_AUTO_UPDATE=1 to enable launcher updates before execution"
  fi
  log "Run: initx python myapp"
}

main "$@"
