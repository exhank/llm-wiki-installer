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

Upstream Skills were written for their authors' own vault layouts. When a
Skill references paths or config files that do not exist here (for example
`_raw/`, `_staging/`, a root-level `index.md` or `log.md`, `.manifest.json`,
or `~/.obsidian-wiki/config`), map them to this vault's layout (`raw/`,
`inbox/`, `wiki/index.md`, `wiki/log.jsonl`) or ignore that instruction. Do
not create the missing upstream files or restructure this vault to match a
Skill.

## Review cadence

Humans review sources at promotion time (`inbox/` to `raw/`) and review the
wiki by digest and sampling, not diff by diff. A periodic digest is enough:

```bash
git --no-pager log --since="1 week ago" --stat -- wiki
```

Summarize what changed, which topics grew, and any flagged contradictions
into `outputs/` when the user asks for a digest. Fix problems found at read
time; any wiki page can be recompiled from `raw/` if it degrades.

## Tags and index

All new and edited wiki pages must follow `wiki/tags.md` and use flat
`kebab-case` tags. Reuse an accurate existing tag whenever possible. If a new
tag is needed, add it to `wiki/tags.md` in the same change.

Vault-wide tag redesigns are schema/policy migrations: update `wiki/tags.md`,
affected page frontmatter, `wiki/index.md` when navigation changes, and append
a `schema-update` entry to `wiki/log.jsonl`.
