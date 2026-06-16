# Organize Working-Tree Changes into Focused PRs — Design

**Created:** 2026-05-23
**Repo:** `github.com/omair-inam/dotfiles` (PUBLIC) — chezmoi source dir at `/Users/omair/.local/share/chezmoi`
**Base:** `origin/main`

---

## Context

A prior session reconciled the user's local config files with their chezmoi source (settings.json
merge, zsh completions, gitconfig signing, mise terraform, Obsidian plugin, etc.). That work, plus
unrelated changes that had accumulated, left the chezmoi working tree with a large, mixed set of
uncommitted changes spanning Claude Code config, shell config, tooling, git config, and docs.

The goal is to land all of that as a set of **fine-grained, focused PRs** — one concern per PR —
each branched from `origin/main`, so every change is independently reviewable and revertable. This
matches the repo's newer conventions (conventional commits, focused PRs, branch from `origin/main`)
which are themselves part of this changeset.

**Outcome:** ~11 small PRs, nothing sensitive leaked to the public repo, and a clean
`chezmoi diff` afterward (only the always-run `run_` scripts remaining, which is expected).

---

## Decisions

- **Granularity:** ~11 fine-grained PRs, one concern each (user choice).
- **`migration-kit-backup/`:** gitignored, local-only. The repo is PUBLIC and the directory
  contains a Keychain catalog, a list of private work repo paths, a 5.6 MB macOS defaults dump,
  and a `0600` personal `chezmoi.toml`. Never committed.
- **`.claude/`:** gitignored (machine-local Claude settings + a nested git worktree).
- **`cmdiff.txt`:** gitignored (scratch file; sibling `chezmoi_diff.txt` is already ignored).
- **Untracked docs:** committed — they pair with already-tracked design docs.
- **Commit signing:** stays disabled (the user disabled it deliberately); the source is edited to
  match, so this is a real tracked change, not drift.

---

## Files to EXCLUDE (never committed)

| Path | Reason | Action |
|---|---|---|
| `migration-kit-backup/` | Public repo; Keychain catalog, work repo paths, 5.6 MB defaults, `0600` config | `.gitignore` (PR 10) |
| `.claude/` | Machine-local Claude settings + nested worktree | `.gitignore` (PR 10) |
| `cmdiff.txt` | Scratch diff file | `.gitignore` (PR 10) |

---

## The PRs

Each PR = one branch off `origin/main`, built in its **own worktree**, conventional-commit title,
PR body opening with the required AI-assistance alert.

| # | Branch / title | Files |
|---|---|---|
| 1 | `chore(claude): reconcile settings with local config` | `home/dot_claude/settings.json` |
| 2 | `chore(claude): track plugin manifests as create_ templates` | `home/dot_claude/plugins/create_known_marketplaces.json`, `create_private_installed_plugins.json` (incl. renames from non-`create_` names) |
| 3 | `chore(claude): remove unused agents and agent-slack skill` | delete `home/dot_claude/agents/code-implementation-expert.md`, `agents/documentation-retriever.md`, `skills/agent-slack/{SKILL.md,references/commands.md,references/output.md,references/targets.md}` |
| 4 | `docs(claude): add git-workflow, worktree, and 1Password Touch ID guidance` | `home/dot_claude/CLAUDE.md.tmpl` |
| 5 | `feat(zsh): add Claude auto-mode aliases (cca/ccah/ccas/ccao)` | `home/dot_zsh_aliases.tmpl` + root `CLAUDE.md` (aliases doc line, ~L59) |
| 6 | `refactor(zsh): load ~/.zfunc completions before compinit` | `home/dot_zshrc.tmpl` |
| 7 | `chore(mise): add terraform` | `home/dot_config/mise/config.toml.tmpl` |
| 8 | `chore(brew): add googleworkspace-cli` | `home/.chezmoidata/packages.toml` |
| 9 | `chore(git): disable 1Password commit signing` | `home/dot_gitconfig.tmpl` |
| 10 | `chore(repo): gitignore local .claude/, scratch, and migration backup` | `.gitignore` (+ `.claude/`, `cmdiff.txt`, `migration-kit-backup/`) + root `CLAUDE.md` (migration-kit note, L23) |
| 11 | `docs: add zsh-prompts note and implementation plans` | `docs/notes/2026-02-28-zsh-prompts-compared.md`, `docs/plans/2026-02-27-readme-audit-plan.md`, `docs/plans/2026-03-01-ollama-zsh-completion-plan.md` |

