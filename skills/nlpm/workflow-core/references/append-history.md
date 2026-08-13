# Atomic score history

Persist non-empty scoring results to `<project>/.codex/nlpm-history.json`. Never write history or configuration under `.claude/`.

On the first run only, if the Codex history does not exist and `.claude/nlpm-history.json` does, read the legacy JSON and use its valid `snapshots` array as the starting value. Do not rename, edit, or delete the legacy file. Record `legacy_imported_from: ".claude/nlpm-history.json"` at the document root. Ignore malformed legacy data with a one-line warning.

The document schema is:

```json
{
  "schema_version": 1,
  "snapshots": [{
    "timestamp": "2026-08-13T00:00:00Z",
    "overall": 85,
    "files": {"path": {"score": 92, "type": "skill"}},
    "scope": "full",
    "files_scored": 1
  }]
}
```

Use `full`, `changed`, or `path:<normalized-path>` scope. Compute `overall` as the rounded arithmetic mean. Skip an empty result. If the last snapshot has the same scope and files map, update its timestamp instead of appending. Write UTF-8 JSON with two-space indentation and a trailing newline to `.codex/nlpm-history.json.tmp`, then atomically replace the final path. If the project is not writable, warn and return the score successfully.

