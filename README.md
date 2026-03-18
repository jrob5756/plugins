# Plugin Marketplace

Personal plugin marketplace for **Claude Code** and **VS Code Copilot** — my collection of agents and skills for web research, browser automation, Microsoft tools, Azure DevOps, git workflows, and more.

## Plugins

| Plugin | Description |
|--------|-------------|
| **web** | Web research agent — DuckDuckGo, Bing, Exa search engines |
| **playwright** | Browser automation agent — scraping, form filling, multi-step workflows |
| **ms-tools** | Microsoft Learn, WorkIQ, and EngHub MCP servers |
| **ado** | Azure DevOps — work items, repos, PRs, pipelines, wikis |
| **git-tools** | Git workflow commands and GitHub CLI skill |
| **conductor** | Workflow orchestration for multi-agent automation |
| **dependabot** | Dependabot PR review, fix, and merge automation |

## Installation

### Claude Code

```bash
/plugin marketplace add jrob5756/claude-plugins
/plugin install web@jason-tools
```

### VS Code Copilot

```jsonc
// settings.json
{
  "chat.plugins.marketplaces": ["jrob5756/claude-plugins"]
}
```

Browse via **Extensions** → `@agentPlugins`, or `Chat: Install Plugin From Source`.

## Format

Shared plugin format compatible with both Claude Code and VS Code Copilot:

- `.claude-plugin/marketplace.json` — primary registry
- `.github/plugin/marketplace.json` — copy for Copilot-native discovery (keep in sync)
- Skills follow the [agentskills.io](https://agentskills.io) open standard
