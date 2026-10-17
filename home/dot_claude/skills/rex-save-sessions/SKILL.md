---
name: rex-save-sessions
description: Snapshot every running Rex session, window, split layout, and the Claude Code conversation in each block to a JSON file so they can be restored later. Use before upgrading, restarting, or stopping the Rex server, before a reboot, or when Omair says "save my rex sessions", "persist rex", or "I'm about to upgrade rex".
---

# Save Rex sessions

1. Run:

   ```bash
   ~/.claude/skills/rex-save-sessions/scripts/rexsnap.py save
   ```

   It writes `~/.local/state/rex-snapshots/<timestamp>.json`, copies it to `latest.json`, and prints each session with its blocks. A block running Claude Code shows `claude <session-id>`.

2. Check the printout against `rex ls`. Every session must appear. A block that should be running Claude but prints a shell name means its Claude process has exited, so its conversation will not come back. Tell Omair which one.

3. Tell Omair the snapshot path, then tell him it is safe to upgrade or restart the server. To restore later, use the `rex-restore-sessions` skill.

What the snapshot holds:

- Each session's label, window order, and active window.
- Each window's label and split tree: direction, ratio, and the block on each side.
- Each block's label, working directory, and foreground program.
- For Claude blocks: the session ID, name, and `CLAUDE_CONFIG_DIR`. These come from `<config dir>/sessions/<pid>.json` for the block's foreground process.

What the snapshot does not hold:

- Rex IDs, which change on restore.
- Terminal scrollback.
- Floating layers, which are skipped with a warning.
- Non-Claude programs. Restore opens a login shell in the same directory instead of rerunning them.
