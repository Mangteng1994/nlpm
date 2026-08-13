---
name: security-scan
description: "Scan a Codex plugin or NL artifact repository for security risks in executable artifacts, hooks, scripts, MCP configuration, and dependencies. Use when the user invokes $nlpm-security-scan or requests this exact NLPM workflow."
---

# $nlpm-security-scan

Treat the text following `$nlpm-security-scan` in the user's request as the command arguments. Preserve empty input as empty; never invent flags.

# Security Scan

Scan a plugin or skill repo for security risks before auditing or contributing.

## Step 1: Parse Input

If arguments provided: use as target directory path.
If no arguments: use the current working directory.

Check the target exists and contains at least one of:
- `.codex-plugin/`
- `.codex/agents/`
- `.agents/skills/`
- `skills/`
- `.codex/hooks.json`
- `scripts/`
- a static non-Codex audit surface such as `.claude-plugin/`, `commands/`, `agents/`, or `hooks/`

If none found: report "Not an NL plugin or artifact directory" and stop.

## Step 2: Dispatch Security Scanner

Delegate to the `security-scanner` subagent on the target directory.

Wait for the agent to complete and collect its report.

## Step 3: Present Results

Display the full report in this exact structure: the agent report as the body, followed by the gate banner as the footer. The `security-scanner` agent emits the body; this command appends only the banner.

```
{security-scanner agent report — verbatim}

────────────────────────────────────────────────────────────
{GATE BANNER — chosen per recommendation, see below}
────────────────────────────────────────────────────────────
```

Gate banners:

If the recommendation is BLOCK:
```
SECURITY GATE: BLOCKED
Critical/High security findings. Do NOT install or contribute to this plugin without resolving these findings first.
```

If the recommendation is REVIEW:
```
SECURITY GATE: REVIEW NEEDED
Medium-severity findings detected. Review the findings before proceeding.
```

If the recommendation is PASS:
```
SECURITY GATE: PASSED
No Critical/High security findings. Safe to proceed with audit and contribution.
```

**Error handling:**
- Target path does not exist → "Directory not found: {path}"
- `security-scanner` agent returns no report → "Security scan failed: no report produced. Re-run $nlpm-security-scan {path}."
