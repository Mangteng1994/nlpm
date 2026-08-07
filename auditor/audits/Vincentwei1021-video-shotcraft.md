# NLPM Audit: Vincentwei1021/video-shotcraft
**Date**: 2026-04-06  |  **Artifacts**: 2  |  **Strategy**: single
**NL Score**: 100/100
**Security**: REVIEW
**Bugs**: 0  |  **Quality Issues**: 0  |  **Security Findings**: 5

## NL Score Summary
| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| .claude-plugin/plugin.json | Plugin manifest | 100 | None — required fields present, `skills` path resolves |
| SKILL.md | Skill | 100 | None — frontmatter complete, all cross-references resolve, no vague quantifiers found |

## Security Scan
| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 2 |
| Low | 3 |

### Execution Surface Inventory
| Surface | Files |
|---------|-------|
| Hooks | none |
| Scripts | `assets/scripts/capture-template.mjs`, `gallery/app.js`, `gallery/build-seo.py`, `gallery/fetch-media.sh`, `gallery/sync-from-cards.py` |
| MCP configs | none |
| Package manifests | `template/package.json` |

### Security Findings
| # | Severity | File | Line | Pattern | Description |
|---|----------|------|------|---------|-------------|
| 1 | Medium | gallery/app.js | 152 | unescaped-attribute-interpolation | `style.media.url` is interpolated directly into a `data-src="..."` attribute with no `escapeHtml()` call, unlike the sibling `title`/`sourceUrl` values in the same function that are escaped; a value containing `"` could break out of the attribute and inject markup/handlers. |
| 2 | Medium | gallery/app.js | 158 | unescaped-attribute-interpolation | Same unescaped `style.media.url` interpolation in the `<video data-src="...">` branch of `mediaMarkup()`. |
| 3 | Low | gallery/fetch-media.sh | 7 | network-call | `gh release download` fetches media assets from GitHub over the network; benign (hardcoded repo, no user-controlled input) but recorded per the execution-surface inventory. |
| 4 | Low | template/package.json | 17 | unpinned-semver | `@types/react` pinned with caret range `^19.2.17` while runtime deps (`remotion`, `react`) are pinned to exact versions. |
| 5 | Low | template/package.json | 18 | unpinned-semver | `typescript` pinned with caret range `^6.0.3`, inconsistent with the exact-pinned runtime dependencies. |

## Bugs (PR-worthy)
No bugs found.

## Security Fixes (PR-worthy, Medium/Low only)
| # | File | Issue | Suggested Fix |
|---|------|-------|---------------|
| 1 | gallery/app.js | `style.media.url` interpolated unescaped into `data-src` attribute (lines 152, 158) | Wrap with `escapeHtml(style.media.url)`, matching the existing pattern used for `sourceUrl` and `title` in the same file. |
| 2 | template/package.json | `@types/react` and `typescript` devDependencies use caret ranges while runtime deps are exact-pinned | Pin `@types/react` and `typescript` to exact versions for build reproducibility, consistent with `remotion`/`react`/`react-dom`. |

## Quality Issues (informational)
No quality issues found.

## Cross-Component
- `plugin.json`'s `skills: "./"` correctly resolves to the repo root, where `SKILL.md` lives with a matching `name: video-shotcraft`.
- Every file `SKILL.md` references (`template/TEMPLATE.md`, `references/pipeline.md`, `references/guided-free-creation.md`, `references/final-review.md`, `references/aesthetic-rules.md`, `references/sound-design.md`, `references/music-beat-sync.md`, `gallery/api/library.json`, `assets/audio/ATTRIBUTION.md`, `demos/_fixtures/Fixtures.tsx`, `gallery/library.html`) exists on disk — no broken references.
- The "104 张镜头配方卡" / "161 条动态样片" counts stated in `SKILL.md` match `gallery/api/library.json`'s computed stats exactly (`cardCount: 104`, `styleCount: 161`, `previewCount: 161`) and the on-disk count of `references/shots/*/*.md` (104 files) — no stale-count drift.
- No orphaned components found among the two audited NL artifacts.

## Recommendation
REVIEW — NL artifacts are fully clean (no bug or quality PRs needed). Submit a PR for the two Low-severity security fixes (unpinned devDependency versions); the two Medium-severity `escapeHtml()` gaps in `gallery/app.js` are low-exploitability today (data source is repo-controlled `library.json`) but are still worth a defensive-hardening PR — flag them in the PR description rather than treating as urgent.
