# NLPM

Natural-Language Programming Manager for Codex. NLPM discovers, scores, checks, fixes, tests, and reports on skills, agents, hooks, manifests, project instructions, and related NL artifacts.

The runtime and delivery surface is Codex-only. The rubric still recognizes Claude Code and Antigravity artifacts as static audit targets, so a Codex user can review cross-tool repositories without installing those runtimes.

## Install

Add the xiaolai marketplace and install the plugin with the Codex CLI:

```bash
codex plugin marketplace add xiaolai/nlpm
codex plugin add nlpm@xiaolai
```

For local development, clone the repository and run Codex from its root. Codex discovers the canonical skills through `.agents/skills`, project subagents through `.codex/agents`, and the advisory edit hook through `.codex/hooks.json`.

Requirements:

- Codex CLI 0.147.0 or newer
- Python 3.11+ for `bin/nlpm-check` and report tooling
- `OPENAI_API_KEY` for GitHub Actions that invoke Codex

## Commands

| Codex skill | Purpose |
|---|---|
| `$nlpm-ls` | Discover and inventory NL artifacts |
| `$nlpm-score` | Score quality on a 100-point scale |
| `$nlpm-check` | Check cross-artifact consistency |
| `$nlpm-fix` | Apply safe mechanical fixes and rescore |
| `$nlpm-trend` | Compare score history |
| `$nlpm-test` | Run NL-TDD specifications |
| `$nlpm-init` | Initialize `.codex/nlpm.local.md` and a baseline |
| `$nlpm-security-scan` | Inspect executable surfaces and dependencies |
| `$nlpm-vocab-init` | Bootstrap a controlled-vocabulary registry |
| `$nlpm-vocab-drift` | Run registry-free drift analysis |
| `$nlpm-report` | Render a self-contained HTML report |
| `$nlpm-spec-sync` | Compare tool overlays with current official specifications |

Examples:

```text
$nlpm-ls
$nlpm-score
$nlpm-score --changed
$nlpm-score .codex/agents/scorer.toml
$nlpm-check
$nlpm-report
```

`$nlpm-score --changed` uses `git diff --name-only HEAD`, classifies only changed NL artifacts, delegates scorer and vague-word passes in parallel, prints the normal score report, and writes a `changed` snapshot to `.codex/nlpm-history.json`.

## Architecture

```text
.codex-plugin/plugin.json       Codex plugin manifest
.agents/skills                  link to the canonical skills directory
.agents/plugins/marketplace.json
.codex/agents/*.toml            eight role-specific subagent definitions
.codex/hooks.json               PostToolUse advisory hook
.codex/config.toml              hooks + multi-agent project configuration
skills/nlpm/                    one canonical, publishable skill tree
  {12 command skills}/          explicit $nlpm-* workflows
  workflow-core/                discovery, classification, history contracts
  {knowledge skills}/           rules, scoring, conventions, authoring guidance
scripts/check-artifact.py       fail-open Codex hook implementation
bin/nlpm-check                  stdlib-only deterministic validator
```

Named subagent TOMLs are active when developing this repository. Installed command skills also have a defined fallback: they spawn a generic Codex subagent and pass the bundled role's `developer_instructions`, sandbox policy, and reasoning effort. This keeps the packaged plugin functional on Codex surfaces that do not activate repository-local subagent files from a plugin.

Runtime state is written only to `.codex/`:

- `.codex/nlpm.local.md`
- `.codex/nlpm-history.json`
- `.codex/nlpm-reports/`

On first use, NLPM may read legacy `.claude/nlpm.local.md` or `.claude/nlpm-history.json` once and import valid settings or snapshots. It never writes back to the legacy path.

## Standalone validator

`bin/nlpm-check` is a single Python 3.11+ file using only the standard library. It validates manifest paths, skill registration, frontmatter, and hook event names for Codex plugins while retaining static checks for legacy Claude manifests.

```bash
python3 bin/nlpm-check .
python3 bin/nlpm-check --json .
python3 -m unittest tests.test_nlpm_check
```

Pre-commit and CI templates live in `templates/`.

## Development

```bash
python3 -m unittest discover -s tests -p "test_*.py"
python3 -m unittest tests.test_nlpm_check
python3 bin/nlpm-check .
```

Before a release, update `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json` together. The pre-release gate uses `openai/codex-action@v1`; Auditor workflows require `OPENAI_API_KEY` and any workflow-specific GitHub token.

See [docs/for-authors.md](docs/for-authors.md), [the migration matrix](analysis/codex-migration-matrix.md), and [nlpm.com](https://nlpm.com).

## License

ISC
