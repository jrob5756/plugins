---
name: gh-cli
description: GitHub interactions using the GH CLI. Triggers: create issue, list PRs, open pull request, merge PR, view repo, clone repository, check workflow, run actions, create release, search issues, review PR, gh command, GitHub API, repo settings, create gist, list releases, check CI status, switch GitHub account. More generally anything with GitHub should use this skill.
---

# GitHub CLI

Use the GitHub CLI (`gh`) for **all** GitHub interactions — issues, PRs, repos, releases, gists, workflows, and API calls. Never use the GitHub REST/GraphQL API directly or the MCP GitHub tools when `gh` can accomplish the task.

## Documentation

Full command reference: https://cli.github.com/manual/

Use your knowledge of `gh` commands first. Consult the documentation only when unsure about flags, subcommands, or newer features.

## Multi-Account Setup

Two GitHub accounts are configured:

| Account | Usage |
|---------|-------|
| `jrob5756` | Personal & Microsoft OSS |
| `jasonrobert_microsoft` | Microsoft GitHub EMU |

### Handling 404 or Access Denied

If a `gh` command returns a **404**, **403**, or any permission/access error:

1. Check which account is active: `gh auth status`
2. Switch to the other account: `gh auth switch --user <other_user>`
3. Retry the original command

Try both accounts before reporting an access failure.

## Common Commands

```bash
# Auth
gh auth status                          # Show active account
gh auth switch --user jrob5756          # Switch accounts

# Repos
gh repo view owner/repo
gh repo clone owner/repo

# Issues
gh issue list -R owner/repo
gh issue create -R owner/repo --title "..." --body "..."
gh issue view 123 -R owner/repo

# Pull Requests
gh pr list -R owner/repo
gh pr create --title "..." --body "..."
gh pr view 123 -R owner/repo
gh pr checkout 123
gh pr merge 123 --squash

# Workflows / Actions
gh run list -R owner/repo
gh run view <run-id> -R owner/repo
gh workflow list -R owner/repo

# API (escape hatch for anything not covered by a subcommand)
gh api repos/owner/repo/contents/path
```

## Guidelines

- Always pass `-R owner/repo` when operating on a repo that isn't the current working directory's origin.
- Prefer `--json` output with `--jq` filters when you need to parse results programmatically.
- Use `gh api` with `--paginate` for large result sets.
- For destructive operations (delete, merge, close), confirm with the user first unless they explicitly asked for it.

## Adding Pending PR Review Comments

To add pending (not yet submitted) review comments to a PR, use the GitHub API directly via `gh api`.

### Steps

1. **Build a JSON payload file** (e.g., `/tmp/pr-review-payload.json`):

```json
{
  "comments": [
    {
      "path": "relative/path/to/file.ts",
      "position": 10,
      "body": "Your review comment here.\n\nSupports **markdown**."
    }
  ]
}
```

**Field reference:**

| Field | Description |
|-------|-------------|
| `path` | File path relative to repo root (must match a file in the PR diff) |
| `position` | Line position **within the diff hunk** (not the file line number). Count lines from the `@@` hunk header, starting at 1. |
| `body` | Comment body (supports GitHub-flavored markdown, use `\n` for newlines) |

2. **Create the review** — Do NOT include an `event` field. Omitting it creates the review in PENDING state:

```bash
gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews \
  --method POST --input /tmp/pr-review-payload.json
```

3. **Verify** — The response will include `"state": "PENDING"`. The comments are now visible only to the author on the PR page, ready to be submitted.

### Gotchas

- **Do NOT set `"event": "PENDING"`** — this is not a valid event value and will return a 422 error. Simply omit the `event` field entirely to get PENDING state.
- **Do NOT use `--field` for the comments array** — `gh` will serialize it as a string, not JSON. Always write to a file and use `--input`.
- **Do NOT set `"event": "COMMENT"` or `"event": "APPROVE"`** — this will immediately submit the review. Omit `event` to keep it pending.
- **Finding the diff position**: Run `gh api repos/{owner}/{repo}/pulls/{pr_number}/files` to see each file's `patch` field, then count lines within the relevant hunk.
