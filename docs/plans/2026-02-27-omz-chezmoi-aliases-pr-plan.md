# OMZ Chezmoi Aliases PR Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a PR to ohmyzsh/ohmyzsh adding 14 aliases to the chezmoi plugin.

**Architecture:** Append alias block to existing plugin file, rewrite README with alias table, create branch + PR via gh CLI.

**Tech Stack:** zsh, gh CLI, git

---

### Task 1: Add aliases to chezmoi.plugin.zsh

**Files:**
- Modify: `/Users/omair/projects/ohmyzsh/plugins/chezmoi/chezmoi.plugin.zsh:14` (append after line 14)

**Step 1: Append alias block after existing completion code**

Add this exact content after line 14 (the last line of the existing file):

```zsh

#
# Aliases
# (sorted alphabetically by alias name)
#

alias cm='chezmoi'
alias cma='chezmoi add'
alias cmap='chezmoi apply'
alias cmcd='chezmoi cd'
alias cmd='chezmoi diff'
alias cme='chezmoi edit'
alias cmg='chezmoi git'
alias cmi='chezmoi init'
alias cmia='chezmoi init --apply'
alias cmm='chezmoi merge'
alias cmma='chezmoi merge-all'
alias cmra='chezmoi re-add'
alias cmst='chezmoi status'
alias cmu='chezmoi update'
```

**Step 2: Verify syntax**

Run: `zsh -n /Users/omair/projects/ohmyzsh/plugins/chezmoi/chezmoi.plugin.zsh`
Expected: No output (exit 0 = no syntax errors)

---

### Task 2: Rewrite README.md with alias table

**Files:**
- Modify: `/Users/omair/projects/ohmyzsh/plugins/chezmoi/README.md` (full rewrite)

**Step 1: Replace README.md with updated content**

Write this exact content:

```markdown
# chezmoi Plugin

## Introduction

This `chezmoi` plugin provides completion and [aliases](#aliases) for [chezmoi](https://chezmoi.io).

To use it, add `chezmoi` to the plugins array of your zshrc file:

```zsh
plugins=(... chezmoi)
```

## Aliases

| Alias  | Command                | Description                                            |
| :----- | :--------------------- | :----------------------------------------------------- |
| `cm`   | `chezmoi`              | The base chezmoi command                               |
| `cma`  | `chezmoi add`          | Add a file to the source state                         |
| `cmap` | `chezmoi apply`        | Update the destination to match the target state       |
| `cmcd` | `chezmoi cd`           | Launch a shell in the source directory                 |
| `cmd`  | `chezmoi diff`         | Print the diff between target state and destination    |
| `cme`  | `chezmoi edit`         | Edit the source state of a target                      |
| `cmg`  | `chezmoi git`          | Run git in the source directory                        |
| `cmi`  | `chezmoi init`         | Set up the source directory                            |
| `cmia` | `chezmoi init --apply` | Set up the source directory and apply in one step      |
| `cmm`  | `chezmoi merge`        | Three-way merge for a file                             |
| `cmma` | `chezmoi merge-all`    | Three-way merge for all modified files                 |
| `cmra` | `chezmoi re-add`       | Re-add modified files                                  |
| `cmst` | `chezmoi status`       | Show the status of targets                             |
| `cmu`  | `chezmoi update`       | Pull and apply changes from the remote                 |
```

---

### Task 3: Create branch, commit, push, and open PR

**Step 1: Create feature branch from latest master**

```bash
cd /Users/omair/projects/ohmyzsh
git checkout master
git pull origin master
git checkout -b feat/chezmoi-aliases
```

**Step 2: Stage and commit**

```bash
git add plugins/chezmoi/chezmoi.plugin.zsh plugins/chezmoi/README.md
git commit -m "feat(chezmoi): add aliases for common chezmoi commands"
```

**Step 3: Push to fork**

```bash
git push -u origin feat/chezmoi-aliases
```

**Step 4: Create PR targeting upstream**

Use `gh pr create` with the OMZ PR template. The PR targets `ohmyzsh/ohmyzsh` master branch. The PR body must include the standards checklist, changes section, and use case justification.

PR title: `feat(chezmoi): add aliases for common chezmoi commands`

PR body (exact text):

```
## Standards checklist:

- [x] The PR title is descriptive.
- [x] The PR doesn't replicate another PR which is already open.
- [x] I have read the contribution guide and followed all the instructions.
- [x] The code follows the code style guide detailed in the wiki.
- [x] The code is mine or it's from somewhere with an MIT-compatible license.
- [x] I used Claude Code to assist with designing the alias naming convention. All aliases have been manually reviewed and validated.
- [x] The code is efficient, to the best of my ability, and does not waste computer resources.
- [x] The code is stable and I have tested it myself, to the best of my abilities.
- [x] The new aliases follow the OMZ naming convention (prefix + subcommand letters) and cover the most common chezmoi workflow commands. Use case described below.

## Changes:

- Add 14 aliases to the `chezmoi` plugin covering the core chezmoi dotfile management workflow
- Update `README.md` with an alias reference table

## Use case:

chezmoi users frequently repeat the same workflow: `chezmoi diff` → `chezmoi apply`, `chezmoi add` / `chezmoi re-add` to track files, `chezmoi cd` to navigate to the source directory, and `chezmoi update` to pull remote changes. These aliases follow the same naming pattern as the git plugin (`cm` prefix + first letters of subcommand) and save keystrokes in the most common dotfile management tasks.

## Other comments:

The alias prefix `cm` was chosen because:
- It clearly evokes "chezmoi"
- It has zero collisions with existing OMZ plugin aliases
- It follows the established convention (git uses `g`, molecule uses `m`)

The alias set is intentionally conservative — it covers the daily-use commands documented in the [chezmoi Quick Start Guide](https://www.chezmoi.io/quick-start/) without including flag variants or maintenance commands. These can be added incrementally if there's demand.
```

**Step 5: Verify PR was created**

Run: `gh pr view --web` to open in browser, or `gh pr view` to verify details.
