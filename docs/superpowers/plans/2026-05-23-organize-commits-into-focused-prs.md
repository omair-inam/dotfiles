# Organize Working-Tree Changes into Focused PRs — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the chezmoi repo's mixed uncommitted working-tree changes into ~12 fine-grained, focused PRs — one concern per PR, each branched from `origin/main` in its own worktree — without leaking sensitive files to the public repo.

**Architecture:** Snapshot the entire working tree to a throwaway branch first (safety net + content source). Then build each PR in an isolated worktree off `origin/main`, populating only that PR's files from the snapshot (`git checkout <snapshot> -- <files>`), verifying isolation, committing with a conventional-commit message, pushing, and opening a PR. Three sensitive/scratch paths are never committed.

**Tech Stack:** git (worktrees), `gh` CLI, chezmoi, 1Password SSH (Touch ID for push/PR).

**Spec:** `docs/superpowers/specs/2026-05-23-organize-commits-into-focused-prs-design.md`

---

## Overall Status

> Executor: keep this table in sync — update the **Status** cell after each task completes. Legend: ⬜ pending · 🔄 in progress · ✅ done · ⏸️ blocked (e.g. waiting on 1Password Touch ID).

> Snapshot of state at end of Phase 1 (all branches built + committed locally; pushes + PRs are Phase 2, pending user Touch ID).

| Task | PR / concern | Branch | Built | Committed (SHA) | Pushed | PR | Status |
|---|---|---|---|---|---|---|---|
| 0 | Preflight: snapshot (fetch skipped — origin/main current) | `wip/pre-split-snapshot` | n/a | ✅ fd85fcc | n/a | n/a | ✅ |
| 1 | `chore(claude): reconcile settings` | `chore/claude-settings` | ✅ | ✅ 64e4c25 | ⬜ | ⬜ | Phase 1 ✅ |
| 2 | `chore(claude): plugin manifests as create_` | `chore/claude-plugins` | ✅ | ✅ eae2116 | ⬜ | ⬜ | Phase 1 ✅ |
| 3 | `chore(claude): remove unused agents + skill` | `chore/claude-prune-agents` | ✅ | ✅ f48f034 | ⬜ | ⬜ | Phase 1 ✅ |
| 4 | `docs(claude): instructions additions` | `docs/claude-instructions` | ✅ | ✅ 43d697a | ⬜ | ⬜ | Phase 1 ✅ |
| 5 | `feat(zsh): auto-mode aliases` | `feat/zsh-auto-mode-aliases` | ✅ | ✅ 45f86c1 | ⬜ | ⬜ | Phase 1 ✅ |
| 6 | `refactor(zsh): completion loading` | `refactor/zsh-completions` | ✅ | ✅ 3e1ceb9 | ⬜ | ⬜ | Phase 1 ✅ |
| 7 | `chore(mise): add terraform, drop agent-slack npm tool` | `chore/mise-terraform` | ✅ | ✅ fc44cb3 | ⬜ | ⬜ | Phase 1 ✅ |
| 8 | `chore(brew): add googleworkspace-cli` | — | n/a | n/a | n/a | #55 | ⏭️ SKIP (already open as PR #55) |
| 9 | `chore(git): disable commit signing` | `chore/git-disable-signing` | ✅ | ✅ 411e82d | ⬜ | ⬜ | Phase 1 ✅ |
| 10 | `chore(repo): gitignore local artifacts` | `chore/repo-gitignore` | ✅ | ✅ 4b87e96 | ⬜ | ⬜ | Phase 1 ✅ |
| 11 | `docs: zsh-prompts note + plans` | `docs/planning-notes` | ✅ | ✅ fd22767 | ⬜ | ⬜ | Phase 1 ✅ |
| 12 | `docs(planning): commit-org spec + plan` | `docs/commit-organization-plan` | ✅ | 🔄 this commit | ⬜ | ⬜ | Phase 1 |
| — | Supersede: close PR #54 | n/a | n/a | n/a | n/a | close | ⬜ (Phase 2) |
| 13 | Cleanup: remove worktrees + snapshot | n/a | n/a | n/a | n/a | n/a | ⬜ (Phase 2) |

