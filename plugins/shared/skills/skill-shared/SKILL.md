---
name: skill-shared
argument-hint: "[shared | common] [question]"
description: |
  Shared utility skill referenced by multiple plugins. Use for common
  operations that span plugin1 and plugin2.
  Triggers: shared, common, utility.
---

# Shared Utility Skill

Provide common utility operations shared across multiple plugins.

## Dispatch

| User says | Action |
|-----------|--------|
| "shared", "common" | Perform shared operation |
| "utility", "test" | Acknowledge and respond |

## Constraints

- This skill lives in `plugins/shared/` and is referenced by both plugin1 and plugin2
- It is a test fixture for cross-experience shared artifact validation
