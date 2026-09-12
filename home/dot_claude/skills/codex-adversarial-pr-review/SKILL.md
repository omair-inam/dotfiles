---
name: codex-adversarial-pr-review
description: Use when a pull request needs an adversarial second-opinion review from Codex — before merge, after implementation is complete, or when the user says "codex review the PR", "adversarial review", "red-team this PR", or "get a second opinion on this change".
---

# Codex adversarial PR review

Dispatch a sub-agent that runs the Codex plugin's `adversarial-review` and posts the result as a PR comment. Then, in the main context, address every finding.

Do NOT use the `codex:codex-rescue` agent for this — its runtime skill forbids calling `adversarial-review`. Dispatch a `pstack:poteto-agent` sub-agent.

## 1. Preflight (main agent)

```bash
COMPANION=$(ls -d "$HOME"/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)
gh pr view --json number,url,baseRefName
```

- `COMPANION` empty → the Codex plugin is not installed; stop and tell the user.
- `no pull requests found` → stop and tell the user (offer to create the PR first).

## 2. Dispatch the sub-agent

One `pstack:poteto-agent` agent, background is fine. Prompt template (fill `<...>`):

```
Run an adversarial Codex review of PR #<number> and post it as a PR comment.

1. Run and capture stdout (this can take several minutes; do not background it):
   node "<COMPANION>" adversarial-review --wait --base <baseRefName> <optional focus text>
2. If the command fails or stdout is empty, post NOTHING and return the error verbatim.
3. Write the comment body to a temp file:
   - First, this header verbatim:
     > [!IMPORTANT]
     > *This review comment was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*
   - Then a "## Codex adversarial review" heading.
   - Then the review output verbatim — do not paraphrase, soften, or fix anything.
4. Post it: gh pr comment <number> --body-file <tmpfile>
5. Return: the comment URL and the full review text. Your final text is data for the caller, not a user-facing message.
```

## 3. Address the findings (main agent)

When the sub-agent returns, do not stop at relaying the review:

1. Verify each finding against the code before acting — triage each per poteto-mode's `references/bugbot-triage.md` (fix, dismiss with a reason, or ask). Adversarial reviews are calibrated to break confidence; some findings are rebuttable.
2. Fix the real ones; commit and push to the PR branch.
3. Reply on the PR (with the same header) listing each finding as fixed (commit SHA) or rebutted (why), so the thread doesn't read as ignored.

## Common mistakes

- Routing through `codex:codex-rescue` or `task` — wrong command, and the rescue agent must not orchestrate.
- Sub-agent posting a comment after a failed/empty review run.
- Passing `--scope staged`/`unstaged` — adversarial-review doesn't support them; use `--base <ref>` for PR scope.
- Main agent skipping step 3 — the review is input, not the deliverable.
