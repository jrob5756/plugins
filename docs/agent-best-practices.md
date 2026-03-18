# Custom Agent Best Practices

Synthesized from official documentation, community patterns, and workspace analysis.

## Sources

| Source | URL |
|--------|-----|
| VS Code Custom Agents Docs | https://code.visualstudio.com/docs/copilot/customization/custom-agents |
| GitHub Custom Agents Config Ref | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| VS Code Agent Tools | https://code.visualstudio.com/docs/copilot/agents/agent-tools |
| VS Code MCP Servers | https://code.visualstudio.com/docs/copilot/customization/mcp-servers |
| VS Code MCP Config Reference | https://code.visualstudio.com/docs/copilot/reference/mcp-configuration |
| VS Code Security | https://code.visualstudio.com/docs/copilot/security |
| Awesome Copilot Agents | https://github.com/github/awesome-copilot |
| Awesome Copilot Agent Guidelines | https://github.com/github/awesome-copilot/blob/main/instructions/agents.instructions.md |
| Claude Code Sub-Agents | https://code.claude.com/docs/en/sub-agents |
| Claude Code Plugins Reference | https://code.claude.com/docs/en/plugins-reference |
| GitHub Model Comparison | https://docs.github.com/en/copilot/reference/ai-models/model-comparison |

---

## YAML Frontmatter Reference

### Core Fields

| Field | Required | Notes |
|-------|----------|-------|
| `description` | **Yes** | Shown as placeholder text in chat input; drives automatic subagent delegation |
| `name` | No | Display name. Defaults to filename (without `.md` / `.agent.md`) |
| `tools` | No | Tools available to the agent. Omit = all tools; `[]` = no tools |
| `model` | No | Model name (string) or prioritized fallback list (array). Omit = user's picker selection |
| `agents` | No | Subagent names available. `*` for all (default), `[]` for none. Requires `agent` in `tools` |
| `argument-hint` | No | Hint text shown in chat input when agent is selected |

### Visibility & Invocation Controls

| Field | Default | Notes |
|-------|---------|-------|
| `user-invocable` | `true` | Set `false` to hide from agents dropdown (subagent-only) |
| `disable-model-invocation` | `false` | Set `true` to prevent automatic subagent delegation |
| `target` | — | `vscode` or `github-copilot`. Omit = available in both |

### Workflow Fields

| Field | Notes |
|-------|-------|
| `handoffs` | Suggested next-action buttons after a response completes (VS Code only) |
| `handoffs[].label` | Button display text |
| `handoffs[].agent` | Target agent identifier |
| `handoffs[].prompt` | Prompt sent to the target agent |
| `handoffs[].send` | Auto-submit the prompt (default `false`) |
| `handoffs[].model` | Model override for the handoff |
| `hooks` | Agent-scoped hook commands (Preview; requires `chat.useCustomAgentHooks`) |

### Claude Code Extensions

| Field | Notes |
|-------|-------|
| `color` | Agent color in UI (Claude Code only — not in VS Code spec) |
| `disallowedTools` | Explicit tool denylist (Claude Code only) |
| `maxTurns` | Maximum conversation turns |
| `skills` | Preloaded skill names injected at startup |
| `memory` | Scope: `user`, `project`, or `local` |
| `background` | Run concurrently in background |
| `isolation` | Git worktree isolation for safe edits |
| `permissionMode` | Not available in plugin agents — must be promoted to user/project scope |

### Common Mistakes

| Mistake | Consequence |
|---------|-------------|
| Missing `description` | Agent loads but is never auto-delegated as subagent |
| Description too vague | Agent under-triggers — other agents won't delegate to it |
| Invalid tool names | Silently ignored — agent runs without expected tools |
| YAML tabs instead of spaces | Parse error, agent silently ignored |
| `tools` as comma string in `.agent.md` | Use YAML array in VS Code format; comma strings are Claude format only |
| Granting all tools to every agent | Violates least privilege; degrades focus and security |
| Exceeding 128 tools | Hard error: "Cannot have more than 128 tools per request" |
| Exceeding 30,000 characters | Body truncated or rejected |
| Using `infer` field | Deprecated — use `user-invocable` + `disable-model-invocation` |

