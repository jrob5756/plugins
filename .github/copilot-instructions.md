# Plugin Marketplace Workspace

This is a dual-compatible plugin marketplace repository for **Claude Code** and **VS Code Copilot**.

Read [AGENTS.md](../AGENTS.md) for full workspace conventions and structure.

## Key Rules

- Plugin names must be lowercase kebab-case
- MCP server keys in `.mcp.json` should be short, descriptive identifiers
- Agent descriptions should clearly state when to use the agent
- Never commit secrets, API keys, or `.env` files
- When adding a new plugin, update both `.claude-plugin/marketplace.json` and `.github/plugin/marketplace.json` (keep in sync), plus the plugin's own `plugin.json`
