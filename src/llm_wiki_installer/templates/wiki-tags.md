# Tag Registry

This file is the canonical tag registry for the knowledge vault.

## Rules

- Use YAML `tags` lists in frontmatter.
- Do not prefix YAML tag values with `#`.
- Use flat tags only; do not use nested tags with `/`.
- Use `kebab-case`: lowercase letters, numbers, and hyphens.
- Reuse existing tags before creating new ones.
- Avoid synonyms and near-duplicates.

Do not use:

```text
type/source
topic/ai
long_context
LongContext
long context
```

## Core Tags

Use these tags for broad page roles when they apply:

```text
source
entity
concept
comparison
synthesis
question
map
decision
playbook
note
```

## Topic Tags

Topic tags may grow with the vault. Examples:

```text
llm
rag
model-evaluation
prompt-engineering
knowledge-graph
long-context
```

## Maintenance

Before adding a tag, check this file and existing wiki frontmatter. Reuse a
nearby existing tag when it is accurate. When a new tag is needed, add it here
with the same `kebab-case` standard.

Do not redesign tags for small edits. Only design a tag migration when the
vault structure, topic boundaries, or content scale changes substantially. A
tag migration must update this file, affected page frontmatter, `wiki/index.md`
when navigation changes, and append a `schema-update` entry to `wiki/log.jsonl`.
