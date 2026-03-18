# Fix Workflow

Fix a specific Dependabot pull request to make it CI-green and ready for merge.

## Inputs

- **PR number** (required)
- **Review report path** (optional) — if provided, use the Fix Instructions section for the specified PR

## Steps

### Step 1: Gather Context

**If review report provided:**
- Read the report file
- Locate the Fix Instructions section for the PR
- Use the documented root cause and fix steps

**If no report provided:**
- Analyze the PR directly to identify the root cause of CI failures

### Step 2: Diagnose Issue

Common Dependabot PR issues:

| Issue | Symptoms | Fix |
|-------|----------|-----|
| Lockfile out of sync | `npm ci` fails with missing packages | `npm install` and commit lockfile |
| Outdated branch | Merge conflicts or stale checks | Rebase on main |
| Breaking changes | Test failures | Update code for new API |
| Type errors | TypeScript compilation fails | Update type definitions |

### Step 3: Apply Fix

```bash
# Checkout the PR branch
gh pr checkout <pr-number>

# Ensure main is up to date
git fetch origin main

# Apply fix based on diagnosis (example: lockfile sync)
npm install
git add package-lock.json
git commit -m "fix: sync lockfile with package.json"

# Push changes
git push
```

### Step 4: Verify Fix

Confirm the fix worked:
- CI status is passing or pending
- No merge conflicts
- PR is mergeable

Wait for CI to complete after pushing:
```bash
gh pr checks <pr-number> --watch
```

### Step 5: Update Report (if provided)

If a review report path was provided:

1. Update the Execution Plan row for the PR:
   - Status: ✅ Complete (if CI passes) or ❌ Failed (if CI fails)
   - Notes: Add fix description and timestamp

2. Update Execution Progress:
   - Last Updated: current timestamp

3. Save the report file

### Step 6: Report Result

**Success:**
```
✅ PR #[n] fixed and ready for merge
- Fix applied: [description]
- CI Status: All checks passing
- Next: Run merge workflow or `gh pr merge [n] --squash --delete-branch`
```

**Failure:**
```
❌ PR #[n] fix incomplete
- Issue: [description]
- CI Status: [status]
- Action needed: [next steps]
```

## Common Fix Patterns

### Lockfile Sync
```bash
gh pr checkout <pr-number>
npm install
git add package-lock.json
git commit -m "fix: sync lockfile with package.json"
git push
```

### Rebase on Main
```bash
gh pr checkout <pr-number>
git fetch origin main
git rebase origin/main
git push --force-with-lease
```

### Update After Upstream Merge
```bash
gh pr checkout <pr-number>
git fetch origin main
git merge origin/main
# Resolve conflicts if any
npm install
git add .
git commit -m "fix: merge main and update lockfile"
git push
```
