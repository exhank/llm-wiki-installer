# llm-wiki-installer

[![CI](https://github.com/exhank/llm-wiki-installer/actions/workflows/ci.yml/badge.svg)](https://github.com/exhank/llm-wiki-installer/actions/workflows/ci.yml)
[![Release](https://github.com/exhank/llm-wiki-installer/actions/workflows/release.yml/badge.svg)](https://github.com/exhank/llm-wiki-installer/actions/workflows/release.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue.svg)](pyproject.toml)
[![PyPI](https://img.shields.io/pypi/v/llm-wiki-installer.svg)](https://pypi.org/project/llm-wiki-installer/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

`llm-wiki-installer` generates a Git-auditable, agent-friendly Obsidian
Markdown knowledge vault from one command.

It turns an empty folder into a durable Markdown knowledge system with clear
evidence boundaries, agent policy, helper scripts, qmd setup, and selected
upstream Skills. The generated vault is designed for a simple loop: collect
approved sources, compile them into `wiki/`, retrieve from the wiki first, and
review every change through Git.

It is not itself an initialized vault. This repository builds the generator; the
generated vault lives in a separate target repository.

## 30-Second Start

Create a vault with one command:

```bash
uvx --python 3.13 llm-wiki-installer --no-interactive ./knowledge-vault
```

Inspect the generated vault:

```bash
cd knowledge-vault
bash .scripts/postrun.sh
git status --short
```

Preview the same install without writing files or running network steps:

```bash
uvx --python 3.13 llm-wiki-installer --dry-run --json .
```

The package is published on PyPI as
[`llm-wiki-installer`](https://pypi.org/project/llm-wiki-installer/).
For pinned automation, include the package version you want to reproduce:

```bash
uvx --python 3.13 llm-wiki-installer==<version> --dry-run --json /path/to/knowledge-vault
```

If you do not use `uv`, the release-pinned shell bootstrap can resolve the
latest GitHub release tag and install in one line:

```bash
/bin/bash -c "$(curl -fsSL "https://raw.githubusercontent.com/exhank/llm-wiki-installer/$(curl -fsSLI -o /dev/null -w '%{url_effective}' https://github.com/exhank/llm-wiki-installer/releases/latest | sed 's#.*/tag/##')/install.sh")" -- --no-interactive ./knowledge-vault
```

## Why This Exists

Most AI note workflows stop at chat answers or ad hoc generated notes. This
project sets up a stricter vault contract:

- `raw/` keeps user-approved source evidence.
- `wiki/` keeps compiled long-term Markdown knowledge.
- `wiki/index.md` and `wiki/maps/` provide stable retrieval entry points.
- `wiki/log.md`, Git diff, and generated scripts make changes auditable.
- Upstream Skills are copied as third-party artifacts and pinned in a manifest.

## Features

- One-command local or streamed installer.
- Python installer package with no runtime third-party dependencies.
- Interactive default-all selectors for dependency tools and upstream Skill
  sources.
- Optional qmd collection setup with Node.js 22+ validation.
- Generated AGENTS policy, README, scripts, Codex config, index, log, and
  Markdown plus JSON manifests.
- Pinned upstream Skill commits for reproducible generated vaults.
- Safety checks that refuse to generate into this generator repository.
- Unit, shell integration, type, lint, coverage, and package checks.

## What It Generates

`llm-wiki-installer` turns an empty target repository into a working vault
contract:

```text
knowledge-vault/
+-- raw/                 # user-approved source evidence
+-- wiki/                # durable compiled knowledge
|   +-- index.md         # retrieval entry point
|   +-- log.md           # change log
|   +-- maps/            # topic maps for navigation
+-- outputs/             # generated reports and exports
+-- inbox/               # incoming material awaiting review
+-- archive/             # retired material
+-- AGENTS.md            # runtime policy for agents
+-- .agents/
|   +-- skill-manifest.md
|   +-- skill-manifest.json
|   +-- skills/upstream/ # pinned third-party Skill artifacts
+-- .codex/config.toml
+-- .scripts/            # verification helpers
```

The operating model is intentionally file-first:

```text
approved sources -> raw/ -> wiki pages -> wiki/index.md + wiki/maps/
                         \-> wiki/log.md -> Git diff review

agents read AGENTS.md -> retrieve with qmd/rg/fzf -> verify against raw/
```

## Generate A Vault

Install with the published PyPI package:

```bash
uvx --python 3.13 llm-wiki-installer /path/to/knowledge-vault
```

Pin the package version for repeatable automation:

```bash
uvx --python 3.13 llm-wiki-installer==<version> /path/to/knowledge-vault
```

Install into the current directory with a release-pinned one-line shell
bootstrap that resolves the latest release tag from
[GitHub Releases](https://github.com/exhank/llm-wiki-installer/releases/latest):

```bash
/bin/bash -c "$(curl -fsSL "https://raw.githubusercontent.com/exhank/llm-wiki-installer/$(curl -fsSLI -o /dev/null -w '%{url_effective}' https://github.com/exhank/llm-wiki-installer/releases/latest | sed 's#.*/tag/##')/install.sh")"
```

Pass installer options through the same pattern:

```bash
/bin/bash -c "$(curl -fsSL "https://raw.githubusercontent.com/exhank/llm-wiki-installer/$(curl -fsSLI -o /dev/null -w '%{url_effective}' https://github.com/exhank/llm-wiki-installer/releases/latest | sed 's#.*/tag/##')/install.sh")" -- --force
```

The streamed launcher also clones the release ref embedded in that launcher.
Set `LLM_WIKI_INSTALLER_REF` only when intentionally testing another ref. Using
the same release tag in the curl URL and launcher ref keeps the bootstrap path
anchored to the same published source.

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
bash install.sh --tools qmd,rg --skills kepano /path/to/knowledge-vault
bash install.sh --tools none --skills none /path/to/knowledge-vault
```

Run without network bootstrap operations:

```bash
bash install.sh --offline --tools rg --skills none /path/to/knowledge-vault
```

Run without automatically installing missing selectable tools:

```bash
bash install.sh --no-install-tools --tools qmd,rg /path/to/knowledge-vault
```

When run from an interactive terminal, the installer shows two onboarding
selectors before generating files:

- dependency tools: `qmd`, `rg`, and `fzf`
- upstream Skill sources: `Ar9av/obsidian-wiki` and `kepano/obsidian-skills`

Both selectors default to all options selected. Use Up/Down to move, Space to
toggle an option, and Enter to continue. Non-interactive runs, including
scripted installs with redirected output, use the all-selected default. To force
that behavior from a terminal, pass:

```bash
bash install.sh --no-interactive /path/to/knowledge-vault
```

The installer refuses to use a checked-out generator repository, or any path
inside one, as the target. If you run `bash install.sh` from this repository, it
exits instead of writing vault files here.

## Generated Target Layout

The target vault receives:

```text
inbox/
raw/
wiki/
outputs/
archive/
AGENTS.md
README.md
.agents/skill-manifest.md
.agents/skill-manifest.json
.agents/skills/upstream/
.codex/config.toml
.codex/hooks/
.scripts/postrun.sh
.scripts/check-index-log.sh
.gitignore
```

Selected upstream Skills are installed into `.agents/skills/upstream/` and
recorded in `.agents/skill-manifest.md` and `.agents/skill-manifest.json`.
Skipped sources are recorded as skipped and are not left behind as stale upstream
directories. When qmd is selected, the installer initializes a `knowledge-vault`
collection at the target root.

## Requirements

- Python 3.13+
- Git
- Node.js 22+ and npm when qmd is selected
- `rg` when selected
- `fzf` when selected
- Network access to PyPI for `uvx`, GitHub for streamed installs and upstream
  Skills, and npm when qmd is selected and missing

If `qmd` is selected and missing, the installer runs:

```bash
npm install -g @tobilu/qmd
```

Pass `--no-install-tools` to require preinstalled tools instead. Pass
`--offline` to disable npm installation and upstream Skill cloning; when
`--offline` is used without `--skills`, upstream Skills default to `none`.

## CLI Options

```text
--force              overwrite generated files in the target vault
--no-interactive     use default all-selected prompts without asking
--yes                alias for --no-interactive
--tools LIST         qmd,rg,fzf, all, or none
--skills LIST        Ar9av,kepano, all, or none
--no-install-tools   fail if a selected missing tool would need installation
--offline            do not run network bootstrap operations
--dry-run            print the install plan without writing files
--json               print dry-run or final install summaries as JSON
```

## Failure Handling

Installer failures are intended to be actionable. Common fixes:

- Missing Python: install Python 3.13+ or use `uvx --python 3.13`.
- Missing Git: install Git and rerun the same command.
- Missing Node.js/npm with qmd selected: install Node.js 22+ and npm, or run
  with `--tools rg,fzf`.
- qmd install blocked: install `@tobilu/qmd` manually, or use
  `--no-install-tools` to fail before any automatic install attempt.
- Network unavailable: use `--offline --skills none`; selected upstream Skills
  require GitHub access.

## Privacy And Network Boundaries

The installer does not include telemetry. It writes only under the target vault
root after rejecting the generator repository itself and child paths. Network
access is limited to documented bootstrap operations: fetching the published
package from PyPI when using `uvx`, cloning this installer for streamed
installs, cloning selected pinned upstream Skill sources, and installing
`@tobilu/qmd` with npm when qmd is selected and missing. Use `--dry-run` to
inspect the plan first, and `--offline` to disable installer-managed network
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
- [`@tobilu/qmd`](https://www.npmjs.com/package/@tobilu/qmd) for Markdown
  collection indexing and retrieval.
- [ripgrep](https://github.com/BurntSushi/ripgrep) and
  [fzf](https://github.com/junegunn/fzf) for fast local search and selection.
- [Git](https://git-scm.com/), [Python](https://www.python.org/), and
  [Node.js](https://nodejs.org/) for the portable installer and verification
  toolchain.

These acknowledgements do not imply endorsement by those projects. They are
included to make the dependencies and inspiration behind `llm-wiki-installer`
clear.

## License

MIT. See `LICENSE`.
