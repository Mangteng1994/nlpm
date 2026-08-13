---
name: ls
description: "Discover all natural language programming artifacts in a repository. Use when the user invokes $nlpm-ls or requests this exact NLPM workflow."
---

# $nlpm-ls

Treat the text following `$nlpm-ls` in the user's request as the command arguments. Preserve empty input as empty; never invent flags.

## User Input

```text
<invocation-arguments>
```

## Workflow

### Step 1: Determine Path

| Input | Path |
|-------|------|
| (empty) | current working directory |
| directory path | use that path |
| file path | ERROR: "Expected a directory. Use $nlpm-score for individual files." |
| nonexistent path | ERROR: "Directory not found: {path}" |

### Step 2: Discover Artifacts

Delegate to the `scanner` agent with the target directory. The scanner follows the discovery patterns from `skills/nlpm/workflow-core/references/discover.md` to discover all Category A (plugin) and Category B (project config) artifacts.

### Step 3: Display Report

Print the scanner's report verbatim, using the exact structure defined in `.codex/agents/scanner.toml` (Output Format): the Category A (plugin) and Category B (project config) tables listing each artifact's path, line count, and token count, followed by the Total line. If no artifacts found: "No NL programming artifacts found in {path}."
