# Wiki Page Schema

Use this schema when creating a new `wiki/*.md` page or substantially reshaping
an existing wiki page.

## Frontmatter

```yaml
---
title: ""
tags: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

## Tag Rules

All new and edited wiki pages must follow `wiki/tags.md`. Use YAML `tags` lists
with flat `kebab-case` values, without `#` prefixes or nested slash tags.
Before introducing a tag, check `wiki/tags.md` and existing wiki frontmatter.
Reuse an accurate existing tag whenever possible. If a new tag is needed, add it
to `wiki/tags.md` in the same change.

Small local tag additions are normal page edits. Vault-wide tag redesigns are
schema/policy migrations: update `wiki/tags.md`, affected page frontmatter,
`wiki/index.md` when navigation changes, and append a `schema-update` entry to
`wiki/log.jsonl`.

## Body

Recommended body:

```md
# Title

## Summary

## Key Points

## Evidence / Sources

- source: `raw/path/to/source`

## Open Questions

## Related
```
