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
- `schema/` is reserved for schema and policy documents that guide LLM maintenance.
- `schema/log.md` defines the detailed `wiki/log.jsonl` event schemas.
- `schema/wiki-page.md` defines the detailed `wiki/*.md` page template.
- `schema/map.md` defines the detailed `wiki/maps/*.md` map template.

## Directory guide

```text
inbox/     unprocessed input
raw/       user-approved immutable source material
attachments/ default Obsidian attachments
wiki/      compiled long-term Markdown knowledge
wiki/tags.md flat kebab-case tag registry
outputs/   final deliverables
archives/   inactive old outputs only
schema/
  log.md   wiki/log.jsonl event schemas
  wiki-page.md wiki/*.md page template
  map.md   wiki/maps/*.md map template
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
{{SEARCH_COMMANDS}}
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
