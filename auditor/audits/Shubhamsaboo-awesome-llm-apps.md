# NLPM Audit: Shubhamsaboo/awesome-llm-apps
**Date**: 2026-04-06  |  **Artifacts**: 11  |  **Strategy**: single
**NL Score**: 96/100
**Security**: BLOCKED
**Bugs**: 2  |  **Quality Issues**: 6  |  **Security Findings**: 14

## NL Score Summary
| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| generative_ui_agents/ai-mcp-app-builder/apps/mcp-use-server/.agent/skills/chatgpt-app-builder/SKILL.md | Skill | 85 | Broken reference: points to nonexistent `mcp-app-builder` skill |
| generative_ui_agents/ai-mcp-app-builder/apps/mcp-use-server/.agent/skills/mcp-builder/SKILL.md | Skill | 85 | Broken reference: points to nonexistent `mcp-app-builder` skill |
| advanced_ai_agents/multi_agent_apps/agent_teams/ai_travel_planner_agent_team/backend/agents/README.md | Documentation | 96 | Vague quantifiers ("properly", "various") |
| agent_skills/thinking-out-loud/SKILL.md | Skill | 96 | Vague quantifier ("several" x2) |
| generative_ui_agents/ai-mcp-app-builder/apps/mcp-use-server/.agent/skills/mcp-apps-builder/SKILL.md | Skill | 96 | Vague quantifier ("relevant" x2) |
| agent_skills/advisor-orchestrator-worker/SKILL.md | Skill | 98 | Vague quantifier ("reasonable") |
| agent_skills/commit-archaeologist/SKILL.md | Skill | 98 | Vague quantifier ("relevant") |
| agent_skills/dependency-doctor/SKILL.md | Skill | 98 | Vague quantifier ("several") |
| agent_skills/project-graveyard/SKILL.md | Skill | 100 | None |
| agent_skills/scope-creep-detector/SKILL.md | Skill | 100 | None |
| generative_ui_agents/generative-ui-starter-project/CLAUDE.md | Memory | 100 | None |

## Security Scan
| Severity | Count |
|----------|-------|
| Critical | 3 |
| High | 8 |
| Medium | 2 |
| Low | 1 |

### Execution Surface Inventory
| Surface | Files |
|---------|-------|
| Hooks (Claude Code `hooks.json`) | 0 (only stock `.git/hooks/*.sample` and unrelated React `hooks/` component directories — not execution surfaces) |
| Scripts (`.sh`/`.py`/`.js`) | 591 (9 `.sh`, 527 `.py`, 55 `.js`) across ~40 independent example apps |
| MCP configs (`.mcp.json`) | 1 — `generative_ui_agents/ai-shadcn-component-generator/.mcp.json` |
| package.json manifests with `postinstall`/`preinstall` | 4 |
| requirements.txt manifests | 156 |

**Scope note**: this is a large multi-app tutorial monorepo (~40 independent example projects). A line-by-line read of all 591 scripts and 156 requirements.txt files was not feasible in one pass; findings below come from a targeted pattern sweep (curl-pipe-shell, `eval(`, `os.system`, `subprocess(...shell=True)`, base64-decode-exec, reverse-shell markers, `sudo`, `postinstall`/`preinstall`) across every script and manifest in the repo, followed by manual read-and-verify of every match. The Low-severity unpinned-dependency finding is representative of a repo-wide pattern, not an exhaustive per-file audit — flagging this explicitly per the "no silent caps" rule rather than implying full coverage.

