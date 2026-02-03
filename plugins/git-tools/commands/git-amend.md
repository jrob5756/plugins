---
description: Amend the last commit
argument-hint: [new message]
allowed-tools: Bash, Read
---

# Git Amend

Amend the last commit with staged changes and/or a new message.

## Steps

1. Run `git log -1 --oneline` to show current last commit
2. Run `git status` to check for staged/unstaged changes
3. If unstaged changes exist, ask if user wants to stage them
4. Determine action:
   - If message provided ($ARGUMENTS), use it
   - Otherwise ask: keep current message or provide new one?
5. Run appropriate amend command:
   - Keep message: `git commit --amend --no-edit`
   - New message: use HEREDOC format below

## Commit Message Format

```bash
git commit --amend -m "$(cat <<'EOF'
Your new message here

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

## Warnings

- **If commit was pushed**: Warn that `git push --force-with-lease` will be needed
- **Never force push to main/master** without explicit user confirmation
- Show the difference between old and new commit
