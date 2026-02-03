---
description: Create a new feature branch
argument-hint: [branch-name]
allowed-tools: Bash, Read
---

# Git Branch

Create a new branch from the current branch or main/master.

## Steps

1. Run `git status` to check current state
2. Use branch name: $ARGUMENTS
   - If not provided, ask the user for a name
3. Ask if branching from current branch or main/master
4. If branching from main/master:
   ```bash
   git fetch origin
   git checkout main
   git pull
   ```
5. Create and checkout the new branch:
   ```bash
   git checkout -b <branch-name>
   ```
6. Push and set upstream:
   ```bash
   git push -u origin <branch-name>
   ```

## Branch Naming Conventions

Suggest conventional names based on description:
- `feature/<description>` - new features
- `fix/<description>` - bug fixes
- `chore/<description>` - maintenance
- `docs/<description>` - documentation
