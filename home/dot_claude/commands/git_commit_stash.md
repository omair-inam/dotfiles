---
allowed-tools: Bash(git status:*), Bash(git stash:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*)
description: Apply and commit changes from a stash
---

## Context

- Current git status: !`git status`
- Current branch: !`git branch --show-current`
- Available stashes: !`git stash list`
- Recent commits: !`git log --oneline -10`

## Your task

Think.
1. Parse the stash documentation provided below to identify:
   - The stash reference (e.g., stash@{0})
   - The original branch name
   - Summary of changes
2. Apply the stash using `git stash apply <stash-ref>`
3. Review the applied changes
4. Create a commit with an appropriate message based on the stash documentation
5. Optionally drop the stash after successful commit

Important: The stash documentation content should be provided below:

$ARGUMENTS