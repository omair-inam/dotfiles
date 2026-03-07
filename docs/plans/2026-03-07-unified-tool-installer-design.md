# Unified Global Tool Installer via mise

**Date:** 2026-03-07
**Status:** Approved

## Problem

Global dev tools are installed by three separate chezmoi scripts using different mechanisms:
- Script 11: `uv tool` for Python CLIs
- Script 12: `mise use -g` for Java runtimes
- Script 13: `mise use -g` for Python runtime

Adding new tools (npm packages, Go binaries, GitHub releases) has no established pattern. There is no unified, data-driven way to declare and install global tools across ecosystems.

## Solution

Replace all three scripts with a single system: chezmoi templates mise's native config file (`~/.config/mise/config.toml`), and a single install script runs `mise install` to install everything declared.

## Design

### Mise Config Template

`home/dot_config/mise/config.toml.tmpl` — chezmoi manages mise's native config directly.

```toml
[tools]
node = "lts"
"npm:@anthropic-ai/claude-code" = "latest"
"pipx:showboat" = "latest"
"pipx:rodney" = "latest"
python = "3.13"

{{ if .work_device -}}
"npm:@arizeai/phoenix-cli" = "latest"
java = ["temurin-24", "temurin-21"]
{{ end -}}

[settings]
trusted_config_paths = ["."]
```

Device-specific tools use chezmoi `{{ if }}` conditionals. No custom data file needed — mise's config is the data layer.

### Supported Backends

| Backend | Syntax | Use case |
|---------|--------|----------|
| `core` | `node = "lts"` | Runtimes (node, java, python) |
| `npm` | `"npm:package" = "latest"` | npm packages |
| `pipx` | `"pipx:package" = "latest"` | Python CLI tools (uses uv if available) |
| `go` | `"go:pkg/path" = "latest"` | Go packages |
| `github` | `"github:owner/repo" = "latest"` | GitHub release binaries |

The `ubi` backend is deprecated; use `github` instead.

### Version Pinning

Versions default to `"latest"`. Pin when needed:
- `node = "lts"` or `node = "24"`
- `java = ["temurin-24", "temurin-21"]` for multiple versions
- `"npm:prettier" = "3.1.0"` for specific version

### Install Script

`home/.chezmoiscripts/run_onchange_before_11_install_tools.sh.tmpl`:

```bash
#!/bin/bash
set -eufo pipefail

if [[ -f /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Bootstrap node (required by npm backend)
mise install node
# Install all tools declared in config
mise install
```

Two-step install: node first (npm backend dependency), then everything else. `mise install` runs in parallel by default. The `run_onchange` trigger re-runs when the rendered config changes.

### Node Runtime

Node is declared in the config as a tool but exists solely as an npm backend dependency. It is not intended for direct use.

## Migration

### Created
- `home/dot_config/mise/config.toml.tmpl`
- `home/.chezmoiscripts/run_onchange_before_11_install_tools.sh.tmpl`

### Deleted
- `home/.chezmoiscripts/run_onchange_before_11_install_python.sh.tmpl` (uv tool setup)
- `home/.chezmoiscripts/run_onchange_before_12_install_java.sh.tmpl` (mise java)
- `home/.chezmoiscripts/run_onchange_before_13_install_python.tmpl` (mise python)

### Modified
- `home/.chezmoiscripts/run_onchange_before_14_install_chrome_for_testing.sh.tmpl` — remove `mise install node@lts` and `mise exec node@lts --` wrapper; call `pnpm dlx @puppeteer/browsers install chrome@stable` directly (node is now globally available after script 11)

### Unchanged
- Script 10 (Homebrew packages)
- Scripts 14+ (completions caching)
- `packages.toml`
- `dot_zshrc.tmpl`

## Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Tool manager | mise | Already installed, supports all ecosystems |
| Data layer | mise native config (templated) | Eliminates custom data file; `mise install` reads it directly |
| Device filtering | chezmoi `{{ if }}` blocks | Simpler than sectioned data file with merge logic |
| Version strategy | Optional pinning, default `"latest"` | Most tools want latest; pin when needed |
| Node declaration | Explicit in config | Required by npm backend; visible and intentional |
| Python CLIs | pipx backend (via uv) | Consolidates uv tool management into mise |
| GitHub binaries | `github:` backend | `ubi:` is deprecated |
| Chrome for Testing | Separate script, simplified | Different concern (browser binary download, not a dev tool) |
