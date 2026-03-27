---
name: generic-utility
argument-hint: "[time | info] [question]"
description: |
  Generic utility skill for testing. Use when the user asks for the current time,
  basic utility operations, or invokes plugin1 by name.
  Triggers: time, what time, current time, utility, plugin1.
---

# Generic Utility

Provide simple utility operations like time lookups and basic information retrieval.

## Dispatch

| User says | Action |
|-----------|--------|
| "what time is it", "current time" | Use time MCP server |
| "utility", "test" | Acknowledge and respond |

## Constraints

- Always use the `plugin1` subagent via the Task tool — never call MCP tools directly
- This skill is a test fixture for cross-experience validation
