---
description: Sync current branch with remote using pull --rebase
allowed-tools: Bash, Read
---

# Git Sync

Synchronize the current branch with its remote tracking branch.

## Steps

1. Run `git status` to check for uncommitted changes
2. If uncommitted changes exist, warn the user and suggest:
   - Run `/git-acp` first to commit them, OR
   - Stash with `git stash` before syncing
3. Run `git fetch` to get latest remote refs
4. Run `git pull --rebase` to rebase local commits on top of remote
5. Run `git status` to show final state

## Handling Conflicts

If rebase conflicts occur:
1. List the conflicting files
2. Explain resolution steps:
   - Edit files to resolve conflicts
   - `git add <files>` to mark resolved
   - `git rebase --continue` to proceed
   - Or `git rebase --abort` to cancel
