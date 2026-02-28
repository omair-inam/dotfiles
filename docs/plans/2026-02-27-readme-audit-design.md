# README Audit Design

**Date:** 2026-02-27
**Scope:** Audit README.md for accuracy/completeness against repo content; clean up iTerm2 references across the repo.

## Issues Found

| Issue | Severity | Type |
|---|---|---|
| Missing `chezmoi init` + `chezmoi apply` steps after install.sh | Critical | Incomplete |
| Missing chezmoi config prompts (`personal_device`, `work_device`, `email`) | Critical | Incomplete |
| Missing 1Password prerequisite before `chezmoi apply` | High | Incomplete |
| `docs/casks.md` link is broken (file doesn't exist) | High | Incorrect |
| iTerm2 section present — user has switched to Ghostty | High | Stale |
| "Apps pinned to older versions" has no actionable guidance | Low | Stale/Vague |
| Rosetta 2 installed automatically by script 01 — not documented | Low | Incomplete |

## Approach

Fix-in-place: patch each issue where it lives in the README, preserving the overall structure. Remove iTerm2 references across the repo as a parallel workstream.

## Change Set

### Workstream A: README fixes

| # | Section | Action | Change |
|---|---|---|---|
| 1 | Install section | Add | After install.sh, document `chezmoi init` + `chezmoi apply` steps |
| 2 | Install section | Add | Note the three prompts (`personal_device`, `work_device`, `email`) |
| 3 | Install section | Add | Prerequisite: 1Password must be installed and unlocked before `chezmoi apply` |
| 4 | macOS updates | Keep | Valid for initial setup; note automation kicks in after first apply |
| 5 | iTerm2 section | Remove | Entire section + image reference |
| 6 | Pinned apps note | Remove | Not actionable |
| 7 | Other docs link | Fix | Remove broken `docs/casks.md` link |

### Workstream B: iTerm2 cleanup

| File | Change |
|---|---|
| `home/.chezmoidata/packages.toml` | Remove `iterm2` from common casks |
| `home/.chezmoidata/packages.toml` | Remove `itermocil` from work formulae |
| `home/.chezmoidata/packages.toml` | Remove `TomAnthony/brews/itermocil` from personal formulae |
| `notes.md` | Remove `brew install --cask iterm2` line |
| `Natural text editing.png` | Delete (only referenced in removed README section) |
| `migration-kit-backup/` | Leave untouched — historical archive |
