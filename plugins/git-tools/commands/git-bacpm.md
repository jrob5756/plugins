---
name: git.bacpm
description: Branch, add, commit, push, merge, delete changes in one command
tools: ['vscode', 'execute', 'read', 'agent', 'edit', 'search', 'web', 'todo']
---

# Git Branch-Add-Commit-Push-Merge-Delete

Full workflow: ensure you're on main, pull latest, create a feature branch from pending changes, commit, push, open a PR, and optionally merge.

## Steps

1. **Verify on main** — run `git branch --show-current`. If not on `main`, stop.

2. **Pull latest** — rebase on top of remote main:
   ```bash
   git pull --rebase origin main
   ```

3. **Review changes** — run `git diff` and `git status` to understand what's pending. If there are no changes, inform the user and stop.

4. **Create a branch** — based on the diff, generate a short descriptive branch name using conventional format (e.g., `feat/add-github-skill`, `fix/typo-in-readme`). Then:
   ```bash
   git checkout -b <branch-name>
   ```

5. **Stage, commit, and push** — stage specific files (avoid secrets like `.env`, credentials, keys). Generate a conventional commit message from the changes:
   ```bash
   git add <files> && git commit -m "type(scope): description" && git push -u origin <branch-name>
   ```

6. **Create a PR** — use the GH CLI to open a pull request against main:
   ```bash
   gh pr create --base main --title "type(scope): description" --body "Summary of changes"
   ```

7. **Ask to merge** — ask the user: *"PR created. Would you like to merge it now?"*
   - If **yes**: merge with squash, delete the remote branch, switch back to main, pull latest, and delete the local branch:
     ```bash
     gh pr merge --squash --delete-branch && git checkout main && git pull --rebase origin main && git branch -d <branch-name>
     ```
   - If **no**: stop and report the PR URL.

## Important

- Never commit files that look like secrets (`.env`, credentials, keys)
- If `gh` returns a 404 or permission error, try switching GitHub accounts (`gh auth switch`) and retry
- If there are no pending changes, inform the user and stop
