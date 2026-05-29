# Security Model

`llm-wiki-installer` is an installer that writes a knowledge vault into a
separate target repository. Its main security goal is to make every filesystem
write, network fetch, generated script, and command execution explicit enough
for users and maintainers to audit.

## Trust Boundaries

- The generator repository is trusted installer code.
- The target vault is user-owned content and must not be confused with the
  generator repository.
- Upstream Skill repositories are third-party content copied as artifacts.
- `qmd`, `rg`, `fzf`, Git, Node.js, and npm are external tools.
- Generated scripts run inside the target vault and must treat user content as
  untrusted input.

## Network Access

The installer may access the network only for documented bootstrap operations:

- PyPI-based installs fetch the published `llm-wiki-installer` distribution,
  typically through `uvx --python 3.13 llm-wiki-installer`;
- streamed installs clone `llm-wiki-installer` from the configured repository
  and release ref, defaulting to `v0.1.0`;
- selected upstream Skill sources are cloned at pinned commit SHAs;
- npm may install `@tobilu/qmd` when qmd is selected and missing.

Pinned upstream commits make generated vaults reproducible for a given installer
release. Updating those pins is a generator release decision and should be
reviewed like any other supply-chain change.

Obsidian theme and community plugin assets are bundled as installer templates.
The installer does not download Obsidian plugin code at target generation time.
Updating bundled Obsidian assets is a supply-chain change and should be
reviewed like an upstream pin update.

Users can pass `--dry-run` to inspect planned filesystem and network operations
without writing files or running network steps. `--offline` disables network
bootstrap operations; when it is used without an explicit `--skills` selection,
upstream Skills default to `none`. `--no-install-tools` disables npm-based
installation of missing selectable tools.

## Filesystem Safety

The installer must refuse to generate into this generator repository or any
child path. Generated files are written only under the target root. Symlink
checks protect generated paths and upstream Skill copy targets from escaping the
target vault.

Existing generated files are preserved unless `--force` is passed. User-owned
knowledge files under `raw/`, `wiki/`, `outputs/`, `inbox/`, and `archive/` are
not overwritten by normal template generation.

## Command Execution

Commands are executed through argument lists, not shell strings, in the Python
installer. Shell scripts use `set -euo pipefail`, quote paths and variables, and
should fail closed when required tools or policy checks are missing.

Security-sensitive commands include:

- Git clone, fetch, checkout, init, and diff operations;
- npm global installation of `@tobilu/qmd`;
- qmd collection initialization, update, and embed;
- generated post-run and index/log verification scripts.

## Generated Vault Policy

The generated `AGENTS.md` is the runtime policy authority. Upstream Skills are
copied under `.agents/skills/upstream/` and must not override `AGENTS.md`.
Generated manifests record selected tools, skipped tools, upstream pinned
commits, resolved commits, and install results in both Markdown and JSON.
Stable Obsidian settings, pinned community plugin assets, and the bundled theme
are generated under `.obsidian/`; volatile workspace state is excluded.

## Maintainer Checklist

- Review every change that adds a command execution path.
- Update tests for every generated path, manifest field, template, or safety
  policy change.
- Treat upstream commit pin changes as supply-chain updates.
- Keep streamed install defaults on release tags rather than mutable branches.
- Keep GitHub Actions release dependencies pinned to reviewed commit SHAs.
- Publish PyPI releases through GitHub Actions Trusted Publishing from the
  protected `pypi` environment; do not store long-lived PyPI API tokens in the
  repository.
- Verify each release through the GitHub Release page and the PyPI project page
  before announcing the version in user-facing docs.
- Do not commit secrets, private paths, generated vault output, or build
  artifacts.
