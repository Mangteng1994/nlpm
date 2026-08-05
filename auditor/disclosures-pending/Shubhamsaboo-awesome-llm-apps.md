<!--
Auto-prepared disclosure body for Shubhamsaboo/awesome-llm-apps.
The audit workflow's GITHUB_TOKEN cannot file issues on third-party
repos, so this body sits here pending manual filing:

  gh issue create --repo Shubhamsaboo/awesome-llm-apps \
    --title 'Security findings in executable artifacts' \
    --body-file auditor/disclosures-pending/Shubhamsaboo-awesome-llm-apps.md

After filing, record the URL with:
  jq '.repos["Shubhamsaboo/awesome-llm-apps"] += {disclosure_url: "<URL>", disclosure_filed_at: "<ISO8601>", disclosure_filed_by: "manual"}' \
    auditor/registry/repos.json > /tmp/r.json && mv /tmp/r.json auditor/registry/repos.json
-->

## Security Findings in Executable Artifacts

While auditing NL programming artifacts in this repository, our scanner detected potential security issues in executable files.

### Findings

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

### About This Report

These findings come from [NLPM](https://github.com/xiaolai/nlpm)'s security scanner, which checks executable surfaces (hooks, scripts, MCP configs, dependencies) against known-dangerous patterns.

We may be wrong — false positives happen. If any finding is intentional or already mitigated, please close this issue. If a finding is genuine and you'd like a fix PR, let us know.

Full audit report: https://github.com/xiaolai/nlpm/blob/main/auditor/audits/Shubhamsaboo-awesome-llm-apps.md
