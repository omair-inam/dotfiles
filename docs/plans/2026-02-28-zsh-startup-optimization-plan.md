# ZSH Startup Optimization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reduce ZSH startup time to under 500ms by removing redundancies, dead weight, and deferring expensive initialization — without changing the OMZ framework or Powerlevel10k prompt.

**Architecture:** Edit the chezmoi-managed `dot_zshrc.tmpl` and `dot_p10k.zsh` to remove duplicate work, drop unused tools, cache completions, and add evalcache for expensive `eval "$(tool init)"` calls. All changes are to the chezmoi source directory; the user runs `chezmoi apply` (alias `cma`) to deploy.

**Tech Stack:** ZSH, Oh My Zsh, chezmoi templates, evalcache plugin

**Design doc:** `docs/plans/2026-02-28-zsh-startup-optimization-design.md`

---

### Task 0: Measure baseline startup time

**Files:** None (read-only measurement)

**Step 1: Record baseline timing**

Run from an existing shell (not inside the shell being measured):

```bash
# Run 5 times and note the average
for i in {1..5}; do time zsh -i -c exit; done
```

Record the `real` time from each run. This is the "before" number.

**Step 2: Commit nothing** — this is observation only.

---

### Task 1: Remove duplicate `compinit` call

**Files:**
- Modify: `home/dot_zshrc.tmpl:183`

**Step 1: Delete the duplicate compinit line**

Remove this line (currently line 183):
```
autoload -U compinit && compinit
```

OMZ calls `compinit` internally when it sources `oh-my-zsh.sh` on line 187. The duplicate scans every file in `$fpath` a second time for no benefit.

**Step 2: Verify with chezmoi diff**

Run: `chezmoi diff ~/.zshrc`

Expected: The diff shows only the removal of the `compinit` line.

**Step 3: Commit**

```bash
git add home/dot_zshrc.tmpl
git commit -m "perf(zsh): remove duplicate compinit call

OMZ already calls compinit internally. The duplicate at line 183
ran before source oh-my-zsh.sh, scanning \$fpath twice (~50-100ms
wasted)."
```

---

### Task 2: Remove duplicate aliases and functions from `.zshrc`

**Files:**
- Modify: `home/dot_zshrc.tmpl:8-23`

The `ifactive` alias (line 8-9), `ssh-hosts` alias (line 10), and the `.` function (lines 16-23) are already defined in `home/dot_zsh_aliases.tmpl` (lines 1-14). Since `.zsh_aliases` is sourced on line 11, the `.zshrc` copies are redundant.

**Step 1: Remove the duplicate alias lines**

Remove lines 8-10 (the two aliases before `source ~/.zsh_aliases`):
```
### Alias to list active network interfaces
alias ifactive="ifconfig | pcregrep -M -o '^[^\t:]+:([^\n]|\n\t)*status: active'"
alias ssh-hosts="grep -hE 'Host (.+)' ~/.ssh/config | sed 's/Host //'"
```

The file should go directly from the p10k instant prompt block to `source ~/.zsh_aliases`.

**Step 2: Remove the duplicate `.` function**

Remove lines 16-23 (the `.` function):
```
### Typing '.' will source ~/.zshrc
function . {
    if [[ $# -eq 0 ]]; then
        builtin . ~/.zshrc
    else
        builtin . "$@"
    fi
}
```

This same function exists in `home/dot_zsh_aliases.tmpl` at lines 7-14.

**Step 3: Verify with chezmoi diff**

Run: `chezmoi diff ~/.zshrc`

Expected: Only the duplicate lines are removed. `source ~/.zsh_aliases` remains.

**Step 4: Commit**

```bash
git add home/dot_zshrc.tmpl
git commit -m "perf(zsh): remove duplicate aliases and dot function from .zshrc

These are already defined in .zsh_aliases, which is sourced on the
next line."
```

---

### Task 3: Remove autojump (redundant with zoxide)

**Files:**
- Modify: `home/dot_zshrc.tmpl:221`

**Step 1: Remove the autojump source line**

Remove these two lines:
```
# Enable autojump
[ -f /opt/homebrew/etc/profile.d/autojump.sh ] && . /opt/homebrew/etc/profile.d/autojump.sh
```

The `zoxide` OMZ plugin (in the plugins array at line 167) provides the same `z` command for directory jumping, is written in Rust (faster), and is already active.

**Step 2: Verify with chezmoi diff**

Run: `chezmoi diff ~/.zshrc`

Expected: Only the autojump lines are removed.

