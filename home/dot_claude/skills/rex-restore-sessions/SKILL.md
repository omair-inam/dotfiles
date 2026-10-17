---
name: rex-restore-sessions
description: Recreate Rex sessions, windows, and split layouts from a snapshot made by rex-save-sessions, resuming each Claude Code conversation in its original block. Use after a Rex server upgrade, restart, or reboot, or when Omair says "restore my rex sessions", "bring back my rex sessions", or "restart all my rex sessions".
---

# Restore Rex sessions

The script is shared with `rex-save-sessions`. It lives at `~/.claude/skills/rex-save-sessions/scripts/rexsnap.py`.

1. Dry run:

   ```bash
   ~/.claude/skills/rex-save-sessions/scripts/rexsnap.py restore
   ```

   This reads `~/.local/state/rex-snapshots/latest.json`. To use an older snapshot, pass its path. The output prints every `rex` command it would run. It skips any session whose label is already running, so reruns never duplicate.

2. Confirm that `claude` resolves in a login shell with `zsh -lc 'command -v claude'`. Rex starts block commands through the login environment, so an alias defined only in `.zshrc` will not work.

3. Apply:

   ```bash
   ~/.claude/skills/rex-save-sessions/scripts/rexsnap.py restore --apply
   ```

   Add `--only LABEL` (repeatable) to restore a subset. The script waits 8 seconds, then runs `verify`. `verify` checks that every session exists, that window counts match, and that every saved Claude session ID is held by a live process. It exits non-zero on any mismatch.

4. If a session was half-created, for example a window failed, kill it with `rex kill <label>` and rerun step 3 with `--only <label>`.

5. Report each restored session to Omair, with its window count and Claude session IDs. Rex session, window, and block IDs are new. Labels and Claude conversations carry over.

To re-check later without restoring anything, run `rexsnap.py verify`.