**Note on root `CLAUDE.md` (split file):** touched by PR 5 (aliases line, ~L59) and PR 10
(migration-kit note, L23). Non-adjacent hunks → Git auto-merges regardless of merge order. The
working-tree (and therefore the snapshot) currently contains **only** the aliases change; the
migration-kit note does not exist yet. Therefore:
- **PR 5** populates `CLAUDE.md` via `git checkout wip/pre-split-snapshot -- CLAUDE.md` (gets the
  aliases change, which is the only change present).
- **PR 10** must author the migration-kit note **fresh** in its worktree on top of clean
  `origin/main` — do NOT checkout `CLAUDE.md` from the snapshot there, or PR 5's aliases change
  would leak into PR 10.

**PR 12 — `docs(planning): add commit-organization spec and plan`:** this spec plus the
implementation plan (`docs/superpowers/plans/...`). Built in its own worktree per the repo
convention for committing implementation documents.

---

## Execution Model

Every change currently lives uncommitted in the **main** working tree. To split it into
independent PRs off `origin/main` without losing anything:

1. **Snapshot first.** Commit the entire current working tree to a throwaway branch
   `wip/pre-split-snapshot` (does not get pushed). This is the source of truth for all file
   subsets and the safety net.
2. **`git fetch origin`** to ensure `origin/main` is current.
3. **Per PR:** create a worktree under `.worktrees/<pr-slug>` off `origin/main`, then populate only
   that PR's files from the snapshot:
   - Modified/added files: `git checkout wip/pre-split-snapshot -- <files>`
   - Deletions (PR 3): `git rm <files>`
   - Renames (PR 2): restore the `create_`-named files from the snapshot and `git rm` the old
     names (or `git mv` then overwrite content) so the rename is recorded.
4. **Verify isolation:** `git status` in the worktree shows only that PR's files; `git diff
   --staged --stat` matches the table row.
5. **Commit** with the conventional-commit title.
6. **Push** the branch and **`gh pr create`** with the AI-assistance alert in the body.
7. **Remove the worktree** when the PR is open (`git worktree remove`).

`origin` push and `gh pr create` each require 1Password Touch ID; these are batched and paused for
the user. `chezmoi apply` is **not** part of this work — the live machine is already in sync.

---

## Conventions

- **Branches:** always from `origin/main` (`git fetch origin && git worktree add -b <branch>
  .worktrees/<slug> origin/main`).
- **Commit messages:** conventional-commit titles per the table; trailer
  `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`.
- **PR bodies:** MUST begin with:
  ```
  > [!IMPORTANT]
  > *This PR was developed with AI assistance provided by [Claude Code](https://claude.ai/code)*
  ```
- **gh auth:** if `gh` fails with an auth error, tell the user to run `ghinit` outside Claude Code;
  do not loop on 1Password failures.

---

## Verification

- After all worktrees are built (before pushing): each worktree's `git diff origin/main --stat`
  contains exactly the files listed for that PR — no spillover.
- The union of all PR file sets equals the snapshot's changed files **minus** the three EXCLUDE
  entries. Run a reconciliation check: snapshot changed-file list vs. sum of per-PR file lists.
- `migration-kit-backup/`, `.claude/`, `cmdiff.txt` appear in no PR except PR 10's `.gitignore`.
- After PRs merge and a `git pull`, `git status` is clean and `chezmoi diff` shows only the
  always-run `run_` scripts (`00_dock_position`, `10_install-claude-code-native`,
  `99_restart_ui`).
