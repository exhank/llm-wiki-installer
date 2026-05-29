# llm-wiki Generation Guide

Verification date: 2026-05-28.

This document guides LLMs in stably generating the llm-wiki setup wrapper, AGENTS file, hooks, scripts, README, manifest, upstream Skill installation, and verification flow for an LLM-Native Obsidian Markdown PKB.

---

## 1. Generation Goal

Generate repeatable, auditable, and verifiable repository-root initialization artifacts:

```text
fixed filenames
fixed directory structure
fixed templates
fixed dependency names with latest resolved versions recorded
fixed check scripts
fixed qmd collection
fixed manifest
fixed diff output
latest selected upstream Skill versions recorded
```

Implementation rule:

```text
Keep install.sh as a small compatibility launcher.
Put installer control flow in focused Python modules under src/llm_wiki_installer/.
Put generated file bodies in template files under src/llm_wiki_installer/templates/.
Do not hide long generated Markdown or shell scripts inside install.sh heredocs.
```

The generated result must satisfy:

```text
technical design is concise and stable
runtime rules are written into AGENTS.md
templates are written into AGENTS.md and this guide
scripts are executable
qmd is usable
selected upstream Skills are installed
test files and test artifacts are deleted after unit tests pass
```

---

## 2. Fixed Artifact List

The setup wrapper must generate these paths at repository root:

```text
./
├─ inbox/
├─ raw/
├─ wiki/
│  ├─ maps/
│  ├─ index.md
│  └─ log.md
├─ outputs/
├─ archive/
├─ AGENTS.md
├─ README.md
├─ .agents/
│  ├─ skills/
│  │  └─ upstream/              # selected upstream sources only
│  ├─ skill-manifest.md
│  └─ skill-manifest.json
├─ .codex/
│  ├─ hooks/
│  └─ config.toml
├─ .scripts/
│  ├─ postrun.sh
│  └─ check-index-log.sh
└─ .gitignore
```

Must not generate:

```text
.codex/rules/
tests/
fixtures/
examples/
.obsidian/plugins/
third-party Skill rewrites or local substitutes
project-owned SKILL.md
```

The installer must refuse targets that are the generator repository itself or a
child path inside the generator repository.

When an upstream Skill source is skipped, its `.agents/skills/upstream/<source>/`
directory must not be left behind from a previous install. The manifest records
the skipped state instead.

---

## 3. Markdown Template Generation Spec

### 3.1 General wiki Page frontmatter Template

All new `wiki/*.md` pages use this by default:

