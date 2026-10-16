---
name: obsidian
description: Read and write Omair's Obsidian vault with the `obsidian` CLI. Use whenever Omair wants to create a note, jot or log something in today's daily note, or find, search, look up, or read anything in his notes — even when he says "my notes", "jot this down", "add to today", "what did I write about X", or names a note without saying Obsidian.
---

# Obsidian

The `obsidian` CLI (`/usr/local/bin/obsidian`) talks to the running Obsidian app. There is one vault, `omair-obsidian-vault`, at `/Users/omair/omair-obsidian-vault`, so `vault=` is never needed. Use the CLI rather than editing files directly: it resolves wikilink-style names, honours the daily-note settings, and keeps Obsidian's index in sync.

## Syntax

Arguments are `key=value`; quote any value with spaces. In `content=`, `\n` is a newline and `\t` a tab. `file=` resolves a name the way a wikilink does (`file="Claim state map"`); `path=` is exact from the vault root (`path="Projects/I.AI/Claim state map.md"`). `obsidian help` lists every command.

Content goes through the shell, so wrap it in single quotes when it contains backticks, `$`, or `!`.

## Vault conventions

- New standalone notes live at the vault root unless Omair names a folder. Other folders: `Projects/I.AI/` for work project notes, `Pages/` for reference pages.
- Daily notes: `Daily Notes/YYYY/YYYY-MM-DD.md`.
- Notes use `###` headings and `* ` bullets, with tab-indented sub-bullets. Link other notes as `[[Note name]]`.

## Create a note

```shell
obsidian create name="Note title" content="* first point\n* second point"
obsidian create path="Projects/I.AI/Note title.md" content="..."
```

`create` does not fail when the note exists: it silently writes `Note title 1.md` beside it. Check first with `obsidian file file="Note title"`; if it exists, ask whether to append to it or pick a new title. Pass `overwrite` only when Omair asks to replace the note. Add `open` to show it in Obsidian.

## Append to today's daily note

```shell
obsidian daily:append content="* the thing to log"
```

Format the text as a `* ` bullet to match the rest of the note, unless it is already a heading or block. `daily:prepend` puts it at the top; `daily:read` shows the note; `daily:path` gives its path. To add under a particular heading instead of at the end, read the note, then edit the file at the vault path.

## Search

```shell
obsidian search:context query="turbopuffer" limit=10   # matching lines, as path:line: text
obsidian search query="turbopuffer" format=json        # matching file paths only
obsidian read file="Migrate embeddings to Turbopuffer" # full note
```

Search is case-insensitive unless you pass `case`. Narrow with `path="Daily Notes/2026"` or `path=Projects`. Start with `search:context`, since the matched lines usually answer the question; `read` the notes that look relevant before summarising. Cite each note by name so Omair can open it.

Related lookups: `tags counts`, `tag name=<tag> verbose`, `backlinks file=<name>`, `tasks todo daily`.

## Errors

The CLI exits 0 even on failure, so read the output: errors start with `Error:` (for example `Error: File "X" not found.`). If a command prints nothing or an error about the app, Obsidian is probably not running. Tell Omair rather than falling back to editing the vault files directly.
