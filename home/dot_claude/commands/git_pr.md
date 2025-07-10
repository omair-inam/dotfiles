---
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git push:*), Bash(gh pr create:*), Bash(git branch:*), Bash(git remote:*)
description: Create a GitHub pull request
---

## Context

- Current git status: !`git status`
- Current branch: !`git branch --show-current`
- Branch tracking info: !`git status -sb`
- Commits to be included in PR: !`git log origin/$(git symbolic-ref --short refs/remotes/origin/HEAD | cut -d'/' -f2)..HEAD --oneline 2>/dev/null || git log --oneline -10`
- All changes since base branch: !`git diff origin/$(git symbolic-ref --short refs/remotes/origin/HEAD | cut -d'/' -f2)...HEAD --stat 2>/dev/null || echo "Unable to determine base branch"`
- Remote URL: !`git remote get-url origin`

## Your task
Think.
1. Verify we're not on the main/master branch
2. Check if the current branch needs to be pushed to remote (look at the tracking info)
3. If the branch needs to be pushed, push it with: `git push -u origin <branch-name>`
4. Create a pull request using this format:

```bash
gh pr create --title "<suitable PR title>" --body "$(cat <<'EOF'
## Summary
<Analyze all the commits and changes to write 1-5 bullet points summarizing what this PR does>

## Test plan
<Based on the changes, suggest appropriate testing steps>

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
)"
```

Important: 
- Analyze ALL commits that will be included in the PR (not just the latest)
- The summary should reflect all changes in the branch since it diverged from the base

$ARGUMENTS