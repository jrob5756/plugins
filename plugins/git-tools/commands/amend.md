---
description: Amend the last commit and force push pending changes
argument-hint: [new message]
allowed-tools: Bash, Read
---

# Git Amend & Force Push

Stage pending changes into the last commit and force push.

## Steps

1. **Review state** — check for pending changes and the last commit message:
   ```bash
   git status --short && git log --oneline -1
   ```
   If there are no pending changes, inform the user and stop.

2. **Amend and push** in one call:
   ```bash
   git add . && git commit --amend --no-edit && git push --force-with-lease
   ```
   If `$ARGUMENTS` is provided, use it as the new commit message instead:
   ```bash
   git add . && git commit --amend -m "$ARGUMENTS" && git push --force-with-lease
   ```

## Important

- Never use `--force` — always use `--force-with-lease`
- Never commit files that look like secrets (`.env`, credentials, keys, tokens)
