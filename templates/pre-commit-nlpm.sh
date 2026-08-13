#!/usr/bin/env bash
# Pre-commit hook for Codex plugin and NL artifact authors.
#
# Runs nlpm-check (the deterministic NLPM validator) against staged changes
# and blocks the commit on high-confidence findings.
#
# Installation:
#   1. Place this file at .git/hooks/pre-commit in your plugin repo
#   2. chmod +x .git/hooks/pre-commit
#   3. Place nlpm-check on PATH, OR set NLPM_CHECK_BIN below to its path
#
# To bypass (not recommended): git commit --no-verify

set -euo pipefail

# Locate nlpm-check
NLPM_CHECK_BIN="${NLPM_CHECK_BIN:-nlpm-check}"
if ! command -v "$NLPM_CHECK_BIN" >/dev/null 2>&1; then
    # Prefer a repository copy, then a conventional user binary location.
    REPO_BIN="$(git rev-parse --show-toplevel 2>/dev/null)/bin/nlpm-check"
    for candidate in "$REPO_BIN" "$HOME/.local/bin/nlpm-check"; do
        if [[ -n "$candidate" && -x "$candidate" ]]; then
            NLPM_CHECK_BIN="$candidate"
            break
        fi
    done
fi

if ! command -v "$NLPM_CHECK_BIN" >/dev/null 2>&1 && [[ ! -x "$NLPM_CHECK_BIN" ]]; then
    echo "pre-commit-nlpm: nlpm-check not found on PATH" >&2
    echo "  install: https://github.com/xiaolai/nlpm#install-the-binary" >&2
    echo "  or set NLPM_CHECK_BIN=/path/to/nlpm-check" >&2
    exit 1
fi

# Only run if the commit touches plugin artifacts.
# Bash case-pattern `*` matches across slashes, so the patterns below
# also cover nested layouts (e.g. multi-plugin monorepos with
# plugins/<sub>/agents/foo.md). nlpm-check itself walks the tree and
# auto-detects multi-plugin layouts (v0.8.5+).
STAGED=$(git diff --cached --name-only --diff-filter=ACMR)
RELEVANT=0
while IFS= read -r file; do
    case "$file" in
        *.codex-plugin/plugin.json|*.agents/plugins/marketplace.json) RELEVANT=1 ;;
        *.claude-plugin/plugin.json|*.claude-plugin/marketplace.json) RELEVANT=1 ;; # static audit target
        *skills/*SKILL.md) RELEVANT=1 ;;
        *.codex/agents/*.toml) RELEVANT=1 ;;
        *agents/*.md) RELEVANT=1 ;;
        *commands/*.md) RELEVANT=1 ;;
        *hooks/hooks.json|*hooks.json|*.mcp.json) RELEVANT=1 ;;
    esac
done <<< "$STAGED"

if [[ "$RELEVANT" -eq 0 ]]; then
    exit 0
fi

# Run the check against a snapshot of the staged content (the exact
# bytes that would land in the commit), not the working tree. The
# working tree can include unstaged edits that mask staged regressions.
STAGE_DIR=$(mktemp -d)
trap 'rm -rf "$STAGE_DIR"' EXIT
git checkout-index --prefix="$STAGE_DIR/" -a 2>/dev/null || {
    # Fall back to working-tree check if checkout-index fails (older git,
    # detached scenarios, etc.). Document the fallback.
    echo "pre-commit-nlpm: warning — could not snapshot index, checking working tree" >&2
    "$NLPM_CHECK_BIN" .
    exit $?
}
"$NLPM_CHECK_BIN" "$STAGE_DIR"
