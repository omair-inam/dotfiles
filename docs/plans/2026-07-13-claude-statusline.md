# Claude Code Status Line (ccstatusline) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `~/.claude/statusline.sh` with a three-line powerline status line (identity, telemetry, full cwd path) rendered by a pinned ccstatusline install, per the spec at `docs/specs/2026-07-13-claude-statusline-design.md`.

**Architecture:** Three small bash scripts in `~/.claude/statusline.d/` feed `CustomCommand` widgets; built-in widgets cover model, thinking effort, and telemetry. ccstatusline reads `~/.config/ccstatusline/settings.json` (version-3 schema) and Claude Code invokes the pinned `ccstatusline` binary. Everything lands in the chezmoi source repo on branch `claude-statusline-spec`.

**Tech Stack:** bash, jq, git, ccstatusline 2.2.23 (npm global), chezmoi.

## Status

| # | Task | Status |
|---|------|--------|
| 1 | `whereami.sh` + test harness | Done |
| 2 | `ports.sh` | Done |
| 3 | `ponytail.sh` | Done |
| 4 | Pinned install + ccstatusline config + render check | Done |
| 5 | Cut over `~/.claude/settings.json`, retire `statusline.sh`, chezmoi capture | Done |
| 6 | Live verification (manual gate) | Not started |

Update this table and the task-level `Status:` line as tasks complete.

## Global Constraints

- ccstatusline pinned at **2.2.23** (`npm install -g ccstatusline@2.2.23`; fall back to `bun install -g ccstatusline@2.2.23` if npm is absent). The clone at `~/libs/ccstatusline` is reference only; never modify it.
- All commits go to `~/.local/share/chezmoi` on the existing branch `claude-statusline-spec`. Commit ONLY the paths named in each task; the repo has unrelated dirty files. `git add <exact paths>`, never `git add -A`.
- Do not push: the repo's remote (`intellij` = omair-inam/dotfiles) rejects the active `omairiai` credential. Omair pushes and opens the PR.
- Widget type strings come from `src/utils/widget-manifest.ts` and are exact: `custom-command`, `model`, `thinking-effort`, `context-percentage`, `reset-timer`, `weekly-usage`, `git-changes`.
- Every script must fail silent: bad/missing input prints nothing and exits 0, so ccstatusline hides the segment.
- Chezmoi flow per task: edit the LIVE file under `$HOME`, test it, then `chezmoi add <live path>` and commit the generated source file. Script sources land as `home/dot_claude/statusline.d/executable_<name>.sh`.

---

### Task 1: `whereami.sh` + test harness

**Status:** Done

**Files:**
- Create: `~/.claude/statusline.d/whereami.sh` (live), then `chezmoi add`
- Create: `~/.claude/statusline.d/test_statusline_d.sh` (live), then `chezmoi add`

**Interfaces:**
- Consumes: Claude Code status JSON on stdin (`.workspace.current_dir // .cwd`).
- Produces: one line of text. Linked worktree: `repo⧸worktree` plus ` branch` only when the branch differs from the worktree dir name. Main checkout: `repo branch`. Non-git: cwd basename. Tasks 2-3 append to the same test file.

- [ ] **Step 1: Write the failing test**

```bash
mkdir -p ~/.claude/statusline.d
cat > ~/.claude/statusline.d/test_statusline_d.sh <<'EOF'
#!/usr/bin/env bash
# Self-check for statusline.d scripts. Run: bash ~/.claude/statusline.d/test_statusline_d.sh
set -u
d=$(cd "$(dirname "$0")" && pwd)
fails=0
check() {
    if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: expected [$2] got [$3]"; fails=$((fails+1)); fi
}
payload() { printf '{"cwd":"%s","workspace":{"current_dir":"%s"}}' "$1" "$1"; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

repo="$tmp/myrepo"
git init -q -b main "$repo"
git -C "$repo" -c user.email=t@t -c user.name=t commit -q --allow-empty -m x
git -C "$repo" worktree add -q -b iai-1-fix "$repo/.worktrees/iai-1-fix"
git -C "$repo" worktree add -q -b feature/other "$repo/.worktrees/wt2"

# --- whereami.sh ---
check "main checkout"          "myrepo main"                 "$(payload "$repo" | bash "$d/whereami.sh")"
check "worktree, branch==name" "myrepo⧸iai-1-fix"            "$(payload "$repo/.worktrees/iai-1-fix" | bash "$d/whereami.sh")"
check "worktree, branch diff"  "myrepo⧸wt2 feature/other"    "$(payload "$repo/.worktrees/wt2" | bash "$d/whereami.sh")"
check "non-git dir"            "$(basename "$tmp")"          "$(payload "$tmp" | bash "$d/whereami.sh")"
check "empty payload"          ""                            "$(printf '{}' | bash "$d/whereami.sh")"

[ "$fails" -eq 0 ] && echo "ALL OK" || { echo "$fails failing"; exit 1; }
EOF
chmod +x ~/.claude/statusline.d/test_statusline_d.sh
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash ~/.claude/statusline.d/test_statusline_d.sh`
Expected: `FAIL` lines (whereami.sh does not exist yet), exit 1.

