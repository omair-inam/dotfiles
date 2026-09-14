# README Audit & iTerm2 Cleanup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix README.md to accurately reflect the full installation process, and remove all active iTerm2 references from the repo.

**Architecture:** Two workstreams executed sequentially — iTerm2 cleanup first (simpler, no dependencies), then README fixes. No code to test; verification is manual inspection of file diffs and chezmoi template rendering.

**Tech Stack:** chezmoi, Homebrew, Bash, Go templates, Markdown

---

## Context for the Implementer

- This is a chezmoi dotfiles repo at `/Users/omair/.local/share/chezmoi`
- `home/` maps to `~/`; `dot_*` → `.*`, `.tmpl` files are Go templates rendered at `chezmoi apply` time
- The user has fully switched to Ghostty terminal — iTerm2 is no longer used
- `migration-kit-backup/` is a historical archive — **do not touch it**
- Git commits are GPG-signed via 1Password SSH — **1Password must be unlocked** before committing
- After making changes, prompt the user to run `chezmoi apply` or use alias `cma`

---

## Workstream A: iTerm2 Cleanup

### Task 1: Remove `iterm2` from common casks in packages.toml

**Files:**
- Modify: `home/.chezmoidata/packages.toml:26`

**Step 1: Open the file and locate the line**

File: `home/.chezmoidata/packages.toml`
Find and remove this line (around line 26):
```toml
            "iterm2",                      # Terminal emulator
```

**Step 2: Verify the file looks correct**

Run:
```bash
grep -n "iterm" home/.chezmoidata/packages.toml
```
Expected: Only `itermocil` lines remain (not yet removed — that's Task 2).

---

### Task 2: Remove `itermocil` from work and personal formulae in packages.toml

**Files:**
- Modify: `home/.chezmoidata/packages.toml` (two lines)

**Step 1: Remove from work formulae**

Find and remove (around line 120):
```toml
            "itermocil",                   # iTerm2 session manager
```

**Step 2: Remove from personal formulae**

Find and remove (around line 139):
```toml
            "TomAnthony/brews/itermocil"  # Alternative iTerm2 session manager
```

**Step 3: Verify no active iTerm2 references remain in packages.toml**

Run:
```bash
grep -in "iterm" home/.chezmoidata/packages.toml
```
Expected: No output.

---

### Task 3: Remove iTerm2 line from notes.md

**Files:**
- Modify: `notes.md`

**Step 1: Remove the line**

Find and remove line 8:
```bash
brew install --cask iterm2
```

**Step 2: Verify**

Run:
```bash
grep -in "iterm" notes.md
```
Expected: No output.

---

### Task 4: Delete the `Natural text editing.png` image

This file is only referenced in the README's iTerm2 section, which will be removed in Task 5.

**Step 1: Delete the file**

Run:
```bash
git rm "Natural text editing.png"
```

**Step 2: Verify**

Run:
```bash
ls "Natural text editing.png" 2>/dev/null && echo "still exists" || echo "deleted"
```
Expected: `deleted`

---

### Task 5: Commit iTerm2 cleanup

**Step 1: Stage all changes**

```bash
git add home/.chezmoidata/packages.toml notes.md
```

**Step 2: Commit**

```bash
git commit -m "chore: remove iTerm2 — switched to Ghostty"
```

> Note: 1Password must be unlocked for GPG signing.

---

## Workstream B: README Fixes

### Task 6: Remove the iTerm2 section from README.md

**Files:**
- Modify: `README.md`

**Step 1: Remove the entire iTerm2 section**

Locate and delete these lines:
```markdown
### iTerm2 updates
#### Enable natural text editing
In version 3.4, open iTerm preferences. Select Profiles > Keys > Key Mappings > Presets > Natural Text Editing.

![alt text](Natural text editing.png)

```

**Step 2: Verify**

Run:
```bash
grep -in "iterm" README.md
```
Expected: No output.

---

### Task 7: Remove the "Apps pinned to older versions" section from README.md

**Files:**
- Modify: `README.md`

**Step 1: Remove this section**

Locate and delete:
```markdown
### Apps pinned to older versions

* Beyond Compare 4
* Forklift 3

```

**Step 2: Verify**

Run:
```bash
grep -n "pinned" README.md
```
Expected: No output.

---

### Task 8: Fix the broken `docs/casks.md` link in README.md

**Files:**
- Modify: `README.md`

**Step 1: Remove the broken link**

Locate the "Other docs" section at the bottom:
```markdown
## Other docs

[Creating new casks](docs/casks.md)
```

Remove this entire section (the `docs/casks.md` file does not exist).

**Step 2: Verify**

Run:
```bash
grep -n "casks.md" README.md
```
Expected: No output.

---

### Task 9: Add missing install steps to the README

**Files:**
- Modify: `README.md`

**Step 1: Expand the install section**

The current install section reads:
```markdown
## Installation directions
###  Install Homebrew, chezmoi and ohmyzsh
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/omair-inam/dotfiles/refs/heads/main/install.sh)"
```
```

Replace the entire `## Installation directions` section with:

```markdown
## Installation directions

### Prerequisites

- **1Password** must be installed and unlocked before running `chezmoi apply`.
  Templates use 1Password to fetch secrets (NPM token, Maven settings, git signing key).

### 1. Install Homebrew, chezmoi, Oh My Zsh, and plugins

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/omair-inam/dotfiles/refs/heads/main/install.sh)"
```

This script installs: Homebrew, Oh My Zsh, Powerlevel10k, zsh plugins (autosuggestions, forgit, completions, etc.), and chezmoi.

### 2. Initialise and apply dotfiles

```bash
chezmoi init https://github.com/omair-inam/dotfiles.git
chezmoi apply
```

During `chezmoi apply` you will be prompted for three values (cached after first run):

| Prompt | Type | Purpose |
|---|---|---|
| `personal_device` | true/false | Enables personal apps and configs |
| `work_device` | true/false | Enables work apps and configs (DNAstack) |
| `email` | string | Used in git config |

`chezmoi apply` will then: install Homebrew packages, configure macOS defaults, set up Rosetta 2, install pipx/poetry, and (for work devices) install Java and Python via asdf.
```

**Step 2: Verify the new section reads correctly**

Run:
```bash
head -60 README.md
```
Confirm the new sections appear in order: Prerequisites → Step 1 (install.sh) → Step 2 (chezmoi init + apply + prompts table).

---

### Task 10: Commit README fixes

**Step 1: Stage changes**

```bash
git add README.md
```

**Step 2: Commit**

```bash
git commit -m "docs: update README with accurate install steps, remove stale iTerm2 section"
```

> Note: 1Password must be unlocked for GPG signing.

---

### Task 11: Prompt user to apply chezmoi changes

After committing, remind the user:

```
Run: chezmoi apply   (or alias: cma)
```

This will reflect the removed iTerm2 packages in the next Homebrew bundle run.
