---
name: worktree-audit
description: Audit all git worktrees in a repository and produce a categorized, read-only report (safe-to-close vs. needs-attention vs. active). Use when the user asks to "clean up worktrees", "audit worktrees", "list worktrees with merged PRs", "which worktrees can I delete", or any phrasing about reviewing the state of worktrees before reclaiming them. Cross-references each branch against GitHub PRs via the `gh` CLI and inspects each worktree for uncommitted changes and unpushed commits. Read-only — never deletes or modifies anything.
---

# Worktree Audit

## What this skill does

Runs `scripts/audit_worktrees.py` against the current repository. The script:

1. Enumerates worktrees via `git worktree list --porcelain` (skips the main worktree).
2. Looks up each branch's PR via `gh pr list --head <branch> --state all`.
3. Inspects each worktree for uncommitted changes and unpushed commits.
4. Emits a markdown report with these sections: `Safe to close (merged)`, `Safe to close (closed without merging)`, `Needs attention before closing`, `Active (PR open)`, `Active (no PR yet)`, plus an `Unusual / skipped` section if relevant.

## Constraints

- **Read-only.** Never run `git worktree remove`, `git branch -d`, `git push --delete`, `rm -rf .worktrees/...`, or any destructive command. The user reviews the report and decides what to do.
- **Hard fail on unauthenticated `gh`.** If `gh auth status` fails, abort and tell the user to run `ghinit` / `ghinitdna` (per their CLAUDE.md). Do not guess PR state.
- The user may follow up by asking to remove specific worktrees. Treat each removal as a separate, explicit instruction — don't batch-remove based on the audit alone.

## How to run

From any checkout of the target repository:

```bash
~/.claude/skills/worktree-audit/scripts/audit_worktrees.py
```

Or against a specific repo path:

```bash
~/.claude/skills/worktree-audit/scripts/audit_worktrees.py --repo /path/to/repo
```

The script prints markdown to stdout. Pipe it directly to the user — don't rewrite the report. If the report is long, present it verbatim and let the user choose what to act on.

## Categorization rules

The script uses these rules — re-state them to the user if asked:

| Category | Conditions |
|---|---|
| Safe to close (merged) | PR `MERGED` AND no uncommitted changes AND no unpushed commits |
| Safe to close (closed without merging) | PR `CLOSED` AND no uncommitted changes — flagged for confirmation since work was abandoned |
| Needs attention | PR `MERGED` or `CLOSED` BUT has uncommitted changes or unpushed commits — lists what would be lost |
| Active (PR open) | PR is `OPEN` |
| Active (no PR yet) | No PR found for the branch (or directory-name fallback) |
| Unusual / skipped | Detached HEAD, bare worktrees, or worktrees outside `.worktrees/` |

PR matching tries the branch name first, then falls back to the worktree directory name (annotated in the report when used).

## After presenting the report

Do not propose removals unless the user asks. If they do, for each worktree they pick:

1. Re-verify status (a worktree's state may have changed since the audit).
2. Show the exact commands you would run (`git worktree remove <path>`, optionally `git branch -d <branch>`).
3. Wait for explicit approval before running them.

Never use `git worktree remove --force` without explicit instruction — the `--force` flag bypasses the dirty-tree safety check that prevents data loss.
