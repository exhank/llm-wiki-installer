# Repository Guidelines

This repository builds the `llm-wiki` installer. It is not itself an
initialized knowledge vault. The installer reads the design documents in
`docs/`, then generates a vault layout, policy files, helper scripts, and
upstream skills into a separate target repository.

## Project Layout

- `install.sh` is the compatibility launcher for local and streamed installs.
  Keep it small; installer control flow belongs in Python.
- `src/llm_wiki_installer/` contains the Python installer package and CLI.
- `src/llm_wiki_installer/cli.py` and `__main__.py` provide the package entry
  points for `llm-wiki-install` and `python -m llm_wiki_installer`.
- `src/llm_wiki_installer/installer.py` owns top-level install orchestration
  and target safety checks.
- `src/llm_wiki_installer/install_options.py` parses CLI options.
- `src/llm_wiki_installer/terminal_ui.py` owns interactive selector behavior.
- `src/llm_wiki_installer/toolchain.py` checks dependency tools.
- `src/llm_wiki_installer/upstream_skills.py` installs upstream Skill sources.
- `src/llm_wiki_installer/target_layout.py` generates target directories and
  files.
- `src/llm_wiki_installer/template_renderer.py` renders packaged text
  templates.
- `src/llm_wiki_installer/command_runner.py` wraps subprocess execution.
- `src/llm_wiki_installer/path_safety.py` rejects generated writes that would
  traverse symlinks under the target root.
- `src/llm_wiki_installer/errors.py` contains user-facing installer errors.
- `src/llm_wiki_installer/templates/` contains generated vault file bodies.
  Do not hide long generated Markdown or shell scripts in `install.sh`.
- `docs/technical-design.md` is the product architecture source of truth.
- `docs/llm-wiki-generation-guide.md` is the generation spec.
- `docs/security-model.md` documents trust boundaries, network access,
  filesystem safety, command execution, and supply-chain controls.
- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, and `CHANGELOG.md` are
  user-facing project and release documents.
- `tests/test_installer.py` covers installer orchestration and generated
  layout behavior.
- `tests/test_terminal_ui.py` covers interactive selector behavior.
- `tests/test_template_context.py` covers template context and generated log
  templates.
- `tests/test_security_boundaries.py` covers symlink, clone, and target safety
  boundaries.
- `tests/install_test.sh` is the shell-level integration harness with stubbed
  external tools.

## Repository vs Generated Vault

- This repository may contain `src/`, `tests/`, `docs/`, and packaging files.
- A generated vault must not contain generator-only folders such as `src/`,
  `tests/`, `fixtures/`, or `examples/`.
- The generated vault policy lives in
  `src/llm_wiki_installer/templates/AGENTS.md`; this root file governs work on
  the generator itself.
- Build, coverage, and local environment artifacts such as `.venv/`,
  `.coverage`, `.mypy_cache/`, `.pytest_cache/`, `dist/`, `build/`, and
  `*.egg-info/` are development outputs, not source.
- When changing generated vault behavior, update the relevant template, the
  design or generation guide if the contract changed, and tests that assert the
  generated output.

## Development Setup

