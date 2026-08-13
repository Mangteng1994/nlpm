---
# NLPM Configuration — Codex runtime
strictness: strict
score_threshold: 90
rule_overrides:
  R51:
    enabled: true
    vocabulary_skill: skills/nlpm/vocabulary/
  R05:
    suppress: true
    paths:
      - skills/nlpm/conventions-claude/SKILL.md
      - skills/nlpm/conventions-codex/SKILL.md
      - skills/nlpm/conventions-antigravity/SKILL.md
      - skills/nlpm/scoring/SKILL.md
      - skills/nlpm/rules/SKILL.md
    reason: "Canonical reference documents have scoped overflow references and are not ordinary artifacts."
---

# NLPM Settings

Use strict scoring and flag artifacts below 90/100. R51 reads `skills/nlpm/vocabulary/registry.yaml`. Runtime state is written only below `.codex/`; legacy `.claude/nlpm.local.md` and `.claude/nlpm-history.json` may be read once for migration but are never modified.

