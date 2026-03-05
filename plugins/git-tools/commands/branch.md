---
description: Create a new feature branch named based on unstaged changes
allowed-tools: Bash, Read
---

# Git Branch from Changes

Analyze pending changes and create a descriptively named feature branch.

## Steps

1. **Review changes** — inspect the working tree:
   ```bash
   git status --short && git diff
   ```
   Analyze file paths, extensions, and diff content to understand the intent of the work.

2. **Choose a branch name** using the prefix convention:
   - `feature/` — new features or capabilities
   - `fix/` — bug fixes
   - `chore/` — maintenance, config, dependency updates
   - `docs/` — documentation-only changes
   - `refactor/` — restructuring without behavior change
   - `test/` — test additions or updates

   Format: `prefix/kebab-case-description`. The name should capture _what_ the changes do, not just list filenames.
   If `$ARGUMENTS` is provided, use it as a hint or override.

3. **Branch from the right base**:
   - If on `main` or `master`, pull latest first, then stash pending changes:
     ```bash
     git stash && git pull --rebase origin main
     ```
   - Otherwise, branch from the current branch (no stash needed).

4. **Create the branch, restore changes, and push**:
   ```bash
   git checkout -b <branch-name> && git stash pop && git push -u origin <branch-name>
   ```
   If nothing was stashed, omit `git stash pop`.

## Important

- If there are no pending changes, inform the user and stop.
