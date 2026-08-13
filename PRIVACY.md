# Privacy Policy — NLPM

_Last updated: 2026-08-13_

NLPM analyzes natural-language artifacts inside your repository. Its explicit
`$nlpm-*` workflows are delivered as a Codex plugin; the scoring rubric covers
artifacts authored for Claude Code, Codex CLI, and Antigravity. The standalone
Python validator (`bin/nlpm-check`) runs without an agent runtime. This policy
describes the data NLPM handles.

## What NLPM reads

The contents of files in your project (skills, agents, commands, rules, hooks,
manifests, and related configuration) when you invoke an `$nlpm-*` workflow.
NLPM reads `.codex/nlpm.local.md` when present. During a one-time migration it
may read legacy NLPM configuration or history from `.claude/`, but never writes
there.

## What NLPM writes

NLPM may write `.codex/nlpm.local.md`, `.codex/nlpm-history.json`, and
`.codex/nlpm-reports/`. `$nlpm-fix` edits only the target artifacts selected by
the user. These files stay in the project. The standalone validator
(`bin/nlpm-check`) reads and exits without writing.

## What NLPM transmits

NLPM has no backend, telemetry collector, or phone-home service. When Codex
orchestrates a workflow, the repository context it needs is processed by
OpenAI under the terms and controls of the user's Codex account. The standalone
validator performs its deterministic checks locally and makes no network call.

## Third parties

Optional badge fetching from shields.io occurs only if you opt in by embedding the "Validated by NLPM" badge URL in your README. shields.io's privacy policy applies in that case.

## What about the auditor pipeline?

The `auditor/` directory inside the NLPM source repo runs a separate GitHub Actions pipeline that audits **other** public plugin and skill repositories (today: Claude Code plugins; Codex CLI and Antigravity discovery is planned). That pipeline runs on the maintainer's GitHub account, not on your machine. Installing NLPM as a plugin does **not** enroll your repository in that pipeline.

## Data deletion

There is no centralized NLPM service data to delete. To remove local NLPM
state, delete `.codex/nlpm-history.json`, `.codex/nlpm.local.md`, and
`.codex/nlpm-reports/` from your projects, then run
`codex plugin remove nlpm`.

## Contact

For privacy questions or to report a discrepancy with this policy: **xiaolaiapple@gmail.com**.
