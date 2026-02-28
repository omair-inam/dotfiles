# Oh-My-Zsh Plugin Survey

**Date:** 2026-02-28

Survey of available Oh-My-Zsh plugins cross-referenced against installed
packages (`packages.toml`) and current plugin list (`dot_zshrc.tmpl`).

---

## Current Plugins (30)

| Plugin | Type | Matching Package |
|--------|------|------------------|
| `asdf` | built-in | `asdf` formula (swapped to `mise` — see cleanup notes) |
| `aws` | built-in | No matching package in packages.toml |
| `gcloud` | built-in | `gcloud-cli` work cask |
| `git` | built-in | Core tool |
| `forgit` | custom | Git interactive tool |
| `alias-tips` | custom | Shows alias hints |
| `zsh-autosuggestions` | custom | Fish-like suggestions |
| `zsh-completions` | custom | Extra completions |
| `zsh-eza` | custom | eza integration |
| `zsh-history-substring-search` | custom | History search |
| `kubectl` | built-in | `kubernetes-cli` work formula |
| `colored-man-pages` | built-in | General utility |
| `bgnotify` | built-in | Background task notifier |
| `copyfile` | built-in | Copy file contents to clipboard |
| `copybuffer` | built-in | Ctrl-O copies command |
| `copypath` | built-in | Copy working dir to clipboard |
| `dircycle` | built-in | Ctrl-Shift-Left/Right cycles dirs |
| `docker` | built-in | `docker` work formula |
| `docker-compose` | built-in | Docker Compose |
| `forklift` | built-in | `forklift3` cask |
| `httpie` | built-in | **No matching package** |
| `sudo` | built-in | Esc-Esc prepends sudo |
| `sfdx` | built-in | **No matching package** |
| `sublime` | built-in | **No matching package** |
| `vscode` | built-in | `visual-studio-code` cask |
| `zsh-interactive-cd` | built-in | fzf-powered cd |
| `python` | built-in | `python@3.13` formula |
| `zoxide` | built-in | `zoxide` formula |
| `direnv` | built-in | `direnv` formula |
| `dotenv` | built-in | Auto-loads .env files |

### Cleanup Candidates

These plugins have no matching package in `packages.toml`:

- **`httpie`** — HTTPie CLI not installed; remove or install the tool
- **`sfdx`** — Salesforce DX CLI not installed; remove
- **`sublime`** — Sublime Text not in casks; remove (VS Code is primary editor)
- **`asdf`** — already swapped to `mise` plugin in zshrc

---

## Recommended Additions

### Tier 1 — High Value (direct match to installed tools)

| Plugin | Matching Package | What It Provides |
|--------|-----------------|------------------|
| **`chezmoi`** | `chezmoi` formula | Completions + aliases (`chz apply`, `chz edit`, etc.) |
| **`gh`** | `gh` formula | Completions for GitHub CLI |
| **`mise`** | `mise` formula | Tab completions for runtime manager (already added) |
| **`brew`** | Homebrew (core) | Completions + aliases (`bubo` = update+outdated, `bubc` = upgrade+cleanup) |
| **`macos`** | macOS native | `ofd` (open Finder here), `tab` (new terminal tab), `pfd`, `quick-look`, `trash` |
| **`1password`** | `1password-cli` cask | Completions for `op` CLI |
| **`uv`** | `uv` formula | Completions for the Python package manager |
| **`fzf`** | `fzf` formula | Replaces manual `source <(fzf --zsh)` + adds keybindings/completions |
| **`helm`** | `helm` work formula | Completions for Kubernetes package manager |
| **`kubectx`** | `kubectx` work formula | Aliases: `kctx` = kubectx, `kns` = kubens |
| **`mvn`** | `maven` formula | Completions for Maven goals and lifecycle phases |

### Tier 2 — Useful Utilities (general productivity)

| Plugin | What It Provides |
|--------|------------------|
| **`extract`** | Universal `x` command — extracts tar.gz, zip, 7z, rar without remembering flags |
| **`encode64`** | `e64` / `d64` for base64 encode/decode — handy for JWT/API work |
| **`jsontools`** | `pp_json` (pretty-print), `is_json` (validate), `urlencode_json` — complements jq |
| **`urltools`** | `urlencode` / `urldecode` — useful for web/API work |
| **`aliases`** | `als` command to list all active aliases |
| **`alias-finder`** | Suggests existing aliases when you type full commands (overlaps with custom alias-tips) |
| **`gitignore`** | `gi python,java,node` generates .gitignore from gitignore.io |
| **`web-search`** | `google "query"`, `github "query"` from terminal (currently commented out in zshrc) |

### Tier 3 — Conditional / Work-Specific

These should be gated with `{{ if .work_device }}` in the template.

| Plugin | Matching Package | What It Provides |
|--------|-----------------|------------------|
| **`azure`** | `azure-cli` work formula | Completions for `az` commands |
| **`k9s`** | `k9s` work formula | Aliases for Kubernetes TUI |
| **`tailscale`** | `tailscale` formula | Completions for VPN commands |
| **`golang`** | `go` formula | Aliases: `gob` = go build, `got` = go test, `gog` = go get |
| **`yarn`** | `yarn` formula | Aliases: `ya` = yarn add, `yb` = yarn build |
| **`nmap`** | `nmap` formula | Aliases for common scan types |
| **`rclone`** | `rclone` formula | Completions for cloud sync |
| **`postgres`** | `postgresql@14` formula | Aliases: `pgstart`, `pgstop`, `pgrestart` |
| **`eza`** | `eza` formula | Built-in eza aliases (may overlap with custom zsh-eza plugin) |
| **`tldr`** | `tealdeer` formula | Completions for tldr/tealdeer |

### Tier 4 — Nice to Have

| Plugin | What It Provides |
|--------|------------------|
| **`isodate`** | `isodate`, `isodate_utc` — date formatting shortcuts |
| **`common-aliases`** | Predefined aliases for ls, grep, find |
| **`history`** | `h` = history, `hs` = history \| grep |
| **`git-auto-fetch`** | Auto-fetches remotes every 60s in git repos |
| **`fancy-ctrl-z`** | Ctrl-Z toggles foreground/background (press again to `fg`) |

---

## Notes

- **Startup time:** Each plugin adds ~5-50ms. Powerlevel10k instant prompt mitigates
  perceived delay, but keep the list lean.
- **`fzf` plugin vs manual source:** The `fzf` OMZ plugin does the same as
  `source <(fzf --zsh)` on line 200 of zshrc. Using the plugin would be cleaner.
- **`eza` vs `zsh-eza`:** The built-in `eza` plugin may overlap with the custom
  `zsh-eza` plugin. Compare aliases before enabling both.
- **`alias-finder` vs `alias-tips`:** Both suggest aliases — `alias-tips` is custom
  and more feature-rich. No need for both.
- **Work-gated plugins:** `helm`, `kubectx`, `azure`, `k9s`, `docker`, `docker-compose`,
  `kubectl`, `gcloud` should ideally be inside `{{ if .work_device }}` blocks.
