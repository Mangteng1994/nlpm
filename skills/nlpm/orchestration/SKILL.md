---
name: orchestration
description: "Design Codex multi-agent workflows with parallel delegation, sequential pipelines, quality gates, bounded retries, and deterministic aggregation."
---

# Codex multi-agent orchestration

Delegate only work that is independently bounded and useful in parallel. Give each worker a role, exact input scope, output contract, permissions, and completion condition. The coordinator owns synthesis and user-facing errors.

## Parallel fan-out

Use parallel subagents when tasks do not mutate overlapping files, such as scoring and literal word counting. Cap batches explicitly, collect every result, and define precedence for conflicts. NLPM uses deterministic vague-word counts to override heuristic counts from the scorer.

## Sequential pipeline

Use a pipeline when later input depends on earlier output: discover → classify → score → render → persist. Validate each handoff before starting the next stage. A failed optional persistence step must not erase a successful score result.

## Quality gate and retry

Define a machine-checkable acceptance condition. Retry a failed stage at most the workflow's stated limit, with the observed defect and unchanged requirements. Do not retry permanent policy blocks or malformed user input.

## Shared contracts

Put reusable discovery, classification, and persistence behavior in a canonical skill reference or deterministic script. User-facing skills reference that contract instead of copying it. Avoid hidden state and normalize repository paths before aggregation.

## Installed-plugin fallback

When a named `.codex/agents/<role>.toml` is unavailable after plugin installation, spawn a generic Codex subagent and pass the bundled role's `developer_instructions`, reasoning effort, and sandbox policy. The coordinator must not silently collapse a required parallel role into its own reasoning.

Review checklist:

- parallel branches are independent;
- mutation ownership cannot overlap;
- the coordinator handles missing, empty, and failed results;
- aggregation precedence is deterministic;
- retries are bounded and evidence-driven;
- state writes are atomic and occur only after validation.