- [ ] **Step 3: Write the implementation**

```bash
cat > ~/.claude/statusline.d/whereami.sh <<'EOF'
#!/usr/bin/env bash
# Session identity: repo⧸worktree [branch-if-differs] | repo branch | dir basename
input=$(cat)
dir=$(printf '%s' "$input" | jq -r '.workspace.current_dir // .cwd // empty')
[ -n "$dir" ] || exit 0
if ! top=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null); then
    printf '%s' "$(basename "$dir")"
    exit 0
fi
gitdir=$(git -C "$dir" rev-parse --absolute-git-dir)
common=$(git -C "$dir" rev-parse --path-format=absolute --git-common-dir)
branch=$(git -C "$dir" branch --show-current)
name=$(basename "$top")
if [ "$gitdir" != "$common" ]; then
    # linked worktree: common dir is <main-repo>/.git
    repo=$(basename "$(dirname "$common")")
    out="$repo⧸$name"
    [ -n "$branch" ] && [ "$branch" != "$name" ] && out="$out $branch"
else
    [ -n "$branch" ] || branch=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null)
    out="$name $branch"
fi
printf '%s' "$out"
EOF
chmod +x ~/.claude/statusline.d/whereami.sh
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash ~/.claude/statusline.d/test_statusline_d.sh`
Expected: 5 `ok` lines, `ALL OK`, exit 0.

- [ ] **Step 5: Capture in chezmoi and commit**

```bash
chezmoi add ~/.claude/statusline.d/whereami.sh ~/.claude/statusline.d/test_statusline_d.sh
cd ~/.local/share/chezmoi
git add home/dot_claude/statusline.d/executable_whereami.sh home/dot_claude/statusline.d/executable_test_statusline_d.sh
git commit -m "statusline: add whereami.sh segment script with self-check"
```

---

### Task 2: `ports.sh`

**Status:** Done

**Files:**
- Create: `~/.claude/statusline.d/ports.sh` (live), then `chezmoi add`
- Modify: `~/.claude/statusline.d/test_statusline_d.sh` (append checks)

**Interfaces:**
- Consumes: same stdin JSON; reads `.ports` (`BACKEND_PORT=`, `FRONTEND_PORT=`) and `.ports.adk` (`ADK_WEB_PORT=`) at the git toplevel of the payload dir.
- Produces: `be:8012 fe:3002 adk:8204` (present parts only); empty when neither file exists.

- [ ] **Step 1: Append failing tests**

Insert before the final `[ "$fails" -eq 0 ]` line of `test_statusline_d.sh`:

```bash
# --- ports.sh ---
printf 'BACKEND_PORT=8012\nFRONTEND_PORT=3002\n' > "$repo/.ports"
printf 'ADK_WEB_PORT=8204\n' > "$repo/.ports.adk"
check "ports both files"       "be:8012 fe:3002 adk:8204"    "$(payload "$repo" | bash "$d/ports.sh")"
check "ports per-worktree"     ""                            "$(payload "$repo/.worktrees/wt2" | bash "$d/ports.sh")"
rm "$repo/.ports.adk"
check "ports .ports only"      "be:8012 fe:3002"             "$(payload "$repo" | bash "$d/ports.sh")"
rm "$repo/.ports"
check "ports none"             ""                            "$(payload "$repo" | bash "$d/ports.sh")"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash ~/.claude/statusline.d/test_statusline_d.sh`
Expected: whereami checks `ok`, ports checks `FAIL`, exit 1.

- [ ] **Step 3: Write the implementation**

```bash
cat > ~/.claude/statusline.d/ports.sh <<'EOF'
#!/usr/bin/env bash
# Dev-server ports from this worktree's .ports / .ports.adk (see repo Makefiles)
input=$(cat)
dir=$(printf '%s' "$input" | jq -r '.workspace.current_dir // .cwd // empty')
[ -n "$dir" ] || exit 0
top=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) || top=$dir
out=""
if [ -r "$top/.ports" ]; then
    be=$(sed -n 's/^BACKEND_PORT=//p' "$top/.ports" | tr -d '"')
    fe=$(sed -n 's/^FRONTEND_PORT=//p' "$top/.ports" | tr -d '"')
    [ -n "$be" ] && out="be:$be"
    [ -n "$fe" ] && out="$out${out:+ }fe:$fe"
fi
if [ -r "$top/.ports.adk" ]; then
    adk=$(sed -n 's/^ADK_WEB_PORT=//p' "$top/.ports.adk" | tr -d '"')
    [ -n "$adk" ] && out="$out${out:+ }adk:$adk"
fi
printf '%s' "$out"
EOF
chmod +x ~/.claude/statusline.d/ports.sh
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash ~/.claude/statusline.d/test_statusline_d.sh`
Expected: 9 `ok` lines, `ALL OK`, exit 0.

