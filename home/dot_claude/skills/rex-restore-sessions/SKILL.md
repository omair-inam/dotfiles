---
name: rex-restore-sessions
description: Recreate Rex sessions, windows, and split layouts from a snapshot made by rex-save-sessions, resuming each Claude Code conversation in its original block. Use after a Rex server upgrade, restart, or reboot, or when Omair says "restore my rex sessions", "bring back my rex sessions", or "restart all my rex sessions".
---

# Restore Rex sessions

For Rex CLI usage, read `~/.claude/skills/rex/SKILL.md`.

The script is shared with `rex-save-sessions`. It lives at `~/.claude/skills/rex-save-sessions/scripts/rexsnap.py`.

1. Dry run:

   ```bash
   ~/.claude/skills/rex-save-sessions/scripts/rexsnap.py restore
   ```

   This reads `~/.local/state/rex-snapshots/latest.json`. To use an older snapshot, pass its path. The output prints every `rex` command it would run.

   A session whose label is already live is adopted, not recreated. Rex (through rexurrect) usually reopens the sessions and windows after a restart but leaves each block at a shell prompt, often with the last command, such as `claude`, typed but not run. For each saved Claude conversation not already running, the script matches the live window by position and the block by layout order. If that block's foreground is a shell, it sends Ctrl-C to discard the typed text, then types `claude --resume <id>` and Enter. A block running anything else is skipped and reported. Saved windows missing from a live session are created. Conversations already running are skipped, so reruns never duplicate.

   Labels are matched exactly. A session renamed since the snapshot counts as missing and gets recreated; check the dry run for this and pass `--only` to leave it out.

2. Confirm that `claude` resolves in a login shell with `zsh -lc 'command -v claude'`. An alias defined only in `.zshrc` does not count.

3. Apply:

   ```bash
   ~/.claude/skills/rex-save-sessions/scripts/rexsnap.py restore --apply
   ```

   Add `--only LABEL` (repeatable) to restore a subset. The script waits 8 seconds, resends once to any adopted block whose conversation has not started and whose shell is still idle, then runs `verify`. `verify` checks that every session exists, that window counts match, and that every saved Claude session ID is held by a live process. It exits non-zero on any mismatch.

4. Never type a resume command into a reopened block yourself with `rex send`. A pre-typed command at the prompt turns it into `claudeclaude --resume ...`. Use the script, which clears the line first.

5. If a session was half-created, for example a window failed, kill that Rex session and rerun step 3 with `--only <label>`.

6. Report each restored session to Omair, with its window count and Claude session IDs. Labels and Claude conversations carry over. Rex IDs do not.

To re-check later without restoring anything, run `rexsnap.py verify`.
