# Logical Commits Plan — Chezmoi Repo Cleanup

**Created:** 2026-02-27
**Branch:** main
**Goal:** Organize all pending working-copy changes into logical, atomic commits.

---

## Files to EXCLUDE (do NOT commit)

| File | Reason | Action |
|---|---|---|
| `.DS_Store` | OS artifact | Add to `.gitignore` |
| `home/.DS_Store` | OS artifact | Add to `.gitignore` |
| `.idea/` | IDE config | Add to `.gitignore` |
| `chezmoi_diff.txt` | Temp debug file | Delete or ignore |
| `demo.gif` | Unknown provenance | Ask owner |
| `fix-zsh-java-init-conversation.md` | Session notes | Ask owner |
| `docs/` | Plans directory (this file lives here) | Commit separately if desired |

---

## Commits

### Commit 1: 1Password plugin config and gh token reference
- [x] **Committed** — `7693ca0` (pushed)

**Message:**
```
Update 1Password plugin config and add op plugin shell setup

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Files:**
| File | Status | Description |
|---|---|---|
| `.op/plugins/gh.json` | Modified | Updated `item_id` to new PAT vault entry |
| `home/dot_config/private_op/plugins.sh` | New | 1Password plugin alias source (`export OP_PLUGIN_ALIASES_SOURCED=1`, `alias gh=...`) |

**Rationale:** Both files are the 1Password CLI plugin integration for `gh`. The `.op` config points to the credential; `plugins.sh` exports the shell alias. Tightly coupled.

---

### Commit 2: SSH config and public keys
- [x] **Committed** — `5ed0aa5`

**Message:**
```
Add SSH config with 1Password agent and GitHub host aliases

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Files:**
| File | Status | Description |
|---|---|---|
| `home/dot_ssh/private_config` | New | SSH config: 1Password agent socket, OrbStack include, 4 GitHub host aliases (omairinam, omairdna, omairvalence, omairiai) |
| `home/dot_ssh/private_omairinam.pub` | New | Ed25519 public key for omairinam |
| `home/dot_ssh/private_omairdna.pub` | New | Ed25519 public key for omairdna |
| `home/dot_ssh/omairiai.pub` | New | Ed25519 public key for omairiai |

**Rationale:** Standalone SSH identity configuration. No dependencies on other changes.

---

### Commit 3: Ghostty terminal config
- [x] **Committed** — `9bb6bc1`

**Message:**
```
Add Ghostty terminal configuration

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Files:**
| File | Status | Description |
|---|---|---|
| `home/dot_config/ghostty/config` | New | Ghostty config: GitHub Dark Default theme, macOS option-as-alt, desktop notifications, keybinds |

**Rationale:** Self-contained terminal emulator config. Independent of all other changes.

---

### Commit 4: Shell environment (zsh aliases + zshrc)
- [x] **Committed** — `0d786ce`

**Message:**
```
Update zsh config: add chezmoi aliases, yolo/fly aliases, direnv/dotenv plugins

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Files:**
| File | Status | Description |
|---|---|---|
| `home/dot_zsh_aliases.tmpl` | Modified | Replace `claude` alias with `yolo`; add 23 chezmoi OMZ-style aliases; add `fly` alias; add `op plugin` alias at bottom |
| `home/dot_zshrc.tmpl` | Modified | Add `direnv` + `dotenv` OMZ plugins; add `WORKSPACE` env var |

**Rationale:** Both files are shell environment configuration. The aliases and zshrc are commonly edited together — all changes represent "shell customization."

**Note:** The chezmoi aliases follow the OMZ convention designed in `docs/plans/2026-02-27-chezmoi-aliases-design.md`.

---

### Commit 5: Packages and Java tooling
- [x] **Committed** — `425ada8`

**Message:**
```
Add bats-core package and Temurin JDK 24 to install scripts

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Files:**
| File | Status | Description |
|---|---|---|
| `home/.chezmoidata/packages.toml` | Modified | Add `bats-core` formula; fix trailing comma on `meetingbar` |
| `home/.chezmoiscripts/run_onchange_before_12_install_java.sh.tmpl` | Modified | Add `asdf install java temurin-24.0.2+12` |

**Rationale:** Both are "add new dev tools" — a Homebrew formula and a JDK version. Logically one "update dev tooling" change.

---

### Commit 6: CLAUDE.md template updates
- [x] **Committed** — `78214e5`

**Message:**
```
Update CLAUDE.md: add About Me, 1Password docs, auth guidance, Python CLI tools

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Files:**
| File | Status | Description |
|---|---|---|
| `home/dot_claude/CLAUDE.md.tmpl` | Modified | Add "About Me" section; add 1Password CLI plugin docs; add gh auth error guidance; add Python CLI tools PEP 723 reference; minor whitespace fixes |

