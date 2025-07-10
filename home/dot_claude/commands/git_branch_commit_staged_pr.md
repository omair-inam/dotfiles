---
allowed-tools: Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*), Bash(git branch:*), Bash(git checkout:*), Bash(git push:*), Bash(gh pr create:*), Bash(git remote:*)
description: Create branch, commit staged changes, and create PR
---

## Context

- Current git status: !`git status`
- Staged changes: !`git diff --cached`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`
- Remote URL: !`git remote get-url origin 2>/dev/null || echo "No remote configured"`

## Your task

Think.
1. Create a new branch with a suitable name
2. Checkout the new branch
3. Commit ONLY the staged changes to this new branch
4. Push the branch to remote with `git push -u origin <branch-name>`
5. Create a pull request using:

```bash
gh pr create --title "<descriptive title based on changes>" --body "$(cat <<'EOF'
## Summary
<Analyze the staged changes and write 1-5 bullet points summarizing what this PR does>

## Test plan
<Based on the changes, suggest appropriate testing steps>

> Generated with [Claude Code](https://claude.ai/code)
EOF
)"
```

Important: 
- Do not stage any additional files. Only commit what is already staged.
- The PR title should be descriptive based on the committed changes
- Return the PR URL when complete

$ARGUMENTS