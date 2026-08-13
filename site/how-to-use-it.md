---
title: How to use NLPM
outline: [2, 3]
---

# How to use NLPM

Every interactive workflow is an explicit Codex skill. Run it from the repository you want to inspect.

## Core loop

```text
$nlpm-init
$nlpm-ls
$nlpm-score --changed
$nlpm-check
$nlpm-fix
$nlpm-test
$nlpm-trend
$nlpm-report
```

- `$nlpm-init` writes project policy to `.codex/nlpm.local.md` and captures a baseline.
- `$nlpm-ls [path]` inventories supported NL artifacts.
- `$nlpm-score [path|--changed]` delegates scorer and vague-word passes in parallel and appends history.
- `$nlpm-check [path]` checks references, registration, contradictions, and vocabulary.
- `$nlpm-fix [path]` applies only documented mechanical repairs, then rescores.
- `$nlpm-test [spec]` evaluates `.nlpm-test/*.spec.md` files.
- `$nlpm-trend [path]` compares snapshots with matching scopes.
- `$nlpm-report [path]` writes `.codex/nlpm-reports/index.html`.

## Security and vocabulary

```text
$nlpm-security-scan
$nlpm-vocab-init
$nlpm-vocab-drift
```

The security scan reads executable surfaces without executing the inspected code. Vocabulary initialization creates a reviewable registry; drift scanning is advisory and requires no registry.

## Specification maintenance

```text
$nlpm-spec-sync codex
$nlpm-spec-sync all
```

The workflow browses official upstream documentation, delegates one read-only researcher per selected overlay, applies only well-supported corrections, and runs `bin/nlpm-check`. It never commits or pushes.

## State and hooks

NLPM writes runtime state only below `.codex/`. Its `PostToolUse` hook watches Codex file edits, stays silent for non-NL files, and adds a `$nlpm-score` reminder for matching artifacts. Malformed hook input fails open.

## CI

Use `python3 bin/nlpm-check .` for the deterministic floor. NLPM's own judgment-based Auditor jobs use `openai/codex-action@v1` with `OPENAI_API_KEY`.

The rubric remains multi-tool: Claude Code and Antigravity formats can be discovered and scored as data, but neither runtime is required or invoked.
