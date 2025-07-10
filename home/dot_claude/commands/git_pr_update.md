---
allowed-tools: Bash(git status:*), Bash(git push:*), Bash(gh pr view:*), Bash(gh pr comment:*), Bash(git log:*)
description: Push changes and update existing PR
---

## Context

- Current branch: !`git branch --show-current`
- Current PR status: !`gh pr view --json state,number,title 2>/dev/null || echo "No PR found"`
- Recent commits: !`git log --oneline -5`
- Unpushed commits: !`git log origin/$(git branch --show-current)..HEAD --oneline 2>/dev/null || echo "Branch not pushed yet"`

## Your task

Think.
1. Push the current branch to remote
2. If a PR exists
  * update PR description to incorporate changes from new commits.
  * add a comment about the new commits
3. Show the PR URL and status

$ARGUMENTS