---
name: mining-sessions
description: Use when asked to mine, review, or harvest recent Claude Code sessions for patterns — content ideas, repeated setup steps, corrections, failed commands, or things worth adding to CLAUDE.md, a slash command, a skill, or a hook. Triggers on "read my recent sessions", "find patterns in my sessions", "what should I add to CLAUDE.md from my sessions".
disable-model-invocation: true
---

# Mining Sessions

## Overview

Read the user's recent Claude Code session transcripts, surface reusable patterns, and propose where each one belongs. **Propose only, change nothing.** Output is a numbered list with a concrete edit location per item; the user picks what to apply. The poteto `reflect` skill is the version that applies the edits itself; use it when you want changes made rather than listed.

## Where sessions live

Claude Code sessions: `~/.claude/projects/*/*.jsonl`

Each file is JSONL — one event per line: user messages, assistant tool calls, shell commands, and their output.

Default to the **20 most recent** sessions unless the user says otherwise. Sort by file mtime:

```bash
ls -t ~/.claude/projects/*/*.jsonl | head -20
```

## What to look for

- **Content-worthy moments** — things the user did that would make a good article, tweet, tutorial, diagram, prompt, product idea, or example.
- **Friction** — commands or tools that errored, or that were run several times before they worked.
- **Corrections** — moments the user corrected you: "no", "actually", "that is wrong", "don't do that again".
- **Rediscovery** — the same setup step figured out from scratch in more than one session.

## Where each pattern belongs

Tag every pattern with exactly one destination:

- a content idea to draft or add to the idea library
- a line to add to CLAUDE.md / AGENTS.md
- a slash command or skill to add or update
- a hook that should run automatically
- a tool or CLI that should be fixed
- a config or settings change
- nothing — it was a one-off

## Rules

- **Redact anything sensitive** in what you show: emails, tokens, keys.
- **Change nothing.** No edits, no new files, no config writes — just the report.
- Give a **numbered list of proposals**. Each proposal carries **the one evidence line it came from** (quoted, redacted).
- Name the file and section each proposal would land in, so applying one is a single edit.

## Output shape

```
1. [destination] Short description of the pattern.
   Evidence: "<the single redacted line from the transcript>"

2. [destination] ...
   Evidence: "..."
```
