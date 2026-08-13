---
name: writing-plugins
description: "Design, package, validate, and document Codex plugins with one canonical skill tree, a current manifest, optional hooks or MCP, and a repository marketplace entry."
---

# Writing Codex plugins

A minimal skills plugin contains `.codex-plugin/plugin.json` and a skill root:

```json
{
  "name": "example",
  "version": "1.0.0",
  "description": "One concrete user outcome",
  "skills": "./skills/"
}
```

Add only capabilities the plugin ships. A plugin can include skills, MCP configuration, and hooks. Repository-local subagents live at `.codex/agents/*.toml`; when installed behavior depends on them, provide an explicit generic-subagent fallback from a skill because plugin packaging does not make project TOMLs globally addressable on every Codex surface.

Keep one source of truth. Point the manifest at the authored skill tree, and use `.agents/skills` only as a repository discovery link when necessary. Never maintain a second copied skill tree.

Plugin hook paths are `./`-prefixed, remain inside the plugin root, and may point to `.codex/hooks.json` or another bundled hook file. MCP servers use Codex-native configuration rather than a `.mcp.json` bridge.

Repository marketplace entries live at `.agents/plugins/marketplace.json` and identify a GitHub, Git, or local source. Update its version with the plugin manifest.

Validation checklist:

- parse every JSON, TOML, YAML, and frontmatter file;
- verify every manifest path exists and stays inside the plugin root;
- verify every publishable `SKILL.md` is registered exactly once;
- run representative explicit skill invocations, including empty and invalid input;
- simulate hook JSON and failure paths;
- run `python3 bin/nlpm-check .` when NLPM is available;
- search delivery docs and CI for removed runtime actions or secrets;
- never commit, push, publish, or mutate a marketplace without explicit authority.
