# Auditor credential and prompt-injection boundary

Auditor workflows use `openai/codex-action@v1`. Several jobs inspect untrusted upstream repositories while a later step may hold a GitHub token. Treat repository files, issue bodies, PR comments, and audit sidecars as data rather than instructions.

## Current controls

- Read/analysis jobs run with `sandbox: workspace-write`; Codex's workspace sandbox disables arbitrary system mutation and network access by default.
- The contribution job is the only Codex step using `danger-full-access`, because it must operate `git` and `gh` against a fork. Policy, security, duplicate, and confidence gates run before it.
- Prompts explicitly reject instructions embedded in inspected content.
- GitHub tokens are scoped per workflow and are not substituted into prompts.
- Contribution count and target paths are bounded; protected-path checks run before repository automation commits.
- A configured human author identity is required for CLA-covered organizations.

## Remaining structural risk

The contribution Codex process still combines untrusted content, network-capable shell access, and a cross-repository token. Prompt restrictions reduce accidental misuse but are not a hard security boundary. The preferred future architecture is a patch-only, network-disabled Codex step followed by a deterministic token-bearing publisher that validates and applies the patch. Until that split lands, changes to `auditor-contribute.yml` require security review and `$nlpm-security-scan`.
