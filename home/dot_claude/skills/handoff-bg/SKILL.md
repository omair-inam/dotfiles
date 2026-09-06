---
name: handoff-bg
description: Hand the current conversation off to a fresh background Claude Code session that continues the work immediately, optionally on a different model or effort level.
argument-hint: "[on <model>] [at <effort> effort] <what the next session will focus on>"
disable-model-invocation: true
---

# handoff-bg

`/handoff`, then launch a background session that picks the doc up. Seven steps, in order.

## 1. Parse the argument

- **model**: a word the CLI accepts (`fable`, `opus`, `sonnet`, `haiku`, or a full id such as `claude-sonnet-5`) following "on", "with", or "model".
- **effort**: exactly one of `low`, `medium`, `high`, `xhigh`, `max`, anywhere in the argument. Nothing else counts; "think hard" is not an effort.
- **focus**: whatever remains after removing the model and effort clauses. Empty is fine.

Unrecognized model or effort words: omit that flag, say so in the report. Do not validate further; the CLI rejects bad values itself.

## 2. Name the session

The name is the whole of what `claude agents` and the job list show. It has to say what the work is to someone who never saw this conversation. Build it before the doc, so the doc's slug and the session's name share one essence.

```
<emoji> <TICKET-ID> <essence>
```

- **emoji**: one type marker from the table below. Exactly one, always first.
- **TICKET-ID**: `IAI-1340` when the work has a ticket. Drop the segment when it does not; never invent one.
- **essence**: the change itself, in the work's own nouns, three to eight words, no trailing punctuation.

Cap the whole name at 60 characters. Trim the essence to fit; never drop the emoji or the ticket.

**The essence comes from the ticket, not from the user's phrasing.** "work on IAI-1340" names nothing. Compress the ticket's own title. Fetch it with `mcp__linear-server__get_issue` when you do not already have it. With no ticket, compress the conversation's subject the same way. Name the outcome, not the activity: cut "work on", "continue", "handle", "look at", "help with", "investigate".

For IAI-1340, titled "Perception reads a named series as one work instead of its first member":

| | |
|---|---|
| Useless | `🤝 work on IAI-1340` |
| Vague | `✨ IAI-1340 perception improvements` |
| Right | `✨ IAI-1340 series named whole becomes one work` |

**Type emoji.** Take it from the poteto playbook this handoff runs. With no playbook, take it from the nature of the work.

| Emoji | Type | Playbook |
|---|---|---|
| 🐛 | bug fix | Bug fix |
| 🔍 | investigation | Investigation, runtime forensics, trace forensics |
| ✨ | feature | Feature, Prototype |
| ♻️ | refactor | Refactoring |
| ⚡ | perf | Perf issue, Hillclimb |
| 🧪 | eval | Eval |
| 🛠 | tooling | Authoring a skill, CI, dev workflow |
| 📝 | writing | Specs, plans, docs, PR prose |
| 🚢 | ship | Babysit, Shipping |

No 🤝. Every handoff carried it, so it separated nothing.

**Color.** The job list colors each session, and the emoji and the color say different things: the emoji is the kind of work, the color is the phase the child starts in. Pick one from this table. `claude --bg` has no color flag, so step 5 sets it after launch.

| Kind and phase | Color |
|---|---|
| Bug, diagnosis | red |
| Bug, fixing | orange |
| Bug, validation | yellow |
| Feature, brainstorming | purple |
| Feature, implementation | blue |
| Feature, validation | cyan |
| Done or merged | green |
| Spike, off-track, or anything the table does not name | pink |

Those eight are the whole palette. Nothing else is a valid value.

## 3. Write the handoff doc

Path: `/tmp/handoff-<YYYY-MM-DD>-<slug>.md`, slug from the essence you just built. Never inside the workspace.

Contents, same rules as `/handoff`:
- Summarize the conversation so a fresh agent can continue. Tailor to the focus when one was given.
- Reference specs, plans, tickets, commits, and diffs by path or URL; do not restate them.
- A "Suggested skills" section naming skills the next session should invoke.
- Redact secrets and personal data.
- State the working directory and the uncommitted state the next session inherits.

## 4. Launch

One command, run from the current working directory. The background session inherits this worktree and its uncommitted changes; do not create a new worktree or branch.

```bash
claude --bg -n "<name from step 2>" [--model <model>] [--effort <effort>] "Read /tmp/handoff-<date>-<slug>.md, then continue the work it describes."
```

Flags appear only when parsed. The prompt is that one sentence; the doc carries the context. Use `claude --bg`, not the `Agent` tool: a subagent has no `--effort`, and it dies with this session.

## 5. Set the color

`claude --bg` prints the short id. Pass it and the color from step 2 to the bundled setter:

```bash
~/.claude/skills/handoff-bg/set-job-color.py <short-id> <color>
```

It writes the `color` field in `~/.claude/jobs/<short-id>/state.json`, which is the same field the in-session `/color` command sets. It waits for the file, merges rather than replaces, and rejects a color outside the palette. Every other writer of that file merges onto a fresh read, so the color persists.

To recolor a session later, run the setter again, or attach and use `/color <name>`. `/color default` clears it. A session that is a member of a team refuses `/color`, because the leader owns its color; the setter still works.

## 6. Report

Four lines and nothing else:

```
Doc:     /tmp/handoff-<date>-<slug>.md
Session: <name>  (model: <x or default>, effort: <y or default>)
Color:   <color>
Follow:  claude attach <id printed by --bg>   ·   claude agents
```

If `claude --bg` errored, relay its message verbatim instead of the last three lines.

## 7. After launch

The doc is write-once and the child reads it at start. If you learn something later that changes the child's work (a blocked base branch, a merged dependency, a changed decision), send it: `ListAgents`, then `SendMessage` to the child session if it is listed. If it is not, post to a channel the doc names, the base PR's comments or the ticket, so the child finds it when it looks. Telling the user alone leaves the child to rediscover it.