- [ ] **Step 5: Capture and commit**

```bash
chezmoi add ~/.claude/statusline.d/ports.sh ~/.claude/statusline.d/test_statusline_d.sh
cd ~/.local/share/chezmoi
git add home/dot_claude/statusline.d/executable_ports.sh home/dot_claude/statusline.d/executable_test_statusline_d.sh
git commit -m "statusline: add ports.sh segment script"
```

---

### Task 3: `ponytail.sh`

**Status:** Done

**Files:**
- Create: `~/.claude/statusline.d/ponytail.sh` (live), then `chezmoi add`
- Modify: `~/.claude/statusline.d/test_statusline_d.sh` (append smoke check)

**Interfaces:**
- Consumes: nothing (ignores stdin).
- Produces: the ponytail badge text (ANSI-colored; ccstatusline strips colors via `preserveColors=false`), or nothing when the plugin is absent.

- [ ] **Step 1: Append failing smoke check**

Insert before the final `[ "$fails" -eq 0 ]` line of `test_statusline_d.sh`:

```bash
# --- ponytail.sh --- (smoke: must exist and exit 0; output depends on plugin presence)
bash "$d/ponytail.sh" </dev/null >/dev/null 2>&1 || { echo "FAIL ponytail runs"; fails=$((fails+1)); }
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash ~/.claude/statusline.d/test_statusline_d.sh`
Expected: `FAIL ponytail runs`, exit 1.

- [ ] **Step 3: Write the implementation** (logic lifted from the retiring `statusline.sh`)

```bash
cat > ~/.claude/statusline.d/ponytail.sh <<'EOF'
#!/usr/bin/env bash
# glob the version dir so a ponytail upgrade doesn't silently drop the badge
for pt in "$HOME"/.claude/plugins/cache/ponytail/ponytail/*/hooks/ponytail-statusline.sh; do
    [ -f "$pt" ] || continue
    badge=$(bash "$pt")
    [ -n "$badge" ] && printf '%s' "$badge"
done
exit 0
EOF
chmod +x ~/.claude/statusline.d/ponytail.sh
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash ~/.claude/statusline.d/test_statusline_d.sh`
Expected: `ALL OK`, exit 0. Also eyeball: `bash ~/.claude/statusline.d/ponytail.sh` prints the `[PONYTAIL]` badge on this machine.

- [ ] **Step 5: Capture and commit**

```bash
chezmoi add ~/.claude/statusline.d/ponytail.sh ~/.claude/statusline.d/test_statusline_d.sh
cd ~/.local/share/chezmoi
git add home/dot_claude/statusline.d/executable_ponytail.sh home/dot_claude/statusline.d/executable_test_statusline_d.sh
git commit -m "statusline: add ponytail.sh segment script"
```

---

### Task 4: Pinned install + ccstatusline config + render check

**Status:** Done

**Files:**
- Modify: `~/.config/ccstatusline/settings.json` (replace the stale single-line config), then `chezmoi add`

**Interfaces:**
- Consumes: the three scripts from Tasks 1-3 at `~/.claude/statusline.d/`.
- Produces: a `ccstatusline` binary on PATH and a config Task 5's cutover points at.

- [ ] **Step 1: Install the pinned binary**

Run: `npm install -g ccstatusline@2.2.23` (if npm is missing: `bun install -g ccstatusline@2.2.23`)
Verify: `command -v ccstatusline` prints a path; `ccstatusline --version 2>/dev/null || true` runs.

- [ ] **Step 2: Write the config**

```bash
mkdir -p ~/.config/ccstatusline
cat > ~/.config/ccstatusline/settings.json <<'EOF'
{
  "version": 3,
  "lines": [
    [
      { "id": "w1", "type": "custom-command", "commandPath": "bash ~/.claude/statusline.d/ponytail.sh", "preserveColors": false, "timeout": 500, "maxWidth": 14 },
      { "id": "w2", "type": "custom-command", "commandPath": "bash ~/.claude/statusline.d/whereami.sh", "timeout": 1000 },
      { "id": "w3", "type": "model" },
      { "id": "w4", "type": "thinking-effort" },
      { "id": "w5", "type": "custom-command", "commandPath": "bash ~/.claude/statusline.d/ports.sh", "timeout": 1000 }
    ],
    [
      { "id": "w6", "type": "context-percentage" },
      { "id": "w7", "type": "reset-timer" },
      { "id": "w8", "type": "weekly-usage" },
      { "id": "w9", "type": "git-changes" }
    ],
    [
      { "id": "w10", "type": "current-working-dir", "rawValue": true, "metadata": { "abbreviateHome": "true" } }
    ]
  ],
  "flexMode": "full-minus-40",
  "compactThreshold": 60,
  "colorLevel": 2,
  "inheritSeparatorColors": false,
  "globalBold": false,
  "gitCacheTtlSeconds": 5,
  "minimalistMode": false,
  "powerline": {
    "enabled": true,
    "theme": "nord",
    "separators": [""],
    "separatorInvertBackground": [false],
    "startCaps": [],
    "endCaps": [""],
    "autoAlign": false,
    "continueThemeAcrossLines": true
  }
}
EOF
```

