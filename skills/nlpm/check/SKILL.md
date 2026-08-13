---
name: check
description: "Check cross-artifact consistency — reference integrity, orphans, contradictions. Use when the user invokes $nlpm-check or requests this exact NLPM workflow."
---

# $nlpm-check

Treat the text following `$nlpm-check` in the user's request as the command arguments. Preserve empty input as empty; never invent flags.

## User Input

```text
<invocation-arguments>
```

## Workflow

### Step 1: Discover ALL Artifacts

Parse the invocation arguments for a path (default: cwd). Use `skills/nlpm/workflow-core/references/discover.md` to discover all Category A+B artifacts. Read every file.

If no artifacts found → "No NL programming artifacts found."

If fewer than 2 artifacts → "Cross-artifact check requires multiple artifacts. Use $nlpm-score for individual files."

### Step 2: Run the Cross-Artifact Check

Delegate to the `checker` agent with ALL artifacts and the instruction to perform cross-artifact checks:

1. **Reference integrity**
   - Codex command skills reference workflow-core files → check each path exists
   - Subagent definitions reference canonical knowledge skills → check each path exists
   - Hooks reference scripts through `${PLUGIN_ROOT}` → check each path exists
   - Legacy command, agent, or hook references discovered as static audit targets → check each path exists

2. **Orphaned artifacts**
   - Workflow-core references not used by any command skill → orphan
   - Knowledge skills not referenced by any command skill or subagent → orphan
   - Scripts not referenced by any hook, skill, or workflow → orphan

3. **Behavioral contradictions**
   - Command says "always do X" but referenced partial says "never do X"
   - Two agents claim the same responsibility domain
   - Rules contradict each other or the applicable memory file (`AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`)

4. **Terminology drift**
   - Same concept called different names across artifacts
   - Inconsistent naming (kebab vs camelCase vs snake_case)

### Step 3: Report

```markdown
NLPM Cross-Artifact Check

Artifacts checked: {N}

Reference Integrity:
  {N} references checked, {N} broken
  {list broken references}

Orphaned Artifacts:
  {N} orphans found
  {list orphans}

Contradictions:
  {N} found
  {list contradictions with both sides}

Terminology:
  {N} inconsistencies
  {list}

Verdict: {CLEAN | {N} findings}
```

**Error handling:**
- Unreadable files → skip with warning, note in report
- Path doesn't exist → "Directory not found: {path}"
