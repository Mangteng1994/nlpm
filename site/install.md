---
title: Install NLPM for Codex
outline: [2, 3]
---

# Install NLPM for Codex

NLPM is delivered as a Codex plugin. Its runtime, skills, subagent orchestration, hooks, configuration, and GitHub automation use Codex and OpenAI capabilities. Cross-tool scoring still recognizes Claude Code and Antigravity files as static input.

## Plugin install

```bash
codex plugin marketplace add Mangteng1994/nlpm
codex plugin add nlpm@mangteng1994
```

Start Codex in a repository and invoke a skill explicitly:

```text
$nlpm-ls
$nlpm-score --changed
$nlpm-check
$nlpm-report
```

Requirements are Codex CLI 0.147.0+ and Python 3.11+ for the standalone checker/report scripts.

## Project initialization

```text
$nlpm-init
```

This creates `.codex/nlpm.local.md` and an initial `.codex/nlpm-history.json` snapshot when artifacts exist. A legacy `.claude` config or history file may be imported once, read-only; all later writes go to `.codex/`.

## Standalone checker

`bin/nlpm-check` is a standard-library-only Python file for deterministic pre-commit and CI checks:

```bash
git clone https://github.com/Mangteng1994/nlpm
python3 nlpm/bin/nlpm-check /path/to/plugin
```

Templates are available in `templates/pre-commit-nlpm.sh` and `templates/workflows/nlpm-check.yml`.

## Vocabulary discipline

```text
$nlpm-vocab-init
$nlpm-vocab-drift
```

Enable R51 in `.codex/nlpm.local.md` after reviewing the generated registry.

## Update or uninstall

```bash
codex plugin marketplace upgrade xiaolai
codex plugin remove nlpm
```

See [How to use NLPM](/how-to-use-it), [the framework reference](/reference/), and the [Auditor dashboard](/dashboard.html).
