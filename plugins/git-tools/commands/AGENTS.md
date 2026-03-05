# Git Commands — Agent Guidelines

## Self-Contained Commands

Every command file must be **fully self-contained**. Do not reference or delegate to other command files. Each command includes all the steps it needs inline, even if that means duplicating logic across commands. This ensures reliability — the AI never has to resolve cross-file references or interpret markdown links as directives.

If a command shares steps with another (e.g., `bacp` includes all of `acp`'s logic plus branching), duplicate those steps directly rather than writing "follow steps in X."

## Combine Commands with `&&`

Chain sequential git operations into a single shell invocation wherever possible. Fewer tool calls = faster execution and less room for the AI to drift between steps.

```bash
# Good — one call
git add <files> && git commit -m "message" && git push -u origin <branch>

# Bad — three separate calls
git add <files>
git commit -m "message"
git push -u origin <branch>
```

Use `&&` so the chain stops on the first failure. Group operations that logically belong together:

- **Stage + commit + push**: `git add <files> && git commit -m "msg" && git push`
- **Merge + cleanup**: `gh pr merge --squash --delete-branch && git checkout main && git pull --rebase origin main && git branch -d <branch>`
- **Stash + switch + pull**: `git stash && git checkout main && git pull`
- **Amend + force push**: `git add . && git commit --amend --no-edit && git push --force-with-lease`

## Standard Patterns

### Reviewing Changes

Always inspect the working tree before acting. Combine status and diff:

```bash
git status --short && git diff --stat
```

Use `git diff` (full diff) when the command needs to understand the _content_ of changes (e.g., to generate a commit message or branch name). Use `git status --short` when you just need the file list.

### Staging Files

Prefer staging specific files over `git add -A` or `git add .`. This avoids accidentally committing secrets (`.env`, credentials, keys, tokens). List the files explicitly:

```bash
git add src/file1.ts src/file2.ts
```

Never commit files that look like secrets.

### Commit Messages

Use conventional commit format: `type(scope): description`.

For multi-line messages, use a HEREDOC:

```bash
git commit -m "$(cat <<'EOF'
type(scope): short description

Longer body explaining what and why.
EOF
)"
```

Generate the message from the diff — describe _what_ the changes do, not which files changed.

### Branching

Infer the branch name from the changes. Use this prefix convention:

| Prefix | When |
|--------|------|
| `feature/` | New features or capabilities |
| `fix/` | Bug fixes |
| `chore/` | Maintenance, config, dependency updates |
| `docs/` | Documentation-only changes |
| `refactor/` | Restructuring without behavior change |
| `test/` | Test additions or updates |

Format: `prefix/kebab-case-description` (e.g., `feature/add-user-auth`, `docs/update-readme`).

If `$ARGUMENTS` is provided, use it as a hint or override for the name.

### Pushing

- First push on a new branch: `git push -u origin <branch-name>`
- Subsequent pushes: `git push`
- After amending: `git push --force-with-lease` (never `--force`)

### Syncing

Always rebase when pulling:

```bash
git pull --rebase origin main
```

Check for uncommitted changes before syncing. If present, either commit or stash first.

### Creating PRs

Use the GitHub CLI:

```bash
gh pr create --base main --title "type(scope): description" --body "Summary of changes"
```

If `gh` returns a 404 or permission error, try `gh auth switch` and retry.

### Merging & Cleanup

Squash-merge, delete the remote branch, return to main, and clean up local:

```bash
gh pr merge --squash --delete-branch && git checkout main && git pull --rebase origin main && git branch -d <branch-name>
```

Always ask the user before merging.

## Handling Errors

- If there are no pending changes, inform the user and stop — don't create empty commits.
- If a rebase has conflicts, list the conflicting files and explain resolution steps (`git add` → `git rebase --continue` or `git rebase --abort`).
- If the user is on the wrong branch for a command that requires `main`, stop and tell them.
