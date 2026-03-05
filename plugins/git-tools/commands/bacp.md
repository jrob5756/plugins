---
description: Branch, add, commit, push, and open a PR in one command
allowed-tools: Bash, Read, Glob, Grep
---

# Git Branch-Add-Commit-Push

From main: pull latest, create a feature branch, stage, commit, push, and open a PR — all in one workflow.

## Steps

1. **Verify on main** — run `git branch --show-current`. If not on `main`, stop and tell the user.

2. **Pull latest**:
   ```bash
   git pull --rebase origin main
   ```

3. **Review changes** — inspect the working tree:
   ```bash
   git status --short && git diff
   ```
   If there are no changes, inform the user and stop.

4. **Create a branch** — infer a descriptive branch name from the diff using the prefix convention:
   - `feature/` — new features or capabilities
   - `fix/` — bug fixes
   - `chore/` — maintenance, config, dependency updates
   - `docs/` — documentation-only changes
   - `refactor/` — restructuring without behavior change
   - `test/` — test additions or updates

   Format: `prefix/kebab-case-description`. If `$ARGUMENTS` is provided, use it as a hint.
   ```bash
   git checkout -b <branch-name>
   ```

5. **Stage, commit, and push** — stage specific files (never `git add -A`), generate a conventional commit message from the diff, and push in one call:
   ```bash
   git add <files> && git commit -m "type(scope): description" && git push -u origin <branch-name>
   ```
   For multi-line messages, use a HEREDOC:
   ```bash
   git add <files> && git commit -m "$(cat <<'EOF'
   type(scope): short description

   Longer body explaining what and why.
   EOF
   )" && git push -u origin <branch-name>
   ```

6. **Create a PR** — use the GitHub CLI:
   ```bash
   gh pr create --base main --title "type(scope): description" --body "Summary of changes"
   ```

## Important

- Never commit files that look like secrets (`.env`, credentials, keys, tokens)
- Prefer staging specific files over `git add .` to avoid secrets
- Generate the commit message from the diff — describe _what_ the changes do, not which files changed
- If `gh` returns a 404 or permission error, try `gh auth switch` and retry
- If there are no pending changes, inform the user and stop