---

## Pre-existing open PRs (discovered at execution time)

Two PRs were already open from prior sessions:
- **PR #55** `feat(brew): add googleworkspace-cli formula` (branch `feat/add-googleworkspace-cli`) — identical to planned PR 8. **Skip Task 8 entirely**; leave #55 as-is. `packages.toml` stays a working-tree change covered by #55.
- **PR #54** `fix(claude): reconcile Claude Code config with live state` (branch `fix/reconcile-claude-code-config`) — a bundled, now-stale version of PRs 1–4 (its `settings.json` predates this conversation's Obsidian/toggles merge). **Decision: supersede.** In Phase 2, close #54 (`op plugin run -- gh pr close 54 -c "Superseded by fine-grained PRs"`) and let the fresh PRs 1–4 replace it (with the up-to-date merged `settings.json` and the `agent-slack` deletion that #54 lacked).

## Execution Mode: Local-First (chosen)

- **Phase 1 (unattended, no Touch ID):** for Tasks 1–12 run only **Steps 1–4** (worktree → populate → verify isolation → commit). **Skip Step 5 (push + PR).** Do **not** remove the worktree in Step 6 yet — leave all worktrees in place for review.
- **Phase 2 (user present):** after all 12 branches are committed and the user has reviewed them, run **Step 5 for every task** (push + `op plugin run -- gh pr create`), batched, approving Touch ID together. Then run Task 13 (cleanup: remove worktrees + delete snapshot).
- Branches persist independently of their worktrees, so Phase 2 pushes work whether or not a worktree is still mounted.

---

## Conventions (apply to every PR task)

- **Repo root:** `/Users/omair/.local/share/chezmoi` (run git commands from here unless inside a worktree).
- **Snapshot branch:** `wip/pre-split-snapshot` — never pushed; deleted in Task 13.
- **Worktree path:** `.worktrees/<branch-leaf>` (e.g. `.worktrees/claude-settings`). `.worktrees/` is gitignored.
- **Commit trailer:** end every commit message with
  `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`
- **PR body** MUST begin with:
  ```
  > [!IMPORTANT]
  > *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*
  ```
- **1Password Touch ID:** `git push` and `gh pr create` each trigger it. Plain `git commit` does NOT (signing is unset, and the `prevent_unsigned_commits.py` hook only blocks explicit `--no-gpg-sign` / `-c commit.gpgsign=false`). On a 1Password auth failure (`failed to fill whole buffer`, etc.) do NOT retry automatically — pause and tell the user. If `gh` reports an auth error, tell the user to run `ghinit` outside Claude Code.
- **`gh` invocation:** the Bash tool runs a non-interactive shell where the `gh` alias (`op plugin run -- gh`) is NOT active, so a bare `gh` runs unauthenticated. Every `gh` command in this plan MUST be invoked as `op plugin run -- gh …` (shown that way in each Step 5). Equivalent fallback: `GITHUB_TOKEN=$(op plugin run -- gh auth token) gh …`.
- **Isolation check (the "test"):** before every commit, run from inside the worktree
  `git status --porcelain` and `git diff --staged --stat` — the staged set must match the task's file list exactly, no more, no less.

---

### Task 0: Preflight — snapshot and fetch

**Files:** none (git plumbing only).

- [ ] **Step 1: Confirm clean starting point and current branch**

Run: `cd /Users/omair/.local/share/chezmoi && git status --short && git branch --show-current`
Expected: branch `main`; the mixed change set from the spec is present (modified/deleted/renamed + untracked `docs/`, `migration-kit-backup/`, `.claude/`, `cmdiff.txt`).

- [ ] **Step 2: Fetch latest origin/main**

Run: `git fetch origin`
Expected: `origin/main` ref updated (or already current).

- [ ] **Step 3: Create the snapshot branch with all in-scope changes (excluding the 3 EXCLUDE paths)**

```bash
git switch -c wip/pre-split-snapshot
git add -A -- home/ CLAUDE.md docs/
git commit -m "wip: pre-split snapshot (do not push)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```
Note: scoping `git add` to `home/ CLAUDE.md docs/` deliberately excludes `migration-kit-backup/`, `.claude/`, and `cmdiff.txt` (the never-commit paths) and the nested git worktree under `.claude/`.

