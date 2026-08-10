# llm-wiki Generation Guide

Verification date: 2026-08-10.

This document is the generation contract for the llm-wiki installer: which
artifacts are generated, what each must contain, and which invariants tests
must hold. It intentionally does not duplicate template bodies. The canonical
body of every generated file lives in `src/llm_wiki_installer/templates/`;
when this guide and a template disagree, fix the mismatch in the same patch
and treat the template as the rendered truth.

---

## 1. Generation Goal

Generate repeatable, auditable, and verifiable repository-root initialization
artifacts:

```text
fixed filenames
fixed directory structure
fixed templates
fixed check scripts
fixed diff output
```

Implementation rules:

```text
Keep install.sh as a small compatibility launcher.
Put installer control flow in focused Python modules under src/llm_wiki_installer/.
Put generated file bodies in template files under src/llm_wiki_installer/templates/.
Do not hide long generated Markdown or shell scripts inside install.sh heredocs.
Do not duplicate template bodies into documentation.
```

---

## 2. Fixed Artifact List

The installer generates these paths at the target repository root:

```text
./
├─ inbox/                        # + .gitkeep
├─ raw/                          # + .gitkeep
├─ attachments/                  # + .gitkeep
├─ wiki/
│  ├─ maps/                      # + .gitkeep
│  ├─ index.md
│  ├─ tags.md
│  └─ log.jsonl
├─ outputs/                      # + .gitkeep
├─ archives/                     # + .gitkeep
├─ schema/
│  ├─ workflow.md
│  ├─ log.md
│  ├─ wiki-page.md
│  └─ map.md
├─ AGENTS.md                     # canonical cross-agent policy
├─ CLAUDE.md                     # imports AGENTS.md for Claude Code
├─ README.md
├─ .agents/
│  └─ skills/<skill-name>/       # selected upstream skills, flattened
├─ .claude/
│  └─ skills -> ../.agents/skills   # symlink for Claude Code discovery
├─ .codex/
│  ├─ config.toml
│  └─ hooks.json
├─ .scripts/
│  ├─ postrun.sh
│  └─ check-index-log.sh
├─ .obsidian/                    # stable settings, obsidian-git assets, Things theme
└─ .gitignore
```

Empty contract directories receive a `.gitkeep` placeholder so the layout
survives commit, push, and clone.

Must not generate:

```text
.codex/rules/
tests/
fixtures/
examples/
third-party Skill rewrites or local substitutes
project-owned SKILL.md
.obsidian/workspace.json
.obsidian/workspaces.json
```

Target safety rules:

```text
Refuse the generator repository itself or any child path inside it.
Refuse a non-empty target directory unless --force is passed. Entries that are
  harmless (.git, .DS_Store, .localized, .obsidian) do not count as non-empty,
  and re-running inside an already generated vault is always allowed.
Refuse a target nested inside another Git repository unless --force is passed.
Verification failures after generation are reported but do not fail the install.
```

---

## 3. Markdown Template Contracts

Canonical bodies: `templates/wiki-index.md`, `templates/wiki-tags.md`,
`templates/wiki-log.jsonl`, `templates/schema/*.md`.

- `wiki/index.md` is the global retrieval entry point and lists the core
  files. `wiki/index.md` may omit frontmatter.
- `wiki/tags.md` is the canonical flat kebab-case tag registry: YAML `tags`
  lists, no `#` prefixes, no nested slash tags, reuse before creation, and
  tag redesigns are schema migrations logged to `wiki/log.jsonl`.
- `wiki/log.jsonl` is an append-only JSONL ledger. Each line is one JSON
  object with `schema_version`, UTC `timestamp`, `actor`, `type`, `scope`,
  `reason`, `review`, `impact`, and `files`. Event examples live in
  `schema/log.md`. Scripts do not enforce an event-type whitelist.