**Step 3: Commit**

```bash
git add home/dot_zshrc.tmpl
git commit -m "perf(zsh): remove autojump, redundant with zoxide

Zoxide (already loaded as OMZ plugin) provides the same z command
for directory jumping. Autojump is Python-based and slower."
```

**Step 4: Note for user** — After applying, optionally run `brew uninstall autojump` to clean up the Homebrew package.

---

### Task 4: Remove rbenv init and p10k rbenv segment

**Files:**
- Modify: `home/dot_zshrc.tmpl:235-238`
- Modify: `home/dot_p10k.zsh:65`

**Step 1: Remove the rbenv init block from .zshrc**

Remove these lines:
```
# Initialize rbenv if it exists
if command -v rbenv >/dev/null 2>&1; then
  eval "$(rbenv init - zsh)"
fi
```

Mise now manages Ruby versions, making rbenv unnecessary.

**Step 2: Comment out rbenv from p10k right-prompt elements**

In `home/dot_p10k.zsh`, change line 65 from:
```
    rbenv                   # ruby version from rbenv (https://github.com/rbenv/rbenv)
```
to:
```
    # rbenv                   # ruby version from rbenv (https://github.com/rbenv/rbenv)
```

The `mise` segment on line 53 already shows runtime versions managed by mise.

**Step 3: Verify with chezmoi diff**

Run: `chezmoi diff ~/.zshrc && chezmoi diff ~/.p10k.zsh`

Expected: The rbenv block is removed from .zshrc; the rbenv segment is commented out in .p10k.zsh.

**Step 4: Commit**

```bash
git add home/dot_zshrc.tmpl home/dot_p10k.zsh
git commit -m "perf(zsh): remove rbenv init and p10k segment

Mise manages Ruby versions now. The rbenv eval subprocess added
~100-200ms to every shell start."
```

---

### Task 5: Cache JWT completions to file

**Files:**
- Modify: `home/dot_zshrc.tmpl:223-225` (remove subprocess call)
- Modify: `home/dot_zshrc.tmpl` (add fpath entry before OMZ source)
- Create: `home/.chezmoiscripts/run_onchange_before_14_cache-jwt-completions.sh.tmpl`

**Step 1: Create the completion cache script**

Create `home/.chezmoiscripts/run_onchange_before_14_cache-jwt-completions.sh.tmpl`:

```bash
#!/bin/bash
# Cache JWT CLI completions for ZSH so we don't spawn a subprocess on every shell start.
# Regenerates when jwt binary changes (chezmoi detects via hash comment below).
# hash: {{ if lookPath "jwt" }}{{ output "jwt" "--version" | trim }}{{ else }}not-installed{{ end }}

set -euo pipefail

COMP_DIR="$HOME/.zsh_completions"
mkdir -p "$COMP_DIR"

if command -v jwt >/dev/null 2>&1; then
  echo "Caching JWT ZSH completions to $COMP_DIR/_jwt..."
  jwt completion zsh > "$COMP_DIR/_jwt"
else
  echo "jwt not found, skipping completion cache"
fi
```

This is a `run_onchange` script — chezmoi re-runs it only when the hash comment (jwt version) changes.

**Step 2: Add fpath entry before OMZ source**

In `home/dot_zshrc.tmpl`, add this line before the `export ZSH=` line (around line 35):

```bash
# Cached CLI completions (jwt, etc.)
fpath=(~/.zsh_completions $fpath)
```

**Step 3: Remove the subprocess call**

Remove these lines from `home/dot_zshrc.tmpl`:
```
if hash jwt > /dev/null; then
  source <(jwt completion zsh)
fi
```

**Step 4: Verify with chezmoi diff**

Run: `chezmoi diff ~/.zshrc`

Expected: The jwt subprocess block is gone; the fpath line is added.

**Step 5: Commit**

```bash
git add home/dot_zshrc.tmpl home/.chezmoiscripts/run_onchange_before_14_cache-jwt-completions.sh.tmpl
git commit -m "perf(zsh): cache JWT completions to file instead of subprocess

Replace source <(jwt completion zsh) with a cached file at
~/.zsh_completions/_jwt. A chezmoi run_onchange script regenerates
it when the jwt binary version changes."
```

---

### Task 6: Remove unused plugins (sfdx, aws)

**Files:**
- Modify: `home/dot_zshrc.tmpl` (plugins array)

**Step 1: Remove sfdx and comment out aws**

In the plugins array, remove the `sfdx` line entirely:
```
  sfdx
```