### Security Findings
| # | Severity | File | Line | Pattern | Description |
|---|----------|------|------|---------|-------------|
| 1 | Critical | generative_ui_agents/generative-ui-starter-project/Dockerfile | 31 | curl-pipe-sh | `curl -fsSL https://deb.nodesource.com/setup_20.x \| bash -` — remote script fetched over HTTPS and piped directly into `bash` with no checksum/signature verification |
| 2 | Critical | generative_ui_agents/ai-financial-coach-agent/Dockerfile | 21 | curl-pipe-sh | Same NodeSource curl-pipe-bash pattern |
| 3 | Critical | advanced_ai_agents/multi_agent_apps/agent_teams/ai_travel_planner_agent_team/backend/Dockerfile | 20 | curl-pipe-sh | Same NodeSource curl-pipe-bash pattern |
| 4 | High | advanced_ai_agents/multi_agent_apps/ai_news_and_podcast_agents/beifong/tests/tts_kokoro_test.py | 20 | os-system-fstring | `os.system(f"afplay {file_path}")` — shell command built via unsanitized f-string interpolation |
| 5 | High | advanced_ai_agents/multi_agent_apps/ai_news_and_podcast_agents/beifong/tests/tts_kokoro_test.py | 22 | os-system-fstring | `os.system(f"aplay {file_path}")` — same pattern |
| 6 | High | advanced_ai_agents/multi_agent_apps/ai_news_and_podcast_agents/beifong/tests/tts_kokoro_test.py | 24 | os-system-fstring | `os.system(f'start "" "{file_path}"')` — same pattern (Windows branch) |
| 7 | High | advanced_ai_agents/multi_agent_apps/ai_news_and_podcast_agents/beifong/scheduler.py | 99 | subprocess-shell-true | `subprocess.Popen(command, shell=True, ...)` where `command` is read verbatim from a DB-stored scheduled-task row (`command = task["command"]` at line 144) — command injection if task rows are ever attacker-influenced |
| 8 | High | generative_ui_agents/generative-ui-starter-project/package.json | 13 | postinstall-script | `"postinstall": "npm run install:agent"` runs automatically on every `npm install` |
| 9 | High | generative_ui_agents/ai-financial-coach-agent/package.json | 13 | postinstall-script | Same automatic postinstall pattern |
| 10 | High | generative_ui_agents/ai-dashboard-canvas-agent/package.json | 14 | postinstall-script | Same automatic postinstall pattern |
| 11 | High | generative_ui_agents/ai-mcp-app-builder/apps/mcp-use-server/package.json | 28 | postinstall-script | `"postinstall": "mcp-use generate-types \|\| node -e \"process.exit(0)\""` runs automatically on install |
| 12 | Medium | ai_agent_framework_crash_course/google_adk_crash_course/4_tool_using_agent/4_2_function_tools/calculator_agent/tools.py | 30 | eval-with-input | `eval(safe_expression)` evaluates an LLM-tool-supplied string; a character whitelist strips letters (blocking obvious `__import__`-style injection) but `eval()` is still used on dynamic input instead of a real expression evaluator |
| 13 | Medium | generative_ui_agents/ai-shadcn-component-generator/.mcp.json | 4-8 | broad-mcp-permission | MCP server is launched via `npx shadcn@latest mcp` — unpinned version, re-fetched and executed fresh on every launch |
| 14 | Low | advanced_llm_apps/multimodal_video_moment_finder/backend/requirements.txt | 1 | unpinned-semver | Dependencies pinned with floor-only `>=` constraints, no upper bound (`fastapi>=0.115.0`, etc.); representative of the majority of this repo's 156 requirements.txt files |

## Bugs (PR-worthy)
| # | File | Issue | Impact |
|---|------|-------|--------|
| 1 | generative_ui_agents/ai-mcp-app-builder/apps/mcp-use-server/.agent/skills/chatgpt-app-builder/SKILL.md | Deprecation notice tells the agent to check for / install a skill named `mcp-app-builder` (singular "app"); the actual skill on disk is `mcp-apps-builder` (plural "apps") — verified via directory listing, no `mcp-app-builder` directory exists anywhere in the repo | An agent following the pointer literally won't find the already-installed local skill and may run `npx skills install mcp-use/mcp-use --skill mcp-app-builder`, installing a duplicate/differently-named skill instead of using `mcp-apps-builder` |
| 2 | generative_ui_agents/ai-mcp-app-builder/apps/mcp-use-server/.agent/skills/mcp-builder/SKILL.md | Same broken pointer: deprecation notice references `mcp-app-builder`, which does not exist; only `mcp-apps-builder` does | Same as above |

