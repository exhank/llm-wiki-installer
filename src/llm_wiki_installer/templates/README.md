# Knowledge Vault

This is an LLM-native Obsidian Markdown knowledge vault.

## Design idea

- `inbox/` is the capture buffer.
- `raw/` is the user-approved evidence layer.
- `attachments/` is the default Obsidian attachment folder.
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
attachments/ default Obsidian attachments
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
