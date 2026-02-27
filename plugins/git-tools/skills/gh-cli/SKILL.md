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
