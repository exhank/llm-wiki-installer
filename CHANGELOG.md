# Changelog

All notable changes to this project will be documented here.

This project follows a simple human-readable changelog. Versions are published
when the package version in `src/llm_wiki_installer/__init__.py` changes.

## 0.2.0 - 2026-08-10

Contract-repair release following an architecture review: make the default
install succeed on ordinary machines, and make the generated vault stop
contradicting its own review-through-Git design.

Installer:

- Lower the Python requirement from 3.13+ to 3.10+ (the code never needed
  3.13); the streamed launcher now suggests `uvx` when `python3` is too old.
- Remove the `--no-install-tools` flag and the README claim that missing
  tools are installed automatically; that behavior never existed. Missing
  selected tools now fail with an actionable message.
- Refuse non-empty target directories and targets nested inside another Git
  repository unless `--force` is passed; re-running inside a generated vault
  is always allowed.
- Run the post-install verification without failing the install, so
  re-running the installer on a vault with legitimate uncommitted work
  succeeds and reports findings instead of erroring.
- Flush progress output so piped and CI logs are ordered correctly.

Generated vault:

- Configure the bundled obsidian-git plugin for manual commits: no auto
  commit-and-sync, no auto pull or push, no `mergeStrategy: "theirs"`.
  Automatic background commits bypassed the Git review gate and blinded the
  check scripts.
- Generate `CLAUDE.md` (an `@AGENTS.md` import) and a `.claude/skills`
  symlink so Claude Code, which reads neither `AGENTS.md` nor
  `.agents/skills/`, receives the same policy and skills.
- Split the check scripts: `postrun.sh` now enforces only the hard `raw/`
  evidence boundary; `check-index-log.sh` requires index and log updates only
  for new, deleted, moved, or renamed pages, exempts content edits, drops the
  log event-type whitelist, and demotes kebab-case naming issues to warnings.
  Stray `SKILL.md` files (for example user-installed Claude Code skills) are
  no longer rejected.
- Default the upstream Skill selection to `kepano/obsidian-skills`;
  `Ar9av/obsidian-wiki` is opt-in because its skills target that project's
  own vault layout, and the generated workflow schema now tells agents to map
  or ignore foreign layout references instead of restructuring the vault.
- Wire `.codex/hooks.json` to run the structural checks on the Codex `Stop`
  event (active after the project is trusted) instead of shipping an empty
  hook object.
- Add `.gitkeep` placeholders to the empty contract directories so the layout
  survives commit, push, and clone.
- Replace the ~500-line concatenated `.gitignore` with a minimal note-safe
  ignore file; the old one silently ignored user note directories named
  `logs`, `dist`, `out`, `lib`, `build`, or `target`.
- State one-descriptive-commit-per-task in `AGENTS.md` and exempt
  user-created filenames from the kebab-case rule.
- Add claim-provenance markers (`extracted` / `inferred` / `ambiguous`) to the
  wiki page schema and a digest-and-sampling review cadence to the workflow
  schema, so verification effort scales with use instead of with write volume.

Documentation:

- Rewrite the generation guide as a contract that points at
  `src/llm_wiki_installer/templates/` instead of duplicating every template
  body, and sync the technical design, security model, and README with the
  behavior above.

## 0.1.7 - 2026-05-29

- Generate `schema/wiki-page.md` and `schema/map.md` so detailed page and map
  templates are progressively disclosed from the generated `AGENTS.md`.
- Generate `schema/log.md` for detailed `wiki/log.jsonl` event schemas and
  keep generated `AGENTS.md` focused on high-level runtime log rules.
- Create an empty generated `schema/` directory and document the schema layer in
  the generated `AGENTS.md` template.
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
