---
name: workflow-core
description: "Internal NLPM workflow contracts for artifact discovery, path classification, and atomic Codex history snapshots. Use when an nlpm command skill needs shared workflow behavior."
---

# NLPM workflow core

This is the single shared implementation contract for the user-facing NLPM skills. Load only the reference required by the active workflow:

- `references/discover.md` for repository traversal and artifact inventory.
- `references/classify.md` for first-match artifact typing.
- `references/append-history.md` for score/trend persistence.

Use forward-slash repository-relative paths in reports on every operating system. Static Claude Code and Antigravity artifacts remain discoverable audit targets; this skill itself never invokes either runtime.

When a workflow delegates to a named role, use the matching definition in `${PLUGIN_ROOT}/.codex/agents/<role>.toml`. Project-local development lets Codex discover these definitions directly. An installed plugin must remain functional even when plugin packaging does not activate project-local agent files: in that case spawn a generic Codex subagent, pass the TOML `developer_instructions`, and provide the resolved `PLUGIN_ROOT` so its required knowledge paths can be read. Preserve its sandbox policy and reasoning effort. This is the required fallback, not a reason to run the role in the coordinator.