---

## Agent Discovery & Loading

### File Locations

| Scope | Location |
|-------|----------|
| Workspace (VS Code) | `.github/agents/` |
| Workspace (Claude Code) | `.claude/agents/` |
| Plugin (Claude Code) | `plugins/<name>/agents/` |
| User profile | `~/.copilot/agents/` or current VS Code profile's `agents/` folder |
| Organization | `.github-private` repo (requires `github.copilot.chat.organizationCustomAgents.enabled`) |
| Custom | Configurable via `chat.agentFilesLocations` setting |

### Discovery Rules

- VS Code detects **any `.md` files** in `.github/agents/` as agents
- Files in `.claude/agents/` use Claude format — VS Code maps tool names automatically
- Legacy `.chatmode.md` files should be renamed to `.agent.md`
- Naming conflicts: lowest-level config wins (repo > org > enterprise)
- Monorepos: enable `chat.useCustomizationsInParentRepositories` for parent root discovery

---

## How Agent Triggering Works

Agents activate through two primary mechanisms:

1. **User selection** — Pick from the agents dropdown, type `@agent-name`, or use `claude --agent <name>`
2. **Subagent delegation** — The active agent recognizes a subtask and delegates based on the candidate agent's `description` field

Unlike skills (which use progressive disclosure), agents load their **full system prompt immediately** when activated. The `description` field still carries the burden of triggering for subagent delegation — if it doesn't convey when the agent is useful, orchestrators won't delegate to it.

### Invocation Control Matrix

| `user-invocable` | `disable-model-invocation` | Dropdown | Subagent | Use case |
|---|---|---|---|---|
| true (default) | false (default) | Yes | Yes | General-purpose |
| false | false | No | Yes | Subagent-only (background specialist) |
| true | true | Yes | No | On-demand only (user must explicitly select) |
| false | true | No | No | Effectively disabled |

---

## Writing Effective Descriptions

### Formula: WHAT + WHEN + BOUNDARY

1. **WHAT** the agent specializes in (domain expertise)
2. **WHEN** to use it (imperative: "Use for…")
3. **BOUNDARY** to prevent misuse ("NEVER call X tools directly outside this agent")

### Principles

- **50–150 characters** — shown as placeholder text in the chat input
- **Use imperative phrasing**: "Use for all ADO-related tasks" not "Can handle ADO tasks"
- **Be pushy**: Agents tend to under-trigger. Include "Use proactively" or "Regardless of complexity"
- **Set boundaries**: Explicitly state what should NOT invoke this agent
- **Include exclusivity claims** for tool-owning agents to prevent tool leakage

### Good Examples

```yaml
# Tool-owning agent with exclusivity boundary
description: >
  Azure DevOps specialist for managing work items, repositories, pull requests,
  pipelines, wikis, test plans, and more. Use for all ADO-related tasks.
  NEVER call ADO MCP tools directly outside of this agent.
```

```yaml
# Proactive agent with broad trigger
description: >
  Web research specialist. Use proactively for searching the web, finding
  documentation, fetching article content, or researching topics across
  multiple sources.
```

```yaml
# Focused agent with complexity override
description: >
  Browser automation with playwright mcp. Use for all playwright-based tasks.
  Regardless of the complexity of the task. NEVER call playwright mcp tools
  directly outside of this agent.
```

### Argument Hints

When an agent accepts structured input, use `argument-hint`:

```yaml
argument-hint: "[review | merge | fix] — omit to run all three"
argument-hint: "[URL] [action to perform]"
```

---

## Agent Body Structure

### Size Constraints

- **Maximum 30,000 characters** (hard limit)
- Keep instructions **focused and scannable** — the LLM receives this as the system prompt
- Move detailed reference material to separate files loaded via Markdown links
- Add what the agent lacks, omit what it already knows

### Recommended Sections

