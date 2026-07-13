# Claude Code status line via ccstatusline

Date: 2026-07-13. No Linear ticket (personal tooling).

## Goal

Replace the hand-rolled `~/.claude/statusline.sh` with a two-line powerline status line rendered by ccstatusline, showing session identity on line 1 and usage telemetry on line 2. Keep the ponytail badge and add the per-worktree dev-server ports.

## Decisions

| Question | Decision |
|---|---|
| Layout | Two lines: identity, then telemetry |
| Usage widgets | Context %, block reset timer, weekly usage. No per-session cost, no Opus/Sonnet split |
| Dir/branch | Repo + worktree name; branch only when it differs from the worktree name |
| Ports | Show `.ports` and `.ports.adk` values when present |
| SessionName | Skip. Claude Code already displays it |
| Engine | ccstatusline, pinned global install (`ccstatusline` on PATH). The clone at `~/libs/ccstatusline` stays for reference only |
| Look | Powerline mode (Nerd Font arrows, per-segment backgrounds) |

## Architecture

Claude Code pipes a status JSON payload to `statusLine.command` on each refresh. ccstatusline reads that payload, renders widgets per `~/.config/ccstatusline/settings.json` (version-3 schema), and prints ANSI lines. Custom segments run as `CustomCommand` widgets: ccstatusline re-pipes the same payload to each script's stdin with a 1s default timeout.

Components:

1. **Pinned global install.** Run the TUI (`bunx ccstatusline@latest` or from the clone), choose "Pinned global install". The TUI installs the binary globally and writes `"statusLine": {"command": "ccstatusline"}` plus `statusLine.refreshInterval` to `~/.claude/settings.json`. No `npx` resolution on the render path.
2. **Config file** `~/.config/ccstatusline/settings.json`, hand-authored in the same schema the TUI writes, so the TUI can still edit it later. Replaces the stale single-line config currently in that file.
3. **Three helper scripts** in `~/.claude/statusline.d/` (new dir):
   - `ponytail.sh`: runs the existing ponytail hook glob (copied from the current `statusline.sh`), prints the badge text. ccstatusline strips its ANSI colors (`preserveColors=false`) so the powerline segment colors it instead.
   - `whereami.sh`: reads `.workspace.current_dir // .cwd` from stdin JSON. In a linked worktree prints `repo⧸worktree`, appending the branch only when the branch name differs from the worktree dir name. In a main checkout prints `repo branch`. Outside git prints the basename of the cwd. `git -C <dir> rev-parse --show-toplevel --git-common-dir` distinguishes linked worktrees.
   - `ports.sh`: finds the git toplevel from the same JSON, sources `.ports` and `.ports.adk` when readable, prints for example `be:8012 fe:3002 adk:8204`. Prints nothing when neither file exists, which hides the segment.
4. **Retire** `~/.claude/statusline.sh`. Its model/think rendering moves to built-in widgets; ponytail moves to `ponytail.sh`.

## Line composition

Line 1 (identity):

| # | Widget | Content |
|---|---|---|
| 1 | CustomCommand `ponytail.sh` | `[PONYTAIL]` badge, hidden when hook absent |
| 2 | CustomCommand `whereami.sh` | `iv-living-archive⧸iai-632-adk-web` |
| 3 | Model | `Fable 5` |
| 4 | ThinkingEffort | `high` (live `effort.level`, mid-session `/effort` changes included) |
| 5 | CustomCommand `ports.sh` | `be:8012 fe:3002 adk:8204`, hidden without `.ports*` |

Line 2 (telemetry):

| # | Widget | Content |
|---|---|---|
| 1 | ContextPercentage | Window fill. Manual-compact tripwire since auto-compact is off |
| 2 | BlockResetTimer | Time until the 5-hour block resets |
| 3 | WeeklyUsage | Weekly plan usage % |
| 4 | GitChanges | `+N -M` insertions/deletions, 5s git cache |

Powerline enabled with the stock `` separator, `flexMode` left at `full-minus-40` so line 1 truncates from the right in narrow splits.

## Failure modes

- Custom script error or >1s timeout: ccstatusline prints a short marker (`[Timeout]`, `[Cmd not found]`) in that segment; the rest of the line renders.
- Empty script output hides the segment (ports outside a dev worktree, ponytail without the plugin).
- `effort` absent from the payload (model without the effort parameter): ThinkingEffort falls back to transcript, then `~/.claude/settings.json`, then shows `default`.
- Terminal without a Nerd Font renders the powerline arrows as boxes. Accepted; Omair runs Nerd Fonts in his terminals.

## Config management

`chezmoi add` the three scripts and `~/.config/ccstatusline/settings.json`. `~/.claude/settings.json` is already chezmoi-managed (`home/dot_claude/settings.json`); re-add it after the `statusLine` change so the source captures it. Remove the retired `statusline.sh` from chezmoi (`chezmoi forget` + delete).

## Testing

- Pipe `~/libs/ccstatusline/scripts/payload.example.json` through the installed `ccstatusline` binary; confirm both lines render with powerline segments.
- Pipe three edited payloads through it: thinking on with effort, thinking off, no `effort` key.
- Run `whereami.sh` against a payload pointing at a linked worktree, the main checkout, and a non-git dir.
- Run `ports.sh` in a worktree with `.ports` + `.ports.adk` fixtures and in one without.
- Live check: open a new Claude Code session, confirm both lines, then `/effort low` and confirm the ThinkingEffort segment updates.

## Out of scope

- Modifying ccstatusline itself (the clone is reference only).
- Per-session cost, Opus/Sonnet weekly splits, SessionName, voice/remote-control indicators.
- Any change to the iv-living-archive repo.
