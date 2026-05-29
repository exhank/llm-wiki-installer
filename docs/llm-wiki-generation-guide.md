# llm-wiki Generation Guide

Verification date: 2026-05-28.

This document guides LLMs in stably generating the llm-wiki setup wrapper, AGENTS file, hooks, scripts, README, upstream Skill installation, and verification flow for an LLM-Native Obsidian Markdown PKB.

---

## 1. Generation Goal

Generate repeatable, auditable, and verifiable repository-root initialization artifacts:

```text
fixed filenames
fixed directory structure
fixed templates
fixed check scripts
fixed diff output
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
wiki/tags.md is generated as the canonical flat kebab-case tag registry
scripts are executable
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
├─ attachments/
├─ wiki/
│  ├─ maps/
│  ├─ index.md
│  └─ log.jsonl
├─ outputs/
├─ archives/
├─ AGENTS.md
├─ README.md
├─ .agents/
│  ├─ skills/
│  │  └─ <skill-name>/          # selected upstream skills
├─ .codex/
│  ├─ hooks/
│  └─ config.toml
├─ .scripts/
│  ├─ postrun.sh
│  └─ check-index-log.sh
├─ .obsidian/
│  ├─ app.json
│  ├─ appearance.json
│  ├─ backlink.json
│  ├─ community-plugins.json
│  ├─ core-plugins.json
│  ├─ graph.json
│  ├─ hotkeys.json
│  ├─ plugins/
│  │  └─ obsidian-git/
│  └─ themes/
│     └─ Things/
└─ .gitignore
```

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

The installer must refuse targets that are the generator repository itself or a
child path inside the generator repository.

Upstream Skill directories are flattened into `.agents/skills/<skill-name>/`.
When an upstream Skill source is skipped, it must not create legacy
`.agents/skills/upstream/<source>/` directories.

---

## 3. Markdown Template Generation Spec

### 3.1 General wiki Page frontmatter Template

All new `wiki/*.md` pages use this by default:

