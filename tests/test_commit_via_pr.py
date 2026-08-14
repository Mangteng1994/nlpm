"""Regression tests for the auditor bot PR commit helper."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "auditor" / "scripts" / "commit-via-pr.sh"


class CommitViaPrTests(unittest.TestCase):
    def test_missing_label_is_repaired_before_any_commit(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")

        ensure_function = script.index("ensure_auditor_bot_label()")
        create_label = script.index('gh label create "$LABEL"', ensure_function)
        ensure_call = script.index("ensure_auditor_bot_label\n", ensure_function)
        commit = script.index('commit -m "$MSG"')
        push = script.index('git push -u origin "$BRANCH"')
        create_pr = script.index('gh pr create', ensure_function)

        self.assertLess(ensure_function, create_label)
        self.assertLess(create_label, ensure_call)
        self.assertLess(ensure_call, commit)
        self.assertLess(ensure_call, push)
        self.assertLess(ensure_call, create_pr)


if __name__ == "__main__":
    unittest.main()
