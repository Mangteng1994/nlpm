"""Regression gates for the Codex-only NLPM runtime and package."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tomllib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
COMMANDS = (
    "ls",
    "score",
    "check",
    "fix",
    "trend",
    "test",
    "init",
    "security-scan",
    "vocab-init",
    "vocab-drift",
    "report",
    "spec-sync",
)
AGENTS = (
    "scanner",
    "scorer",
    "checker",
    "vague-scanner",
    "tester",
    "security-scanner",
    "vocab-drift-scanner",
    "spec-researcher",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class CommandSkillTests(unittest.TestCase):
    def test_all_twelve_command_skills_have_success_empty_and_error_contracts(self) -> None:
        for command in COMMANDS:
            with self.subTest(command=command):
                path = ROOT / "skills" / "nlpm" / command / "SKILL.md"
                self.assertTrue(path.is_file())
                body = path.read_text(encoding="utf-8")
                self.assertIn(f"name: {command}", body)
                self.assertIn(f"$nlpm-{command}", body)
                self.assertRegex(body.lower(), r"empty|no arguments|no artifacts|current working directory")
                self.assertRegex(body.lower(), r"error|not found|fail")
                self.assertRegex(body, r"(?m)^## .+")

    def test_score_changed_parallel_history_contract(self) -> None:
        body = read("skills/nlpm/score/SKILL.md")
        for token in (
            "--changed",
            "git diff --name-only HEAD",
            "in parallel",
            "scorer",
            "vague-scanner",
            ".codex/nlpm-history.json",
            "append-history.md",
        ):
            self.assertIn(token, body)

    def test_state_writes_are_codex_only(self) -> None:
        bodies = "\n".join(
            (ROOT / "skills" / "nlpm" / name / "SKILL.md").read_text(encoding="utf-8")
            for name in COMMANDS
        )
        self.assertNotIn("Write `.claude/", bodies)
        self.assertNotIn("Create `.claude/", bodies)
        self.assertNotIn(".claude/nlpm-reports", bodies)
        self.assertIn("read it once as migration input", bodies)

    def test_shared_contracts_cover_discovery_classification_and_history(self) -> None:
        discover = read("skills/nlpm/workflow-core/references/discover.md")
        classify = read("skills/nlpm/workflow-core/references/classify.md")
        history = read("skills/nlpm/workflow-core/references/append-history.md")
        self.assertIn(".codex/agents/*.toml", discover)
        self.assertIn("static Claude audit targets", discover)
        self.assertIn("codex-agent", classify)
        self.assertIn("atomically replace", history)
        self.assertIn("read the legacy JSON", history)
        self.assertIn("Never write history or configuration under `.claude/`", history)


class SubagentTests(unittest.TestCase):
    def test_all_subagent_definitions_parse_and_preserve_policy(self) -> None:
        for name in AGENTS:
            with self.subTest(agent=name):
                path = ROOT / ".codex" / "agents" / f"{name}.toml"
                with path.open("rb") as handle:
                    data = tomllib.load(handle)
                self.assertEqual(name, data["name"])
                self.assertGreaterEqual(len(data["description"]), 40)
                self.assertNotEqual("|", data["description"].strip())
                self.assertEqual("read-only", data["sandbox_mode"])
                self.assertIn(data["model_reasoning_effort"], {"low", "high"})
                self.assertIn("Output", data["developer_instructions"])
                self.assertNotRegex(data.get("model", ""), r"(?i)claude|anthropic")

    def test_subagents_load_their_required_canonical_knowledge(self) -> None:
        expected = {
            "scanner": ("conventions/SKILL.md", "workflow-core/references"),
            "scorer": ("scoring", "conventions-codex", "vocabulary"),
            "checker": ("conventions", "conventions-codex", "vocabulary"),
            "tester": ("testing", "scoring"),
            "security-scanner": ("security/SKILL.md",),
            "vocab-drift-scanner": ("vocabulary", "conventions"),
        }
        for name, references in expected.items():
            with self.subTest(agent=name):
                body = read(f".codex/agents/{name}.toml")
                self.assertIn("${PLUGIN_ROOT}", body)
                for reference in references:
                    self.assertIn(reference, body)

    def test_installed_plugin_has_generic_subagent_fallback(self) -> None:
        core = read("skills/nlpm/workflow-core/SKILL.md")
        self.assertIn("generic Codex subagent", core)
        self.assertIn("developer_instructions", core)
        self.assertIn("${PLUGIN_ROOT}/.codex/agents/<role>.toml", core)


class HookTests(unittest.TestCase):
    def run_hook(self, payload: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check-artifact.py")],
            input=json.dumps(payload),
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )

    def test_hook_manifest_uses_current_codex_contract(self) -> None:
        hooks = json.loads(read(".codex/hooks.json"))
        entry = hooks["hooks"]["PostToolUse"][0]
        self.assertIn("apply_patch", entry["matcher"])
        handler = entry["hooks"][0]
        self.assertIn("${PLUGIN_ROOT}", handler["command"])
        self.assertIn("commandWindows", handler)

    def test_hook_target_file_returns_additional_context(self) -> None:
        result = self.run_hook(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "apply_patch",
                "tool_input": {"command": "*** Update File: skills/demo/SKILL.md\n"},
            }
        )
        self.assertEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("PostToolUse", payload["hookSpecificOutput"]["hookEventName"])
        self.assertIn("$nlpm-score", payload["hookSpecificOutput"]["additionalContext"])

    def test_hook_non_target_is_silent(self) -> None:
        result = self.run_hook({"tool_input": {"file_path": "src/app.py"}})
        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertEqual("", result.stderr)

    def test_hook_malformed_input_fails_open(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check-artifact.py")],
            input="{not-json",
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stdout)


class PackageAndAutomationTests(unittest.TestCase):
    def test_legacy_runtime_delivery_surfaces_are_removed(self) -> None:
        for relative in (
            ".claude-plugin",
            ".claude",
            "CLAUDE.md",
            ".gemini",
            "GEMINI.md",
            "commands",
            "agents",
            "hooks",
            "codex",
            "scripts/check-artifact.sh",
        ):
            with self.subTest(path=relative):
                target = ROOT / relative
                if target.is_dir():
                    self.assertFalse(any(path.is_file() for path in target.rglob("*")))
                else:
                    self.assertFalse(target.exists())

    def test_manifest_paths_exist_and_all_publishable_skills_are_registered(self) -> None:
        manifest = json.loads(read(".codex-plugin/plugin.json"))
        self.assertEqual("2.0.4", manifest["version"])
        for key in ("skills", "hooks"):
            target = (ROOT / manifest[key]).resolve()
            self.assertTrue(target.exists(), f"missing manifest target {key}: {target}")
            self.assertTrue(target.is_relative_to(ROOT.resolve()))
        skill_root = (ROOT / manifest["skills"]).resolve()
        published = {path.resolve() for path in skill_root.rglob("SKILL.md")}
        on_disk = {path.resolve() for path in (ROOT / "skills" / "nlpm").rglob("SKILL.md")}
        self.assertEqual(on_disk, published)
        self.assertGreaterEqual(len(published), len(COMMANDS) + 17)

    def test_marketplace_and_project_config_parse(self) -> None:
        marketplace = json.loads(read(".agents/plugins/marketplace.json"))
        self.assertEqual("2.0.4", marketplace["plugins"][0]["version"])
        with (ROOT / ".codex" / "config.toml").open("rb") as handle:
            config = tomllib.load(handle)
        self.assertTrue(config["features"]["hooks"])
        self.assertTrue(config["features"]["multi_agent"])
        self.assertNotIn("mcp_servers", config)

    def test_auditor_automation_uses_codex_action_and_openai_key(self) -> None:
        workflow_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / ".github" / "workflows").glob("*.yml")
        )
        workflow_text += "\n" + read("auditor/README.md")
        workflow_text += "\n" + read("auditor/scripts/cla-gate-messages/cla_author_missing.md")
        workflow_text += "\n" + read("auditor/scripts/vendor_default_filter.py")
        self.assertIn("openai/codex-action@v1", workflow_text)
        for forbidden in (
            "anthropics/claude-code-action",
            "CLAUDE_CODE_OAUTH_TOKEN",
            "claude_code_oauth_token",
            "claude_args:",
        ):
            self.assertNotIn(forbidden, workflow_text)

    def test_auditor_pr_writers_have_pull_request_permission(self) -> None:
        for workflow in (ROOT / ".github" / "workflows").glob("auditor-*.yml"):
            text = workflow.read_text(encoding="utf-8")
            if "commit-via-pr.sh" not in text:
                continue
            with self.subTest(workflow=workflow.name):
                permissions = text.split("permissions:\n", 1)[1].split("\n\n", 1)[0]
                permission_keys = [
                    line.strip().split(":", 1)[0]
                    for line in permissions.splitlines()
                    if line.startswith("  ") and ":" in line
                ]
                self.assertEqual(len(permission_keys), len(set(permission_keys)))
                self.assertIn("issues: write", permissions)
                self.assertIn("pull-requests: write", permissions)

    def test_user_docs_are_codex_only(self) -> None:
        docs = "\n".join(
            read(path)
            for path in (
                "README.md",
                "docs/for-authors.md",
                "site/install.md",
                "site/how-to-use-it.md",
                "PRIVACY.md",
                "RULES.md",
            )
        )
        for forbidden in ("claude plugin", "/nlpm:", "CLAUDE_CODE_OAUTH_TOKEN"):
            self.assertNotIn(forbidden, docs)
        self.assertIn("codex plugin add nlpm@mangteng1994", docs)

    def test_migration_matrix_has_twelve_rows_and_release_gate(self) -> None:
        matrix = read("analysis/codex-migration-matrix.md")
        for command in COMMANDS:
            self.assertIn(f"`commands/{command}.md`", matrix)
            self.assertIn(f"`$nlpm-{command}`", matrix)
        self.assertNotIn("IN PROGRESS", matrix)
        self.assertNotIn("| BLOCKED |", matrix)
        self.assertEqual(20, matrix.count("| PASS |"))
        self.assertIn("## Release rule", matrix)

    def test_standard_library_checker_remains_dependency_free(self) -> None:
        body = read("bin/nlpm-check")
        for third_party in ("yaml", "click", "pydantic", "requests"):
            self.assertNotRegex(body, rf"(?m)^\s*(?:from|import)\s+{third_party}\b")


if __name__ == "__main__":
    unittest.main()