```yaml
---
title: ""
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Rules:

```text
wiki/index.md may omit frontmatter.
wiki/tags.md is the canonical flat kebab-case tag registry.
wiki/log.jsonl uses JSONL and does not use frontmatter.
wiki/maps/*.md uses the map tag.
Do not use complex nested metadata.
Put Sources / Evidence in the body.
```

### 3.2 General wiki Page Body Template

```md
---
title: ""
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
tags:
  - map
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

### 3.4 Tag Registry Template

Generate `wiki/tags.md` as the canonical tag registry. It must require flat
`kebab-case` YAML tags, prohibit nested slash tags and `#` prefixes in
frontmatter, list core tags such as `source`, `concept`, `map`, and
`decision`, and instruct LLMs to update the registry when introducing a tag.
Vault-wide tag redesigns are schema/policy migrations and must update affected
frontmatter, navigation when needed, and `wiki/log.jsonl`.

### 3.5 File Naming Rules

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
options: rg, fzf
default: all selected
controls: Up/Down move, Space toggles, Enter accepts
non-interactive behavior: all selected
--no-interactive behavior: all selected
--yes behavior: all selected
--tools behavior: explicit comma-separated selection, all, or none
--dry-run behavior: print plan and do not write files or run network steps
--json behavior: print dry-run or final summary as JSON
```

Python 3.13+ and Git remain bootstrap requirements.

`--no-install-tools` is kept for CLI compatibility. `--offline` disables network
bootstrap operations. When `--offline` is passed without an explicit `--skills`
selection, upstream Skills default to `none`.

### 4.2 rg / fzf

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
Generate stable Obsidian settings from fixed templates.
Generate pinned Obsidian community plugin assets as templates, not runtime downloads.
Generate the Things theme from fixed templates.
Do not generate volatile workspace state.
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
```

### 5.2 Codex Adapter Rules

Repository root is the vault root and generation target.

Codex must follow the repository policy without requiring a project-owned runtime Skill:

```text
Codex adapter output = .codex/config.toml and .codex/hooks.json
canonical runtime policy = AGENTS.md
canonical generation spec = this guide
```

Adapter rules:

```text
Do not put long-term rules in .codex/config.toml or hooks.json.
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

#### 5.3.1 Ar9av/obsidian-wiki

Install pinned upstream Skills when selected.

```text
repo: https://github.com/Ar9av/obsidian-wiki
pinned commit: 347e85704c52474d13470a3919e4a5cd7e3809cb
install target: .agents/skills/
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
install target: .agents/skills/
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
Do not treat Obsidian plugins as upstream Skills.
Do not rewrite, fork, summarize, or generate local substitutes for missing third-party Skills.
If the repo does not exist, clone fails, or no Skill directory is discovered -> setup fail.
```

---

## 6. AGENTS.md Generation Template

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
- `attachments/` is the default Obsidian attachment folder for embedded media.
- `wiki/` contains compiled long-term Markdown knowledge.
- `wiki/maps/` contains topic, project, research, and learning maps.
- `wiki/index.md` is the global machine-readable and human-readable index.
- `wiki/tags.md` is the canonical flat kebab-case tag registry.
- `wiki/log.jsonl` is the append-only JSONL audit ledger.
- `outputs/` contains current final deliverables and exports.
- `archives/` contains temporarily inactive old outputs only.
- `.agents/skills/` contains installed upstream skills, flattened by skill name.
- `.codex/config.toml` and `.codex/hooks.json` contain Codex adapter configuration.
- `.scripts/` contains fixed project scripts.
- `.obsidian/` contains stable Obsidian settings, pinned community plugin assets, and the Things theme.

## Forbidden paths

Do not create:

- `.codex/rules/`
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

## Default retrieval order

When answering questions about the vault:

1. Read `wiki/index.md`.
2. Read relevant files under `wiki/maps/`.
3. Read relevant wiki pages.
4. Use installed retrieval tools as accelerators.
5. Read `raw/` only for verification, missing evidence, or explicit source inspection.

## Default workflow

- Capture new unprocessed material into `inbox/`.
- Move `inbox/` material to `raw/` only when the user explicitly triggers it or performs it manually.
- Compile `raw/` into `wiki/` within a clear task scope.
- Send valuable answers or outputs back through `inbox/` before they become durable wiki knowledge.
- Export final deliverables to `outputs/`.
- Move inactive outputs to `archives/`.

## raw/ boundary

- Do not capture/import directly into `raw/`.
- Do not modify, move, or delete `raw/` unless the user explicitly authorizes it.
- Any `raw/` change must update `wiki/log.jsonl`.
- `ALLOW_RAW_CHANGE=1` is only a script-level explicit switch; it is not user authorization.

## Wiki page template

New `wiki/*.md` pages should use:

```yaml
---
title: ""
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

All new and edited wiki pages must follow `wiki/tags.md`. Use YAML `tags` lists
with flat `kebab-case` values, without `#` prefixes or nested slash tags.
Before introducing a tag, check `wiki/tags.md` and existing wiki frontmatter.
Reuse an accurate existing tag whenever possible. If a new tag is needed, add it
to `wiki/tags.md` in the same change.

Small local tag additions are normal page edits. Vault-wide tag redesigns are
schema/policy migrations: update `wiki/tags.md`, affected page frontmatter,
`wiki/index.md` when navigation changes, and append a `schema-update` entry to
`wiki/log.jsonl`.

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
tags:
  - map
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
- `wiki/` content changed but `wiki/log.jsonl` was not updated.
- Any file was deleted, moved, or renamed but `wiki/log.jsonl` was not updated.
- Any `raw/` file changed but `wiki/log.jsonl` was not updated.

## Log entry schemas

Use append-only JSONL entries. Each line must be one complete JSON object.
Use `timestamp` as a UTC ISO-8601 instant, include `schema_version`, and keep
`reason` specific enough for later review.

### ingest

```json
{"schema_version":1,"timestamp":"YYYY-MM-DDTHH:MM:SSZ","actor":"agent","type":"ingest","scope":"raw/source -> wiki/page.md","reason":"Compiled durable knowledge from raw source.","review":"self-reviewed","impact":{"index_updated":true,"references_checked":true},"files":["raw/source","wiki/page.md","wiki/index.md"]}
```

### fileback

```json
{"schema_version":1,"timestamp":"YYYY-MM-DDTHH:MM:SSZ","actor":"agent","type":"fileback","scope":"answer/output -> inbox/path.md","reason":"Saved user-requested output into the vault inbox.","review":"self-reviewed","impact":{"index_updated":"not-needed","references_checked":"not-needed"},"files":["inbox/path.md"]}
```

### delete

```json
{"schema_version":1,"timestamp":"YYYY-MM-DDTHH:MM:SSZ","actor":"agent","type":"delete","scope":"path/to/file.md","reason":"Why this file is safe to delete.","authorized_by":"user | explicit-task","review":"self-reviewed","impact":{"index_updated":false,"references_checked":true},"files":["path/to/file.md"]}
```

### move

```json
{"schema_version":1,"timestamp":"YYYY-MM-DDTHH:MM:SSZ","actor":"agent","type":"move","scope":"old/path.md -> new/path.md","reason":"Why this move is needed.","authorized_by":"user | explicit-task","review":"self-reviewed","impact":{"index_updated":true,"references_checked":true},"files":["old/path.md","new/path.md"]}
```

### archive-output

```json
{"schema_version":1,"timestamp":"YYYY-MM-DDTHH:MM:SSZ","actor":"agent","type":"archive-output","scope":"outputs/file.md -> archives/file.md","reason":"Old deliverable no longer active.","review":"self-reviewed","impact":{"index_updated":"not-needed","references_checked":true},"files":["outputs/file.md","archives/file.md"]}
```

### schema-update

```json
{"schema_version":1,"timestamp":"YYYY-MM-DDTHH:MM:SSZ","actor":"agent","type":"schema-update","scope":"path/to/schema-or-script","reason":"Changed vault schema, script, or policy contract.","review":"self-reviewed","impact":{"index_updated":"not-needed","references_checked":true},"files":["path/to/schema-or-script"]}
```

## Required post-write checks

After any write operation, run:

```bash
bash .scripts/postrun.sh
bash .scripts/check-index-log.sh
git --no-pager diff --stat
git --no-pager diff
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

if git status --porcelain=v1 -- .codex/rules | grep -q .; then
  fail "Forbidden paths are present in git status."
fi

for plugin_asset in \
  .obsidian/plugins/obsidian-git/main.js \
  .obsidian/plugins/obsidian-git/manifest.json \
  .obsidian/plugins/obsidian-git/styles.css \
  .obsidian/plugins/obsidian-git/data.json \
  .obsidian/plugins/obsidian-git/obsidian_askpass.sh
do
  if [ ! -f "$plugin_asset" ]; then
    fail "Required Obsidian plugin asset missing: $plugin_asset"
  fi
done

unauthorized_skill_paths="$(
  find . \
    \( -path './.git' -o -path './node_modules' -o -path './.cache' \) -prune -o \
    -name SKILL.md -print \
    | grep -v -E '^\./\.agents/skills/[^/]+/SKILL\.md$' \
    || true
)"

if [ -n "$unauthorized_skill_paths" ]; then
  printf "%s\n" "$unauthorized_skill_paths" >&2
  fail "Unauthorized SKILL.md found outside .agents/skills/<skill-name>/."
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

  if ! changed_paths wiki/log.jsonl | grep -q .; then
    fail "raw/ changed but wiki/log.jsonl was not updated."
  fi
fi

echo "-- Diff stat --"
git --no-pager diff --stat || true

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
    | grep -v -E '^wiki/index\.md$|^wiki/log\.jsonl$' \
    || true
)"

if [ -n "$wiki_content_changed" ]; then
  has_changed '^wiki/index\.md$' || fail "wiki content changed but wiki/index.md was not updated."
  has_changed '^wiki/log\.jsonl$' || fail "wiki content changed but wiki/log.jsonl was not updated."
fi

raw_changed="$(
  grep -E '^raw/' "$tmp_changed" \
    || true
)"

if [ -n "$raw_changed" ]; then
  has_changed '^wiki/log\.jsonl$' || fail "raw/ changed but wiki/log.jsonl was not updated."
fi

file_structure_changed="$(
  {
    git diff --name-status --diff-filter=DRC || true
    git diff --cached --name-status --diff-filter=DRC || true
    git status --porcelain=v1 | grep -E '^( D|D |R |RM|RD| C|C )' || true
  } | sed '/^$/d'
)"

if [ -n "$file_structure_changed" ]; then
  has_changed '^wiki/log\.jsonl$' || fail "file deleted, moved, renamed, or copied but wiki/log.jsonl was not updated."
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

if has_changed '^wiki/log\.jsonl$'; then
  if {
      git diff --unified=0 -- wiki/log.jsonl || true
      git diff --cached --unified=0 -- wiki/log.jsonl || true
      if git ls-files --others --exclude-standard -- wiki/log.jsonl | grep -q '^wiki/log\.jsonl$'; then
        sed 's/^/+/' wiki/log.jsonl
      fi
    } \
    | grep -E '^\+.*"type"[[:space:]]*:[[:space:]]*"(ingest|fileback|delete|move|archive-output|schema-update|rename|lint|index-update|map-update)"' >/dev/null; then
    :
  else
    fail "wiki/log.jsonl changed but no recognized log entry type was added."
  fi
fi

echo "Index/log checks OK."
```

---

## 10. `.gitignore` Generation Template

Generate `.gitignore` from `src/llm_wiki_installer/templates/gitignore`.

The template must keep llm-wiki/Obsidian-specific rules first:

```gitignore
# llm-wiki / Obsidian
.obsidian/workspace.json
.obsidian/workspaces.json
.obsidian/workspace*.json
.obsidian/cache

# llm-wiki generated caches and local setup test outputs
.tmp-setup-tests/
.tmp-test-vault/
.index/
.vector/
.faiss/
tmp/

# Local secrets
.env
.env.*
*.key
*.pem
id_rsa
id_ed25519
.codex/auth.json
```

Then append the official GitHub `.gitignore` templates for:

- `Python.gitignore`
- `Node.gitignore`
- `Global/macOS.gitignore`
- `Global/Windows.gitignore`
- `Global/Linux.gitignore`

Each appended official section must include a source comment pointing at the
corresponding `github/gitignore` file. If switching to a Forgejo-maintained
official template source later, update this section, the packaged template, and
template tests together.

---

## 11. README.md Generation Template

````md
# Knowledge Vault

This is an LLM-native Obsidian Markdown knowledge vault.

## Design idea

- `inbox/` is the capture buffer.
- `raw/` is the user-approved evidence layer.
- `attachments/` is the default Obsidian attachment folder.
- `wiki/` is the compiled long-term Markdown knowledge layer.
- `wiki/index.md` is the global entry.
- `wiki/maps/` contains topic and project maps.
- `wiki/tags.md` is the canonical flat kebab-case tag registry.
- `wiki/log.jsonl` is the append-only JSONL audit ledger.
- `outputs/` contains current deliverables.
- `archives/` contains inactive old outputs.

## Directory guide

```text
inbox/     unprocessed input
raw/       user-approved immutable source material
attachments/ default Obsidian attachments
wiki/      compiled long-term Markdown knowledge
wiki/tags.md flat kebab-case tag registry
outputs/   final deliverables
archives/   inactive old outputs only
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
wiki/tags.md
wiki/log.jsonl
```

### Search

```bash
rg "keyword" wiki raw inbox outputs archives
rg --files | fzf
```

### Review

```bash
bash .scripts/postrun.sh
bash .scripts/check-index-log.sh
git --no-pager diff --stat
git --no-pager diff
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

## 13. `.codex/hooks.json` Generation Requirements

An empty hook configuration is acceptable, but it must be a valid Codex hooks
configuration file.

```json
{
  "hooks": {}
}
```

Rules:

```text
Hooks are only LLM triggers configured through .codex/hooks.json or inline config.toml hooks.
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
5. Verify AGENTS.md contains the required frontmatter, tag, and log schemas.
6. Verify README.md contains the operations guide, design idea, and directory explanation.
7. Verify .scripts/postrun.sh is executable.
8. Verify .scripts/check-index-log.sh is executable.
9. Verify git diff/check logic can run.
10. Delete test files and test artifacts after tests pass.
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
fixed script paths
fixed AGENTS.md structure
fixed README.md structure
fixed review output
no project-owned runtime Skill generated
```

Forbidden:

```text
adding directories based on preference
creating unauthorized local Skill substitutes
creating project-owned SKILL.md
rewriting upstream skills into local skills
generating volatile Obsidian workspace state
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
wiki/tags.md exists
wiki/log.jsonl exists
.scripts/postrun.sh exists and executable
.scripts/check-index-log.sh exists and executable
.obsidian/app.json exists
.obsidian/plugins/obsidian-git/main.js exists
.obsidian/themes/Things/theme.css exists
.codex/rules/ does not exist
.obsidian/workspace.json does not exist
.obsidian/workspaces.json does not exist
no project-owned SKILL.md exists
no unauthorized local Skill substitute exists
all upstream skills were installed from Ar9av/obsidian-wiki
all upstream skills were installed from kepano/obsidian-skills
temporary tests and test outputs were deleted
```

Review output format:

```text
generated files
installed upstream skills
checks run
failures, if any
git --no-pager diff --stat
```