```markdown
You are a [role]. Your role is to [core capability].

## When Invoked                   — Entry point: what to do first
## Core Workflow                  — Step-by-step procedures by scenario
  ### For [Scenario A]
  ### For [Scenario B]
## Available Tools                — Quick-reference table of tools by domain
## Output Guidelines              — Format rules, what to include/exclude
## Best Practices                 — Domain-specific conventions
## Constraints                    — Hard rules, security, what NOT to do
```

### Design Patterns

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Domain Expert** | Deep knowledge of one technology | Terraform specialist, ADO specialist |
| **Workflow Automator** | Multi-step processes with clear sequencing | Release manager, PR reviewer |
| **Quality Gate** | Enforces standards and checks | Accessibility auditor, security reviewer |
| **Orchestrator** | Delegates to sub-agents, validates results | Planning → implementation → review pipeline |
| **Mentor** | Guides through Socratic questioning | Learning-focused agent that teaches, not tells |

### Structural Tips

- **Start with a clear identity**: "You are a [role] specialized in [purpose]"
- **Use imperative language**: "Always do X", "Never do Y"
- **Document tools in the body** with a grouped reference table (see `ado.md`, `ms-tools.md`)
- **Define output format explicitly**: headings, bullet points, source citations
- **Include reasoning behind rules**: "Use `date-fns` because moment.js is deprecated"
- **Show preferred patterns with concrete examples**

---

## Tool Configuration

### Principle of Least Privilege

Only enable tools the agent needs. Fewer tools = clearer purpose, better performance, and stronger security.

| Agent Type | Recommended Tools |
|------------|-------------------|
| Read-only / reviewer | `Read`, `Glob`, `Grep`, `search`, `codebase` |
| Implementation | Add `Edit`, `terminal`, `Write` |
| External service | MCP tools for that service only |
| Orchestrator | `agent` tool + read tools for validation |

### Tool Formats

**VS Code `.agent.md`** — YAML array:
```yaml
tools:
  - search
  - fetch
  - myServer/*            # all tools from an MCP server
  - myServer/specificTool  # one specific MCP tool
```

**Claude Code `.md`** — comma-separated string:
```yaml
tools: Read, Glob, Grep, mcp__plugin_ado_ado__mcp_ado_wit_get_work_item
```

### MCP Tool Naming

**VS Code format**: `<server-name>/<tool-name>` or `<server-name>/*`

**Claude plugin format**: `mcp__plugin_<plugin>_<server>__<tool>`
- Plugin name = plugin directory name
- Server name = key from `.mcp.json` under `mcpServers`
- Tool name = as registered by the MCP server

Examples from this workspace:
| Full Tool Name | Plugin | Server | Tool |
|---|---|---|---|
| `mcp__plugin_ado_ado__mcp_ado_wit_get_work_item` | `ado` | `ado` | `mcp_ado_wit_get_work_item` |
| `mcp__plugin_playwright_playwright__browser_navigate` | `playwright` | `playwright` | `browser_navigate` |
| `mcp__plugin_web_web-search__search` | `web` | `web-search` | `search` |

### Tool Isolation via Instructions

For agents that own a set of MCP tools, enforce isolation in both the description and body:

```yaml
description: "... NEVER call ADO MCP tools directly outside of this agent ..."
```

This prevents other agents or the main conversation from bypassing tool restrictions.

---

## Model Selection

### Decision Matrix

| Task Complexity | Recommended Tier | Models | Cost Multiplier |
|----------------|------------------|--------|----------------|
| Search, fetch, simple dispatch | Fast | Haiku, GPT-5 mini, Gemini Flash | 0–0.33x |
| General coding, review, analysis | Balanced | Sonnet, GPT-5.x, Gemini Pro | 1x |
| Complex reasoning, architecture, debugging | Capable | Opus, GPT-5.4 | 3–30x |

### When to Use Each Tier

**Fast (Haiku / GPT-5 mini)** — Use when the agent primarily:
- Searches and fetches from APIs or documentation
- Dispatches CRUD operations to external services
- Performs simple routing or lookup
- Example: `web-searcher` (search/fetch), `ms-tools` (docs lookup), `ado` (API dispatch)

