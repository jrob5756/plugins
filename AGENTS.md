# Agents

See [CLAUDE.md](./CLAUDE.md) for full workspace conventions and structure.

## Plugin Agents

Each plugin defines its agent in `plugins/<name>/agents/<name>.md`:

- [web-searcher](./plugins/web-searcher/agents/web-searcher.md) - Web research specialist
- [playwright](./plugins/playwright/agents/playwright.md) - Browser automation with Playwright
- [ms-tools](./plugins/ms-tools/agents/ms-tools.md) - Microsoft Learn, WorkIQ, and EngHub
- [ado](./plugins/ado/agents/ado.md) - Azure DevOps work items, repos, pipelines, wikis
- [git-tools](./plugins/git-tools/) - Git workflow commands and GitHub CLI skill

## Checklist for New Plugins

- [ ] Create `plugins/<name>/.claude-plugin/plugin.json`
- [ ] Create `plugins/<name>/.mcp.json` with server config
- [ ] Create `plugins/<name>/agents/<name>.md` with frontmatter and instructions
- [ ] **Add entry to [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json)**
- [ ] Bump marketplace version
- [ ] Update this file's agent list
