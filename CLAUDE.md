## Chezmoi Dotfiles Repository

### How This Repo Works
* This is a chezmoi source directory for macOS dotfiles
* `chezmoi apply` renders templates, runs scripts, and installs files to `~/`
* Three template variables control device configuration:
  - `.personal_device` (bool) — personal apps/configs
  - `.work_device` (bool) — work apps/configs (DNAstack)
  - `.email` (string) — user email
* These are set in `home/.chezmoi.toml.tmpl` via `promptBool`/`promptStringOnce`

### Repository Structure
* `home/` — chezmoi source dir; maps to `~/`
* `home/.chezmoidata/` — TOML data files auto-loaded into template context
* `home/.chezmoiscripts/` — scripts run by `chezmoi apply`
* `home/dot_*` → `~/.*`, `private_dot_*` → `~/.*` (mode 0600)
* `.tmpl` suffix — Go template files rendered by chezmoi
* `home/dot_claude/` — Claude Code global config (commands, agents, CLAUDE.md.tmpl)
* `home/dot_config/` — app configs (ghostty, lnav, 1password)
* `home/dot_local/bin/` — custom executable scripts
* `home/dot_ssh/` — SSH config and public keys
* `docs/` — planning documents
* `migration-kit-backup/` — pre-wipe migration audit trail (local-only, gitignored — contains sensitive Keychain/repo audits; never commit to this public repo)

### Key Data Files
* `home/.chezmoidata/packages.toml` — Homebrew formulae, casks, taps, Mac App Store apps
  - Consumed by `run_onchange_before_10_install-packages.sh.tmpl`
  - Split into `common`, `work`, `personal`; merged based on device flags

### Script Execution Order
Scripts in `home/.chezmoiscripts/` run in alphabetical order within each phase:
* **`run_before_`** — runs every `chezmoi apply` (environment-dependent logic)
* **`run_onchange_before_`** — runs only when rendered content changes (idempotent config)
* **`run_after_`** — runs every `chezmoi apply`, after file updates (restart services)

Current scripts:
* `run_before_00_bootstrap` — Xcode CLT, Rosetta 2, Homebrew, Oh My Zsh + plugins (all guarded, idempotent)
* `run_before_00_dock_position` — Dock orientation by monitor count; restarts Dock only on change
* `run_before_10_install-claude-code-native` — Claude Code native installer
* `run_onchange_before_01_mac_setup` — Dock tile size, scroll direction, hotkeys; restarts Dock/Finder/SystemUIServer
* `run_onchange_before_10_install-packages` — Homebrew taps + `brew bundle` (common + device-specific)
* `run_onchange_before_14_*`, `15_*`, `16_*` — cached jwt, op, gh completions
* `run_onchange_after_11_install_tools` — `mise install` for everything in `dot_config/mise/config.toml.tmpl`. An `after` script, because a `before` script runs before chezmoi writes `~/.config/mise/config.toml` and installs nothing on a fresh machine
* `run_onchange_after_14_install_chrome_for_testing` — Chrome for Testing via `mise exec node -- pnpm` (needs node from 11)

`sudo` never appears in a script. Anything that needs it is a manual step in `README.md`.

### Template Conventions
* `{{ if .work_device }}` / `{{ if .personal_device }}` gate sections
* `concat`, `sortAlpha`, `uniq` — merge and deduplicate lists
* `promptBool`, `promptStringOnce` — user prompts (cached after first run)
* `{{- }}` trims whitespace; `{{ $var := ... }}` for local variables
* Data accessed as `.packages.*`, `.email`, `.chezmoi.os`

### Key Managed Files
* `dot_zshrc.tmpl` — main shell config (Oh-My-Zsh, Powerlevel10k, mise, fzf)
* `dot_zsh_aliases.tmpl` — aliases: chezmoi (`cm*`), kubernetes (`k*`), 1Password gh plugin
* `dot_zsh_aliases.tmpl` — Claude Code model aliases: `cch/ccs/cco` (model shortcuts), `yoloh/yolos/yoloo` (dangerous + model), `cca/ccah/ccas/ccao` (auto-mode + model)
* `dot_gitconfig.tmpl` — git config with 1Password SSH signing, Beyond Compare merge tool
* `dot_m2/settings.xml.tmpl` — Maven settings pinned to HTTPS Maven Central

### Editing Workflow
* Edit files here (chezmoi source dir), NOT in `~/` directly
* After editing: prompt user to run `chezmoi apply` or use alias `cma`
* To add an unmanaged file: `chezmoi add ~/path/to/file`
* Aliases file: `home/dot_zsh_aliases.tmpl` — follow existing Oh-My-Zsh naming convention

### Gotchas
* Interactive `gh` goes through the 1Password plugin alias. Non-interactive shells get `GH_TOKEN` for the `omair-inam` account from `.envrc`, which reads it with a 1Password service account token stored in the Keychain. Git ignores `GH_TOKEN`, so push over HTTPS with `git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push`
* Git commits are SSH-signed through the 1Password agent. `Couldn't find key in agent?` does not mean 1Password is locked. It means `SSH_AUTH_SOCK` points at the empty launchd agent. Set it to `$HOME/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock` and rerun.
* `run_onchange` scripts re-run when template *output* changes, not just source edits
* Use `run_before_`/`run_after_` (not `run_onchange_`) for scripts that depend on runtime environment (e.g., monitor count)
* chezmoi source is available locally at `/Users/omair/libs/chezmoi` for reference
* `chezmoi apply/diff` always uses the configured source dir, not `$PWD` — in git worktrees, use `--source=<worktree>/home` or the `cmaw`/`cmdw` aliases