**Balanced (Sonnet / GPT-5.x)** — Use when the agent:
- Writes or reviews code
- Synthesizes information from multiple sources
- Makes judgment calls about quality or correctness
- Example: code reviewer, release manager

**Capable (Opus)** — Use when the agent:
- Requires multi-step visual or spatial reasoning
- Handles complex browser automation with decision-making
- Debugs across multiple interconnected files
- Plans architecture or weighs complex trade-offs
- Example: `playwright` (browser automation)

### Model Field Formats

**VS Code** — string or prioritized fallback array:
```yaml
model: Claude Sonnet 4
# or with fallbacks:
model:
  - Claude Sonnet 4
  - GPT-5
```

**Claude Code** — aliases or full IDs:
```yaml
model: haiku          # fastest, cheapest
model: sonnet         # balanced
model: opus           # most capable
model: claude-haiku-4.5  # specific version
```

### Cost-Conscious Routing

Opus costs ~9x more per request than Haiku. Route simple tasks to cheap models aggressively. The built-in `Explore` subagent demonstrates this — it uses Haiku for read-only codebase exploration despite being a general-purpose tool.

---

## Agents vs. Skills — When to Use Which

> "Use custom agents when you need a persistent persona with specific tool restrictions, model preferences, or handoffs between roles. For portable, reusable capabilities with scripts and resources, use agent skills."
> — VS Code docs

| Dimension | Agent (`.agent.md`) | Skill (`SKILL.md`) |
|-----------|--------------------|--------------------|
| **Purpose** | Define a *persona* with behavior, tools, model | Teach a *capability* or workflow |
| **Portability** | VS Code + Claude Code | Open standard — works across VS Code, CLI, coding agent, Claude Code |
| **Context** | Runs in isolated context window (as subagent) | Runs inline in current conversation (unless `context: fork`) |
| **Tool restrictions** | Can allowlist/denylist tools | Can specify `allowed-tools` (experimental) |
| **Model selection** | Can specify model per agent | Limited model control |
| **Handoffs** | Supports workflow transitions | No handoff mechanism |
| **Progressive disclosure** | Full prompt loads immediately | Discovery → Activation → Execution (3 stages) |

### Choose an Agent When You Need

- **Tool restrictions** — read-only agents, MCP tool isolation
- **Model routing** — Haiku for cheap tasks, Opus for complex ones
- **Context isolation** — verbose output stays in the subagent
- **Workflow transitions** — handoffs between steps
- **Persistent persona** — consistent behavior across a session

### Choose a Skill When You Need

- **Domain knowledge** or procedures that should run inline
- **Portability** across tools (VS Code, CLI, Claude Code)
- **Scripts and resources** bundled with instructions
- **Progressive loading** — many skills installed, only relevant ones activated

---

## Plugin Structure

When packaging an agent as a plugin (as in this workspace), follow this structure:

```
plugins/<plugin-name>/
├── .claude-plugin/plugin.json    # Manifest: name, version, metadata
├── .mcp.json                     # MCP server configuration
├── agents/
│   └── <agent-name>.md           # Agent definition with frontmatter
├── skills/                       # Optional: bundled skills
│   └── <skill-name>/SKILL.md
└── commands/                     # Optional: slash commands
    └── <command>.md
```

### Checklist for New Plugins

See [AGENTS.md](../AGENTS.md) for the full checklist:

- [ ] Create `plugins/<name>/.claude-plugin/plugin.json`
- [ ] Create `plugins/<name>/.mcp.json` with server config
- [ ] Create `plugins/<name>/agents/<name>.md` with frontmatter and instructions
- [ ] Add entry to `.claude-plugin/marketplace.json`
- [ ] Bump marketplace version
- [ ] Update `AGENTS.md` agent list

### `.mcp.json` Best Practices

