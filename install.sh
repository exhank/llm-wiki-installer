#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'HELP'
Usage: bash install.sh [options] [path/to/knowledge-vault]

Generate an llm-wiki knowledge vault in the target repository root.
When no target path is provided, the current working directory is used.

Options:
  --force  Overwrite generated files in the target vault.
  --no-interactive
           Use the default selection for dependency tools and upstream skills.
  --yes
           Alias for --no-interactive.
  --tools LIST
           Select dependency tools: qmd,rg,fzf, all, or none.
  --skills LIST
           Select upstream Skill sources: Ar9av,kepano, all, or none.
  --no-install-tools
           Do not install missing selectable tools such as qmd with npm.
  --offline
           Do not perform network bootstrap operations.
  --dry-run
           Print the install plan without writing files or running network steps.
  --json
           Print dry-run or final install summaries as JSON.
  -h, --help
           Show this help.

The script refuses to generate into a checked-out llm-wiki generator
repository. When streamed through stdin, the current working directory is used
unless it looks like the generator repository.
HELP
}

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

if [ "${LLM_WIKI_INSTALL_LIB_ONLY:-0}" = "1" ]; then
  return 0 2>/dev/null || exit 0
fi

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

command -v python3 >/dev/null || fail "Python 3.13+ is required to run the llm-wiki installer."
PYTHON_VERSION="$(python3 -c 'import platform; print(platform.python_version())')" ||
  fail "Python 3.13+ is required to run the llm-wiki installer."
python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 13))' ||
  fail "Python 3.13+ is required to run the llm-wiki installer. Found: $PYTHON_VERSION."

SCRIPT_SOURCE="${BASH_SOURCE[0]:-}"
SCRIPT_DIR=""
if [ -n "$SCRIPT_SOURCE" ] && [ -f "$SCRIPT_SOURCE" ]; then
  SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd -P)"
fi

if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/src/llm_wiki_installer/__main__.py" ]; then
  export LLM_WIKI_INSTALLER_ROOT="$SCRIPT_DIR"
  export PYTHONPATH="$SCRIPT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
  exec python3 -m llm_wiki_installer "$@"
fi

command -v git >/dev/null || fail "git is required to bootstrap the streamed installer."

REPO_URL="${LLM_WIKI_INSTALLER_REPO_URL:-https://github.com/exhank/llm-wiki-installer}"
REPO_REF="${LLM_WIKI_INSTALLER_REF:-v0.1.0}"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/llm-wiki-installer.XXXXXX")"
CLONE_DIR="$TMP_DIR/llm-wiki-installer"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

git init -q "$CLONE_DIR" ||
  fail "failed to initialize temporary llm-wiki-installer checkout."
git -C "$CLONE_DIR" remote add origin "$REPO_URL" ||
  fail "failed to configure llm-wiki-installer remote: $REPO_URL."
git -C "$CLONE_DIR" fetch -q --depth 1 origin "$REPO_REF" ||
  fail "failed to fetch llm-wiki-installer from $REPO_URL at ref $REPO_REF."
git -C "$CLONE_DIR" -c advice.detachedHead=false checkout -q --detach 'FETCH_HEAD^{}' ||
  fail "failed to check out llm-wiki-installer ref $REPO_REF."

[ -f "$CLONE_DIR/install.sh" ] ||
  fail "cloned llm-wiki-installer is missing install.sh."

bash "$CLONE_DIR/install.sh" "$@"
