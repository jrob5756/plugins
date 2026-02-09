# Claude Code Plugins Workspace

This is a Claude Code plugin marketplace repository. Read this file before making any changes.

## Repository Structure

```
.claude-plugin/marketplace.json   # Plugin marketplace registry (MUST be kept in sync)
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json    # Plugin manifest (name, version, metadata)
    .mcp.json                     # MCP server configuration
    agents/                       # Agent definitions
      <agent-name>.md             # Agent markdown with frontmatter
    commands/                     # Slash commands (optional)
    skills/                       # Reference skills (optional)
```

## When Adding a New Plugin

After creating the plugin directory and files, you **MUST** also:

1. Add the plugin entry to `.claude-plugin/marketplace.json` in the `plugins` array
2. Bump the `version` field in `marketplace.json` (patch for fixes, minor for new plugins)
3. Update `metadata.description` if the new plugin adds a new category

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

- Plugin names should be lowercase kebab-case
- MCP server keys in `.mcp.json` should be short, descriptive identifiers
- Agent descriptions should clearly state when to use the agent
- Never commit secrets, API keys, or `.env` files