```yaml
---
title: ""
type: source | entity | concept | comparison | synthesis | question | map | decision | playbook | note
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Rules:

```text
wiki/index.md may omit frontmatter.
wiki/log.md may omit frontmatter.
wiki/maps/*.md uses type: map.
Do not use complex nested metadata.
Put Sources / Evidence in the body.
```

### 3.2 General wiki Page Body Template

```md
---
title: ""
type: note
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Title

## Summary

## Key Points

## Evidence / Sources

- source: `raw/path/to/source`
  claim: ""
  note: ""

## Open Questions

## Related
```

### 3.3 Map Page Template

```md
---
title: ""
type: map
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Map Title

## Scope

## Core Pages

## Source Pages

## Open Questions

## Related Outputs
```

### 3.4 File Naming Rules

LLM-generated wiki, output, script, and config-description files must use lowercase kebab-case.

Allowed:

```text
wiki/flutter-ble-onboarding.md
wiki/llm-wiki-architecture.md
outputs/pkb-technical-report.md
```

Forbidden:

```text
wiki/New Note.md
wiki/untitled.md
wiki/tmp.md
wiki/note.md
```

Original files that users place in `raw/` may keep their original names.

---

## 4. Canonical Tools

### 4.1 Interactive Dependency Selection

Interactive terminal installs must present a keyboard-driven selector for
dependency tools before checking or installing optional tools.

```text
options: qmd, rg, fzf
default: all selected
controls: Up/Down move, Space toggles, Enter accepts
non-interactive behavior: all selected
--no-interactive behavior: all selected
--yes behavior: all selected
--tools behavior: explicit comma-separated selection, all, or none
--dry-run behavior: print plan and do not write files or run network steps
--json behavior: print dry-run or final summary as JSON
```

Python 3.13+ and Git remain bootstrap requirements. Node.js 22+ and npm are
required when qmd is selected.

Skipped tools must be recorded as `skipped` in `.agents/skill-manifest.md` and `.agents/skill-manifest.json`.

`--no-install-tools` prevents automatic installation of missing selectable tools
such as qmd. `--offline` also prevents automatic tool installation and disables
network bootstrap operations. When `--offline` is passed without an explicit
`--skills` selection, upstream Skills default to `none`.

### 4.2 qmd

Canonical qmd source:

```text
repo: https://github.com/tobi/qmd
package: @tobilu/qmd
node: Node.js 22+
preferred install: npm install -g @tobilu/qmd
```

Detection commands:

```bash
command -v qmd || npm install -g @tobilu/qmd
qmd --version
```

When `--no-install-tools` or `--offline` is active, missing qmd must fail with an
actionable error instead of running npm.

Initialization rules:

```bash
qmd collection add "$PWD" --name knowledge-vault
qmd update
qmd embed
```

Indexing rules:

```text
collection name = knowledge-vault
collection path = vault root
index scope = whole-vault index
```

Failure rules when qmd is selected:

```text
qmd is not installed and npm install -g @tobilu/qmd fails -> setup fail
qmd --version fails -> setup fail
qmd collection add fails -> setup fail
qmd update/embed fails -> setup fail
must not silently degrade to rg/fzf only
```

Manifest rules:

```text
record node --version
record npm --version
record qmd --version
record qmd install command
```

If qmd is not selected, skip qmd install, version detection, collection
initialization, update, embed, and generated post-run qmd checks.

### 4.3 rg / fzf

Required when selected:

```bash
command -v rg
command -v fzf
```

Recommended install:

```bash
brew install ripgrep fzf
```

### 4.4 Obsidian

```text
Do not install Obsidian plugins.
Do not generate .obsidian/plugins/.
Do not treat Dataview, Bases, Canvas, or Omnisearch as dependencies.
Obsidian is only the Markdown IDE / viewer.
```

---

## 5. llm-wiki Installer and Skill Installation Rules

### 5.1 llm-wiki Installer Role

`llm-wiki` is the setup wrapper / generator suite name, not a runtime Skill.

Rules:

```text
Do not generate .agents/skills/llm-wiki/SKILL.md.
Do not generate any project-owned SKILL.md.
Use AGENTS.md as the runtime coordinator and canonical agent policy.
Use this guide as the generation-time specification.
Use .agents/skill-manifest.md as the human installation and version record.
Use .agents/skill-manifest.json as the machine-readable mirror.
```

### 5.2 Codex Adapter Rules

Repository root is the vault root and generation target.

Codex must follow the repository policy without requiring a project-owned runtime Skill:

```text
Codex adapter output = .codex/config.toml and optional .codex/hooks/
canonical runtime policy = AGENTS.md
canonical generation spec = this guide
```

Adapter rules:

```text
Do not put long-term rules in .codex/config.toml or hooks.
Do not generate a Codex adapter that makes upstream Skills override AGENTS.md.
Hooks may call only the generated verification scripts.
```

### 5.3 Upstream Skills Installation Rules

Interactive terminal installs must present a second keyboard-driven selector for
upstream Skill sources.

```text
options: Ar9av/obsidian-wiki, kepano/obsidian-skills
default: all selected
controls: Up/Down move, Space toggles, Enter accepts
non-interactive behavior: all selected
--no-interactive behavior: all selected
```

Skipped sources must be recorded as `skipped` in `.agents/skill-manifest.md` and `.agents/skill-manifest.json`.

#### 5.3.1 Ar9av/obsidian-wiki

Install pinned upstream Skills when selected.

```text
repo: https://github.com/Ar9av/obsidian-wiki
pinned commit: 347e85704c52474d13470a3919e4a5cd7e3809cb
install target: .agents/skills/upstream/Ar9av/
selection: all discovered upstream skills at pinned commit
```

Candidate directories to inspect:

```text
.skills/
skills/
```

Rules:

```text
Install as many as are discovered.
Do not maintain a local allowlist.
Do not rewrite, fork, summarize, or generate local substitutes for missing third-party Skills.
If the repo does not exist, clone fails, or no Skill directory is discovered -> setup fail.
Record repo URL, pinned commit SHA, resolved commit SHA, install date, and installed Skill count.
```

#### 5.3.2 kepano/obsidian-skills

Install pinned upstream Skills when selected.

```text
repo: https://github.com/kepano/obsidian-skills
pinned commit: 553ef99aa3306dd23f268e1ba9af752577684f69
install target: .agents/skills/upstream/kepano/
selection: all discovered upstream skills at pinned commit
```

Candidate directories to inspect:

```text
.skills/
skills/
```

Rules:

```text
Install as many as are discovered.
Do not maintain a local allowlist.
Do not install Obsidian plugins.
Do not rewrite, fork, summarize, or generate local substitutes for missing third-party Skills.
If the repo does not exist, clone fails, or no Skill directory is discovered -> setup fail.
Record repo URL, pinned commit SHA, resolved commit SHA, install date, and installed Skill count.
```

---

## 6. Skill Manifest Generation Spec

Generate:

```text
.agents/skill-manifest.md
.agents/skill-manifest.json
```

Must record:

```md
# Skill Manifest

Generated: YYYY-MM-DD

## Canonical Policy

- AGENTS.md is the canonical agent policy.
- This guide is the canonical generation spec.
- Agent adapters are derived outputs.

## qmd

| Field | Value |
|---|---|
| Source | https://github.com/tobi/qmd |
| Package | @tobilu/qmd |
| Install Command | npm install -g @tobilu/qmd |
| Result | installed \| skipped |
| Version | <qmd --version output> |
| Node Version | <node --version output> |
| npm Version | <npm --version output> |
| Collection | knowledge-vault |
| Collection Path | <repository root> |
| Indexed Scope | repository root |

## Tools

| Tool | Version | Result |
|---|---|---|
| qmd | ... | installed \| skipped |
| rg | ... | installed \| skipped |
| fzf | ... | installed \| skipped |

## Upstream Skills

| Repo | Pinned Commit SHA | Resolved Commit SHA | Install Date | Installed Skills | Result |
|---|---|---|---|---:|---|
| https://github.com/Ar9av/obsidian-wiki | ... | ... | YYYY-MM-DD | ... | installed \| skipped |
| https://github.com/kepano/obsidian-skills | ... | ... | YYYY-MM-DD | ... | installed \| skipped |

## llm-wiki Installer

| Field | Value |
|---|---|
| Name | llm-wiki-installer |
| Version | <installer version> |
| Role | setup wrapper / generator suite |
| Runtime Coordinator | AGENTS.md |
| Project-Owned Skill | not generated |

## Generated Files

- AGENTS.md
- README.md
- wiki/index.md
- wiki/log.md
- .scripts/postrun.sh
- .scripts/check-index-log.sh
- .codex/config.toml
- .agents/skill-manifest.md
- .agents/skill-manifest.json
- .gitignore
```

The JSON manifest must contain the same installer, qmd, tool, upstream source,
pin, resolved commit, result, and generated-file information in a
machine-readable structure.

---

## 7. AGENTS.md Generation Template

`AGENTS.md` must be generated at the repository root.

````md
---
vault_type: llm-native-obsidian-pkb
schema_version: 1
generated_by: llm-wiki-generation-guide
generated: YYYY-MM-DD
canonical_policy: true
---

# AGENTS.md

This repository is an LLM-native Obsidian Markdown knowledge vault.

The goal is to maintain a durable Markdown wiki compiled from user-approved raw sources, not to generate one-off chat answers.

## Canonical policy

- This file is the canonical agent policy.
- The llm-wiki generation guide is the canonical generation spec.
- Agent adapters are derived outputs.
- If an upstream skill conflicts with this file, this file wins.

## Core architecture

- `inbox/` is the low-friction unprocessed capture buffer. Agents may write to it.
- `raw/` contains user-approved source material. Agents treat it as read-only by default.
- `wiki/` contains compiled long-term Markdown knowledge.
- `wiki/maps/` contains topic, project, research, and learning maps.
- `wiki/index.md` is the global machine-readable and human-readable index.
- `wiki/log.md` is the append-only audit ledger.
- `outputs/` contains current final deliverables and exports.
- `archive/` contains temporarily inactive old outputs only.
- `.agents/skills/upstream/` contains installed upstream skills.
- `.agents/skill-manifest.md` and `.agents/skill-manifest.json` record installed skills and tool versions.
- `.codex/hooks/` contains LLM hooks.
- `.scripts/` contains fixed project scripts.

## Forbidden paths

Do not create:

- `.codex/rules/`
- `.obsidian/plugins/`
- `projects/`
- `areas/`
- `resources/`
- `core/`
- `work/`
- `tests/`
- `fixtures/`
- `examples/`

## Skill policy

- `llm-wiki-installer` is the setup wrapper / generator suite name, not a runtime Skill.
- Install pinned upstream skills from selected upstream sources.
- Record unselected upstream sources as skipped.
- Copy upstream third-party skills as-is.
- Do not rewrite, fork, summarize, or create local substitutes for missing third-party upstream skills.
- Do not generate a project-owned `SKILL.md`.
- Upstream orchestration, policy, or controller Skills may be installed as upstream artifacts, but must not override or replace `AGENTS.md`.
- Record upstream pinned commit SHAs, resolved commit SHAs, and installed Skill counts in `.agents/skill-manifest.md` and `.agents/skill-manifest.json`.

## qmd policy

- If qmd was selected during installation, use `tobi/qmd`.
- Package: `@tobilu/qmd`.
- Install automatically with `npm install -g @tobilu/qmd` if selected qmd is missing.
- Collection name: `knowledge-vault`.
- Collection path: repository root.
- Index scope: the whole vault.
- If selected qmd installation, version detection, collection initialization, update, or embed fails, stop and report failure.
- If qmd was not selected, do not assume qmd commands are available.

## Default retrieval order

When answering questions about the vault:

1. Read `wiki/index.md`.
2. Read relevant files under `wiki/maps/`.
3. Read relevant wiki pages.
4. Use installed tools recorded in `.agents/skill-manifest.md` as retrieval accelerators.
5. Read `raw/` only for verification, missing evidence, or explicit source inspection.

## Default workflow

- Capture new unprocessed material into `inbox/`.
- Move `inbox/` material to `raw/` only when the user explicitly triggers it or performs it manually.
- Compile `raw/` into `wiki/` within a clear task scope.
- Send valuable answers or outputs back through `inbox/` before they become durable wiki knowledge.
- Export final deliverables to `outputs/`.
- Move inactive outputs to `archive/`.

## raw/ boundary

- Do not capture/import directly into `raw/`.
- Do not modify, move, or delete `raw/` unless the user explicitly authorizes it.
- Any `raw/` change must update `wiki/log.md`.
- `ALLOW_RAW_CHANGE=1` is only a script-level explicit switch; it is not user authorization.

## Wiki page template

New `wiki/*.md` pages should use:

```yaml
---
title: ""
type: source | entity | concept | comparison | synthesis | question | map | decision | playbook | note
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Recommended body:

```md
# Title

## Summary

## Key Points

## Evidence / Sources

- source: `raw/path/to/source`
  claim: ""
  note: ""

## Open Questions

## Related
```

## Map template

New `wiki/maps/*.md` pages should use:

```yaml
---
title: ""
type: map
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Recommended body:

```md
# Map Title

## Scope

## Core Pages

## Source Pages

## Open Questions

## Related Outputs
```

## Naming rules

- LLM-generated wiki, output, script, and config-description files must use lowercase kebab-case.
- User-provided `raw/` filenames may keep their original names.

## index/log rules

Fail and fix if:

- `wiki/` content changed but `wiki/index.md` was not updated.
- `wiki/` content changed but `wiki/log.md` was not updated.
- Any file was deleted, moved, or renamed but `wiki/log.md` was not updated.
- Any `raw/` file changed but `wiki/log.md` was not updated.

## Log entry schemas

Use append-only entries under the current date.

### ingest

```md
- type: ingest
  scope: raw/source -> wiki/page.md
  reason: ""
  review: self-reviewed
  impact:
    index_updated: true
    references_checked: true
  files:
    - raw/source
    - wiki/page.md
    - wiki/index.md
```

### fileback

```md
- type: fileback
  scope: answer/output -> inbox/path.md
  reason: ""
  review: self-reviewed
  impact:
    index_updated: not-needed
    references_checked: not-needed
  files:
    - inbox/path.md
```

### delete

```md
- type: delete
  scope: path/to/file.md
  reason: ""
  authorized_by: user | explicit-task
  review: self-reviewed
  impact:
    index_updated: true | false | not-needed
    references_checked: true
  files:
    - path/to/file.md
```

### move

```md
- type: move
  scope: old/path.md -> new/path.md
  reason: ""
  authorized_by: user | explicit-task
  review: self-reviewed
  impact:
    index_updated: true | false | not-needed
    references_checked: true
  files:
    - old/path.md
    - new/path.md
```

### archive-output

```md
- type: archive-output
  scope: outputs/file.md -> archive/file.md
  reason: ""
  review: self-reviewed
  impact:
    index_updated: not-needed
    references_checked: true
  files:
    - outputs/file.md
    - archive/file.md
```

### schema-update

```md
- type: schema-update
  scope: path/to/schema-or-script
  reason: ""
  review: self-reviewed
  impact:
    index_updated: not-needed
    references_checked: true
  files:
    - path/to/schema-or-script
```

## Required post-write checks

After any write operation, run:

```bash
bash .scripts/postrun.sh
bash .scripts/check-index-log.sh
git diff --stat
git diff
```

If a check fails, fix the issue and rerun the checks.
````

---

## 8. `.scripts/postrun.sh` Generation Template

Generate path:

```text
.scripts/postrun.sh
```

Content:

```bash
#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

changed_paths() {
  git diff --name-only -- "$@" || true
  git diff --cached --name-only -- "$@" || true
  git ls-files --others --exclude-standard -- "$@" || true
}

echo "== Post-run checks =="

if [ -d ".codex/rules" ]; then
  fail ".codex/rules/ must not exist."
fi

if [ -d ".obsidian/plugins" ]; then
  fail ".obsidian/plugins/ must not exist."
fi

if git status --porcelain=v1 -- .codex/rules .obsidian/plugins | grep -q .; then
  fail "Forbidden paths are present in git status."
fi

unauthorized_skill_paths="$(
  find . \
    \( -path './.git' -o -path './node_modules' -o -path './.cache' \) -prune -o \
    -name SKILL.md -print \
    | grep -v -E '^\./\.agents/skills/upstream/[^/]+/.+/SKILL\.md$' \
    || true
)"

if [ -n "$unauthorized_skill_paths" ]; then
  printf "%s\n" "$unauthorized_skill_paths" >&2
  fail "Unauthorized SKILL.md found outside .agents/skills/upstream/<repo>/<skill-name>/."
fi

bad_generated_names="$(
  changed_paths wiki outputs .scripts .codex \
    | grep -E '(^|/)(New Note|untitled|tmp|note)\.md$|[[:space:]]|[A-Z]' \
    || true
)"

if [ -n "$bad_generated_names" ]; then
  printf "%s\n" "$bad_generated_names" >&2
  fail "Generated wiki/output/script/config-description filenames must use lowercase kebab-case."
fi

if git status --porcelain=v1 | grep -q .; then
  echo "-- Changed files --"
  git status --short
fi

if changed_paths raw | grep -q .; then
  if [ "${ALLOW_RAW_CHANGE:-0}" != "1" ]; then
    fail "raw/ changed. Set ALLOW_RAW_CHANGE=1 only when the user explicitly authorized this raw change."
  fi

  if ! changed_paths wiki/log.md | grep -q .; then
    fail "raw/ changed but wiki/log.md was not updated."
  fi
fi

{{QMD_POSTRUN_CHECK}}

echo "-- Diff stat --"
git diff --stat || true

echo "Post-run OK. Review diff before commit."
```

---

## 9. `.scripts/check-index-log.sh` Generation Template

Generate path:

```text
.scripts/check-index-log.sh
```

Content:

```bash
#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

tmp_changed="$(mktemp)"
trap 'rm -f "$tmp_changed"' EXIT

{
  git diff --name-only || true
  git diff --cached --name-only || true
  git ls-files --others --exclude-standard || true
} | sed '/^$/d' | sort -u > "$tmp_changed"

has_changed() {
  grep -E "$1" "$tmp_changed" >/dev/null
}

if [ ! -s "$tmp_changed" ]; then
  echo "No changed files."
  exit 0
fi

wiki_content_changed="$(
  grep -E '^wiki/' "$tmp_changed" \
    | grep -v -E '^wiki/index\.md$|^wiki/log\.md$' \
    || true
)"

if [ -n "$wiki_content_changed" ]; then
  has_changed '^wiki/index\.md$' || fail "wiki content changed but wiki/index.md was not updated."
  has_changed '^wiki/log\.md$' || fail "wiki content changed but wiki/log.md was not updated."
fi

raw_changed="$(
  grep -E '^raw/' "$tmp_changed" \
    || true
)"

if [ -n "$raw_changed" ]; then
  has_changed '^wiki/log\.md$' || fail "raw/ changed but wiki/log.md was not updated."
fi

file_structure_changed="$(
  {
    git diff --name-status --diff-filter=DRC || true
    git diff --cached --name-status --diff-filter=DRC || true
    git status --porcelain=v1 | grep -E '^( D|D |R |RM|RD| C|C )' || true
  } | sed '/^$/d'
)"

if [ -n "$file_structure_changed" ]; then
  has_changed '^wiki/log\.md$' || fail "file deleted, moved, renamed, or copied but wiki/log.md was not updated."
fi

bad_generated_names="$(
  grep -E '^(wiki|outputs|\.scripts|\.codex)/' "$tmp_changed" \
    | grep -E '(^|/)(New Note|untitled|tmp|note)\.md$|[[:space:]]|[A-Z]' \
    || true
)"

if [ -n "$bad_generated_names" ]; then
  printf "%s\n" "$bad_generated_names" >&2
  fail "Generated wiki/output/script/config-description filenames must use lowercase kebab-case."
fi

if has_changed '^wiki/log\.md$'; then
  if {
      git diff --unified=0 -- wiki/log.md || true
      git diff --cached --unified=0 -- wiki/log.md || true
    } \
    | grep -E '^\+.*type: (ingest|fileback|delete|move|archive-output|schema-update|rename|lint|index-update|map-update)' >/dev/null; then
    :
  else
    fail "wiki/log.md changed but no recognized log entry type was added."
  fi
fi

echo "Index/log checks OK."
```

---

## 10. `.gitignore` Generation Template

```gitignore
.DS_Store
Thumbs.db

# Obsidian volatile workspace
.obsidian/workspace.json
.obsidian/workspaces.json
.obsidian/workspace*.json
.obsidian/cache
.obsidian/plugins/

# Node / Python
node_modules/
.venv/
.cache/
dist/
tmp/

# Temporary setup tests
.tmp-setup-tests/
.tmp-test-vault/

# Derived indexes
.index/
.vector/
.faiss/
.qmd/

# Secrets
.env
.env.*
*.key
*.pem
id_rsa
id_ed25519
.codex/auth.json
```

---

## 11. README.md Generation Template

````md
# Knowledge Vault

This is an LLM-native Obsidian Markdown knowledge vault.

## Design idea

- `inbox/` is the capture buffer.
- `raw/` is the user-approved evidence layer.
- `wiki/` is the compiled long-term Markdown knowledge layer.
- `wiki/index.md` is the global entry.
- `wiki/maps/` contains topic and project maps.
- `wiki/log.md` is the append-only audit ledger.
- `outputs/` contains current deliverables.
- `archive/` contains inactive old outputs.

## Directory guide

```text
inbox/     unprocessed input
raw/       user-approved immutable source material
wiki/      compiled long-term Markdown knowledge
outputs/   final deliverables
archive/   inactive old outputs only
```

## Common operations

### Capture input

Put unprocessed material into:

```text
inbox/
```

### Promote input to raw

Ask the agent to promote selected `inbox/` files to `raw/`, or move them manually.

### Compile raw into wiki

Ask the agent to ingest a specific file or folder:

```text
Compile raw/example.pdf into wiki.
```

The agent must update:

```text
wiki/index.md
wiki/log.md
```

### Search

```bash
qmd search "keyword"
rg "keyword" wiki raw inbox outputs archive
rg --files | fzf
```

### Review

```bash
bash .scripts/postrun.sh
bash .scripts/check-index-log.sh
git diff --stat
git diff
```

### Commit

```bash
git add .
git commit -m "Update knowledge vault"
```
````

---

## 12. `.codex/config.toml` Generation Requirements

An empty file or minimal config is acceptable, but it must not contain agent-specific rules that override AGENTS.md.

```toml
# Codex project config.
# Canonical policy lives in AGENTS.md.
```

---

## 13. Hook Generation Rules

Directory:

```text
.codex/hooks/
```

Rules:

```text
Hooks are only LLM triggers.
Project-wide logic goes in .scripts/.
Do not generate .codex/rules/.
```

If a hook is generated, it may only call:

```bash
bash .scripts/postrun.sh
bash .scripts/check-index-log.sh
```

---

## 14. Unit Test Rules

The setup wrapper must run full verification:

```text
1. Create a test repository root in a temporary directory.
2. Generate all fixed artifacts.
3. Verify the directory structure.
4. Verify forbidden paths do not exist.
5. Verify AGENTS.md contains the required frontmatter, log schemas, and qmd policy.
6. Verify README.md contains the operations guide, design idea, and directory explanation.
7. Verify .scripts/postrun.sh is executable.
8. Verify .scripts/check-index-log.sh is executable.
9. Verify qmd is installed automatically when missing and can initialize a collection.
10. Verify git diff/check logic can run.
11. Delete test files and test artifacts after tests pass.
```

The final repository must not retain:

```text
tests/
fixtures/
examples/
```

Python installer unit tests should use pytest with project-level configuration in `pyproject.toml`; install test dependencies through a local `.venv` and `requirements-dev.txt`; avoid per-test `sys.path` mutation and `unittest` boilerplate.

---

## 15. Repeatable Generation Rules

The generator must follow:

```text
fixed directory structure
fixed filenames
fixed templates
fixed qmd collection name
fixed script paths
fixed AGENTS.md structure
fixed README.md structure
fixed Markdown and JSON manifest structure
fixed review output
pinned upstream Skill versions recorded in the manifests
no project-owned runtime Skill generated
```

Forbidden:

```text
adding directories based on preference
creating unauthorized local Skill substitutes
creating project-owned SKILL.md
rewriting upstream skills into local skills
generating Obsidian plugin config
generating .codex/rules/
creating example wiki content
creating tests/ fixtures/ examples/
```

---

## 16. Final Verification

Before final output, confirm:

```text
AGENTS.md exists
README.md exists
wiki/index.md exists
wiki/log.md exists
.agents/skill-manifest.md exists
.agents/skill-manifest.json exists
.scripts/postrun.sh exists and executable
.scripts/check-index-log.sh exists and executable
.codex/rules/ does not exist
.obsidian/plugins/ does not exist
no project-owned SKILL.md exists
no unauthorized local Skill substitute exists
qmd is installed
qmd collection is initialized
all upstream skills were installed from Ar9av/obsidian-wiki
all upstream skills were installed from kepano/obsidian-skills
temporary tests and test outputs were deleted
```

Review output format:

```text
generated files
installed upstream skills
tool versions
checks run
failures, if any
git diff --stat
```
