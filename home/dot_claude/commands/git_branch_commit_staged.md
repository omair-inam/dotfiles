---
allowed-tools: Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*), Bash(git branch:*), Bash(git checkout:*)
description: Create a new branch and commit all staged changes
---

## Context

- Current git status: !`git status`
- Staged changes: !`git diff --cached`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`
- Remote URL: !`git remote get-url origin 2>/dev/null || echo "No remote configured"`

## Your task
Think.
* Create a new branch with a suitable name.
* Checkout the new branch
* Commit ONLY the staged changes to this new branch

Important: Do not stage any additional files. Only commit what is already staged.

$ARGUMENTS