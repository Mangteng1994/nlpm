---
name: writing-hooks
description: "Write or review Codex hooks using current events, matchers, JSON I/O, portable plugin paths, and fail-open advisory behavior."
---

# Writing Codex hooks

Codex reads `hooks.json` beside active config layers, including `.codex/hooks.json`, and installed plugins may declare a hook path in `.codex-plugin/plugin.json`. Use one representation per layer.

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "^apply_patch$|Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "python3 \"${PLUGIN_ROOT}/scripts/review_edit.py\"",
        "commandWindows": "python \"${PLUGIN_ROOT}\\scripts\\review_edit.py\"",
        "timeout": 5
      }]
    }]
  }
}
```

Hook commands receive JSON on stdin. For file edits, the canonical tool name is `apply_patch`; it also matches aliases `Edit` and `Write`. Its input contains the patch in `tool_input.command`, not a guaranteed `file_path`. Shell calls match as `Bash`.

For `PostToolUse`, return JSON containing `systemMessage` and `hookSpecificOutput.additionalContext` when advice should reach the model. Plain stdout is ignored. Advisory hooks must catch malformed input and internal exceptions, emit nothing, and exit zero. Use exit 2 only for an intentionally blocking policy.

Installed plugin hooks resolve files with `${PLUGIN_ROOT}` and writable plugin data with `${PLUGIN_DATA}`. Include `commandWindows` when the default command is POSIX-specific. Never hardcode a user path.

Test at least:

- a matching canonical `apply_patch` payload;
- a non-target file with empty stdout;
- malformed JSON with exit zero;
- Windows and POSIX path separators;
- manifest path existence and valid event casing.
