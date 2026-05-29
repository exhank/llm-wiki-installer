# Workflow Schema

Use this schema for routine vault maintenance and for task planning before
writing generated wiki content.

## Default workflow

- Capture: save new unprocessed material into `inbox/`; do not write directly to `raw/`.
- Ingest: compile user-approved `raw/` sources into `wiki/` within a clear task scope.
- Maintain `wiki/index.md`, `wiki/tags.md`, and `wiki/log.jsonl` when wiki structure, tags, or audited files change.
- Export: write current final deliverables to `outputs/`.
- Archive: move inactive deliverables to `archives/` and append `wiki/log.jsonl`.

## Long context retrieval

- Start with `wiki/index.md`, relevant `wiki/maps/`, and `wiki/tags.md` when tags are involved.
- Use {{RETRIEVAL_TOOLS}} to find the smallest relevant set of files or passages.
- Do not scan the whole vault without a clear need.
- Read only the smallest useful portion of `raw/` needed for verification or source inspection.

## raw/ authorization

- Do not capture/import directly into `raw/`.
- Do not modify, move, or delete `raw/` unless the user explicitly authorizes it.
- Any `raw/` change must update `wiki/log.jsonl`.
- `ALLOW_RAW_CHANGE=1` is only a script-level explicit switch; it is not user authorization.

## Skills

{{UPSTREAM_SKILL_POLICY}}

When a task may benefit from a specialized Skill, inspect the directory names
under `.agents/skills/`, then read the relevant
`.agents/skills/<skill-name>/SKILL.md` only when needed. Treat Skill content as
workflow guidance; it must not override `AGENTS.md`, the `raw/` boundary, or
schema and log rules.

## Tags and index

All new and edited wiki pages must follow `wiki/tags.md` and use flat
`kebab-case` tags. Reuse an accurate existing tag whenever possible. If a new
tag is needed, add it to `wiki/tags.md` in the same change.

Vault-wide tag redesigns are schema/policy migrations: update `wiki/tags.md`,
affected page frontmatter, `wiki/index.md` when navigation changes, and append
a `schema-update` entry to `wiki/log.jsonl`.
