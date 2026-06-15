---
name: work-review
description: Review progress and plan ahead by cross-referencing Gemini meeting notes against real activity (Slack, Linear, GitHub, Claude session logs). Use for "prep my standup", "plan my day", "weekly review", "what did I get done", "plan my week", or the Monday/Friday planning sessions. Takes a MODE — daily | weekly | monday — as its argument.
---

# work-review — review & plan from meeting notes + activity

Produces an honest progress read and a prioritized plan by triangulating what was
*said* in meetings against what *actually happened* in the systems of record.

## Modes (from the user's args; infer from day/context if absent)

| mode | window reviewed | delivers |
|------|-----------------|----------|
| `daily`  | yesterday's standup (9–9:30) + EOD catchup (3:30–4) | a standup update + prioritized list for today |
| `weekly` | this week's standups + EODs (Mon→now) | progress update by theme + prioritized goals for next week |
| `monday` | the most recent Friday weekly progress review | a focused shortlist of today's key tasks |

Cadence context: the team runs **Monday = goal-setting, Friday = accomplishments.**

## Step 0 — GATE (verify access; do NOT proceed until it passes)

Hard gate — produce evidence, then state `GATE PASSED` / `GATE FAILED`. If a
required service fails, STOP and tell the user how to fix it; don't run on partial
data.

- **Google (always required):** live test, not just status —
  `gws drive files list --params '{"pageSize":1,"fields":"files(id,name)"}' 2>/dev/null`.
  If it 401s / `invalid_rapt`, STOP → ask the user to run `gws auth login`.
- **Slack + Linear (required for `daily`/`weekly` cross-ref; optional for `monday`):**
  confirm the `plugin:slack:slack` and `claude.ai Linear` MCPs respond (a trivial
  self lookup / `get_user "me"`). If down for `monday`, skip the cross-check.

## Step 1 — Gather over the mode's window

**Meetings** — use the `gemini-notes` skill to find the doc(s), then extract:
```bash
python3 ~/.claude/skills/gemini-notes/scripts/extract_gemini_doc.py <docId> --tab all --out /tmp/<label>.txt
```
Enumerate every meeting in the window (`weekly` has a variable count; some days
have no summary). Read notes **and** transcript.

**Activity** over the same window:
- **GitHub:** `gh search prs --author omairiai --updated <range>` — note merged vs **closed≠merged** vs open.
- **Linear:** issues assigned to me, `updatedAt` in window; note `completedAt`/status.
- **Slack:** `from:<@U0AG7202M70>` messages in window (confirmations, hand-offs, decisions).
- **Claude logs:**
  ```bash
  python3 ~/.claude/skills/work-review/scripts/session_activity.py --since <YYYY-MM-DD>   # or --hours 24
  ```

## Step 2 — Reconcile

Apply the **`status-reconcile`** method: map each commitment → ✅ done / 🔄
in-progress / ⛔ blocked / ❌ dropped with evidence; then surface the two gaps —
**committed-but-not-done** and **done-but-unreported** (the infra/reliability work
the summaries under-credit). Recency wins on conflicts; triangulate before
declaring status.

## Step 3 — Deliver (per mode)

- **daily:** a present-ready standup update (Yesterday / Today / Blockers) + a
  prioritized action list for today; lead with the most important.
- **weekly:** progress update grouped by workstream/theme + a prioritized set of
  goals for next week (P0/P1/P2 + watching), blockers flagged. Offer an HTML
  report.
- **monday:** a focused, day-sized shortlist (≈3–6 items) of today's key tasks,
  lead with #1, one line of why + any blocker; park the rest under "later this
  week".

## Identities & gotchas

- GitHub `omairiai` · Linear/Google `omair@i.ai` · Slack `U0AG7202M70`.
- All `gws` calls: pipe `2>/dev/null` (keyring line corrupts JSON).
- Dates are **relative to today** — compute the window; "most recent Friday" may
  be >3 days back after a long weekend.
