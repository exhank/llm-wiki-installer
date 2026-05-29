# Changelog

All notable changes to this project will be documented here.

This project follows a simple human-readable changelog. Versions are published
when the package version in `src/llm_wiki_installer/__init__.py` changes.

## 0.1.3 - 2026-05-29

- Fix qmd collection detection for current `qmd collection show` output that
  indents the `Path:` field, avoiding duplicate `knowledge-vault` collection
  add failures during reinstall.

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
- Expand README credits for Obsidian, qmd, ripgrep, fzf, Git, Python, Node.js,
  and upstream Skill maintainers.

## 0.1.0 - 2026-05-29

- Add open-source contributor, security, conduct, issue, pull request, and CI
  project metadata.
- Clarify generated upstream Skill directory behavior for skipped sources.
- Rename user-facing project language to `llm-wiki-installer`.
- Add README badges, product overview, generated layout preview, and
  architecture diagram.
- Pin upstream Skill source commits and record pinned commits in generated
  manifests.
- Generate `.agents/skill-manifest.json` alongside the Markdown manifest.
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
- Record upstream Skill source type and license-review guidance in generated
  manifests.
- Make `src/llm_wiki_installer/__init__.py` the package version source.
- Add generated GitHub release-note categories and a Chinese quickstart.
