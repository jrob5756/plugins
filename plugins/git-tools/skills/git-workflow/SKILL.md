---
name: git-workflow
argument-hint: "[acp | afp | bacp | bacpm | b | mdb | p] [optional hint or message]"
description: |
  Git workflow automation — stage, commit, push, branch, PR, merge, and sync in single operations. Use when the user wants to commit and push changes, amend a commit, create a branch and PR, ship changes end-to-end, merge a PR and clean up, or sync with remote. Triggers: acp, add commit push, commit and push, push my changes, afp, amend, amend commit, force push, update last commit, bacp, branch add commit push, branch and PR, open PR, bacpm, branch commit push merge, ship it, land this, b, branch, create branch, new branch, new branch from changes, mdb, merge, merge PR, merge and delete, merge branch, close branch, p, sync, pull, pull rebase, fetch and pull, update branch. Use this skill even if the user doesn't name a specific workflow — infer the right one from context.
---

# Git Workflows

Automated git workflow shortcuts. Parse the user's request to determine which workflow to run.

## Dispatch

| User says | Workflow |
|-----------|----------|
| "acp", "add commit push", "commit and push", "push my changes" | **ACP** |
| "afp", "amend", "amend commit", "force push", "update last commit" | **Amend** |
| "bacp", "branch and PR", "branch add commit push", "open PR" | **BACP** |
| "bacpm", "ship it", "land this", "branch commit push merge" | **BACPM** |
| "b", "branch", "create branch", "new branch" | **Branch** |
| "mdb", "merge", "merge PR", "merge and delete", "merge branch", "close branch" | **Merge** |
| "p", "sync", "pull", "pull rebase", "fetch", "update branch" | **Sync** |

## Constraints

- **Never commit secrets** — skip files that look like `.env`, credentials, keys, tokens, certificates. If detected, warn the user and exclude them.
- **Never use `--force`** — always use `--force-with-lease` when force-pushing.
- **Never use `git add -A`** — stage specific files, except in the Amend workflow where `git add .` is acceptable.

## Rules

These rules apply to **all** workflows.

### Staging

Stage specific files explicitly:

```bash
git add src/file1.ts src/file2.ts
```

### Commit Messages

Use conventional commits: `type(scope): description`

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`, `ci`, `build`

Generate the message from the diff — describe _what_ the changes do, not which files changed.

For multi-line messages, use a HEREDOC:

```bash
git commit -m "$(cat <<'EOF'
type(scope): short description

Longer body explaining what and why.
EOF
)"
```

### Branch Naming

| Prefix | When |
|--------|------|
| `feature/` | New features or capabilities |
| `fix/` | Bug fixes |
| `chore/` | Maintenance, config, dependency updates |
| `docs/` | Documentation-only changes |
| `refactor/` | Restructuring without behavior change |
| `test/` | Test additions or updates |

Format: `prefix/kebab-case-description`. Use the user's hint if provided.

### Command Chaining

Chain sequential git operations with `&&` in a single shell invocation so the chain stops on first failure.

### GH CLI Errors

If `gh` returns a 404 or permission error, try `gh auth switch` and retry before reporting failure.

---

## Quick Reference

```bash
# ACP — stage, commit, push
git add <files> && git commit -m "type(scope): msg" && git push

# Amend — update last commit
git add . && git commit --amend --no-edit && git push --force-with-lease

# Branch — create from changes
git stash && git pull --rebase origin main && git checkout -b <name> && git stash pop && git push -u origin <name>

# BACP — branch + PR
git checkout -b <name> && git add <files> && git commit -m "msg" && git push -u origin <name> && gh pr create --base main --title "msg" --body "summary"

# BACPM — branch + PR + merge
# BACP steps, then: gh pr merge --squash --delete-branch && git checkout main && git pull --rebase origin main

# Merge — merge PR and delete branch
gh pr merge --squash --delete-branch && git checkout main && git pull --rebase origin main && git branch -d <branch-name>

