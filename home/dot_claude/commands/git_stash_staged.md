---
allowed-tools: Bash(git status:*), Bash(git stash:*), Bash(git diff:*), Edit(stash_*.md), Bash(pbcopystr:*)
description: Stash staged changes and create documentation
---

## Context

- Current git status: !`git status`
- Staged changes: !`git diff --cached`
- Current branch: !`git branch --show-current`
- Current timestamp: !`date +"%Y%m%d_%H%M%S"`

## Your task

Think.
1. Create a partial stash of only the staged changes using `git stash push --staged -m "CC staged ($(git branch --show-current)): <1-line summary of changes>"`.  If no staged changes are found STOP execution and remind user to stage changes first.
2. Generate a filename: stash_<timestamp>_<branch_name>.md
3. Create a markdown file with:
   - Stash reference and date
   - Original branch name
   - Summary of staged changes (files modified, lines added/removed)
   - List of files that were stashed
   - Instructions for applying the stash later
4. Run the command `pbcopystr "<file_path>"` which will copy the file path to the clipboard
5. Show the user the stash reference and file location

$ARGUMENTS