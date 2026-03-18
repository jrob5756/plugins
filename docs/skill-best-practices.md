# Agent Skill Best Practices

Synthesized from official documentation, community patterns, and workspace analysis.

## Sources

| Source | URL |
|--------|-----|
| Agent Skills Open Standard | https://agentskills.io/specification |
| Optimizing Descriptions | https://agentskills.io/skill-creation/optimizing-descriptions |
| Authoring Best Practices | https://agentskills.io/skill-creation/best-practices |
| VS Code Agent Skills Docs | https://code.visualstudio.com/docs/copilot/customization/agent-skills |
| Anthropic Reference Skills | https://github.com/anthropics/skills |
| Awesome Copilot Skills | https://github.com/github/awesome-copilot |

---

## YAML Frontmatter Reference

### Standard Fields (agentskills.io)

| Field | Required | Max | Notes |
|-------|----------|-----|-------|
| `name` | **Yes** | 64 chars | Lowercase, hyphens only. **Must match parent directory name.** |
| `description` | **Yes** | 1024 chars | What + When + Keywords — drives automatic invocation |
| `license` | No | — | SPDX identifier or `LICENSE.txt` reference |
| `compatibility` | No | 500 chars | Environment requirements |
| `metadata` | No | — | Arbitrary key-value pairs (`author`, `version`, etc.) |
| `allowed-tools` | No | — | Space-delimited pre-approved tools (experimental) |

### VS Code Extensions

| Field | Default | Notes |
|-------|---------|-------|
| `argument-hint` | — | Placeholder text in chat input when invoked as `/skill-name` |
| `user-invocable` | `true` | Set `false` to hide from `/` menu but allow auto-invocation |
| `disable-model-invocation` | `false` | Set `true` to require manual `/` invocation only |

### Common Mistakes

| Mistake | Consequence |
|---------|-------------|
| Missing `name` field | Skill not loaded (error only in console) |
| `name` doesn't match directory | Skill silently ignored |
| Uppercase, underscores, or consecutive hyphens in `name` | Invalid per spec |
| `description` over 1024 chars | Truncated or rejected |
| Missing `description` | No trigger criteria — skill never auto-invoked |
| Tabs in frontmatter | YAML parse error, skill silently ignored |

---

## How Skill Triggering Works

Progressive disclosure in three stages:

1. **Discovery** (~100 tokens): Only `name` + `description` loaded at startup for all skills
2. **Activation**: When a user's prompt matches the description, the full SKILL.md body loads into context
3. **Execution**: Agent follows instructions, loading referenced files on demand

**The `description` field carries the entire burden of triggering.** If it doesn't convey when the skill is useful, the agent won't reach for it.

---

## Writing Effective Descriptions

### Formula: WHAT + WHEN + KEYWORDS

1. **WHAT** the skill does (capabilities)
2. **WHEN** to use it (imperative: "Use when…")
3. **Keywords** users might say in prompts (trigger phrases)

### Principles

- **Use imperative phrasing**: "Use this skill when…" rather than "This skill does…"
- **Focus on user intent**, not implementation details
- **Be pushy**: Agents tend to under-trigger. Include "even if they don't explicitly mention X"
- **Include DO NOT TRIGGER guidance** when competing with similar skills
- **Keep under 1024 characters**

### Good Examples

```yaml
# Keyword-dense trigger list style
description: |
  Git workflow shortcuts for common operations. Triggers: acp, add commit push,
  commit and push, bacp, branch and PR, sync, pull rebase.
```

```yaml
# Intent-focused with explicit triggers and anti-triggers
description: |
  Build apps with the Claude API or Anthropic SDK. TRIGGER when: code imports
  anthropic/@anthropic-ai/sdk. DO NOT TRIGGER when: code imports openai.
```

```yaml
# Capability-focused with indirect triggers  
description: |
  Analyze CSV and tabular data — summary statistics, derived columns, charts.
  Use when the user has a CSV, TSV, or Excel file, even if they don't explicitly
  mention 'CSV' or 'analysis.'
```

### Argument Hints

When a skill has discrete sub-actions, use `argument-hint` to guide users:

```yaml
argument-hint: "[review | merge | fix] — omit to run all three in order"
argument-hint: "[test file] [options]"
argument-hint: "[workflow] [branch name]"
```

- Use brackets for parameters, pipe `|` for choices
- Add a brief explanation after the hint
- Keep it short — appears inline as placeholder text

---

## SKILL.md Body Structure

### Size Constraints

- **Keep under 500 lines / ~5,000 tokens**
- Move detailed reference material to `references/`
- Add what the agent lacks, omit what it already knows

### Recommended Sections

For **workflow skills** (multi-action dispatch):

```
## Dispatch                      — User phrase → action mapping table
## Constraints                   — Hard rules (security, tool restrictions)  
## Rules                         — Shared conventions (kept brief)
## Workflows / Actions           — One ### per workflow with:
  - "When to use" annotation
  - Inputs / outputs
  - Steps (or pointer to reference file)
## Quick Reference               — Copy-pasteable commands (optional)
```

For **reference/knowledge skills**:

```
## When to Use Each Guide        — Task → file routing table
## Quick Reference               — Common commands
## Guidelines                    — Global rules
```

### Structural Patterns

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Dispatch table + references** | Multiple complex workflows sharing context | `dependabot` |
| **Inline dispatch** | Workflows are short (<15 lines each) | `git-workflow` |
| **Router + domain variants** | Same capability across platforms/languages | `claude-api` |
| **Task-based routing table** | Mix of simple inline + complex referenced tasks | `azure-devops-cli` |

### When to Use Reference Files

**Use references when:**
- SKILL.md would exceed ~500 lines
- Individual workflows are >5 steps with detailed procedures
- Content is only needed for specific sub-tasks
- Multiple domain variants exist

**Keep inline when:**
- Constraints/gotchas that must be visible on every activation
- Dispatch tables and routing logic
- Shared rules that apply across all workflows
- Total SKILL.md stays under 500 lines

**Rules for references:**
- Keep file references **one level deep** from SKILL.md
- Tell the agent **when** to load each file (not just generic links)
- For large references (>300 lines), include a table of contents

---

## Invocation Control Matrix

| `user-invocable` | `disable-model-invocation` | `/` menu | Auto-loaded | Use case |
|---|---|---|---|---|
| true (default) | false (default) | Yes | Yes | General-purpose |
| false | false | No | Yes | Background knowledge |
| true | true | Yes | No | On-demand only |
| false | true | No | No | Effectively disabled |

---

## Anti-Patterns

- **Vague descriptions**: "Helps with PDFs" — no capabilities, no triggers
- **Implementation-focused descriptions**: "Runs pdfplumber to parse text" — should describe user intent
- **Menus of equal options**: Pick a default, mention alternatives briefly
- **Explaining what the agent knows**: Don't define common terms
- **Deeply nested references**: Keep to one level from SKILL.md
- **No testing**: Write ~20 eval queries (10 should-trigger, 10 should-not) and iterate
- **Overfitting triggers**: Don't add keywords from specific failed queries; generalize

---

## Debugging Skills

1. **Agent Debug Log**: Gear icon in Chat → "Show Agent Debug Logs"
2. **Window trace logs**: Developer Tools → search for `[computeSkillDiscoveryInfo]`
3. **`/skills` command**: Type in chat to see registered skills
4. **Validation**: `skills-ref validate ./my-skill` ([skills-ref library](https://github.com/agentskills/agentskills/tree/main/skills-ref))
