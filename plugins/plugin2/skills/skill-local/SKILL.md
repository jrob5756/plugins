---
name: skill-local
argument-hint: "[time | info] [question]"
description: |
  Local utility skill for plugin2. Use when the user asks for the current time,
  basic utility operations, or invokes plugin2 by name.
  Triggers: time, what time, current time, utility, plugin2.
---

# Local Utility Skill (plugin2)

Provide utility operations local to plugin2.

## Dispatch

| User says | Action |
|-----------|--------|
| "what time is it", "current time" | Use time MCP server |
| "utility", "test" | Acknowledge and respond |

## Constraints

- Always use the `agent-local` subagent via the Task tool — never call MCP tools directly
- This is the local skill for plugin2
