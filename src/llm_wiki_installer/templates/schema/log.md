# Log Schema

`wiki/log.jsonl` is the append-only JSONL audit ledger for meaningful vault
writes. It does not replace Git history.

Each line must be one complete JSON object. Use `timestamp` as a UTC ISO-8601
instant, include `schema_version`, include `actor`, and keep `reason` specific
enough for later review.

Ordinary read-only queries do not write to the log.

## Event Types

Use these event types for log entries:

- `ingest`
- `fileback`
- `delete`
- `move`
- `archive-output`
- `schema-update`

## ingest

```json
{"schema_version":1,"timestamp":"YYYY-MM-DDTHH:MM:SSZ","actor":"agent","type":"ingest","scope":"raw/source -> wiki/page.md","reason":"Compiled durable knowledge from raw source.","review":"self-reviewed","impact":{"index_updated":true,"references_checked":true},"files":["raw/source","wiki/page.md","wiki/index.md"]}
```

## fileback

```json
{"schema_version":1,"timestamp":"YYYY-MM-DDTHH:MM:SSZ","actor":"agent","type":"fileback","scope":"answer/output -> inbox/path.md","reason":"Saved user-requested output into the vault inbox.","review":"self-reviewed","impact":{"index_updated":"not-needed","references_checked":"not-needed"},"files":["inbox/path.md"]}
```

## delete

```json
{"schema_version":1,"timestamp":"YYYY-MM-DDTHH:MM:SSZ","actor":"agent","type":"delete","scope":"path/to/file.md","reason":"Why this file is safe to delete.","authorized_by":"user | explicit-task","review":"self-reviewed","impact":{"index_updated":false,"references_checked":true},"files":["path/to/file.md"]}
```

## move

```json
{"schema_version":1,"timestamp":"YYYY-MM-DDTHH:MM:SSZ","actor":"agent","type":"move","scope":"old/path.md -> new/path.md","reason":"Why this move is needed.","authorized_by":"user | explicit-task","review":"self-reviewed","impact":{"index_updated":true,"references_checked":true},"files":["old/path.md","new/path.md"]}
```

## archive-output

```json
{"schema_version":1,"timestamp":"YYYY-MM-DDTHH:MM:SSZ","actor":"agent","type":"archive-output","scope":"outputs/file.md -> archives/file.md","reason":"Old deliverable no longer active.","review":"self-reviewed","impact":{"index_updated":"not-needed","references_checked":true},"files":["outputs/file.md","archives/file.md"]}
```

## schema-update

```json
{"schema_version":1,"timestamp":"YYYY-MM-DDTHH:MM:SSZ","actor":"agent","type":"schema-update","scope":"path/to/schema-or-script","reason":"Changed vault schema, script, or policy contract.","review":"self-reviewed","impact":{"index_updated":"not-needed","references_checked":true},"files":["path/to/schema-or-script"]}
```
