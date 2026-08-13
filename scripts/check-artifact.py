#!/usr/bin/env python3
"""Codex PostToolUse advisory hook for NL artifact edits.

The hook is deliberately fail-open: malformed input, unknown tool payloads, and
internal errors produce no output and exit successfully.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import PurePosixPath


PATCH_PATH = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)


def _paths(payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return []
    tool_input = payload.get("tool_input", payload.get("toolInput", {}))
    if not isinstance(tool_input, dict):
        return []
    found: list[str] = []
    for key in ("file_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            found.append(value)
    command = tool_input.get("command")
    if isinstance(command, str):
        found.extend(PATCH_PATH.findall(command))
    return found


def _is_artifact(raw_path: str) -> bool:
    path = raw_path.replace("\\", "/")
    parts = PurePosixPath(path).parts
    name = parts[-1] if parts else ""
    joined = "/" + "/".join(parts) + "/"
    if name in {"AGENTS.md", "CLAUDE.md", "GEMINI.md", ".mcp.json", "gemini-extension.json"}:
        return True
    if name == "SKILL.md" and ("/skills/" in joined or "/.agents/skills/" in joined):
        return True
    if name == "openai.yaml" and "/agents/" in joined:
        return True
    if name in {"plugin.json", "marketplace.json"} and (
        "/.codex-plugin/" in joined or "/.claude-plugin/" in joined or "/.agents/plugins/" in joined
    ):
        return True
    if "/.codex/agents/" in joined and name.endswith(".toml"):
        return True
    if path.endswith("/.codex/hooks.json") or path.endswith("/.codex/config.toml"):
        return True
    if "/commands/" in joined and name.endswith(".md"):
        return True
    if "/agents/" in joined and name.endswith(".md"):
        return True
    if "/hooks/" in joined and name.endswith(".json"):
        return True
    if "/.claude/rules/" in joined and name.endswith(".md"):
        return True
    if "/.gemini/commands/" in joined and name.endswith(".toml"):
        return True
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        matches = sorted({path for path in _paths(payload) if _is_artifact(path)})
        if not matches:
            return 0
        shown = ", ".join(matches[:3])
        if len(matches) > 3:
            shown += f" (+{len(matches) - 3} more)"
        message = f"NL artifact edited: {shown}. Run $nlpm-score on the changed path."
        json.dump(
            {
                "systemMessage": message,
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": message,
                },
            },
            sys.stdout,
        )
        sys.stdout.write("\n")
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

