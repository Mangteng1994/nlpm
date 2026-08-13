---
name: writing-agents
description: "Write or review Codex subagent TOML definitions with bounded roles, explicit sandbox policy, stable output contracts, and reliable coordinator handoff."
---

# Writing Codex subagents

Use one file per role at `.codex/agents/<name>.toml` for a project or `~/.codex/agents/<name>.toml` for a user. Required fields are `name`, `description`, and `developer_instructions`. Optional fields include `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, and `skills.config`.

```toml
name = "dependency-auditor"
description = "Inspect dependency metadata and return a bounded risk report."
model_reasoning_effort = "high"
sandbox_mode = "read-only"

developer_instructions = '''
Read only dependency manifests and lockfiles in the assigned scope.
Return: Summary, Findings, Evidence, and Unknowns.
Do not edit files or execute package lifecycle scripts.
'''
```

Make the description a routing rule: include when to delegate, the domain boundary, and the expected product. Keep `developer_instructions` self-contained because the subagent may not inherit every coordinator detail.

Choose the narrowest sandbox that supports the role. Analysis roles use `read-only`; mutation roles require an explicit file ownership boundary. Omit a model pin unless a tested workload requires it; prefer reasoning effort over stale model IDs.

Define an exact output schema and an error shape. A coordinator should be able to distinguish success, a genuine empty result, and missing input without interpreting prose.

For plugin portability, remember that installed plugin packaging may not activate plugin-private project TOMLs as named agents. Bundle the TOMLs as role definitions and let the calling skill spawn a generic Codex subagent with the TOML `developer_instructions`, sandbox, and effort when the named role is unavailable.

Review checklist:

- TOML parses and required fields are non-empty.
- The role has one bounded responsibility.
- Read/write and network permissions match that responsibility.
- Inputs, outputs, empty results, and failures are explicit.
- The coordinator specifies how to merge or reject the result.
- No tool-vendor model name is copied mechanically from another runtime.