- [ ] **Step 4: Verify the snapshot captured the expected files and excluded the rest**

Run: `git show --stat HEAD | head -40`
Expected: lists `home/dot_claude/settings.json`, plugin `create_*.json` (renamed), deleted agents + `agent-slack/*`, `CLAUDE.md.tmpl`, `dot_zsh_aliases.tmpl`, `dot_zshrc.tmpl`, `mise/config.toml.tmpl`, `packages.toml`, `dot_gitconfig.tmpl`, root `CLAUDE.md`, and the new `docs/` files (3 plans/notes + the spec + this plan).
Run: `git status --short` — expected: only `migration-kit-backup/`, `.claude/`, `cmdiff.txt` remain as untracked.

- [ ] **Step 5: Return to main (working tree keeps the live changes via the snapshot commit on this branch)**

Run: `git switch main`
Expected: now on `main`. (The live edits now live as a commit on `wip/pre-split-snapshot`; `main`'s working tree reflects `origin/main` plus the 3 untracked excludes.)

Run: `git status --short`
Expected: clean except the 3 untracked excludes. The tracked changes are safely in the snapshot branch.

---

### Task 1: PR — reconcile Claude settings

**Files:** `home/dot_claude/settings.json` (modify)

- [ ] **Step 1: Create worktree off origin/main**

```bash
git worktree add -b chore/claude-settings .worktrees/claude-settings origin/main
```

- [ ] **Step 2: Populate the file from the snapshot**

```bash
cd .worktrees/claude-settings
git checkout wip/pre-split-snapshot -- home/dot_claude/settings.json
```

- [ ] **Step 3: Verify isolation**

Run: `git status --porcelain && git diff --staged --stat`
Expected: exactly `home/dot_claude/settings.json` staged, nothing else.

- [ ] **Step 4: Commit**

```bash
git commit -m "chore(claude): reconcile settings.json with local config

Drops the understand-anything and cloudflare marketplaces, keeps the
obsidian plugin + obsidian-skills marketplace, and folds local
operational toggles (permissions, verbose, autoCompactEnabled,
remoteControlAtStartup, agentPushNotifEnabled, skipAutoPermissionPrompt)
into the source so apply no longer wipes them.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 5: Push + open PR** (1Password Touch ID)

```bash
git push -u origin chore/claude-settings
op plugin run -- gh pr create --base main --head chore/claude-settings \
  --title "chore(claude): reconcile settings.json with local config" \
  --body '> [!IMPORTANT]
> *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*

Reconciles `~/.claude/settings.json` drift into the chezmoi source: drops the dormant `understand-anything`/`cloudflare` marketplaces, keeps the `obsidian` plugin + `obsidian-skills` marketplace, and preserves local operational toggles.'
```

- [ ] **Step 6: Update the Overall Status table row for Task 1 → ✅ and remove the worktree**

```bash
cd /Users/omair/.local/share/chezmoi
git worktree remove .worktrees/claude-settings
```

---

### Task 2: PR — track plugin manifests as create_ templates

**Files:** rename + modify `home/dot_claude/plugins/known_marketplaces.json` → `create_known_marketplaces.json`; `private_installed_plugins.json` → `create_private_installed_plugins.json`

- [ ] **Step 1: Create worktree**

```bash
git worktree add -b chore/claude-plugins .worktrees/claude-plugins origin/main
cd .worktrees/claude-plugins
```

- [ ] **Step 2: Reproduce the renames (remove old names, add new create_ names from snapshot)**

```bash
git rm home/dot_claude/plugins/known_marketplaces.json home/dot_claude/plugins/private_installed_plugins.json
git checkout wip/pre-split-snapshot -- \
  home/dot_claude/plugins/create_known_marketplaces.json \
  home/dot_claude/plugins/create_private_installed_plugins.json
git add home/dot_claude/plugins/create_known_marketplaces.json home/dot_claude/plugins/create_private_installed_plugins.json
```

- [ ] **Step 3: Verify isolation + rename detection**

Run: `git status --porcelain && git diff --staged --stat -M`
Expected: two renames (`known_marketplaces.json` → `create_known_marketplaces.json`, `private_installed_plugins.json` → `create_private_installed_plugins.json`) with content changes; nothing else.

- [ ] **Step 4: Commit**

```bash
git commit -m "chore(claude): track plugin manifests as create_ templates

Rename known_marketplaces.json and private_installed_plugins.json to the
create_ prefix so chezmoi creates them once without clobbering the live
plugin state on every apply. Refresh versions/timestamps and add the
linear, slack, frontend-design, telegram, and imessage plugins.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 5: Push + open PR** (1Password Touch ID)

```bash
git push -u origin chore/claude-plugins
op plugin run -- gh pr create --base main --head chore/claude-plugins \
  --title "chore(claude): track plugin manifests as create_ templates" \
  --body '> [!IMPORTANT]
> *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*

Renames the two plugin manifests to the chezmoi `create_` prefix (create-once, never clobber) and refreshes installed-plugin state.'
```

- [ ] **Step 6: Update status row → ✅, remove worktree**

```bash
cd /Users/omair/.local/share/chezmoi && git worktree remove .worktrees/claude-plugins
```

---

### Task 3: PR — remove unused agents and agent-slack skill

**Files (delete):** `home/dot_claude/agents/code-implementation-expert.md`, `home/dot_claude/agents/documentation-retriever.md`, `home/dot_claude/skills/agent-slack/SKILL.md`, `references/commands.md`, `references/output.md`, `references/targets.md`

- [ ] **Step 1: Create worktree**

```bash
git worktree add -b chore/claude-prune-agents .worktrees/claude-prune-agents origin/main
cd .worktrees/claude-prune-agents
```

- [ ] **Step 2: Remove the files**

```bash
git rm home/dot_claude/agents/code-implementation-expert.md \
       home/dot_claude/agents/documentation-retriever.md \
       home/dot_claude/skills/agent-slack/SKILL.md \
       home/dot_claude/skills/agent-slack/references/commands.md \
       home/dot_claude/skills/agent-slack/references/output.md \
       home/dot_claude/skills/agent-slack/references/targets.md
```

- [ ] **Step 3: Verify isolation**

Run: `git status --porcelain && git diff --staged --stat`
Expected: exactly the 6 deletions, nothing else.

- [ ] **Step 4: Commit**

```bash
git commit -m "chore(claude): remove unused agents and agent-slack skill

Delete the code-implementation-expert and documentation-retriever agents
and the agent-slack skill (superseded by the official slack plugin).

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 5: Push + open PR** (1Password Touch ID)

```bash
git push -u origin chore/claude-prune-agents
op plugin run -- gh pr create --base main --head chore/claude-prune-agents \
  --title "chore(claude): remove unused agents and agent-slack skill" \
  --body '> [!IMPORTANT]
> *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*

Removes two unused agent definitions and the agent-slack skill (superseded by the official slack plugin).'
```

- [ ] **Step 6: Update status row → ✅, remove worktree**

```bash
cd /Users/omair/.local/share/chezmoi && git worktree remove .worktrees/claude-prune-agents
```

---

### Task 4: PR — Claude instructions additions

**Files:** `home/dot_claude/CLAUDE.md.tmpl` (modify)

- [ ] **Step 1–3: Worktree, populate, verify**

```bash
git worktree add -b docs/claude-instructions .worktrees/claude-instructions origin/main
cd .worktrees/claude-instructions
git checkout wip/pre-split-snapshot -- home/dot_claude/CLAUDE.md.tmpl
git status --porcelain && git diff --staged --stat
```
Expected: exactly `home/dot_claude/CLAUDE.md.tmpl` staged.

- [ ] **Step 4: Commit**

```bash
git commit -m "docs(claude): add git-workflow, worktree, and 1Password Touch ID guidance

Add a Git Workflow section (branch from origin/main, focused PRs), a
Workflow Conventions note (worktree before committing), and 1Password
Touch ID / SSH signing failure-handling guidance.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 5: Push + open PR** (1Password Touch ID)

```bash
git push -u origin docs/claude-instructions
op plugin run -- gh pr create --base main --head docs/claude-instructions \
  --title "docs(claude): add git-workflow, worktree, and 1Password Touch ID guidance" \
  --body '> [!IMPORTANT]
> *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*

Adds git-workflow, worktree, and 1Password Touch ID guidance to the global CLAUDE.md template.'
```

- [ ] **Step 6: Update status row → ✅, remove worktree**

```bash
cd /Users/omair/.local/share/chezmoi && git worktree remove .worktrees/claude-instructions
```

---

### Task 5: PR — zsh auto-mode aliases (+ root CLAUDE.md doc line)

**Files:** `home/dot_zsh_aliases.tmpl` (modify), `CLAUDE.md` (modify — aliases doc line only, from snapshot)

- [ ] **Step 1–3: Worktree, populate, verify**

```bash
git worktree add -b feat/zsh-auto-mode-aliases .worktrees/zsh-auto-mode-aliases origin/main
cd .worktrees/zsh-auto-mode-aliases
git checkout wip/pre-split-snapshot -- home/dot_zsh_aliases.tmpl CLAUDE.md
git status --porcelain && git diff --staged --stat
```
Expected: exactly `home/dot_zsh_aliases.tmpl` and `CLAUDE.md` staged. The `CLAUDE.md` diff must show ONLY the aliases line (`cca/ccah/ccas/ccao`) change — confirm with `git diff --staged CLAUDE.md` (the snapshot has only that change, so this holds).

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(zsh): add Claude auto-mode aliases (cca/ccah/ccas/ccao)

Add cca (auto-mode) and per-model variants ccah/ccas/ccao, and document
them in the repo CLAUDE.md Key Managed Files list.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 5: Push + open PR** (1Password Touch ID)

```bash
git push -u origin feat/zsh-auto-mode-aliases
op plugin run -- gh pr create --base main --head feat/zsh-auto-mode-aliases \
  --title "feat(zsh): add Claude auto-mode aliases (cca/ccah/ccas/ccao)" \
  --body '> [!IMPORTANT]
> *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*

Adds `cca` and per-model `ccah/ccas/ccao` auto-mode aliases; documents them in CLAUDE.md.'
```

- [ ] **Step 6: Update status row → ✅, remove worktree**

```bash
cd /Users/omair/.local/share/chezmoi && git worktree remove .worktrees/zsh-auto-mode-aliases
```

---

### Task 6: PR — zsh completion loading

**Files:** `home/dot_zshrc.tmpl` (modify)

- [ ] **Step 1–3: Worktree, populate, verify**

```bash
git worktree add -b refactor/zsh-completions .worktrees/zsh-completions origin/main
cd .worktrees/zsh-completions
git checkout wip/pre-split-snapshot -- home/dot_zshrc.tmpl
git status --porcelain && git diff --staged --stat
```
Expected: exactly `home/dot_zshrc.tmpl` staged.

- [ ] **Step 4: Commit**

```bash
git commit -m "refactor(zsh): load ~/.zfunc completions before compinit

Add ~/.zfunc to the line-21 fpath (before oh-my-zsh runs compinit) so the
_ax completion loads via the single OMZ compinit, and drop the redundant
trailing fpath+=/compinit re-run.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 5: Push + open PR** (1Password Touch ID)

```bash
git push -u origin refactor/zsh-completions
op plugin run -- gh pr create --base main --head refactor/zsh-completions \
  --title "refactor(zsh): load ~/.zfunc completions before compinit" \
  --body '> [!IMPORTANT]
> *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*

Folds `~/.zfunc` into the line-21 `fpath` before OMZ `compinit` and removes the redundant trailing `compinit` re-run.'
```

- [ ] **Step 6: Update status row → ✅, remove worktree**

```bash
cd /Users/omair/.local/share/chezmoi && git worktree remove .worktrees/zsh-completions
```

---

### Task 7: PR — mise add terraform + drop agent-slack npm tool

**Files:** `home/dot_config/mise/config.toml.tmpl` (modify — adds terraform, removes `npm:agent-slack`)

- [ ] **Step 1–3: Worktree, populate, verify**

```bash
git worktree add -b chore/mise-terraform .worktrees/mise-terraform origin/main
cd .worktrees/mise-terraform
git checkout wip/pre-split-snapshot -- home/dot_config/mise/config.toml.tmpl
git status --porcelain && git diff --staged --stat
```
Expected: exactly `home/dot_config/mise/config.toml.tmpl` staged.

- [ ] **Step 4: Commit**

```bash
git commit -m "chore(mise): add terraform, drop agent-slack npm tool

Add terraform = \"latest\" to the work-tools block and remove the
now-unused npm:agent-slack tool (the agent-slack skill is removed in a
separate PR).

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 5: Push + open PR** (1Password Touch ID)

```bash
git push -u origin chore/mise-terraform
op plugin run -- gh pr create --base main --head chore/mise-terraform \
  --title "chore(mise): add terraform, drop agent-slack npm tool" \
  --body '> [!IMPORTANT]
> *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*

Adds `terraform = "latest"` to the mise work-tools block and removes the unused `npm:agent-slack` tool.'
```

- [ ] **Step 6: Update status row → ✅, remove worktree**

```bash
cd /Users/omair/.local/share/chezmoi && git worktree remove .worktrees/mise-terraform
```

---

### Task 8: PR — brew add googleworkspace-cli

**Files:** `home/.chezmoidata/packages.toml` (modify)

- [ ] **Step 1–3: Worktree, populate, verify**

```bash
git worktree add -b chore/brew-googleworkspace-cli .worktrees/brew-gws origin/main
cd .worktrees/brew-gws
git checkout wip/pre-split-snapshot -- home/.chezmoidata/packages.toml
git status --porcelain && git diff --staged --stat
```
Expected: exactly `home/.chezmoidata/packages.toml` staged.

- [ ] **Step 4: Commit**

```bash
git commit -m "chore(brew): add googleworkspace-cli

Add the googleworkspace-cli formula to the common Homebrew formulae.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 5: Push + open PR** (1Password Touch ID)

```bash
git push -u origin chore/brew-googleworkspace-cli
op plugin run -- gh pr create --base main --head chore/brew-googleworkspace-cli \
  --title "chore(brew): add googleworkspace-cli" \
  --body '> [!IMPORTANT]
> *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*

Adds the `googleworkspace-cli` Homebrew formula to the common package set.'
```

- [ ] **Step 6: Update status row → ✅, remove worktree**

```bash
cd /Users/omair/.local/share/chezmoi && git worktree remove .worktrees/brew-gws
```

---

### Task 9: PR — disable commit signing

**Files:** `home/dot_gitconfig.tmpl` (modify)

- [ ] **Step 1–3: Worktree, populate, verify**

```bash
git worktree add -b chore/git-disable-signing .worktrees/git-disable-signing origin/main
cd .worktrees/git-disable-signing
git checkout wip/pre-split-snapshot -- home/dot_gitconfig.tmpl
git status --porcelain && git diff --staged --stat
```
Expected: exactly `home/dot_gitconfig.tmpl` staged (the `[commit]`/`[gpg "ssh"]` sections become commented out).

- [ ] **Step 4: Commit**

```bash
git commit -m "chore(git): disable 1Password commit signing

Comment out the [commit] gpgsign and [gpg \"ssh\"] sections to match the
intentionally-disabled local state.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 5: Push + open PR** (1Password Touch ID)

```bash
git push -u origin chore/git-disable-signing
op plugin run -- gh pr create --base main --head chore/git-disable-signing \
  --title "chore(git): disable 1Password commit signing" \
  --body '> [!IMPORTANT]
> *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*

Comments out the `[commit] gpgsign` / `[gpg "ssh"]` sections to match the intentionally-disabled local state.'
```

- [ ] **Step 6: Update status row → ✅, remove worktree**

```bash
cd /Users/omair/.local/share/chezmoi && git worktree remove .worktrees/git-disable-signing
```

---

### Task 10: PR — gitignore local artifacts (+ root CLAUDE.md note) — FRESH EDITS

**Files:** `.gitignore` (modify — author fresh), `CLAUDE.md` (modify — author fresh migration-kit note only)

> This is the one task that does NOT pull from the snapshot. The `.gitignore` additions and the `CLAUDE.md` migration-kit note do not exist in the snapshot, and pulling `CLAUDE.md` from the snapshot would drag in Task 5's aliases change. Author both edits fresh off clean `origin/main`.

- [ ] **Step 1: Create worktree**

```bash
git worktree add -b chore/repo-gitignore .worktrees/repo-gitignore origin/main
cd .worktrees/repo-gitignore
```

- [ ] **Step 2: Append the three ignore entries to `.gitignore`**

Append to the end of `.gitignore` (under the existing "Temp files" group):
```
# Local Claude state and scratch
.claude/
cmdiff.txt

# Pre-wipe migration audit (local-only; contains keychain catalog, work repo paths)
migration-kit-backup/
```

- [ ] **Step 3: Update the root `CLAUDE.md` migration-kit line**

Find (line ~23):
```
* `migration-kit-backup/` — pre-wipe migration audit trail
```
Replace with:
```
* `migration-kit-backup/` — pre-wipe migration audit trail (local-only, gitignored — contains sensitive Keychain/repo audits; never commit to this public repo)
```

- [ ] **Step 4: Stage + verify isolation**

```bash
git add .gitignore CLAUDE.md
git status --porcelain && git diff --staged --stat
```
Expected: exactly `.gitignore` and `CLAUDE.md` staged. Confirm `git diff --staged CLAUDE.md` shows ONLY the line-23 migration-kit note change (NOT the aliases line — that belongs to Task 5).

- [ ] **Step 5: Commit**

```bash
git commit -m "chore(repo): gitignore local .claude/, scratch, and migration backup

Ignore machine-local .claude/ (settings + nested worktree), the cmdiff.txt
scratch file, and migration-kit-backup/ (sensitive, local-only). Annotate
the CLAUDE.md migration-kit entry as gitignored.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 6: Push + open PR** (1Password Touch ID)

```bash
git push -u origin chore/repo-gitignore
op plugin run -- gh pr create --base main --head chore/repo-gitignore \
  --title "chore(repo): gitignore local .claude/, scratch, and migration backup" \
  --body '> [!IMPORTANT]
> *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*

Gitignores machine-local `.claude/`, `cmdiff.txt`, and the sensitive `migration-kit-backup/` (keychain catalog + work repo paths) so they never reach this public repo.'
```

- [ ] **Step 7: Update status row → ✅, remove worktree**

```bash
cd /Users/omair/.local/share/chezmoi && git worktree remove .worktrees/repo-gitignore
```

---

### Task 11: PR — zsh-prompts note + implementation plans

**Files (new):** `docs/notes/2026-02-28-zsh-prompts-compared.md`, `docs/plans/2026-02-27-readme-audit-plan.md`, `docs/plans/2026-03-01-ollama-zsh-completion-plan.md`

- [ ] **Step 1–3: Worktree, populate, verify**

```bash
git worktree add -b docs/planning-notes .worktrees/planning-notes origin/main
cd .worktrees/planning-notes
git checkout wip/pre-split-snapshot -- \
  docs/notes/2026-02-28-zsh-prompts-compared.md \
  docs/plans/2026-02-27-readme-audit-plan.md \
  docs/plans/2026-03-01-ollama-zsh-completion-plan.md
git status --porcelain && git diff --staged --stat
```
Expected: exactly the 3 new docs staged.

- [ ] **Step 4: Commit**

```bash
git commit -m "docs: add zsh-prompts note and readme-audit/ollama-completion plans

Add the post-p10k zsh prompts comparison note and the implementation plans
that pair with the already-tracked readme-audit and ollama-completion designs.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 5: Push + open PR** (1Password Touch ID)

```bash
git push -u origin docs/planning-notes
op plugin run -- gh pr create --base main --head docs/planning-notes \
  --title "docs: add zsh-prompts note and implementation plans" \
  --body '> [!IMPORTANT]
> *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*

Adds the zsh-prompts comparison note and two implementation plans pairing with already-tracked designs.'
```

- [ ] **Step 6: Update status row → ✅, remove worktree**

```bash
cd /Users/omair/.local/share/chezmoi && git worktree remove .worktrees/planning-notes
```

---

### Task 12: PR — commit-organization spec + plan

**Files (new):** `docs/superpowers/specs/2026-05-23-organize-commits-into-focused-prs-design.md`, `docs/superpowers/plans/2026-05-23-organize-commits-into-focused-prs.md`

- [ ] **Step 1–3: Worktree, populate, verify**

```bash
git worktree add -b docs/commit-organization-plan .worktrees/commit-organization-plan origin/main
cd .worktrees/commit-organization-plan
git checkout wip/pre-split-snapshot -- \
  docs/superpowers/specs/2026-05-23-organize-commits-into-focused-prs-design.md \
  docs/superpowers/plans/2026-05-23-organize-commits-into-focused-prs.md
git status --porcelain && git diff --staged --stat
```
Expected: exactly the spec + plan staged.

> If this plan was still being edited after Task 0's snapshot, re-snapshot just these two files first from the repo root: `git -C /Users/omair/.local/share/chezmoi stash` is NOT needed; instead copy the latest versions in before committing, or re-run Task 0 Step 3's `git add -A -- docs/ && git commit --amend` on the snapshot branch.

- [ ] **Step 4: Commit**

```bash
git commit -m "docs(planning): add commit-organization spec and plan

Add the brainstorming spec and implementation plan for splitting the
working-tree changes into focused PRs.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 5: Push + open PR** (1Password Touch ID)

```bash
git push -u origin docs/commit-organization-plan
op plugin run -- gh pr create --base main --head docs/commit-organization-plan \
  --title "docs(planning): add commit-organization spec and plan" \
  --body '> [!IMPORTANT]
> *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*

Adds the spec and implementation plan for organizing the working-tree changes into focused PRs.'
```

- [ ] **Step 6: Update status row → ✅, remove worktree**

```bash
cd /Users/omair/.local/share/chezmoi && git worktree remove .worktrees/commit-organization-plan
```

---

### Task 13: Cleanup and final verification

- [ ] **Step 1: Confirm all PR worktrees removed**

Run: `git worktree list`
Expected: only the main worktree (and any unrelated pre-existing ones). No `.worktrees/<pr>` entries from this plan.

- [ ] **Step 2: Reconciliation check — every changed file landed in exactly one PR**

Run from repo root:
```bash
git diff --name-only wip/pre-split-snapshot origin/main
```
Expected: lists all files that differ between the snapshot and origin/main — i.e. everything still pending merge. Cross-check this set equals the union of Tasks 1–12 file lists (Task 10's `.gitignore`/`CLAUDE.md`-note are fresh, so they appear only after their PR merges).

- [ ] **Step 3: Delete the snapshot branch (only after all 12 PRs are open and verified)**

```bash
git branch -D wip/pre-split-snapshot
```

- [ ] **Step 4: Confirm the never-commit paths are untracked and ignored after PR 10 merges**

Run: `git check-ignore migration-kit-backup .claude cmdiff.txt`
Expected (once `chore/repo-gitignore` is merged and pulled): all three echoed back as ignored.

- [ ] **Step 5: Final state**

Run: `git status --short`
Expected: clean except the 3 ignored paths. Update the Overall Status table Task 13 → ✅.

---

## Self-Review (completed during planning)

- **Spec coverage:** every spec PR row (1–11) maps to a task; PR 12 (planning docs) = Task 12; EXCLUDE table = Task 10 + Task 13 Step 4; execution model = Task 0 + per-task worktree steps; verification section = Task 13. ✅
- **Split-file handling:** root `CLAUDE.md` — Task 5 pulls from snapshot (aliases only), Task 10 authors the migration note fresh. No cross-contamination. ✅
- **Placeholder scan:** no TBD/TODO; every step has exact commands. ✅
- **Branch/title consistency:** branch names and PR titles match the Overall Status table and the spec table. ✅