## Security Fixes (PR-worthy, Medium/Low only)
| # | File | Issue | Suggested Fix |
|---|------|-------|---------------|
| 1 | ai_agent_framework_crash_course/google_adk_crash_course/4_tool_using_agent/4_2_function_tools/calculator_agent/tools.py:30 | `eval()` used on a character-filtered but still dynamic string | Replace with a safe arithmetic evaluator (e.g. walk a restricted `ast` node whitelist, or use `asteval`/`numexpr`) instead of `eval()` + char-whitelist filtering |
| 2 | generative_ui_agents/ai-shadcn-component-generator/.mcp.json:4-8 | MCP server pinned to `@latest`, re-resolved on every launch | Pin to an exact `shadcn` version (e.g. `shadcn@2.x.y`) to avoid supply-chain surprises from an unreviewed upstream release |
| 3 | requirements.txt manifests (repo-wide, e.g. advanced_llm_apps/multimodal_video_moment_finder/backend/requirements.txt) | Floor-only `>=` version constraints, no upper bound | Pin exact versions (`==`) or add upper bounds for reproducible builds; consider per-app lockfiles |

## Quality Issues (informational)
| # | File | Issue | Penalty |
|---|------|-------|---------|
| 1 | advanced_ai_agents/multi_agent_apps/agent_teams/ai_travel_planner_agent_team/backend/agents/README.md | Vague quantifiers: "properly synchronized" (line 76), "various tools" (line 81) | -4 |
| 2 | agent_skills/thinking-out-loud/SKILL.md | Vague quantifier "several" (lines 15, 137) | -4 |
| 3 | generative_ui_agents/ai-mcp-app-builder/apps/mcp-use-server/.agent/skills/mcp-apps-builder/SKILL.md | Vague quantifier "relevant" (lines 15, 22) | -4 |
| 4 | agent_skills/advisor-orchestrator-worker/SKILL.md | Vague quantifier "reasonable shape" (line 124) | -2 |
| 5 | agent_skills/commit-archaeologist/SKILL.md | Vague quantifier "one relevant follow-up" (line 119) | -2 |
| 6 | agent_skills/dependency-doctor/SKILL.md | Vague quantifier "several manifests" (line 47) | -2 |

## Cross-Component
- `advanced_ai_agents/.../ai_travel_planner_agent_team/backend/agents/README.md` describes six team members (Destination Explorer, Hotel Search Agent, Dining Agent, Budget Agent, Flight Search Agent, Itinerary Specialist); all six map cleanly to actual files in the same directory (`destination.py`, `hotel.py`, `food.py`, `budget.py`, `flight.py`, `itinerary.py`) plus `team.py` for orchestration — no drift found.
- The `mcp-apps-builder` skill (the live, current skill) and the two deprecated stubs (`chatgpt-app-builder`, `mcp-builder`) show a naming mismatch between the deprecation notices (`mcp-app-builder`, singular) and the real replacement (`mcp-apps-builder`, plural) — see Bugs #1-2. This is the same underlying defect counted once per stub file, not a separate cross-component finding.
- All `references/*.md` and `scripts/*.py` files pointed to from the six `agent_skills/*/SKILL.md` files were confirmed present on disk (advisor-orchestrator-worker, commit-archaeologist, dependency-doctor, project-graveyard, scope-creep-detector, thinking-out-loud) — no broken relative links.
- All `references/**/*.md` files pointed to from `mcp-apps-builder/SKILL.md`'s navigation guide (foundations, authentication, server, widgets, patterns) were confirmed present on disk — no broken links.

## Recommendation
BLOCKED — do not submit PRs. File private security report for the Critical (unauthenticated curl-pipe-bash in 3 Dockerfiles) and High findings (unsanitized `os.system` shell interpolation, `subprocess(shell=True)` on a DB-sourced command string, 4 automatic `postinstall` scripts). Once addressed, the 2 NL bugs (broken skill-deprecation references) and the 3 Medium/Low security fixes (eval-on-input, unpinned MCP version, unpinned dependency floors) are safe to submit as separate PRs.
