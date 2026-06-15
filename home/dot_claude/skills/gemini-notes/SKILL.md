---
name: gemini-notes
description: Find and read "Notes by Gemini" Google Doc meeting notes and transcripts via the gws CLI. Use when the user references a standup, EOD catchup, weekly review, or any Gemini-recorded meeting and you need its notes or full transcript (e.g. "read yesterday's standup notes", "get the transcript from Friday's review"). Handles locating the doc (latest / by date) and extracting both the Notes and the Transcript tabs.
---

# gemini-notes — read Gemini meeting notes & transcripts

Gemini saves meeting notes as Google Docs titled `<Meeting> - <date> - Notes by
Gemini`, with the **notes and the full transcript in two separate tabs** of the
same document. This skill finds the right doc and extracts either tab.

## 1. Find the doc

List candidates with the `gws` CLI. **Always pipe `2>/dev/null`** — `gws` prints
`Using keyring backend: keyring` to stderr, which corrupts JSON parsing:

```bash
gws drive files list --params '{"q":"name contains '"'"'Notes by Gemini'"'"' and modifiedTime > '"'"'<ISO-date>'"'"'","orderBy":"modifiedTime desc","pageSize":25,"fields":"files(id,name,modifiedTime)"}' --format json 2>/dev/null
```

**Enumerate, don't assume.** Pick the newest doc whose title matches the meeting
you want (by meeting name + date) — never hardcode a date. This handles holidays,
skipped meetings, and "the most recent Friday review".

## 2. Extract the text

Use the bundled script (handles the tab walk, nested tables, the keyring/stderr
issue, and an old-format no-tabs fallback):

```bash
python3 ~/.claude/skills/gemini-notes/scripts/extract_gemini_doc.py <documentId> --tab all
#   --tab notes | transcript | all
#   --out FILE   write to a file (recommended for long transcripts)
```

For long transcripts, pass `--out` to a temp file and read that, rather than
dumping ~50KB to stdout.

## Gotchas

- **Two tabs:** `Notes` and `Transcript`. The notes summary compresses away
  detail and sometimes reverses by end-of-day — read the transcript when nuance
  or exact commitments matter.
- **Empty summaries happen** ("not enough conversation in a supported language");
  the transcript is then the only record.
- **Auth:** if extraction errors with an `invalid_rapt`/auth message, the token
  expired — run `gws auth login`. Note `gws auth status` can look valid even when
  the token is dead, so trust a live call.
