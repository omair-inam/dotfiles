---
allowed-tools: Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*)
description: Commit all changes in tracked files
---

## Context

- Current git status: !`git status`
- All changes (staged and unstaged): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your task
Think.
1. Stage all changes in tracked files using `git add -u`
2. Create a git commit with all the changes

$ARGUMENTS

Important: Only stage changes in already tracked files (using -u flag). Do not add untracked files.