- Use `mcpServers` as the top-level key (not `servers` — that's for `.vscode/mcp.json`)
- Use **short, descriptive server names** as keys (e.g., `"ado"`, `"playwright"`, `"web-search"`)
- Never hardcode secrets — use input variables with `password: true` or `.env` files
- Enable sandboxing on macOS/Linux when the server doesn't need broad filesystem/network access

---

## Security Considerations

### Tool-Level Security

- **List only the tools each agent needs** — principle of least privilege
- **Use read-only tool sets** for review / analysis agents
- **Enforce tool isolation in descriptions** — "NEVER call X tools directly outside this agent"
- **Use `agents: []`** to prevent subagent spawning when not needed
- **Review tool lists before sharing** agents in a repository

### MCP Server Security

- MCP servers are an explicit trust boundary — VS Code prompts for trust on first use
- Plugin MCP servers are implicitly trusted when the plugin is installed
- Use `PreToolUse` hooks to programmatically block dangerous operations
- Configure sandboxing to restrict filesystem and network access:

```json
{
  "mcpServers": {
    "example": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@example/mcp-server"],
      "sandboxEnabled": true,
      "sandbox": {
        "filesystem": { "allowWrite": ["${workspaceFolder}"] },
        "network": { "allowedDomains": ["api.example.com"] }
      }
    }
  }
}
```

### Authentication

- Use VS Code input variables (`${input:variable-id}`) with `password: true` for API keys
- Use `envFile` to load variables from `.env` files (keep out of source control)
- For HTTP/SSE servers, use the `headers` field with input variables for bearer tokens

---

## Anti-Patterns

- **Monolithic agent**: One agent handling security, testing, docs, and deployment — split into focused agents
- **Too broad description**: "You are a software engineer" — no focus, no boundaries, no trigger criteria
- **No tool restrictions**: Agent has access to everything when it only needs read access
- **Implementation-focused descriptions**: "Runs pdfplumber to parse text" — describe user intent instead
- **Conflicting instructions**: Agent says "use tabs" but repo `.editorconfig` says "use spaces"
- **Explaining what the agent knows**: Don't define common terms or teach the LLM its base capabilities
- **Missing output expectations**: No defined format leads to inconsistent, verbose responses
- **Overly verbose instructions**: Exceeding 30,000 chars or padding with unnecessary context
- **"Let me just quickly…" syndrome**: Orchestrator reads files itself instead of delegating to subagents
- **Trusting self-reported completion**: Always validate subagent results with a separate check
- **Specification substitution**: Subagent swaps the user's tech choice for its preferred alternative

---

## Handoffs — Workflow Chaining (VS Code Only)

Handoffs create guided workflow transitions between agents:

```yaml
handoffs:
  - label: Start Implementation
    agent: implementation
    prompt: Now implement the plan outlined above.
    send: false
  - label: Run Tests
    agent: tester
    prompt: Run the test suite and report failures.
    send: true
```

### Best Practices

- Use action-oriented labels: "Start Implementation" not "Next"
- Set `send: false` (default) to let users review the prompt before submission
- Use `send: true` only for well-defined, safe transitions
- Keep handoff chains linear — avoid complex branching
- Handoffs preserve conversation context across agent switches

---

## Debugging Agents

1. **Agent Debug Logs**: Gear icon in Chat → "Show Agent Debug Logs"
2. **Developer Tools**: Search console for `[computeSkillDiscoveryInfo]` or agent loading traces
3. **`/agents` command**: Type in chat to list registered agents
4. **Check YAML syntax**: Tabs, missing quotes, or malformed arrays cause silent failures
5. **Verify tool names**: Invalid tool names are silently ignored — agent works but without expected tools
6. **Test triggering**: Write 10+ sample prompts that should delegate to the agent and verify it activates

---

## Quick Reference — Minimal Agent Template

```yaml
---
description: "[Role] specialist for [domain]. Use for [triggers]. NEVER call [tools] directly outside this agent."
name: my-agent
tools: ['read', 'search', 'myServer/*']
model: Claude Sonnet 4
---

You are a [role] specialist. Your role is to [core capability].

## When Invoked

1. Understand what the user needs
2. [First action]
3. [Second action]
4. Return a concise summary with sources

## Core Workflow

### For [Scenario A]
1. Step 1
2. Step 2

### For [Scenario B]
1. Step 1
2. Step 2

## Output Guidelines

- Be concise — return only the information requested
- Structure data with markdown tables, lists, or code blocks
- Include source URLs for every key claim
```