Theme note: `nord` to start; other valid values are `nord-aurora`, `monokai`, `solarized`, `minimal`, `dracula`, `catppuccin`, `gruvbox`, `onedark`, `tokyonight`, or `custom` (per-widget `backgroundColor`). Omair can retheme later in the TUI (`ccstatusline` with no stdin).

- [ ] **Step 3: Render check against the example payload**

Run: `cat ~/libs/ccstatusline/scripts/payload.example.json | ccstatusline`
Expected: two lines with powerline segments; line 1 shows a model name and a thinking-effort value, no `[Cmd not found]` / `[Timeout]` markers.

- [ ] **Step 4: Render check against a real-shaped payload**

```bash
printf '{"cwd":"%s","workspace":{"current_dir":"%s"},"model":{"id":"claude-fable-5","display_name":"Fable 5"},"thinking":{"enabled":true},"effort":{"level":"high"}}' \
  "$HOME/projects/iv-living-archive" "$HOME/projects/iv-living-archive" | ccstatusline
```

Expected: line 1 = ponytail badge, `iv-living-archive main` (or current branch), `Fable 5`, `high`, plus ports if the repo has a `.ports` file. Repeat with `"effort"` removed; the thinking-effort segment falls back (transcript → settings → `default`), and must not error.

- [ ] **Step 5: Capture and commit**

```bash
chezmoi add ~/.config/ccstatusline/settings.json
cd ~/.local/share/chezmoi
git add home/dot_config/ccstatusline/settings.json
git commit -m "statusline: two-line powerline ccstatusline config"
```

---

### Task 5: Cut over `~/.claude/settings.json`, retire `statusline.sh`

**Status:** Done

**Files:**
- Modify: `~/.claude/settings.json` — `statusLine` object only
- Delete: `~/.claude/statusline.sh` (live + chezmoi source)

**Interfaces:**
- Consumes: the binary + config from Task 4.
- Produces: Claude Code renders via ccstatusline on next statusline refresh.

- [ ] **Step 1: Point Claude Code at ccstatusline**

Edit `~/.claude/settings.json`, replacing the existing `statusLine` value:

```json
"statusLine": {
  "type": "command",
  "command": "ccstatusline",
  "refreshInterval": 10
}
```

- [ ] **Step 2: Retire the old script**

```bash
chezmoi forget --force ~/.claude/statusline.sh
rm ~/.claude/statusline.sh
```

- [ ] **Step 3: Capture and commit**

`home/dot_claude/settings.json` had pre-existing uncommitted drift; it rides along in this commit (the file must be committed for the `statusLine` change and chezmoi captures whole files).

```bash
chezmoi add ~/.claude/settings.json
cd ~/.local/share/chezmoi
git add home/dot_claude/settings.json
git rm -q --ignore-unmatch home/dot_claude/executable_statusline.sh
git commit -m "statusline: cut over to ccstatusline, retire statusline.sh"
```

- [ ] **Step 4: Sanity render**

Run: `printf '{"cwd":"%s","model":{"display_name":"Fable 5"},"effort":{"level":"high"},"thinking":{"enabled":true}}' "$PWD" | ccstatusline`
Expected: both lines render. This proves the exact command Claude Code will now invoke works from a bare shell.

---

### Task 6: Live verification (manual gate — Omair)

**Status:** Not started

**Files:** none.

- [ ] **Step 1:** Open a new Claude Code session in `~/projects/iv-living-archive`. Confirm line 1 shows badge / `iv-living-archive main` / model / effort, line 2 shows context % / block reset / weekly usage / git changes.
- [ ] **Step 2:** Run `/effort low`; confirm the thinking-effort segment updates within one refresh (≤10s).
- [ ] **Step 3:** Open a session in a linked worktree with `make dev-bg` running; confirm `repo⧸worktree` and the `be:/fe:` ports appear, and `adk:` after `make adk-web`.
- [ ] **Step 4:** Push branch `claude-statusline-spec` and open the dotfiles PR (personal-account credentials; the agent cannot push).
