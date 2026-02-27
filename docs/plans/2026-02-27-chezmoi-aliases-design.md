# Chezmoi Aliases Design

## Context

Replace the existing two bare `chezmoi` aliases (`cm`, `cmd`) with a comprehensive set of 23 aliases following the OMZ git plugin naming convention.

**Convention:** `cm` prefix + first letter(s) of subcommand + first letter of flags.
Mirrors the OMZ git pattern (`g` + subcommand letters), adapted for the 2-char `cm` prefix.

**Scope:** Daily-use focused with useful flag variants. No template, encryption, or migration aliases.

## Alias Reference

### Base & File Operations

| Alias  | Command                   | Mnemonic         |
|--------|---------------------------|------------------|
| `cm`   | `chezmoi`                 | base command     |
| `cma`  | `chezmoi add`             | cm + add         |
| `cmat` | `chezmoi add --template`  | cm + add + tmpl  |
| `cmra` | `chezmoi re-add`          | cm + re-add      |
| `cme`  | `chezmoi edit`            | cm + edit        |
| `cmf`  | `chezmoi forget`          | cm + forget      |

### Diff, Apply & Merge

| Alias   | Command                    | Mnemonic              |
|---------|----------------------------|-----------------------|
| `cmd`   | `chezmoi diff`             | cm + diff             |
| `cmdr`  | `chezmoi diff --reverse`   | cm + diff + reverse   |
| `cmap`  | `chezmoi apply`            | cm + apply            |
| `cmapv` | `chezmoi apply -v`         | cm + apply + verbose  |
| `cmapn` | `chezmoi apply -v -n`      | cm + apply + dry-run  |
| `cmapf` | `chezmoi apply --force`    | cm + apply + force    |
| `cmm`   | `chezmoi merge`            | cm + merge            |
| `cmma`  | `chezmoi merge-all`        | cm + merge-all        |

### Navigation, Status & Sync

| Alias  | Command                    | Mnemonic           |
|--------|----------------------------|---------------------|
| `cmcd` | `chezmoi cd`               | cm + cd             |
| `cmst` | `chezmoi status`           | cm + status         |
| `cmu`  | `chezmoi update`           | cm + update         |
| `cmg`  | `chezmoi git`              | cm + git            |
| `cmi`  | `chezmoi init`             | cm + init           |
| `cmia` | `chezmoi init --apply`     | cm + init + apply   |

### Maintenance & Verification

| Alias   | Command                | Mnemonic            |
|---------|------------------------|---------------------|
| `cmup`  | `chezmoi upgrade`      | cm + upgrade        |
| `cmv`   | `chezmoi verify`       | cm + verify         |
| `cmec`  | `chezmoi edit-config`  | cm + edit-config    |
| `cmh`   | `chezmoi help`         | cm + help           |
| `cmdoc` | `chezmoi doctor`       | cm + doctor         |

## Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the 2 existing chezmoi aliases with 23 OMZ-convention aliases in dot_zsh_aliases.tmpl.

**Architecture:** Single-file edit. Replace lines 180-182 of `home/dot_zsh_aliases.tmpl` with grouped alias block.

**Tech Stack:** zsh aliases, chezmoi template

---

### Task 1: Replace chezmoi alias block

**Files:**
- Modify: `home/dot_zsh_aliases.tmpl:180-182`

**Step 1: Edit the alias block**

Replace the existing 3 lines (comment + 2 aliases) at lines 180-182:

```
# Chezmoi aliases
alias cm=chezmoi
alias cmd="chezmoi diff"
```

With the full 23-alias block:

```bash
# Chezmoi aliases (OMZ-style: cm + subcommand letters + flag letters)
# Base
alias cm=chezmoi
# File operations
alias cma="chezmoi add"
alias cmat="chezmoi add --template"
alias cmra="chezmoi re-add"
alias cme="chezmoi edit"
alias cmf="chezmoi forget"
# Diff, apply & merge
alias cmd="chezmoi diff"
alias cmdr="chezmoi diff --reverse"
alias cmap="chezmoi apply"
alias cmapv="chezmoi apply -v"
alias cmapn="chezmoi apply -v -n"
alias cmapf="chezmoi apply --force"
alias cmm="chezmoi merge"
alias cmma="chezmoi merge-all"
# Navigation, status & sync
alias cmcd="chezmoi cd"
alias cmst="chezmoi status"
alias cmu="chezmoi update"
alias cmg="chezmoi git"
alias cmi="chezmoi init"
alias cmia="chezmoi init --apply"
# Maintenance & verification
alias cmup="chezmoi upgrade"
alias cmv="chezmoi verify"
alias cmec="chezmoi edit-config"
alias cmh="chezmoi help"
alias cmdoc="chezmoi doctor"
```

**Step 2: Verify the aliases parse correctly**

Run: `zsh -n home/dot_zsh_aliases.tmpl`
Expected: No syntax errors (exit code 0). Note: template directives may cause warnings — that's OK.

**Step 3: Apply with chezmoi and verify**

Run: `chezmoi diff home/dot_zsh_aliases.tmpl` to preview changes.
Run: `chezmoi apply home/dot_zsh_aliases.tmpl` to apply.
Run: `source ~/.zsh_aliases` and test: `type cma` should show `cma is an alias for chezmoi add`.

**Step 4: Commit**

```bash
git add home/dot_zsh_aliases.tmpl
git commit -m "feat: add 23 chezmoi aliases following OMZ git convention"
```

---

## Design Decisions

1. **`cmd` repurposed:** Changed from `chezmoi` base alias to `chezmoi diff` since diff is a top-3 most-used command.
2. **`cmapn` combines `-v -n`:** Dry-run without verbose is rarely useful; combining them shows exactly what apply would change.
3. **No `chezmoi version` alias:** Rare enough to use `cm --version` directly.
4. **`cmg` for `chezmoi git`:** Enables running git commands in source dir without `chezmoi cd`.
