---
allowed-tools: Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*), Bash(git branch:*), Bash(git checkout:*), Bash(git add:*)
description: Create a new branch and commit all changes in tracked files
---

## Context

- Current git status: !`git status`
- All changes (staged and unstaged): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`
- Remote URL: !`git remote get-url origin 2>/dev/null || echo "No remote configured"`

## Your task
Think.
* Create a new branch with a suitable name.
* Checkout the new branch
* Stage all changes in tracked files using `git add -u`
* Commit all the changes

Important: Only stage changes in already tracked files (using -u flag). Do not add untracked files.

$ARGUMENTS