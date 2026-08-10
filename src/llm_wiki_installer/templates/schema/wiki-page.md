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

## Claim Provenance

Mark the confidence of important claims so readers can verify at read time:

- `extracted` - stated directly by a `raw/` source; cite the source path.
- `inferred` - concluded by the LLM from sources; not stated verbatim.
- `ambiguous` - sources conflict or are unclear; say what is uncertain.

Write the marker inline after the claim, for example:
`The API limit is 100 requests per minute (extracted: raw/api-docs.md).`
Unmarked statements in Summary and Key Points are treated as `inferred`.
Verification effort then scales with use: readers check `extracted` claims
against the cited source only when they rely on them, and treat `inferred`
and `ambiguous` claims with proportional care.
