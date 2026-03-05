---
description: Sync current branch with remote using pull --rebase
allowed-tools: Bash, Read
---

# Git Sync

Synchronize the current branch with its remote tracking branch via rebase.

## Steps

1. **Check for uncommitted changes**:
   ```bash
   git status --short
   ```
   If uncommitted changes exist, warn the user and suggest committing or stashing first. Do not proceed with the pull.

2. **Fetch and rebase** in one call:
   ```bash
   git fetch && git pull --rebase
   ```

3. **Show final state**:
   ```bash
   git status --short && git log --oneline -3
   ```

## Handling Conflicts

If rebase conflicts occur:
1. List the conflicting files
2. Explain resolution steps:
   - Edit files to resolve conflicts
   - `git add <files>` to mark resolved
   - `git rebase --continue` to proceed
   - Or `git rebase --abort` to cancel
