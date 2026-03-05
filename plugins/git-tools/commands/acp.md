---
description: Add, commit, and push changes in one command
allowed-tools: Bash, Read, Glob, Grep
---

# Git Add-Commit-Push

Stage changes, create a conventional commit, and push to the remote — all in one step.

## Steps

1. **Review changes** — inspect the working tree:
   ```bash
   git status --short && git diff
   ```
   If there are no changes, inform the user and stop.

2. **Stage, commit, and push** — stage specific files (never `git add -A`), generate a conventional commit message from the diff, and push in one call:
   ```bash
   git add <files> && git commit -m "type(scope): description" && git push
   ```
   For multi-line messages, use a HEREDOC:
   ```bash
   git add <files> && git commit -m "$(cat <<'EOF'
   type(scope): short description

   Longer body explaining what and why.
   EOF
   )" && git push
   ```

## Important

- Never commit files that look like secrets (`.env`, credentials, keys, tokens)
- Prefer staging specific files over `git add .` to avoid secrets
- Generate the commit message from the diff — describe _what_ the changes do, not which files changed
- If no changes exist, inform the user and stop
