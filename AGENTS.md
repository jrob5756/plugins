# Plugin Marketplace Workspace

This is a dual-compatible plugin marketplace repository for **Claude Code** and **VS Code Copilot**. Both tools share the same plugin format — the marketplace registry exists at both `.claude-plugin/marketplace.json` and `.github/plugin/marketplace.json` (must be kept in sync).

## Repository Structure

```
.claude-plugin/marketplace.json   # Plugin marketplace registry (MUST be kept in sync)
.github/
  plugin/
    marketplace.json              # Copy of .claude-plugin/marketplace.json (keep in sync)
  copilot-instructions.md         # Copilot-native always-on instructions
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json    # Plugin manifest (name, version, metadata)
    .mcp.json                     # MCP server configuration
    agents/                       # Agent definitions
      <agent-name>.md             # Agent markdown with frontmatter
    commands/                     # Slash commands (optional)
    skills/                       # Reference skills (optional)
      <skill-name>/
        SKILL.md                  # Skill definition (agentskills.io standard)
        references/               # Supporting documentation
```

## Best Practices

- [Agent Best Practices](./docs/agent-best-practices.md) - Creating custom agents: frontmatter, tools, model selection, security
- [Skill Best Practices](./docs/skill-best-practices.md) - Creating agent skills: SKILL.md structure, descriptions, triggering

## Plugin Agents

Each plugin defines its agent in `plugins/<name>/agents/<name>.md`:

- [web-searcher](./plugins/web/agents/web-searcher.md) - Web research specialist
- [playwright](./plugins/playwright/agents/playwright.md) - Browser automation with Playwright
- [ms-tools](./plugins/ms-tools/agents/ms-tools.md) - Microsoft Learn, WorkIQ, and EngHub
- [ado](./plugins/ado/agents/ado.md) - Azure DevOps work items, repos, pipelines, wikis
- [git-tools](./plugins/git-tools/) - Git workflow commands and GitHub CLI skill
- [dependabot](./plugins/dependabot/) - Dependabot PR review, fix, and merge automation

## When Adding a New Plugin

After creating the plugin directory and files, you **MUST** also:

1. Add the plugin entry to **both** `.claude-plugin/marketplace.json` and `.github/plugin/marketplace.json`
2. Bump the `version` field in `marketplace.json` (patch for fixes, minor for new plugins)
3. Update `metadata.description` if the new plugin adds a new category
4. Include `agents` and/or `skills` arrays in the plugin's `plugin.json` for explicit discoverability

## When Modifying an Existing Plugin

- Bump the `version` in that plugin's `.claude-plugin/plugin.json`
- If the change is significant, bump `marketplace.json` version too

## Agent Markdown Format

Agent files use YAML frontmatter with these fields:
- `name` - Agent identifier
- `description` - When the agent should be invoked
- `tools` - Comma-separated list of tools the agent can use (prefixed with `mcp__plugin_<plugin>_<server>__`)
- `model` - Model to use (e.g. `haiku`, `claude-opus-4.5`)
- `color` - Agent color in UI

## Conventions

- Plugin names must be lowercase kebab-case
- MCP server keys in `.mcp.json` should be short, descriptive identifiers
- Agent descriptions should clearly state when to use the agent
- Never commit secrets, API keys, or `.env` files
- When adding a new plugin, update both `.claude-plugin/marketplace.json` and `.github/plugin/marketplace.json` (keep in sync), plus the plugin's own `plugin.json`

## Checklist for New Plugins

- [ ] Create `plugins/<name>/.claude-plugin/plugin.json` with `agents`/`skills` arrays
- [ ] Create `plugins/<name>/.mcp.json` with server config
- [ ] Create `plugins/<name>/agents/<name>.md` with frontmatter and instructions
- [ ] **Add entry to both [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json) and [`.github/plugin/marketplace.json`](./.github/plugin/marketplace.json)**
- [ ] Bump marketplace version
- [ ] Update this file's agent list
