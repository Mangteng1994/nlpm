"""Tests for the v0.8.17 exemplar pipeline helpers.

Coverage:
1. `load_exemplars_by_rule` (rule-health.py) parses exemplifies: frontmatter
   into rule_id → [slug] correctly, handling missing files, malformed
   frontmatter, and the realistic multi-rule case.
2. `registry_score` and `registry_exemplar_published` (batch-process.py)
   read the registry safely with missing/malformed shapes.
3. The exemplar-writing prompt under auditor/prompts/write-exemplar.md
   stays in sync with the workflow (matching template tokens).

Doesn't cover phase0_label_exemplars or the auditor-exemplar.yml workflow
itself — both require gh CLI / GHA mocking, deferred to integration tests.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RULE_HEALTH = REPO_ROOT / "auditor" / "scripts" / "rule-health.py"
BATCH_PROCESS = REPO_ROOT / "auditor" / "scripts" / "batch-process.py"
EXEMPLAR_PROMPT = REPO_ROOT / "auditor" / "prompts" / "write-exemplar.md"
EXEMPLAR_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "auditor-exemplar.yml"


def _load_module(name: str, path: Path):
    """Load a hyphenated-filename script as a module. See test_validate_rule_ids.py."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"could not load {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class LoadExemplarsByRule(unittest.TestCase):
    """rule-health.py: load_exemplars_by_rule."""

    def setUp(self):
        self.mod = _load_module("rule_health", RULE_HEALTH)

    def test_missing_dir_returns_empty(self):
        cwd = os.getcwd()
        try:
            # Windows file watchers can briefly retain a handle after cwd leaves.
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
                os.chdir(td)
                # EXEMPLARS_DIR is relative to cwd; missing → empty dict
                self.assertEqual(self.mod.load_exemplars_by_rule(), {})
        finally:
            os.chdir(cwd)

    def test_parses_multi_rule_exemplar(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
                os.chdir(td)
                d = Path("auditor/exemplars")
                d.mkdir(parents=True)
                (d / "foo-bar.md").write_text("""---
slug: foo-bar
repo: foo/bar
audited: 2026-05-14
commit_sha: abc1234
score: 95
exemplifies:
  - R04
  - R05
  - R06
---

# Exemplar: foo/bar

(body)
""")
                result = self.mod.load_exemplars_by_rule()
                self.assertEqual(set(result.keys()), {"R04", "R05", "R06"})
                self.assertEqual(result["R04"], ["foo-bar"])
                self.assertEqual(result["R05"], ["foo-bar"])
        finally:
            os.chdir(cwd)

    def test_multiple_exemplars_aggregate_per_rule(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
                os.chdir(td)
                d = Path("auditor/exemplars")
                d.mkdir(parents=True)
                for slug in ("a-x", "b-y"):
                    (d / f"{slug}.md").write_text(f"""---
slug: {slug}
repo: x/{slug}
exemplifies:
  - R04
---
""")
                result = self.mod.load_exemplars_by_rule()
                self.assertEqual(sorted(result["R04"]), ["a-x", "b-y"])
        finally:
            os.chdir(cwd)

    def test_missing_exemplifies_silently_skipped(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
                os.chdir(td)
                d = Path("auditor/exemplars")
                d.mkdir(parents=True)
                (d / "no-frontmatter.md").write_text("# not an exemplar\n")
                (d / "no-exemplifies.md").write_text("""---
slug: no-exemplifies
---
""")
                self.assertEqual(self.mod.load_exemplars_by_rule(), {})
        finally:
            os.chdir(cwd)


class BatchProcessRegistryHelpers(unittest.TestCase):
    """batch-process.py: registry_score and registry_exemplar_published."""

    def setUp(self):
        self.mod = _load_module("batch_process", BATCH_PROCESS)

    def test_registry_score_present(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
                os.chdir(td)
                reg = Path("auditor/registry")
                reg.mkdir(parents=True)
                (reg / "repos.json").write_text(json.dumps({
                    "repos": {"foo/bar": {"score": 92, "security": "CLEAR"}}
                }))
                # The module reads REGISTRY_PATH = "auditor/registry/repos.json"
                # which is relative; we're already in td so this works.
                self.assertEqual(self.mod.registry_score("foo/bar"), 92)
                self.assertEqual(self.mod.registry_score("missing/repo"), 0)
        finally:
            os.chdir(cwd)

    def test_registry_score_handles_malformed(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
                os.chdir(td)
                reg = Path("auditor/registry")
                reg.mkdir(parents=True)
                (reg / "repos.json").write_text("not valid json {")
                self.assertEqual(self.mod.registry_score("foo/bar"), 0)
        finally:
            os.chdir(cwd)

    def test_registry_exemplar_published_flag(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
                os.chdir(td)
                reg = Path("auditor/registry")
                reg.mkdir(parents=True)
                (reg / "repos.json").write_text(json.dumps({
                    "repos": {
                        "foo/published": {"exemplar_published": True},
                        "foo/not-yet": {"score": 95},
                    }
                }))
                self.assertTrue(self.mod.registry_exemplar_published("foo/published"))
                self.assertFalse(self.mod.registry_exemplar_published("foo/not-yet"))
                self.assertFalse(self.mod.registry_exemplar_published("foo/missing"))
        finally:
            os.chdir(cwd)

    def test_exemplar_threshold_env(self):
        # The constant should be importable and an int
        self.assertIsInstance(self.mod.EXEMPLAR_THRESHOLD, int)
        # Default if env unset is 90
        self.assertGreaterEqual(self.mod.EXEMPLAR_THRESHOLD, 1)


class ExemplarPromptAndWorkflow(unittest.TestCase):
    """The prompt template tokens must match the workflow's sed substitutions."""

    def test_prompt_tokens_match_workflow_substitutions(self):
        self.assertTrue(EXEMPLAR_PROMPT.exists(), f"missing: {EXEMPLAR_PROMPT}")
        self.assertTrue(EXEMPLAR_WORKFLOW.exists(), f"missing: {EXEMPLAR_WORKFLOW}")
        prompt = EXEMPLAR_PROMPT.read_text()
        wf = EXEMPLAR_WORKFLOW.read_text()
        tokens = ["TARGET_REPO", "CLONE_DIR", "AUDIT_REPORT_PATH",
                  "EXEMPLAR_PATH", "SCORE", "COMMIT_SHA", "DATE_ISO"]
        for tok in tokens:
            with self.subTest(token=tok):
                self.assertIn("{{" + tok + "}}", prompt,
                              f"prompt missing token {{{{{tok}}}}}")
                self.assertIn("{{" + tok + "}}", wf,
                              f"workflow missing sed substitution for {tok}")

    def test_workflow_fires_on_correct_label(self):
        wf = EXEMPLAR_WORKFLOW.read_text()
        # case-study-clean is the trigger documented in batch-process.py phase0
        self.assertIn("case-study-clean", wf)
        # Not case-study-ready (which fires the article writer)
        self.assertNotIn("case-study-ready", wf)


if __name__ == "__main__":
    unittest.main()
