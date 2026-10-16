---
name: things
description: Work with Omair's Things 3 task list through the `things` CLI. Use whenever Omair wants to add a todo, see what's on today or in the inbox, find a task, reschedule it, tag it, or mark it done, even when he says "my tasks", "my todo list", "remind me to", or "add this to my list" without naming Things.
---

# Things

`things` (`/usr/local/bin/things`, the `things3-cli` project) reads the local Things 3 database and writes through the Things URL scheme. The full flag reference ships with the CLI at `/Users/omair/libs/things3-cli/skills/things/SKILL.md`; read it for anything not covered here, or run `things <command> --help`.

## Read

```shell
things today
things inbox
things upcoming
things projects
things areas
things tasks --search "dentist" --json
things show "Project name"
things tasks --project "Project name" --json
things show --id <uuid> --recursive --json
```

Use `--json` when you need a task's `uuid` for a later update.

`show --id ... --json` omits notes. Read a task's notes from `tasks`, whose JSON carries `uuid`, `title`, `notes`, `start`, `status`, `created`, and `modified`:

```shell
things tasks --search "IAI-1838" --json | jq -r '.[] | .uuid, .title, .notes'
```

## Add

```shell
things add "Call the dentist" --when=today
things add "Review PR" --notes "https://github.com/..." --list "Project or Area" --tags "work"
things add "Pack" --checklist-item="Passport" --checklist-item="Charger"
```

`--when` takes `today`, `tomorrow`, `evening`, `someday`, or a date (`2026-10-20`). With no `--when` or `--list` the task lands in the Inbox.

`--notes` keeps literal newlines inside the quoted value, so Markdown links and `- ` bullets render in Things:

```shell
things add "IAI-1838 Refresh stale chat cards" --when=someday --notes "[IAI-1838](https://linear.app/...)
- First detail.
- Second detail."
```

Search for the title before adding, and search again after. `add` goes through the URL scheme and prints nothing, so it succeeds even when reads fail, and only a read shows whether the task exists once.

## Update

Find the task's `uuid` first, then update by `--id`. Updating by title risks changing the wrong task.

```shell
things update --id <uuid> --completed
things update --id <uuid> --when=tomorrow
things update --id <uuid> --tags "work,urgent"
things update --id <uuid> --notes ""     # an explicit empty value clears the field
```

For bulk changes, run with `--dry-run` first, show Omair the preview, then rerun with `--yes`. `things undo` reverts the last bulk change.

Confirm with Omair before any `delete`.

## Setup problems

- `Error: Things database not found` or a permission error: the program that spawns Claude's shell needs Full Disk Access (System Settings, Privacy & Security), and must restart after the grant. Reads fail until then. That program is not always the terminal app Omair sees. Find it from the process ancestry:

  ```shell
  p=$$; while p=$(ps -o ppid= -p $p | tr -d ' '); [ -n "$p" ] && [ "$p" != 1 ]; do ps -o pid=,comm= -p $p; done
  ```

  In Rex the shells run under `/Applications/Rex Beta.app/Contents/Helpers/Rex Server.app`, not `Rex Beta.app`, so the helper needs the grant and the Rex server needs a restart. Claude Code's sandbox is not the cause; don't retry with it disabled. Tell Omair what to grant; don't hunt for the database path yourself.
- `Things auth token: not set`: `update` needs the token from Things, Settings, General, Things URLs. Omair sets `THINGS_AUTH_TOKEN` or runs `things auth`. Never ask him to paste the token into the chat.