# Sync — fetch + rebase
git fetch && git pull --rebase
```

---

## Workflows

### ACP — Add, Commit, Push

**When to use:** The user wants to commit and push current changes on an existing branch.

1. **Review changes:**
   ```bash
   git status --short && git diff
   ```
   If no changes exist, inform the user and stop.

2. **Stage, commit, and push:**
   ```bash
   git add <files> && git commit -m "type(scope): description" && git push
   ```

**Output:** Confirm the commit hash and that the push succeeded.

---

### Amend — Amend Last Commit & Force Push

**When to use:** The user wants to fold pending changes into the previous commit, optionally with a new message.

1. **Review state:**
   ```bash
   git status --short && git log --oneline -1
   ```
   If no pending changes, inform the user and stop.

2. **Amend and push:**
   ```bash
   git add . && git commit --amend --no-edit && git push --force-with-lease
   ```
   If the user provides a new message, use `--amend -m "new message"` instead of `--no-edit`.

**Output:** Confirm the amended commit hash and that force-push succeeded.

---

### Branch — Create Branch from Changes

**When to use:** The user has uncommitted changes and wants to move them onto a new branch.

1. **Review changes:**
   ```bash
   git status --short && git diff
   ```
   If no changes exist, inform the user and stop.

2. **Prepare the base:**
   - If on `main`/`master`: stash changes and pull latest:
     ```bash
     git stash && git pull --rebase origin main
     ```
   - Otherwise: branch from current (no stash needed).

3. **Create branch, restore changes, and push:**
   ```bash
   git checkout -b <branch-name> && git stash pop && git push -u origin <branch-name>
   ```
   Omit `git stash pop` if nothing was stashed.

**Output:** Confirm the branch name and that it was pushed to remote.

---

### BACP — Branch, Add, Commit, Push, PR

**When to use:** The user wants to create a feature branch from main, commit changes, push, and open a PR — all in one step.

1. **Verify on main.** Run `git branch --show-current`. If not on `main`, stop and tell the user.

2. **Pull latest:**
   ```bash
   git pull --rebase origin main
   ```

3. **Review changes:**
   ```bash
   git status --short && git diff
   ```
   If no changes exist, inform the user and stop.

4. **Create branch** — infer name from the diff using the branch naming convention:
   ```bash
   git checkout -b <branch-name>
   ```

5. **Stage, commit, and push:**
   ```bash
   git add <files> && git commit -m "type(scope): description" && git push -u origin <branch-name>
   ```

6. **Create PR:**
   ```bash
   gh pr create --base main --title "type(scope): description" --body "Summary of changes"
   ```

**Output:** Confirm the PR URL.

---

### BACPM — Branch, Add, Commit, Push, PR, Merge

**When to use:** The user wants the full end-to-end flow — branch, commit, push, PR, merge, and clean up. "Ship it."

Run the full **BACP** workflow (steps 1–6 above), then:

7. **Ask to merge** — prompt the user: *"PR created. Merge now?"*
   - **Yes:**
     ```bash
     gh pr merge --squash --delete-branch && git checkout main && git pull --rebase origin main && git branch -d <branch-name>
     ```
   - **No:** Stop and report the PR URL.

**Output:** Confirm the merge and that the local branch was cleaned up (or the PR URL if not merged).

---

### Merge — Merge PR & Delete Branch

**When to use:** The user wants to merge the current branch's PR and clean up the branch locally and remotely.

1. **Verify not on main:**
   ```bash
   git branch --show-current
   ```
   If on `main`/`master`, stop and tell the user there is nothing to merge.

2. **Check PR status:**
   ```bash
   gh pr view --json state,mergeable,title,url
   ```
   If no PR exists for the current branch, stop and tell the user. If the PR is not mergeable, report the reason.

3. **Merge and clean up:**
   ```bash
   gh pr merge --squash --delete-branch && git checkout main && git pull --rebase origin main
   ```
   Then delete the local branch if it still exists:
   ```bash
   git branch -d <branch-name>
   ```

**Output:** Confirm the PR was merged, the remote branch was deleted, and the local branch was cleaned up.

---

### Sync — Pull with Rebase

**When to use:** The user wants to update their current branch from remote.

1. **Check for uncommitted changes:**
   ```bash
   git status --short
   ```
   If changes exist, warn the user and suggest committing or stashing first. Do not proceed.

2. **Fetch and rebase:**
   ```bash
   git fetch && git pull --rebase
   ```

3. **Show final state:**
   ```bash
   git status --short && git log --oneline -3
   ```

4. **If conflicts occur:** list the conflicting files and explain resolution options:
   - Edit files to resolve → `git add <files>` → `git rebase --continue`
   - Or `git rebase --abort` to cancel

**Output:** Show the latest 3 commits and confirm the branch is up to date.
