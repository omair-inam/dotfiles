---
allowed-tools: Bash(git branch:*), Bash(git worktree:*), Bash(git status:*)
description: Create a new branch with worktree
---

## Context

- Current branch: !`git branch --show-current`
- Existing worktrees: !`git worktree list`
- Repository name: !`basename $(pwd)`

## Your task

Think.
1. Create a new branch with an appropriate name
2. Create a new worktree for this branch in ../$(basename $(pwd))-<branch-name>
3. Show the path to the new worktree
4. Provide instructions for switching to the new worktree

$ARGUMENTS