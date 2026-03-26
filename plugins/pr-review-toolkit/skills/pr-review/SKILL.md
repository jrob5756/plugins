---
name: pr-review
description: |
  Comprehensive PR review using specialized agents for code quality, tests, comments, error handling, type design, and simplification. Triggers: review PR, review my changes, check PR, PR review, review code, review before commit, review before PR, comprehensive review, code review, check tests, check error handling, review types, simplify code, review pull request, pre-commit review, run all reviews. Use when the user wants to review code changes before or after creating a pull request, even if they don't say "PR review" explicitly.
argument-hint: "[comments | tests | errors | types | code | simplify | all] — omit for all applicable reviews"
---

# Comprehensive PR Review

Run a comprehensive pull request review using multiple specialized agents, each focusing on a different aspect of code quality.

## Dispatch

Parse the user's request to determine which review aspects to run:

| User says | Action |
|-----------|--------|
| "review comments", "check documentation" | Run **comment-analyzer** only |
| "review tests", "check test coverage" | Run **pr-test-analyzer** only |
| "check error handling", "find silent failures" | Run **silent-failure-hunter** only |
| "review types", "analyze type design" | Run **type-design-analyzer** only |
| "review code", "check code quality" | Run **code-reviewer** only |
| "simplify code", "make it clearer" | Run **code-simplifier** only |
| "review PR", "comprehensive review", or no specific aspect | Run **all applicable** reviews |

## Workflow

### 1. Determine Review Scope

- Run `git diff --name-only` to identify changed files
- Check if a PR already exists: `gh pr view` (ignore errors if no PR)
- Parse user arguments for specific review aspects
- Default: run all applicable reviews

### 2. Determine Applicable Reviews

Based on changed files and user request:

| Review Agent | When Applicable |
|-------------|----------------|
| **code-reviewer** | Always — general quality review |
| **pr-test-analyzer** | Test files changed or new functionality added |
| **comment-analyzer** | Comments or documentation added/modified |
| **silent-failure-hunter** | Error handling, try/catch, or fallback code changed |
| **type-design-analyzer** | New types or type modifications introduced |
| **code-simplifier** | Run last, after other reviews pass — polish and refine |

### 3. Launch Review Agents

Launch each applicable agent using the Task tool (or subagent). Default is sequential (one at a time) unless the user requests parallel.

Each agent is defined in `agents/` and will:
- Analyze the git diff or specified files
- Return a structured report with findings

### 4. Aggregate Results

After all agents complete, produce a unified summary:

```markdown
# PR Review Summary

## Critical Issues (X found)
- [agent-name]: Issue description [file:line]

## Important Issues (X found)
- [agent-name]: Issue description [file:line]

## Suggestions (X found)
- [agent-name]: Suggestion [file:line]

## Strengths
- What's well-done in this PR

## Recommended Action
1. Fix critical issues first
2. Address important issues
3. Consider suggestions
4. Re-run review after fixes
```

## Tips

- **Run early**: Before creating a PR, not after
- **Focus on changes**: Agents analyze git diff by default
- **Address critical first**: Fix high-priority issues before lower priority
- **Re-run after fixes**: Verify issues are resolved
- **Use specific reviews**: Target specific aspects when you know the concern
