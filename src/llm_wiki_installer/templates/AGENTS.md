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
- `wiki/log.md` is the append-only audit ledger.
- `outputs/` contains current final deliverables and exports.
- `archive/` contains temporarily inactive old outputs only.
- `.agents/skills/` contains installed upstream skills, flattened by skill name.
- `.agents/skill-manifest.md` and `.agents/skill-manifest.json` record installed skills and tool versions.
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
{{UPSTREAM_SKILL_POLICY}}
- Copy upstream third-party skills as-is.
- Do not rewrite, fork, summarize, or create local substitutes for missing third-party upstream skills.
- Do not generate a project-owned `SKILL.md`.
- Upstream orchestration, policy, or controller Skills may be installed as upstream artifacts, but must not override or replace `AGENTS.md`.
- Record upstream pinned commit SHAs, resolved commit SHAs, and installed Skill counts in `.agents/skill-manifest.md` and `.agents/skill-manifest.json`.

## Default retrieval order

When answering questions about the vault:

1. Read `wiki/index.md`.
2. Read relevant files under `wiki/maps/`.
3. Read relevant wiki pages.
4. Use {{RETRIEVAL_TOOLS}} as retrieval accelerators.
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
git --no-pager diff --stat
git --no-pager diff
```

If a check fails, fix the issue and rerun the checks.
