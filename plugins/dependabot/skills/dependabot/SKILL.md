---
name: dependabot
argument-hint: "[review | merge | fix] — omit to run all three in order"
description: |
  Dependabot PR management — review, merge, and fix workflows. Triggers: review dependabot PRs, merge dependabot PRs, fix dependabot PR, dependabot report, analyze dependabot, triage dependabot, process dependabot, dependabot CI failures, lockfile sync, dependabot execution plan.
---

# Dependabot PR Management

A three-stage pipeline for managing Dependabot pull requests: **review** → **merge** → **fix**.

## Dispatch

Parse the user's request to determine which action to run:

| User says | Action |
|-----------|--------|
| "review dependabot PRs", "triage dependabot" | Run **Review** only |
| "merge dependabot PRs", "execute dependabot plan" | Run **Merge** only |
| "fix dependabot PR #123", "repair dependabot CI" | Run **Fix** only |
| "process dependabot", "run dependabot", or no specific action | Run **Review → Merge → Fix** in sequence |

When running all three, chain them: Review produces a report → Merge consumes that report → Fix handles any PRs that Merge halted on.

## Constraint: Use GH CLI

Use `gh` for all GitHub interactions. Do NOT use GitHub MCP tools — they incorrectly report PR status as "pending" even when all checks have passed.

## Actions

### 1. Review — Triage all open Dependabot PRs

Analyze every open Dependabot PR, categorize by status, and generate an execution plan report.

**When to use:** "review dependabot PRs", "triage dependabot", "check dependabot status"

**Output:** A report saved to `docs/projects/dependabot/pr_review_YYYYMMDD_HHmmss.md` with:
- Executive summary (counts by category)
- Ordered execution plan (merge → close → fix)
- Fix instructions for broken PRs
- Per-PR analysis with CI status, risk level, and recommendation

See [references/review-workflow.md](references/review-workflow.md) for the full workflow and mandatory report template.

### 2. Merge — Execute an execution plan

Process the execution plan from a review report, merging/closing PRs sequentially and updating the report status after each action.

**When to use:** "merge dependabot PRs", "execute dependabot plan", "process dependabot report"

**Input:** Path to a review report file

**Behavior:**
- Processes actions in order (merge first, then close, then fix)
- Updates the report's status table after each action
- Halts on FIX actions or any failure
- Saves the report after each status change

See [references/merge-workflow.md](references/merge-workflow.md) for the full workflow.

### 3. Fix — Repair a failing Dependabot PR

Fix a specific Dependabot PR to make it CI-green and ready for merge.

**When to use:** "fix dependabot PR #123", "fix dependabot lockfile", "repair dependabot CI"

**Inputs:**
- PR number (required)
- Path to review report (optional — uses Fix Instructions from the report)

**Common fixes:**

| Issue | Fix |
|-------|-----|
| Lockfile out of sync | `npm install` and commit lockfile |
| Outdated branch | Rebase on main |
| Breaking API changes | Update code for new API |
| Type errors | Update type definitions |

See [references/fix-workflow.md](references/fix-workflow.md) for the full workflow.

## Quick Reference

```bash
# Discover open Dependabot PRs
gh pr list --author "app/dependabot" --state open --json number,title,url,headRefName

# Check CI status for a PR
gh pr checks <pr-number>

# Merge a PR
gh pr merge <pr-number> --squash --delete-branch

# Close a superseded PR
gh pr close <pr-number> -c "Superseded by #<other>"

# Fix lockfile sync issue
gh pr checkout <pr-number> && npm install && git add package-lock.json && git commit -m "fix: sync lockfile" && git push

# Wait for CI after pushing a fix
gh pr checks <pr-number> --watch
```
