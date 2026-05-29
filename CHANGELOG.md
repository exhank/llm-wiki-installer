# Changelog

All notable changes to this project will be documented here.

This project follows a simple human-readable changelog. Versions are published
when the package version in `src/llm_wiki_installer/__init__.py` changes.

## Unreleased

- Generate `wiki/log.jsonl` entries with UTC `timestamp`, `schema_version`, and
  `actor` fields instead of a date-only field, and tighten generated log schema
  examples to avoid blank reasons and stringified booleans.
- Remove generated Markdown frontmatter `type` fields and add `wiki/tags.md` as
  the canonical flat kebab-case tag registry.

## 0.1.6 - 2026-05-29

- Create `attachments/` during installation to match the generated Obsidian
  default attachment folder.
- Remove the Markdown collection indexing integration from installer code,
  generated vault templates, tests, and documentation.
- Install upstream Skills directly under `.agents/skills/<skill-name>/` instead
  of namespacing them under `.agents/skills/upstream/<source>/`.
- Generate `.codex/hooks.json` for Codex project hook configuration instead of
  creating an unused `.codex/hooks/` directory.
- Generate `wiki/log.jsonl` as the append-only audit ledger instead of
  `wiki/log.md`.
- Expand the generated `.gitignore` with Obsidian and llm-wiki rules plus
  concatenated official GitHub Python, Node, macOS, Windows, and Linux
  templates.

## 0.1.5 - 2026-05-29

- Switch the README PyPI badge to a release-specific shields dynamic JSON
  badge so it renders the just-published package version instead of waiting on
  shields' PyPI endpoint cache.
- Generate stable Obsidian configuration, the Things theme, and pinned
  obsidian-git plugin assets while continuing to exclude volatile workspace
  state.
- Use macOS/VSCode-style generated Obsidian hotkeys for quick open, command
  palette, search, file creation, tab management, splits, Markdown formatting,
  headings, sidebars, navigation, and Git pull.

## 0.1.4 - 2026-05-29

- Disable Git's pager for installer diff-stat review output and generated
  review commands, avoiding a blank full-screen pager during interactive
  streamed installs.
- Add a shell integration test for the README one-line curl install command so
  release-tag resolution, raw install script fetching, bootstrap cloning,
  initialization, and generated post-run checks are covered end to end.

## 0.1.3 - 2026-05-29

- Improve collection detection during reinstall.

## 0.1.2 - 2026-05-29

- Make the streamed shell launcher resolve GitHub Releases latest when
  `LLM_WIKI_INSTALLER_REF` is not set, avoiding stale bootstrap clones from a
  previously hard-coded release ref.

## 0.1.1 - 2026-05-29

- Update user-facing documentation now that `llm-wiki-installer` is published
  on PyPI, making `uvx` the primary automation path.
- Clarify that the PyPI Trusted Publisher is configured for future releases.
- Restore one-line install guidance without hard-coding the current release
  version in user-facing commands.
- Suppress stderr for quiet subprocesses so streamed bootstrap and upstream
  Skill Git operations do not leak clone or detached-HEAD noise during normal
  installs.
- Expand README credits for Obsidian, ripgrep, fzf, Git, Python,
  and upstream Skill maintainers.

## 0.1.0 - 2026-05-29

- Add open-source contributor, security, conduct, issue, pull request, and CI
  project metadata.
- Clarify generated upstream Skill directory behavior for skipped sources.
- Rename user-facing project language to `llm-wiki-installer`.
- Add README badges, product overview, generated layout preview, and
  architecture diagram.
- Pin upstream Skill source commits for reproducible generated vaults.
- Add release workflow with package smoke tests, SBOM generation, release
  artifacts, artifact provenance, and PyPI publishing.
- Add a `uvx`-friendly `llm-wiki-installer` entry point and document PyPI
  Trusted Publishing release setup.
- Add a security model document.
- Harden streamed installer bootstrap defaults and clone failure reporting.
- Document release-pinned curl installation and add a 30-second start path.
- Add explicit `--tools`, `--skills`, `--offline`, `--no-install-tools`,
  `--dry-run`, `--json`, and `--yes` installer options.
- Add JSON dry-run planning and final install summaries for automation.
- Make `src/llm_wiki_installer/__init__.py` the package version source.
- Add generated GitHub release-note categories and a Chinese quickstart.
