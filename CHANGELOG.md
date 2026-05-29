# Changelog

All notable changes to this project will be documented here.

This project follows a simple human-readable changelog. Versions are published
when the package version in `src/llm_wiki_installer/__init__.py` changes.

## Unreleased

- Update user-facing documentation now that `llm-wiki-installer` is published
  on PyPI, making `uvx` the primary automation path.
- Clarify that the PyPI Trusted Publisher is configured for future releases.

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
