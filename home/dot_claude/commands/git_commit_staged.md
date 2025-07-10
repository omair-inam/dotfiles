---
allowed-tools: Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*)
description: Commit all staged changes
---

## Context

- Current git status: !`git status`
- Staged changes: !`git diff --cached`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your task
Think.
Based on the staged changes shown above, create a git commit for ONLY the staged changes. Do not stage any additional files.

$ARGUMENTS