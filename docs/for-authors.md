# NLPM for Codex plugin authors

NLPM combines interactive Codex skills with a deterministic Python validator. The interactive layer handles judgment-heavy scoring and cross-artifact reasoning; `bin/nlpm-check` supplies a fast, repeatable floor for local hooks and CI.

## Interactive workflow

Install the Codex plugin, start Codex in the repository, then run:

```text
$nlpm-init
$nlpm-ls
$nlpm-score --changed
$nlpm-check
$nlpm-test
$nlpm-report
```

Configuration lives at `.codex/nlpm.local.md`. Score history is appended atomically to `.codex/nlpm-history.json`; reports are written below `.codex/nlpm-reports/`.

The scorer classifies every path before applying a tool overlay. Codex artifacts receive Tier 2-Codex checks. Claude Code and Antigravity artifacts can still receive their respective static overlays; NLPM does not invoke those runtimes.

## Deterministic local check

```bash
python3 bin/nlpm-check .
python3 bin/nlpm-check --strict .
python3 bin/nlpm-check --json .
```

The binary uses only Python 3.11+ standard-library modules. It verifies:

- manifest JSON and declared-path existence;
- every publishable `SKILL.md` is reachable from the manifest skill root;
- required skill frontmatter and name/directory agreement;
- supported hook event names and casing;
- nested plugin isolation;
- legacy Claude manifests when they appear as static audit inputs.

For pre-commit, copy `templates/pre-commit-nlpm.sh`. For GitHub Actions, copy `templates/workflows/nlpm-check.yml`.

## Codex package layout

```text
.codex-plugin/plugin.json
.agents/plugins/marketplace.json
.agents/skills -> ../skills/nlpm
.codex/agents/*.toml
.codex/hooks.json
skills/nlpm/<skill>/SKILL.md
```

Keep one canonical skill tree. Do not mirror it under `.codex/skills` or another generated directory. The plugin manifest points to `skills/nlpm/`, and `.agents/skills` exposes that same tree during repository development.

Codex plugin packaging currently activates skills and hooks but does not make plugin-private project agent TOMLs globally addressable. NLPM therefore ships both the `.codex/agents/*.toml` role definitions and an installed-plugin fallback: a command skill spawns a generic Codex subagent and passes the role's `developer_instructions`, reasoning effort, and sandbox policy.

## Vocabulary discipline

Run `$nlpm-vocab-init` to create a vocabulary skill and registry, then enable R51 in `.codex/nlpm.local.md`:

```yaml
rule_overrides:
  R51:
    enabled: true
    vocabulary_skill: skills/<plugin>/vocabulary/
```

`$nlpm-vocab-drift` is the registry-free advisory alternative. It never gates scoring or writes a registry.

## Release verification

```bash
python3 -m unittest discover -s tests -p "test_*.py"
python3 -m unittest tests.test_nlpm_check
python3 bin/nlpm-check .
```

Update the version in `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json` together. Do not publish unless the migration matrix and deletion gate are clean.
