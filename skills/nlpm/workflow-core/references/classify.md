# Artifact classification

Normalize separators to `/`, then apply the first matching row. Classification is path-based and does not execute or parse the artifact.

| Priority | Condition | Type |
|---:|---|---|
| 1 | `.agents/skills/**/SKILL.md` or `skills/**/SKILL.md` | `skill` |
| 2 | `.codex/agents/*.toml` | `codex-agent` |
| 3 | `.codex/hooks.json` or `hooks/**/*.json` | `hook-config` |
| 4 | `.codex/config.toml` | `codex-config` |
| 5 | `.codex-plugin/plugin.json` | `codex-manifest` |
| 6 | `.agents/plugins/marketplace.json` | `codex-marketplace` |
| 7 | `agents/openai.yaml` adjacent to `SKILL.md` | `skill-sidecar` |
| 8 | `commands/shared/**/*.md` | `shared-partial` |
| 9 | `.claude/commands/**/*.md` | `user-command` |
| 10 | `commands/**/*.md` | `command` |
| 11 | `agents/**/*.md` | `agent` |
| 12 | `.claude/rules/**/*.md` | `rule` |
| 13 | `.claude-plugin/plugin.json` | `claude-manifest` |
| 14 | `.claude-plugin/marketplace.json` | `claude-marketplace` |
| 15 | `.mcp.json` | `mcp-config` |
| 16 | `.lsp.json` | `lsp-config` |
| 17 | `.gemini/commands/**/*.toml` | `gemini-command` |
| 18 | `gemini-extension.json` | `gemini-manifest` |
| 19 | filename `AGENTS.md` | `agents-md` |
| 20 | filename `CLAUDE.md` | `claude-md` |
| 21 | filename `GEMINI.md` | `gemini-md` |
| 22 | path contains `/memory/` and ends in `.md` | `memory` |
| 23 | `.codex/nlpm.local.md` or `.claude/**/*.local.md` | `plugin-config` |
| 24 | `.claude/settings*.json` | `settings` |
| 25 | fallback | `document` |

