# Claude Plugins

Personal Claude Code plugins for web research and browser automation.

## Plugins

### web-searcher

Web research specialist agent with supporting MCP servers:
- **web-search** - DuckDuckGo, Bing, Exa search engines
- **context7** - Library/framework documentation lookup
- **ms-learn** - Microsoft Learn documentation

### playwright

Browser automation specialist agent with Playwright MCP for:
- Web scraping and content extraction
- Form filling and interactions
- Multi-step browser workflows

## Installation

```bash
# Add this marketplace
/plugin marketplace add jrob5756/claude-plugins

# Install plugins
/plugin install web-searcher@jason-tools
/plugin install playwright@jason-tools
```

## Usage

Both plugins are designed to be used via the Task tool as subagents:

```
# Web research
Use the web-searcher agent to research [topic]

# Browser automation
Use the playwright agent to navigate to [url] and [action]
```

The CLAUDE.md files in each plugin enforce this pattern - direct MCP tool calls are discouraged in favor of the specialized agents.
