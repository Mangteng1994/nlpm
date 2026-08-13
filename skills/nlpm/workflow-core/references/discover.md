# Artifact discovery

Input is a validated directory and an optional category filter. Return unique repository-relative paths, category, artifact type, and UTF-8 line count. Ignore `.git`, `node_modules`, `vendor`, `dist`, `build`, `target`, `.venv`, `__pycache__`, generated `.codex/nlpm-reports`, and auditor historical output.

Category A, executable or packaged NL artifacts:

- `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`
- `.agents/skills/**/SKILL.md`, `skills/**/SKILL.md`
- `.codex/agents/*.toml`, `.codex/hooks.json`, `.codex/config.toml`
- `agents/openai.yaml` sidecars adjacent to a skill
- `.claude-plugin/*.json`, `commands/**/*.md`, `agents/**/*.md`, `hooks/**/*.json`, `.mcp.json`, and `.lsp.json` as static Claude audit targets
- `.gemini/commands/**/*.toml`, `.gemini/skills/**/SKILL.md`, and `gemini-extension.json` as static Antigravity/Gemini audit targets

Category B, project instructions and policy:

- root and nested `AGENTS.md`
- `.codex/nlpm.local.md`
- root and nested `CLAUDE.md`, `.claude/rules/**/*.md`, `.claude/settings*.json`, `.claude/**/*.local.md` as static Claude audit targets
- root and nested `GEMINI.md` as static Antigravity/Gemini audit targets

Category F is Claude memory under `~/.claude/projects/*/memory/*.md`; inspect it only when the caller explicitly requests Category F. Never traverse a user's home directory during a normal repository scan.

For a file input, do not traverse. Classify that one path using `classify.md`. A missing path is an error. A repository containing no matching files is a successful empty result.

