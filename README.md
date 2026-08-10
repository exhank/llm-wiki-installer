# llm-wiki-installer

[![CI](https://github.com/exhank/llm-wiki-installer/actions/workflows/ci.yml/badge.svg)](https://github.com/exhank/llm-wiki-installer/actions/workflows/ci.yml)
[![Release](https://github.com/exhank/llm-wiki-installer/actions/workflows/release.yml/badge.svg)](https://github.com/exhank/llm-wiki-installer/actions/workflows/release.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![PyPI](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpypi.org%2Fpypi%2Fllm-wiki-installer%2F0.2.0%2Fjson&query=%24.info.version&label=PyPI&prefix=v)](https://pypi.org/project/llm-wiki-installer/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

`llm-wiki-installer` generates a Git-auditable, agent-friendly Obsidian
Markdown knowledge vault from one command.

It turns an empty folder into a durable Markdown knowledge system with clear
evidence boundaries, agent policy, helper scripts, and selected upstream
Skills. The generated vault is designed for a simple loop: collect
approved sources, compile them into `wiki/`, retrieve from the wiki first, and
review every change through Git.

It is not itself an initialized vault. This repository builds the generator; the
generated vault lives in a separate target repository.

## Quick Start

From the empty directory you want to turn into an `llm-wiki` vault, run:

```bash
curl -fsSL https://raw.githubusercontent.com/exhank/llm-wiki-installer/main/install.sh | /bin/bash
```

The default flow is interactive. It shows selectors for dependency tools and
upstream Skills, with all options selected by default. When no target path is
provided, the installer writes the vault into the current directory.

If you use `uv`, the package is also published on PyPI as
[`llm-wiki-installer`](https://pypi.org/project/llm-wiki-installer/):

```bash
uvx llm-wiki-installer
```

For pinned automation, include the package version you want to reproduce:

```bash
uvx llm-wiki-installer==<version> --no-interactive /path/to/knowledge-vault
```

## Why This Exists

Most AI note workflows stop at chat answers or ad hoc generated notes. This
project sets up a stricter vault contract:

- `raw/` keeps user-approved source evidence.
- `wiki/` keeps compiled long-term Markdown knowledge.
- `wiki/index.md` and `wiki/maps/` provide stable retrieval entry points.
- `wiki/tags.md` keeps the flat kebab-case tag registry.
- `wiki/log.jsonl`, Git diff, and generated scripts make changes auditable.
- Upstream Skills are copied as third-party artifacts from pinned sources.

## Features

- One-command local or streamed installer.
- Python installer package with no runtime third-party dependencies.
- Interactive selectors for dependency tools and upstream Skill sources.
- Generated AGENTS policy with a CLAUDE.md bridge for Claude Code, README,
  scripts, Codex config and hooks, index, log, and stable Obsidian settings.
- Generated stable Obsidian settings with bundled Things theme and obsidian-git
  plugin assets, configured for manual commits so Git review stays meaningful.
- Skills exposed to Codex and Gemini CLI via `.agents/skills/` and to Claude
  Code via a `.claude/skills/` symlink.
- Pinned upstream Skill commits for reproducible generated vaults.
- Safety checks that refuse to generate into this generator repository, a
  non-empty directory, or a nested Git repository without `--force`.
- Unit, shell integration, type, lint, coverage, and package checks.

## What It Generates

`llm-wiki-installer` turns an empty target repository into a working vault
contract:

```text
knowledge-vault/
+-- raw/                 # user-approved source evidence
+-- attachments/         # Obsidian default attachment folder
+-- wiki/                # durable compiled knowledge
|   +-- index.md         # retrieval entry point
|   +-- tags.md          # flat kebab-case tag registry
|   +-- log.jsonl        # JSONL change log
|   +-- maps/            # topic maps for navigation
+-- outputs/             # generated reports and exports
+-- inbox/               # incoming material awaiting review
+-- archives/             # retired material
+-- schema/              # schema and policy documents
|   +-- workflow.md      # vault maintenance workflow
|   +-- log.md           # wiki/log.jsonl event schemas
|   +-- wiki-page.md     # wiki/*.md page template
|   +-- map.md           # wiki/maps/*.md map template
+-- AGENTS.md            # runtime policy for agents (Codex, Gemini, OpenCode)
+-- CLAUDE.md            # imports AGENTS.md for Claude Code
+-- .agents/
|   +-- skills/          # flattened pinned third-party Skill artifacts
+-- .claude/
|   +-- skills/          # symlink to .agents/skills for Claude Code discovery
+-- .codex/
|   +-- config.toml      # Codex project config
|   +-- hooks.json       # Codex Stop hook running the structural vault checks
+-- .scripts/            # verification helpers
+-- .obsidian/           # stable Obsidian settings, theme, and pinned plugin assets
```

Empty contract directories contain a `.gitkeep` placeholder so the layout
survives commit, push, and clone.

The operating model is intentionally file-first:

```text
approved sources -> raw/ -> wiki pages -> wiki/index.md + wiki/maps/
                         \-> wiki/log.jsonl -> Git diff review

agents read AGENTS.md -> retrieve with rg/fzf -> verify against raw/
```

## Generate A Vault

Install with the published PyPI package:

```bash
uvx llm-wiki-installer /path/to/knowledge-vault
```

Pin the package version for repeatable automation:

```bash
uvx llm-wiki-installer==<version> /path/to/knowledge-vault
```

Install into the current directory with the streamed shell bootstrap:

```bash
curl -fsSL https://raw.githubusercontent.com/exhank/llm-wiki-installer/main/install.sh | /bin/bash
```

Pass installer options through the same pattern:

```bash
curl -fsSL https://raw.githubusercontent.com/exhank/llm-wiki-installer/main/install.sh | /bin/bash -s -- --force
```

The streamed launcher resolves
[GitHub Releases latest](https://github.com/exhank/llm-wiki-installer/releases/latest)
internally when `LLM_WIKI_INSTALLER_REF` is not set. Set
`LLM_WIKI_INSTALLER_REF` only when intentionally testing or pinning another ref:

```bash
curl -fsSL https://raw.githubusercontent.com/exhank/llm-wiki-installer/main/install.sh | LLM_WIKI_INSTALLER_REF=<tag-or-commit> /bin/bash
```

The `uvx` entry point uses the PyPI package and runs the same installer CLI as
`llm-wiki-install`. It is the preferred path for automation because JSON output
comes directly from the Python CLI. The streamed one-line command remains useful
on machines that do not already use `uv`.

Install from a local checkout into the current directory:

```bash
bash /path/to/llm-wiki-installer/install.sh
```

Install into a specific directory:

```bash
bash install.sh /path/to/knowledge-vault
```

Use `--force` with a specific directory only when you intentionally want to
overwrite generated files in the target vault:

```bash
bash install.sh --force /path/to/knowledge-vault
```

Preview an install plan:

```bash
bash install.sh --dry-run /path/to/knowledge-vault
bash install.sh --dry-run --json /path/to/knowledge-vault
```

Select tools and upstream Skills explicitly:

```bash
bash install.sh --tools rg --skills kepano /path/to/knowledge-vault
bash install.sh --tools none --skills none /path/to/knowledge-vault
```

Run without network bootstrap operations:

```bash
bash install.sh --offline --tools rg --skills none /path/to/knowledge-vault
```

The installer never installs missing tools itself. When a selected tool is not
found it fails with an actionable message; install the tool or re-run with a
`--tools` selection that excludes it.

When run from an interactive terminal, the installer shows two onboarding
selectors before generating files:

- dependency tools: `rg` and `fzf` (both selected by default)
- upstream Skill sources: `kepano/obsidian-skills` (selected by default) and
  `Ar9av/obsidian-wiki` (opt-in: its skills target Ar9av's own vault layout
  and are copied as reference material)

Use Up/Down to move, Space to toggle an option, and Enter to continue.
Non-interactive runs, including scripted installs with redirected output, use
the same defaults. To force that behavior from a terminal, pass:

```bash
bash install.sh --no-interactive /path/to/knowledge-vault
```

The installer refuses to use a checked-out generator repository, or any path
inside one, as the target. It also refuses a non-empty target directory and a
target nested inside another Git repository unless `--force` is passed;
re-running inside an already generated vault is always allowed.

## Generated Target Layout

The target vault receives:

```text
inbox/
raw/
attachments/
wiki/
outputs/
archives/
schema/
AGENTS.md
CLAUDE.md
README.md
.agents/skills/
.claude/skills -> .agents/skills
.codex/config.toml
.codex/hooks.json
.scripts/postrun.sh
.scripts/check-index-log.sh
.obsidian/
.gitignore
```

Selected upstream Skills are installed into `.agents/skills/`, flattened by
skill directory name, and exposed to Claude Code through the `.claude/skills/`
symlink. Stable Obsidian settings, the Things theme, and pinned obsidian-git
plugin assets are generated under `.obsidian/`; the plugin is configured for
manual commits (no auto commit, pull, or push), and volatile workspace state is
not generated.

## Requirements

- Python 3.10+ (`uvx` provisions a suitable Python automatically)
- Git
- `rg` when selected
- `fzf` when selected
- Network access to PyPI for `uvx`, GitHub for streamed installs and upstream
  Skills
- macOS or Linux (the interactive selector uses POSIX terminal APIs)

The installer never installs tools itself. Pass `--offline` to disable
upstream Skill cloning; when `--offline` is used without `--skills`, upstream
Skills default to `none`.

## CLI Options

```text
--force              overwrite generated files, and allow non-empty or
                     nested-repository targets
--no-interactive     use default selections without asking
--yes                alias for --no-interactive
--tools LIST         rg,fzf, all, or none (default: all)
--skills LIST        Ar9av,kepano, all, or none (default: kepano)
--offline            do not run network bootstrap operations
--dry-run            print the install plan without writing files
--json               print dry-run or final install summaries as JSON
```

## Failure Handling

Installer failures are intended to be actionable. Common fixes:

- Missing Python: install Python 3.10+ or use `uvx llm-wiki-installer`.
- Missing Git: install Git and rerun the same command.
- Missing `rg` or `fzf`: install the selected tool or rerun with `--tools`
  excluding it.
- Network unavailable: use `--offline --skills none`; selected upstream Skills
  require GitHub access.
- Non-empty target directory: choose an empty directory or re-run with
  `--force`.

The post-install verification step reports issues without failing the install:
re-running the installer inside a vault that has legitimate uncommitted work
succeeds and prints the check findings for review.

## Privacy And Network Boundaries

The installer does not include telemetry. It writes only under the target vault
root after rejecting the generator repository itself and child paths. Network
access is limited to documented bootstrap operations: fetching the published
package from PyPI when using `uvx`, cloning this installer for streamed
installs, and cloning selected pinned upstream Skill sources. Use `--dry-run`
to inspect the plan first, and `--offline` to disable installer-managed network
bootstrap operations after the package or launcher has already started.

## Develop

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
```

Useful development checks:

```bash
make format        # apply isort and Black to src/ and tests/
make format-check  # verify isort and Black without changing files
make lint          # run format checks and Pylint
make typecheck     # run mypy
make test          # run pytest
make coverage      # run pytest with coverage
make shell-test    # run the stubbed shell integration harness
make package-check # build sdist/wheel and run twine check
make verify        # run the full local verification stack
```

Optional local Git hook setup:

```bash
.venv/bin/pre-commit install
```

## Project Map

- `install.sh` is the small compatibility launcher.
- `src/llm_wiki_installer/` contains the Python installer package.
- `src/llm_wiki_installer/templates/` contains generated vault file bodies.
- `docs/technical-design.md` is the architecture source of truth.
- `docs/llm-wiki-generation-guide.md` is the generation contract.
- `docs/security-model.md` describes trust boundaries, network access, command
  execution, and supply-chain controls.
- `tests/test_installer.py` covers installer behavior and generated contracts.
- `tests/install_test.sh` is the shell integration harness with stubbed tools.

## Contributing And Security

Contributions should keep the generator and generated vault contracts aligned:
when generated behavior changes, update the relevant template, docs, and tests
in the same patch. See `CONTRIBUTING.md` for the local workflow,
`docs/security-model.md` for the security model, and `SECURITY.md` for
vulnerability reporting.

## Credits

This project is inspired by Andrej Karpathy's LLM Wiki methodology: compile
approved source material into a long-lived Markdown wiki, retrieve from the wiki
first, and keep changes reviewable through files and Git.

The installer can copy upstream Skills from these projects as third-party
artifacts:

- `Ar9av/obsidian-wiki`
- `kepano/obsidian-skills`

Thanks to the authors and maintainers of the tools and ecosystems this project
builds on:

- [Obsidian](https://obsidian.md/) for the local-first Markdown knowledge base
  model this installer targets.
- [ripgrep](https://github.com/BurntSushi/ripgrep) and
  [fzf](https://github.com/junegunn/fzf) for fast local search and selection.
- [Git](https://git-scm.com/), [Python](https://www.python.org/), and
  related tooling for the portable installer and verification toolchain.

These acknowledgements do not imply endorsement by those projects. They are
included to make the dependencies and inspiration behind `llm-wiki-installer`
clear.

## License

MIT. See `LICENSE`.
