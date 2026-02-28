# ZSH Startup Optimization Design

**Date:** 2026-02-28
**Goal:** Reduce shell startup time to under 500ms while keeping Oh My Zsh, Powerlevel10k, and all essential plugin functionality.

**Approach:** Optimize within the current OMZ + p10k stack. No framework or prompt replacement. Fix redundancies, remove dead weight, defer expensive initialization.

---

## Current State

- **Framework:** Oh My Zsh with ~30 plugins (plus k8s/docker on work devices)
- **Prompt:** Powerlevel10k (lean, 2-line, nerdfont-complete, instant prompt enabled)
- **Known bottlenecks:** duplicate `compinit`, synchronous `rbenv init`, per-shell JWT completion generation, redundant autojump alongside zoxide

## Changes

### 1. Remove duplicate `compinit` call

**File:** `dot_zshrc.tmpl`, line 183

`autoload -U compinit && compinit` runs before `source $ZSH/oh-my-zsh.sh`, which calls `compinit` internally. Each `compinit` call scans every file in `$fpath` — with 30+ plugins, this costs 50-100ms. The duplicate wastes that time for zero benefit.

**Action:** Delete line 183.
**Estimated savings:** 50-100ms

### 2. Remove duplicate aliases and functions from `.zshrc`

**File:** `dot_zshrc.tmpl`, lines 8-10 and 16-23

The `ifactive` alias, `ssh-hosts` alias, and `.` function are defined in both `.zshrc` and `.zsh_aliases`. Since `.zsh_aliases` is sourced on line 11, the `.zshrc` copies are redundant.

**Action:** Remove lines 8-10 and 16-23 from `dot_zshrc.tmpl`.
**Estimated savings:** Negligible (cleanliness, not speed)

### 3. Remove autojump

**File:** `dot_zshrc.tmpl`, line 221

The `zoxide` OMZ plugin (line 167) provides the same directory-jumping functionality. Autojump is slower (Python-based vs Rust-based zoxide) and redundant.

**Action:** Remove line 221. Consider `brew uninstall autojump` as follow-up.
**Estimated savings:** 20-30ms

### 4. Remove `rbenv init` block

**File:** `dot_zshrc.tmpl`, lines 236-238

`eval "$(rbenv init - zsh)"` forks a subprocess on every shell start. Since `mise` now manages Ruby versions, rbenv is unnecessary.

**Action:** Remove lines 236-238. Also remove the `rbenv` segment from `dot_p10k.zsh` right-prompt elements.
**Estimated savings:** 100-200ms

### 5. Cache JWT completions

**File:** `dot_zshrc.tmpl`, lines 223-225

`source <(jwt completion zsh)` regenerates identical completion output on every shell start. Cache the output to a file instead.

**Action:** Replace the subprocess call with a cached file:
- Create `~/.zsh_completions/` directory
- Generate `_jwt` completion file via a chezmoi run_onchange script (or manual one-time command)
- Add `fpath=(~/.zsh_completions $fpath)` before OMZ sourcing
- Remove lines 223-225

**Estimated savings:** 30-50ms

### 6. Remove unused plugins

**File:** `dot_zshrc.tmpl`, plugins array

- Remove `sfdx` — Salesforce CLI, not in use
- Comment out `aws` — not using AWS completions currently; easy to re-enable

**Estimated savings:** ~10-20ms

### 7. Add `evalcache` for expensive plugin init

**New dependency:** [`evalcache`](https://github.com/mroth/evalcache) (install as OMZ custom plugin)

Three OMZ plugins run `eval "$(tool init)"` on every shell start:
- `direnv` (~30-50ms)
- `mise` (~30-50ms)
- `zoxide` (~20-30ms)

`evalcache` caches eval output to `~/.zsh-evalcache/` and sources the cached file on subsequent starts (~1ms each). The cache auto-invalidates when the tool binary changes.

**Action:**
- Install evalcache to `$ZSH_CUSTOM/plugins/evalcache`
- Disable the OMZ `direnv`, `mise`, and `zoxide` plugins
- Add manual init lines using `_evalcache`:
  ```zsh
  _evalcache mise activate zsh
  _evalcache direnv hook zsh
  _evalcache zoxide init zsh
  ```
- Add `evalcache` to the plugins array

**Estimated savings:** 80-130ms
**Trade-off:** Must run `_evalcache_clear` after upgrading these tools (or it auto-detects binary changes)

---

## Estimated Total Savings

| Change | Low estimate | High estimate |
|--------|-------------|--------------|
| Remove duplicate `compinit` | 50ms | 100ms |
| Remove autojump | 20ms | 30ms |
| Remove `rbenv init` | 100ms | 200ms |
| Cache JWT completions | 30ms | 50ms |
| Remove unused plugins | 10ms | 20ms |
| Add evalcache (direnv, mise, zoxide) | 80ms | 130ms |
| **Total** | **290ms** | **530ms** |

With the low estimate alone, a shell starting at ~1s drops to ~700ms. With the high estimate, a ~1.5s shell drops to ~970ms. Combined, these changes should bring startup well under the 500ms target.

## Verification

Measure before and after with:
```zsh
# From an existing shell, time a fresh interactive shell:
time zsh -i -c exit

# For detailed profiling:
# Add to top of .zshrc: zmodload zsh/zprof
# Add to bottom of .zshrc: zprof
```

## What This Design Does NOT Change

- Oh My Zsh remains the framework
- Powerlevel10k remains the prompt (with instant prompt)
- All essential plugins remain loaded
- No visual changes to the prompt
- `alias-finder` automatic mode stays enabled (per-command cost, not startup)
- `zsh-syntax-highlighting` sourced from Homebrew after OMZ (correct ordering preserved)

## Future Considerations (Out of Scope)

- **Starship migration:** If p10k breaks on a future ZSH version, Starship is the recommended replacement. This design is compatible with that future migration.
- **Framework-free setup:** If further speed is needed, replacing OMZ with Antidote or Sheldon + standalone plugins is the next step. Not warranted for the <500ms target.
- **Per-command latency:** `alias-finder` automatic mode adds ~20-50ms per command. Acceptable for the learning benefit but worth revisiting if command responsiveness feels sluggish.