**Rationale:** Single file with multiple additions syncing the CLAUDE.md template with the locally deployed version.

---

### Commit 7: Claude Code plugins and settings
- [x] **Committed** — `08cb3ec`

**Message:**
```
Sync Claude Code plugin config and settings

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Files:**
| File | Status | Description |
|---|---|---|
| `home/dot_claude/settings.json` | Modified | Add `enabledPlugins` block (10 plugins), `alwaysThinkingEnabled`, `skipDangerousModePermissionPrompt` |
| `home/dot_claude/plugins/known_marketplaces.json` | New | Plugin marketplace registry (6 marketplaces) |
| `home/dot_claude/plugins/private_installed_plugins.json` | New | Installed plugins manifest (10 plugins) |

**Rationale:** All three files are the Claude Code plugin ecosystem — marketplaces define sources, installed_plugins tracks what's installed, settings controls what's enabled.

---

### Commit 8: Improve existing Claude slash commands
- [x] **Committed** — `b16d935` (2 files; 4 others already in upstream)

**Message:**
```
Improve Claude commands: recommended tags, file naming, tool permissions

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Files:**
| File | Status | Description |
|---|---|---|
| `home/dot_claude/commands/clarify.md` | Modified | Add section headers; add `(Recommended)` tags to example options |
| `home/dot_claude/commands/dev/approve-plan.md` | Modified | Reorder filename: `task_name-timestamp` instead of `timestamp-task_name` |
| `home/dot_claude/commands/dev/create-prd.md` | Modified | Wrap variables in code block; fix filename vars; add recommended option tags |
| `home/dot_claude/commands/dev/generate-tasks.md` | Modified | Fix `$filePrefix` variable extraction from PRD filename |
| `home/dot_claude/commands/git/wt_switch.md` | Modified | Remove unused `Repository name` context line |
| `home/dot_claude/commands/pr/review.md` | Modified | Update `allowed-tools`; replace `jq` piping with `--jq` flag; remove redundant current-branch-PR context |

**Rationale:** All are incremental improvements to existing Claude slash commands sharing consistent patterns (recommended tags, file naming convention, tool permissions).

---

### Commit 9: Add new Claude commands and agent
- [x] **Committed** — `f9470d9`

**Message:**
```
Add PR respond command, docs explain command, and code-implementation agent

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Files:**
| File | Status | Description |
|---|---|---|
| `home/dot_claude/commands/pr/respond.md` | New | Interactive PR comment response system with code changes and reply posting |
| `home/dot_claude/commands/docs/analyze/explain.md` | New | 10-agent parallel technical explanation command |
| `home/dot_claude/agents/code-implementation-expert.md` | New | Sonnet-based agent for code implementation tasks |

**Rationale:** All are new Claude Code extensibility additions — two new commands and one new agent definition. Grouped as "new Claude capabilities."

---

### Commit 10: Add git-add-intellij-remote utility script
- [x] **Committed** — `6349d6f`

**Message:**
```
Add git-add-intellij-remote script for IntelliJ HTTPS remote setup

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Files:**
| File | Status | Description |
|---|---|---|
| `home/dot_local/bin/executable_git-add-intellij-remote` | New | Bash script: adds a read-only `intellij` remote using HTTPS URL derived from SSH origin |

**Rationale:** Standalone utility script. Self-contained tool with no dependencies on other changes.

---

## Execution Order

Commits are ordered so dependencies come first:

1. **1Password plugin** — foundational credential config
2. **SSH config** — identity setup (may reference 1Password agent from commit 1)
3. **Ghostty config** — standalone terminal config
4. **Shell environment** — references op plugin alias from commit 1
5. **Packages/Java** — standalone tooling
6. **CLAUDE.md** — references 1Password patterns from commit 1
7. **Claude plugins/settings** — standalone
8. **Improve Claude commands** — modifies existing files
9. **New Claude commands/agent** — adds new files (after existing commands cleaned up in 8)
10. **git-add-intellij-remote** — standalone utility

## Post-Commit Cleanup

- [ ] Add `.DS_Store`, `.idea/` to `.gitignore`
- [ ] Decide: keep or delete `demo.gif`
- [ ] Decide: keep or delete `fix-zsh-java-init-conversation.md`
- [ ] Decide: keep or delete `chezmoi_diff.txt`
- [ ] Decide: commit `docs/plans/` directory
