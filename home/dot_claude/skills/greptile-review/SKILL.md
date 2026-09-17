---
name: greptile-review
description: Use when asked to fire off, run, or request a Greptile code review on a GitHub PR, or to handle, address, or resolve Greptile review comments/findings on a PR.
---

# greptile-review

One pass: trigger Greptile on a PR, wait for its findings, verify and fix the
real ones, then reply to **and resolve** every thread. A reply without a
resolve reads as ignored — `pr-watch` and other sweeps re-flag it and offer to
dispatch a fix agent for work already done.

## Verified mechanics (observed on I-AI-Corp/iai-explorer)

| Fact | Value |
|---|---|
| Trigger | Issue comment `@greptileai` on the PR (`@greptileai review` also works) |
| Bot login | `greptile-apps[bot]` |
| Summary | Arrives as an **issue comment** starting `<h3>Greptile Summary</h3>` — not the review body |
| Inline findings | PR **review comments**; body starts with a severity badge image (`badges/p1.svg`, `p2.svg`, …) |
| Latency | Usually 1–5 minutes; a re-trigger on an unchanged head SHA may report no new findings |

## Steps

1. **Trigger.** Record the time, then:
   ```bash
   gh pr comment <N> --body "@greptileai"
   ```
2. **Wait.** Sleep is blocked in the foreground — use the Monitor tool with an
   until-loop, or a backgrounded bash poll. Done when this returns rows with
   `created_at` after the trigger time:
   ```bash
   gh api repos/{owner}/{repo}/pulls/<N>/comments \
     --jq '.[] | select(.user.login=="greptile-apps[bot]") | {id, path, line, created_at, body}'
   ```
   First check after ~2 min, then every 60–90 s. Also fetch the summary from
   `issues/<N>/comments` (same login filter). No response after ~10 min: stop
   and tell the user; do not re-trigger in a loop.
3. **Triage each finding.** Triage per poteto-mode's `references/bugbot-triage.md` (fix, dismiss with a reason, or ask); verify
   against the code before complying; Greptile has false positives. Findings
   anchor at the *usage* line, not the definition, so a quoted snippet can look
   current when the underlying value already changed — check the definition
   before concluding a finding still stands.
4. **Fix.** Edit, run the repo's tests, commit, push. One commit for the batch
   is fine.
5. **Reply to every thread** — fixed ones cite the commit; declined ones state
   why. Start each reply with the AI-assistance header required by CLAUDE.md:
   ```
   > [!IMPORTANT]
   > *This review comment was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*
   ```
   ```bash
   gh api --method POST /repos/{owner}/{repo}/pulls/<N>/comments/<COMMENT_ID>/replies -f 'body=...'
   ```
6. **Resolve every addressed thread.** Resolution is separate state from the
   reply, and GraphQL-only:
   ```bash
   # map comment ids -> thread ids
   gh api graphql -f query='{repository(owner:"OWNER",name:"REPO"){pullRequest(number:N){
     reviewThreads(first:50){nodes{id isResolved comments(first:1){nodes{databaseId author{login} path}}}}}}}'
   # resolve
   gh api graphql -f query='mutation{resolveReviewThread(input:{threadId:"PRRT_..."}){thread{isResolved}}}'
   ```
   Resolve only threads actually fixed or explicitly declined-with-reason.
7. **Report.** Per finding: fixed (commit) / declined (reason) / needs the
   user. Note the Greptile summary verdict if it flagged anything you didn't
   act on.

## Common mistakes

| Mistake | Reality |
|---|---|
| Reply but don't resolve | Indistinguishable from ignoring it; watchers re-flag it |
| Poll `pulls/<N>/reviews` only | The summary is an issue comment; inline findings are review comments |
| Trust a finding's quoted snippet | It anchors at the usage line; check the definition first |
| Re-trigger repeatedly when slow | One trigger, poll, then hand back to the user after ~10 min |
| Blanket-resolve everything | Only resolve what was fixed or declined with a stated reason |
