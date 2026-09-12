---
name: slack-status-updates
description: Use when asked to post status updates, progress, or a status thread to Slack while working through an implementation plan, multi-task change, or ticket — whether given a Slack thread link or no link at all.
---

# Slack status updates

Post the progress of a multi-task implementation to Slack as one thread, anchored to the status tracker file (the implementation plan being checked off).

## Setup (once, before the first post)

1. Ticket ID from the branch name: `iai-970-retry-flow-impl` → `IAI-970`. Omit if not derivable.
2. Headline — the ticket's **own title**, fetched with Linear `get_issue`, copied verbatim. Never paraphrase it from the branch name, the tracker filename, or the task you are about to start: a branch like `iai-981-declared-reading-shape` names one phase of `IAI-981 - Implement architecture perception`, and the thread covers the ticket. With no ticket ID, use the tracker's H1.
3. Tracker URL — always the **branch** version, never main:
   `https://github.com/<owner>/<repo>/blob/<branch>/<tracker-path>`
   (owner/repo from `git remote get-url origin`). Verify the tracker's latest version is on the remote (`git diff origin/<branch> -- <tracker-path>`); commit and push first if not — the link must resolve on arrival. Pushes may need the user's 1Password Touch ID approval.
4. **No thread link given** → send the Initial message to `#iai-dev` (`C0AHXRLFTG8`) and record its `message_ts`.
   **Thread link given** → convert `p1787188257183029` to `thread_ts` `1787188257.183029` (dot before the last 6 digits); every post is a reply with that `thread_ts`. The first reply is the Initial template minus the "Follow 🧵" line.
5. Send with `slack_send_message` directly — the user asked for these updates; never use drafts.

## Templates (exact — no emoji, no extra lines, no task list in the Initial message)

**Initial:**
```
:claude-code: **IAI-xxx** - <ticket title, verbatim>
Starting implementation - Live status available [here](<tracker branch URL>)
Follow 🧵 for updates
```

If the run covers only part of the ticket, that scope goes on the second line (`Starting Phase 0 - <phase name> - Live status available [here](...)`), never in the headline.

**Task update** (thread reply, immediately after each tracker update):
```
Task m - <what was done, under 50 words> completed.
Next: Task n - <under 50 words>
```

**Final task update** (the "Next:" line is replaced):
```
Task m - <what was done, under 50 words> completed.
*Update:* Task fully completed at HH:mm:ss
Total time: <Xh Ym>
```
`HH:mm:ss` is local time. Elapsed is `Xh Ym` with the hours part omitted when zero: 74 minutes is `1h 14m`, 14 minutes is `14m`, under a minute is `0m` — never `0h 0m`. Elapsed time is anchored to the `message_ts` of the first message this run posted (Initial message, or first reply).

**Non-task tracker changes** (blocker hit, task re-scoped, plan amended): free-form thread reply, one or two sentences, no template.

## Cadence

Post the task update immediately after writing the tracker update, before starting the next task. One reply per tracker update — never batch several tasks into one reply.

If the user names a different cadence ("only at milestones", "just start and end"), follow it. Urgency about the work ("hurry", "no ceremony", "we demo in an hour") is not a cadence instruction — threaded replies cost one tool call and ping nobody; keep posting per task.

Replies are plain replies: never set `reply_broadcast`.

## Common mistakes

| Mistake | Fix |
|---|---|
| Headline paraphrased from the branch, the tracker filename, or the first task | The ticket's own title from `get_issue`; the branch may name only one phase |
| Tracker as a bare file path | Full GitHub URL, pinned to the branch |
| Batching updates under time pressure | One reply per tracker update, posted before the next task starts |
| Skipping the timestamp/elapsed lines | Both are required slots in the final update |
| `reply_broadcast` on the final reply | The Initial channel message is the channel's only notification |