- `schema/workflow.md` carries the detailed capture, ingest, export,
  retrieval, raw-authorization, Skills, index, and tag rules, including the
  upstream-Skill compatibility caveat (upstream skills target their authors'
  own layouts and must be mapped onto this vault's paths, never the reverse).
- `schema/wiki-page.md` and `schema/map.md` carry the page and map templates
  (frontmatter with `title`, `tags`, `created`, `updated`; body sections for
  summary, key points, evidence, open questions, related). The page schema
  defines claim-provenance markers (`extracted` with a cited `raw/` path,
  `inferred`, `ambiguous`) so claims can be verified at read time, and the
  workflow schema defines a digest-and-sampling review cadence.

File naming: LLM-generated wiki, output, script, and config-description files
use lowercase kebab-case. Files created by the user are exempt, and the check
scripts warn rather than fail on naming issues.

---

## 4. Canonical Tools

### 4.1 Interactive Selection

Interactive terminal installs present two keyboard-driven selectors before
generating files:

```text
dependency tools: rg, fzf            default: all selected
upstream skills:  Ar9av, kepano      default: kepano only
controls: Up/Down move, Space toggles, Enter accepts
non-interactive behavior: the same defaults
--tools / --skills: explicit comma-separated selection, all, or none
--dry-run: print plan, write nothing, run no network steps
--json: print dry-run or final summary as JSON
```

Python 3.10+ and Git are bootstrap requirements. The installer never installs
missing tools; when a selected tool is absent it fails with an actionable
message.

### 4.2 rg / fzf

Required when selected (`command -v rg`, `command -v fzf`). Recommended
install: `brew install ripgrep fzf`.

### 4.3 Obsidian

```text
Generate stable Obsidian settings from fixed templates.
Generate pinned obsidian-git plugin assets as templates, not runtime downloads.
Configure obsidian-git for manual commits: no auto commit-and-sync, no auto
  pull, no auto push. Automatic commits would bypass the Git review gate and
  blind the check scripts, which diff against HEAD.
Generate the Things theme from fixed templates.
Do not generate volatile workspace state.
Obsidian is only the Markdown IDE / viewer.
```

---

## 5. Installer and Skill Installation Rules

### 5.1 Installer Role

`llm-wiki` is the setup wrapper / generator suite name, not a runtime Skill.

```text
Do not generate .agents/skills/llm-wiki/SKILL.md.
Do not generate any project-owned SKILL.md.
Use AGENTS.md as the runtime coordinator and canonical agent policy.
Generate CLAUDE.md containing an @AGENTS.md import so Claude Code, which does
  not read AGENTS.md natively, receives the same policy.
```

### 5.2 Codex Adapter Rules

```text
Codex adapter output = .codex/config.toml and .codex/hooks.json
canonical runtime policy = AGENTS.md
Do not put long-term rules in .codex/config.toml or hooks.json.
hooks.json wires a Stop hook that runs bash .scripts/check-index-log.sh.
Hooks may call only the generated verification scripts.
Codex loads project .codex/ layers only after the user trusts the project.
Do not generate .codex/rules/.
```

### 5.3 Upstream Skills Installation Rules

Sources and pins:

```text
Ar9av/obsidian-wiki   pinned 347e85704c52474d13470a3919e4a5cd7e3809cb   opt-in
kepano/obsidian-skills pinned 553ef99aa3306dd23f268e1ba9af752577684f69  default
```

Ar9av's skills are written for that project's own vault layout (`_raw/`,
root-level `index.md` and `log.md`, `.manifest.json`, `~/.obsidian-wiki/`
config). They are installed only on explicit selection and are framed in the
generated workflow schema as reference material that must not restructure
this vault.

Mechanics:

```text
Inspect .skills/ then skills/ in each selected source at the pinned commit.
Install every discovered <skill-dir>/SKILL.md skill, flattened into
  .agents/skills/<skill-name>/.
Reject symlinks in upstream sources; reject duplicate skill names across
  sources; verify the resolved commit equals the pin.
Expose .agents/skills to Claude Code via the .claude/skills symlink.
Do not rewrite, fork, summarize, or generate local substitutes.
Record repo URL, pinned commit, resolved commit, and installed skill count.
```

---

## 6. Generated Policy and Script Contracts

Canonical bodies: `templates/AGENTS.md`, `templates/CLAUDE.md`,
`templates/README.md`, `templates/postrun.sh`,
`templates/check-index-log.sh`, `templates/gitignore`,
`templates/codex-config.toml`, `templates/codex-hooks.json`.

`AGENTS.md` must:

```text
Declare the vault map, the source/evidence boundary, and the retrieval path
  (index -> maps -> pages -> search tools -> raw verification).
Keep raw/ read-only by default; inbox/ is the capture path.
Point to schema/workflow.md, schema/log.md, schema/wiki-page.md, and
  schema/map.md for detailed policy (progressive disclosure).
Require one descriptive git commit per completed task.
Require the post-write checks and explain their split:
  postrun.sh   = hard raw/ evidence boundary
  check-index-log.sh = structural consistency (new/deleted/moved pages must
    update wiki/index.md and wiki/log.jsonl; content edits are exempt;
    naming issues warn).
```

`postrun.sh` must fail only on hard boundary violations: `.codex/rules/`
existing, `raw/` changes without `ALLOW_RAW_CHANGE=1`, and `raw/` changes
without a `wiki/log.jsonl` update. It prints changed files and a diff stat.

`check-index-log.sh` must hard-fail only structural inconsistencies: new wiki
pages (untracked or added, excluding `index.md`, `tags.md`, `log.jsonl`, and
`.gitkeep`) without index and log updates, and deletions/renames/copies
without a log update. Kebab-case naming problems emit warnings and exit 0.

`.gitignore` must stay minimal and note-safe: Obsidian volatile workspace
state, OS noise, and local secrets only. It must not contain boilerplate
patterns that can swallow user note directories (`logs`, `dist`, `out`,
`lib/`, `build/`, `target/`, `node_modules`, `tmp/`).

`CLAUDE.md` must contain an `@AGENTS.md` import and nothing that diverges
from AGENTS.md.

`.codex/config.toml` stays comment-only unless a project-scoped Codex setting
is intentionally added; canonical policy stays in AGENTS.md.

---

## 7. Unit Test Rules

The verification stack must cover:

```text
1. Option parsing, including rejection of removed flags.
2. Target safety: generator-repo refusal, non-empty-target refusal,
   nested-repository refusal, and the --force overrides.
3. Directory and .gitkeep generation, CLAUDE.md generation, and the
   .claude/skills symlink.
4. Template rendering with no unresolved tokens.
5. Script contracts: postrun hard-gates only; check-index-log structural
   failures, content-edit exemption, and naming warnings.
6. Upstream skill mechanics: pinned commit verification, symlink rejection,
   duplicate rejection, flattening, and default/opt-in selection.
7. Shell integration through install.sh with stubbed external tools.
8. Test artifacts are deleted after tests pass; the generator repository
   must not retain generated vault output.
```
