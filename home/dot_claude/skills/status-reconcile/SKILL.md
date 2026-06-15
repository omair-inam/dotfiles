---
name: status-reconcile
description: Cross-reference stated commitments or plans against actual activity (Slack, Linear, GitHub, Claude session logs) to determine real status. Use for standup/weekly reviews, 1:1 or sprint-retro prep, or any "what did I say I'd do vs. what actually happened" check — surfacing items committed-but-not-done and work done-but-unreported.
---

# status-reconcile — commitments vs. reality

Turn a list of commitments (meeting "next steps", a plan, a prior task list, a
ticket set) into an honest status read by checking them against the systems of
record.

## Inputs

- **Commitments** — what was promised/planned.
- **Activity sources**, queried over the same time window:
  - **GitHub** — `gh search prs --author <me> --updated <range>`; check **merged
    vs closed (closed ≠ merged) vs open**, and `mergedAt`.
  - **Linear** — issues assigned to me updated in window; `completedAt` / status.
  - **Slack** — `from:<@me>` messages: confirmations, hand-offs, decisions.
  - **Claude session logs** — what was actually worked on
    (`work-review/scripts/session_activity.py`).

## Method

1. For each commitment assign **✅ done / 🔄 in-progress / ⛔ blocked / ❌ dropped**,
   each with concrete evidence (PR #, issue id, message link, log line).
2. Surface the two high-value gaps:
   - **Committed but not done** — promised, but no corresponding activity.
     *Absence is a signal*: e.g. a ticket that was supposed to be created simply
     doesn't exist in Linear.
   - **Done but unreported** — shipped work that never reached a summary (often
     the largest/infra work; explicitly claim it).
3. Note **recurring misses** — a commitment that reappears unfinished across
   several days/meetings is a pattern worth a decision, not just a carry-over.

## Cross-source rules

- **Recency wins** on conflicts — a later EOD supersedes the morning standup.
- **Triangulate** — one source misleads: a *closed* PR may be superseded (the
  logs reveal a pivot), not abandoned.
- **Verify, don't infer** — `closed ≠ merged`; an "In Progress" ticket with a
  merged PR may actually be done.