Comment out the `aws` line:
```
  # aws  # commented out — re-enable when using AWS completions
```

**Step 2: Verify with chezmoi diff**

Run: `chezmoi diff ~/.zshrc`

Expected: `sfdx` removed, `aws` commented out.

**Step 3: Commit**

```bash
git add home/dot_zshrc.tmpl
git commit -m "perf(zsh): remove sfdx plugin, comment out aws

sfdx (Salesforce CLI) is unused. aws completions are not needed
currently — easy to re-enable later."
```

---

### Task 7: Install evalcache and convert mise + zoxide init

**Files:**
- Modify: `home/dot_zshrc.tmpl` (plugins array + add evalcache init lines)

**Important:** The direnv plugin MUST remain as an OMZ plugin. Unlike mise and zoxide which run a one-time init, direnv installs `precmd`/`chpwd` hooks that re-evaluate on every prompt and directory change. Caching that would break `.envrc` loading.

**Step 1: Install evalcache as OMZ custom plugin**

```bash
git clone https://github.com/mroth/evalcache.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/evalcache
```

**Step 2: Update the plugins array**

In `home/dot_zshrc.tmpl`, make these changes to the plugins array:

Add `evalcache` to the top of the plugins list (it must load before we call `_evalcache`):
```
plugins=(
  # Eval caching (must load first)
  evalcache

  # Package managers & tooling
  # mise  # replaced by _evalcache below
  brew
  chezmoi
  uv
```

Remove `mise` and `zoxide` from the plugins array (comment them out with the reason).

Keep `direnv` in the plugins array — it uses hooks, not a one-time eval.

The navigation section becomes:
```
  # Navigation & environment
  # zoxide  # replaced by _evalcache below
  # auto-load .envrc (direnv) and .env (dotenv) per directory
  direnv
  dotenv
```

**Step 3: Add evalcache init lines after OMZ source**

After `source $ZSH/oh-my-zsh.sh` (and before the p10k source line), add:

```bash
# Cached eval for expensive tool init (see evalcache plugin)
# These replace the OMZ mise and zoxide plugins with cached versions.
# Run _evalcache_clear after upgrading these tools.
_evalcache mise activate zsh
_evalcache zoxide init zsh
```

**Step 4: Verify with chezmoi diff**

Run: `chezmoi diff ~/.zshrc`

Expected: evalcache added to plugins, mise/zoxide removed from plugins, `_evalcache` lines added after OMZ source.

**Step 5: Commit**

```bash
git add home/dot_zshrc.tmpl
git commit -m "perf(zsh): add evalcache for mise and zoxide init

Replace OMZ mise and zoxide plugins with evalcache'd manual init.
Caches eval output to ~/.zsh-evalcache/ — subsequent shells source
the file (~1ms) instead of forking subprocesses (~30-50ms each).

direnv stays as OMZ plugin because it installs precmd/chpwd hooks
that must re-evaluate on every prompt, not just once at init."
```

---

### Task 8: Measure results and verify functionality

**Files:** None (read-only verification)

**Step 1: Apply chezmoi changes**

```bash
chezmoi apply -v
```

**Step 2: Open a new shell and measure startup time**

```bash
for i in {1..5}; do time zsh -i -c exit; done
```

Compare against baseline from Task 0. Target: under 500ms.

**Step 3: Verify key functionality still works**

Test each category:
- `gst` — git status alias works (git plugin)
- `z <partial-dir>` — zoxide directory jump works
- Type a long command, see autosuggestion appear (zsh-autosuggestions)
- Press up-arrow with partial text — history substring search works
- `cd` into a directory with `.envrc` — direnv loads it
- `mise current` — mise shows active runtimes
- `Esc Esc` on a command — sudo prepends (sudo plugin)
- `jwt --help` — tab completion works (cached completions)

**Step 4: If startup exceeds 500ms, profile**

```bash
# Add to top of ~/.zshrc temporarily:
zmodload zsh/zprof
# Add to bottom:
zprof
```

Open a new shell, read the profiling output to identify remaining bottlenecks.

**Step 5: Final commit (if any adjustments needed)**

If verification reveals issues, fix and commit. Otherwise, no commit needed for this task.

---

## Task Dependency Order

```
Task 0 (baseline) → Tasks 1-6 (independent, any order) → Task 7 (evalcache) → Task 8 (verify)
```

Tasks 1 through 6 are independent of each other and can be done in any order. Task 7 depends on having a clean state. Task 8 must be last.