Use the repository Makefile from the project root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
```

Common commands:

```bash
make format        # apply isort and Black to src/ and tests/
make format-check  # verify isort and Black without changing files
make lint          # format checks plus Pylint
make typecheck     # mypy
make test          # Python unit tests
make coverage      # pytest with coverage
make shell-test    # shell integration harness with stub tools
make package-check # build sdist/wheel and run twine check
make verify        # full local verification stack
make clean         # remove local test/build caches
```

Run focused tests with:

```bash
.venv/bin/python -m pytest tests/test_installer.py -k <pattern>
```

## Required Verification

- For Python-only changes, run `make lint`, `make typecheck`, and `make test`.
- For changes to `install.sh`, templates, generated scripts, tool
  checks, upstream skill installation, or target layout, run `make verify`.
- For safety-boundary changes, run the focused security tests and then the
  broader required stack:
  `.venv/bin/python -m pytest tests/test_security_boundaries.py`.
- For template context changes, run:
  `.venv/bin/python -m pytest tests/test_template_context.py tests/test_installer.py`.
- If `make verify` is blocked by missing local tools, run the narrowest
  available check and report the blocker clearly.
- Do not mark generated behavior complete until both the Python template tests
  and the shell integration harness cover the changed contract.

## Coding Style

- Support Python 3.13+.
- Prefer standard library code; the runtime package intentionally has no
  third-party dependencies.
- Use isort for import ordering and Black for formatting.
- Use Pylint for linting and mypy for static type checking.
- Use pytest with coverage for behavior checks.
- Use `pathlib.Path` for filesystem paths and pass subprocess commands as
  argument lists, not shell strings.
- Keep user-facing installer failures as `InstallerError` messages.
- Keep functions small enough to test directly when they encode installer
  policy.
- Preserve type hints on public and internal helper functions.
- Avoid broad abstractions unless they reduce real duplication in installer
  policy or template rendering.

## Installer Contracts

- `install.sh` must refuse to generate into this generator repository or one of
  its child paths.
- `install.sh` must continue to work both from a local checkout and through the
  streamed curl pattern documented in `README.md`.
- The installer must create the fixed target layout documented in
  `docs/llm-wiki-generation-guide.md`.
- Generated files must come from packaged templates under
  `src/llm_wiki_installer/templates/`.
- The generated target layout currently includes `inbox/`, `raw/`, `wiki/`,
  `wiki/maps/`, `outputs/`, `archives/`, `.agents/skills/upstream/`,
  `.codex/hooks.json`, `.scripts/`, root `AGENTS.md`, root `README.md`,
  `.codex/config.toml`, `wiki/index.md`, `wiki/log.jsonl`, `.gitignore`, and the
  generated scripts.
- Existing generated files are preserved unless `--force` is passed.
- Generated `.scripts/*.sh` files must be executable.
- The installer must initialize a Git repository in the target if one does not
  already exist.
- Generated write paths and upstream copy targets must reject existing symlinks
  that would escape or redirect writes under the target root.
- Interactive terminal installs must show separate default-all multi-select
  prompts for dependency tools and upstream Skill sources. Up/Down moves, Space
  toggles, and Enter accepts. Non-interactive installs and `--no-interactive`
  must use the all-selected default.

## Tool and Dependency Policy

- Required bootstrap tools are Python 3.13+ and Git. Selectable target tools are
  `rg` and `fzf`; all are selected by default.
- Development-only Python tools are listed in `requirements-dev.txt` and
  configured in `pyproject.toml`; do not add runtime dependencies for tooling.
- Do not vendor third-party Python dependencies into this repository.

## Local Hook Policy

- `.pre-commit-config.yaml` uses local hooks that call `make lint` and
  `make typecheck`.
- Install hooks with `.venv/bin/pre-commit install` after setting up the
  development environment.
- Keep pre-commit hooks aligned with Makefile targets instead of duplicating
  separate tool arguments.

## Packaging Checks

- Use `python -m build` through `make package` to build the sdist and wheel.
- Use `twine check` through `make package-check` before publishing or changing
  packaging metadata.
- Generated `dist/`, `build/`, and `*.egg-info/` artifacts are ignored and
  should not be committed.
- Keep `MANIFEST.in` and `pyproject.toml` aligned so packaged releases include
  `install.sh`, documentation, `py.typed`, and all templates.

## Upstream Skill Policy

- Upstream skills are selectable during interactive install and default to all
  sources selected. Selected upstream skills are copied into generated vaults
  from:
  - `Ar9av/obsidian-wiki`
  - `kepano/obsidian-skills`
- Upstream pins currently live in `src/llm_wiki_installer/upstream_skills.py`.
  Treat pin updates as supply-chain changes and update docs, tests, and release
  notes when behavior changes.
- Copy upstream skill directories as upstream artifacts. Do not rewrite,
  summarize, or create local substitutes for missing upstream skills.
- If an upstream repository has no `.skills/` or `skills/` directory, or no
  discoverable `SKILL.md`, the installer must fail.
- Reject symlinks inside upstream skill sources before copying them into a
  generated vault.
- Tests should use stubs for upstream repositories rather than relying on the
  network.

## Template Rules

- Every generated template must render without unresolved `{{TOKEN}}` values.
- Add new template context keys in one place:
  `template_context()` in `src/llm_wiki_installer/target_layout.py`.
- Update `tests/test_installer.py` whenever template context, generated files,
  executable files, or required output text changes.
- Update `tests/test_template_context.py` when template context or generated
  log output changes.
- Keep generated Markdown compatible with standard GitHub-flavored Markdown.
- Generated wiki, output, script, and config-description filenames should use
  lowercase kebab-case unless preserving a user-provided raw filename.

## Shell Script Rules

- Use `set -euo pipefail`.
- Keep scripts POSIX-friendly where practical, but Bash is allowed because the
  launcher and generated scripts are Bash.
- Quote paths and variables.
- Keep shell tests deterministic with stubbed tools and temporary directories.
- Do not leave generated test artifacts in the repository or target vault.

## Documentation Rules

- Update `README.md` when user-facing install commands, requirements, or
  verification instructions change.
- Update `docs/technical-design.md` when the vault architecture or policy
  boundaries change.
- Update `docs/llm-wiki-generation-guide.md` when generated paths, templates,
  tool requirements, or verification flow change.
- Update `docs/security-model.md` when trust boundaries, network behavior,
  symlink protection, command execution, or supply-chain policy changes.
- Update `CHANGELOG.md` for release-visible installer behavior, packaging,
  generated layout, or security changes.
- Do not duplicate large policy sections across docs unless the generated
  template needs to carry them into target vaults.

## Safety Boundaries

- Never write generated vault artifacts into the repository root as part of a
  normal install test.
- Do not create `.codex/rules/`, `.obsidian/plugins/`, generated vault
  top-level directories, or project-owned runtime `SKILL.md` files in this
  repository unless the task explicitly changes the generator contract.
- Do not hard-code secrets, tokens, private machine paths, or user-specific
  configuration into templates or docs.
- Do not bypass `path_safety.py` for generated writes or upstream copy targets.
- Do not use destructive Git commands to clean the worktree. Respect unrelated
  local changes.

## Commit and PR Guidance

- Keep commits focused and use concise imperative messages.
- Include tests for installer behavior changes and generated output contracts.
- In PR summaries, call out changes to install behavior, generated layout,
  required tools, or upstream skill handling.
- Before review, include the verification command run and any skipped checks
  with the reason.
