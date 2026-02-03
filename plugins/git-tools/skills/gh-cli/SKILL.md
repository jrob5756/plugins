---
name: gh-cli
description: Reference guide for using the GitHub CLI (gh) for PRs, issues, repos, workflows, and API access. Use when working with GitHub operations.
---

# GitHub CLI (gh) Reference Guide

Use this guide when working with GitHub operations via the `gh` CLI.

## Authentication

```bash
gh auth login          # Login to GitHub
gh auth status         # Check auth status
gh auth logout         # Logout
```

## Pull Requests

### Create
```bash
gh pr create                                    # Interactive
gh pr create --title "Title" --body "Body"      # With message
gh pr create --draft                            # Draft PR
gh pr create --base main                        # Specific base
gh pr create --web                              # Open in browser
```

### View/List
```bash
gh pr list                  # List open PRs
gh pr view 123              # View specific PR
gh pr view 123 --web        # Open in browser
gh pr view                  # Current branch's PR
```

### Actions
```bash
gh pr checkout 123                              # Checkout PR locally
gh pr merge 123                                 # Merge PR
gh pr merge 123 --squash                        # Squash merge
gh pr review 123 --approve                      # Approve
gh pr review 123 --request-changes --body "..."  # Request changes
gh pr close 123                                 # Close PR
gh pr comment 123 --body "Comment"              # Add comment
```

### View Comments
```bash
gh api repos/{owner}/{repo}/pulls/123/comments
```

## Issues

### Create
```bash
gh issue create                                 # Interactive
gh issue create --title "Bug" --body "..."      # With details
gh issue create --label "bug,priority:high"     # With labels
gh issue create --assignee username             # Assign
```

### View/List
```bash
gh issue list                                   # List open
gh issue list --label "bug" --assignee "@me"    # Filter
gh issue view 456                               # View specific
gh issue view 456 --web                         # Open in browser
```

### Actions
```bash
gh issue close 456                  # Close
gh issue reopen 456                 # Reopen
gh issue comment 456 --body "..."   # Comment
```

## Repositories

```bash
gh repo clone owner/repo            # Clone
gh repo create my-repo --public     # Create public
gh repo create my-repo --private    # Create private
gh repo fork owner/repo             # Fork
gh repo view --web                  # Open in browser
gh repo list                        # List your repos
```

## Workflows (GitHub Actions)

```bash
gh workflow list          # List workflows
gh run list               # View runs
gh run view 12345         # View specific run
gh run watch 12345        # Watch in progress
gh run rerun 12345        # Rerun failed
gh run download 12345     # Download artifacts
```

## Releases

```bash
gh release list                                           # List
gh release create v1.0.0 --title "v1.0.0" --notes "..."   # Create
gh release create v1.0.0 --generate-notes                 # Auto notes
gh release download v1.0.0                                # Download
```

## Gists

```bash
gh gist create file.txt             # Create private
gh gist create file.txt --public    # Create public
gh gist list                        # List
gh gist view <gist-id>              # View
```

## API Access

```bash
gh api repos/{owner}/{repo}                                        # GET
gh api repos/{owner}/{repo}/issues --method POST --field title="..." # POST
gh api repos/{owner}/{repo}/pulls --jq '.[].title'                 # With jq
```

## Useful Flags

| Flag | Description |
|------|-------------|
| `--web` / `-w` | Open in browser |
| `--json` | Output as JSON |
| `--jq` | Process with jq |
| `--help` | Get help |

## Tips

1. Use `gh pr create --web` for complex PRs with reviewers
2. Use `gh run watch` to monitor CI in terminal
3. Use `gh api` for anything not covered by commands
4. Enable tab completion: `gh completion -s bash >> ~/.bashrc`
