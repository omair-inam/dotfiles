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
* `migration-kit-backup/` — pre-wipe migration audit trail

### Key Data Files
* `home/.chezmoidata/packages.toml` — Homebrew formulae, casks, taps, Mac App Store apps
  - Consumed by `run_onchange_before_10_install-packages.sh.tmpl`
  - Split into `common`, `work`, `personal`; merged based on device flags
* `home/.chezmoidata/onepassword.toml` — 1Password secret references
  - e.g., `secrets.github.tokens.maven_settings = "op://Employee/Github PAT/credential"`
  - Used in `private_dot_npmrc.tmpl` and `dot_m2/settings.xml.tmpl` via `onepasswordRead`

### Script Execution Order
Scripts in `home/.chezmoiscripts/` run in numbered order, all `run_onchange_before`:
* `01_mac_setup` — Dock prefs, NVM dir, macOS updates (work only)
* `10_install-packages` — Homebrew taps + `brew bundle` (common + device-specific)
* `11_install_python` — pipx, poetry
* `12_install_java` — asdf java plugin, JDK 21/24 (work only)
* `13_install_python` — asdf python plugin, Python 3.13.1 (work only)

### Template Conventions
* `{{ if .work_device }}` / `{{ if .personal_device }}` gate sections
* `concat`, `sortAlpha`, `uniq` — merge and deduplicate lists
* `onepasswordRead` — fetch secrets from 1Password
* `promptBool`, `promptStringOnce` — user prompts (cached after first run)
* `{{- }}` trims whitespace; `{{ $var := ... }}` for local variables
* Data accessed as `.packages.*`, `.secrets.*`, `.email`, `.chezmoi.os`

### Key Managed Files
* `dot_zshrc.tmpl` — main shell config (Oh-My-Zsh, Powerlevel10k, asdf, nvm, pyenv, fzf)
* `dot_zsh_aliases.tmpl` — aliases: chezmoi (`cm*`), kubernetes (`k*`), 1Password gh plugin
* `dot_zsh_claude_code_functions.tmpl` — `ccs` (suggest), `cce` (explain), `ccef` (explain failure)
* `dot_gitconfig.tmpl` — git config with 1Password SSH signing, Beyond Compare merge tool
* `private_dot_npmrc.tmpl` — NPM config with 1Password-sourced GitHub token
* `dot_m2/settings.xml.tmpl` — Maven settings with GitHub packages (work only)

### Editing Workflow
* Edit files here (chezmoi source dir), NOT in `~/` directly
* After editing: prompt user to run `chezmoi apply` or use alias `cma`
* To add an unmanaged file: `chezmoi add ~/path/to/file`
* Aliases file: `home/dot_zsh_aliases.tmpl` — follow existing Oh-My-Zsh naming convention

### Gotchas
* `home/.chezmoiignore` excludes `key.txt.age` from apply
* 1Password must be unlocked for templates using `onepasswordRead` to render
* `gh` CLI requires 1Password plugin alias; scripts need `GITHUB_TOKEN=$(op plugin run -- gh auth token)`
* Git commits are GPG-signed via 1Password SSH — signing failures may mean 1Password is locked
* `run_onchange` scripts re-run when template *output* changes, not just source edits
