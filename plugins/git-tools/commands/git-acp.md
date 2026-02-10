---
description: Add, commit, and push changes in one command
argument-hint: [commit message]
allowed-tools: Bash, Read, Glob, Grep
---

# Git Add-Commit-Push

Add all changes, create a commit, and push to the remote.

## Steps

1. Run `git status` to see changed files
2. Run `git diff` to review the changes
3. Stage appropriate files (prefer specific files over `git add -A` to avoid secrets)
4. Create the commit using the message: $ARGUMENTS
   - If no message provided, generate a descriptive one based on changes
5. Push to the current branch

## Commit Message Format

Use a HEREDOC for the commit message:

```bash
git commit -m "$(cat <<'EOF'
Your commit message here

EOF
)"
```

## Important

- Never commit files that look like secrets (.env, credentials, keys)
- If no changes exist, inform the user
