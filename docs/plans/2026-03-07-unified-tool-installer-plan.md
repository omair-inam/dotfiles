# Unified Tool Installer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace three fragmented install scripts with a single mise-based system driven by a chezmoi-templated mise config.

**Architecture:** Chezmoi templates mise's native `~/.config/mise/config.toml` with device-conditional tool declarations. A single `run_onchange` script runs `mise install` to install everything. Three old scripts are deleted.

**Tech Stack:** chezmoi (Go templates), mise, bash

---

### Task 1: Create the mise config template

**Files:**
- Create: `home/dot_config/mise/config.toml.tmpl`

**Step 1: Create the directory structure**

Run: `ls home/dot_config/` to verify parent exists.

The `mise/` subdirectory does not exist yet in chezmoi source. Chezmoi will create it automatically when the file is written.

**Step 2: Create the mise config template**

Create `home/dot_config/mise/config.toml.tmpl`:

```toml
{{- /* Unified tool management via mise */ -}}
{{- /* See docs/plans/2026-03-07-unified-tool-installer-design.md */ -}}

[tools]
# Node runtime (required by npm backend)
node = "lts"

# npm tools
"npm:@arizeai/phoenix-cli" = "latest"
"npm:@anthropic-ai/claude-code" = "latest"

# Python CLI tools (pipx backend uses uv when available)
"pipx:showboat" = "latest"
"pipx:rodney" = "latest"

{{ if .work_device -}}
# Work runtimes
java = ["temurin-24", "temurin-21"]
python = "3.13"
{{ end -}}

[settings]
trusted_config_paths = ["."]
```

**Step 3: Verify the template renders correctly**

Run: `chezmoi execute-template < home/dot_config/mise/config.toml.tmpl`

Expected: A valid TOML file with `[tools]` and `[settings]` sections. If on a work device, java and python lines appear. No template syntax errors.

**Step 4: Verify chezmoi diff shows the new file**

Run: `chezmoi diff --source-path home`

Expected: The diff shows `~/.config/mise/config.toml` as a new or changed file with the rendered content.

**Step 5: Commit**

```bash
git add home/dot_config/mise/config.toml.tmpl
git commit -m "feat(mise): add unified tool config template

Chezmoi-templated mise config.toml declaring all global tools.
Supports npm, pipx, go, and github backends with device-conditional
tool blocks.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Create the unified install script

**Files:**
- Create: `home/.chezmoiscripts/run_onchange_before_11_install_tools.sh.tmpl`

**Step 1: Create the install script**

Create `home/.chezmoiscripts/run_onchange_before_11_install_tools.sh.tmpl`:

```bash
{{- if (eq .chezmoi.os "darwin") -}}
#!/bin/bash

set -eufo pipefail

# Add Homebrew to PATH for the current session (required on Apple Silicon)
if [[ -f /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# mise config hash (triggers run_onchange when tools change):
# {{ include "dot_config/mise/config.toml.tmpl" | sha256sum }}

# Bootstrap node (required by npm backend before mise install)
mise install node

# Install all tools declared in ~/.config/mise/config.toml
mise install

{{ end }}
```

The `sha256sum` of the config template in the comment ensures this script re-runs whenever the tool list changes — even though the script body itself doesn't change.

**Step 2: Verify the template renders**

Run: `chezmoi execute-template < home/.chezmoiscripts/run_onchange_before_11_install_tools.sh.tmpl`

Expected: A valid bash script with the sha256 hash resolved to a hex string. No template errors.

**Step 3: Commit**

```bash
git add home/.chezmoiscripts/run_onchange_before_11_install_tools.sh.tmpl
git commit -m "feat(mise): add unified tool install script

Single run_onchange script that runs mise install to install all
tools declared in the config template. Bootstraps node first for
npm backend. Re-triggers when config.toml.tmpl content changes.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Delete the old install scripts

**Files:**
- Delete: `home/.chezmoiscripts/run_onchange_before_11_install_python.sh.tmpl`
- Delete: `home/.chezmoiscripts/run_onchange_before_12_install_java.sh.tmpl`
- Delete: `home/.chezmoiscripts/run_onchange_before_13_install_python.tmpl`

**Step 1: Verify the old scripts exist and review their content**

Run: `ls -la home/.chezmoiscripts/run_onchange_before_1[1-3]*`

Expected: Three files listed:
- `run_onchange_before_11_install_python.sh.tmpl` — `uv tool update-shell`
- `run_onchange_before_12_install_java.sh.tmpl` — `mise install java@temurin-21`, `mise install java@temurin-24`, `mise use -g java@temurin-24`
- `run_onchange_before_13_install_python.tmpl` — `mise use -g python@3.13`

Confirm all functionality is covered by the new config template (Task 1).

**Step 2: Delete the scripts**

```bash
git rm home/.chezmoiscripts/run_onchange_before_11_install_python.sh.tmpl
git rm home/.chezmoiscripts/run_onchange_before_12_install_java.sh.tmpl
git rm home/.chezmoiscripts/run_onchange_before_13_install_python.tmpl
```

**Step 3: Commit**

```bash
git commit -m "refactor(mise): remove old tool install scripts

These are replaced by the unified install script (11_install_tools)
and mise config template. Removes:
- 11_install_python (uv tool setup)
- 12_install_java (mise java)
- 13_install_python (mise python)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 4: Simplify the Chrome for Testing script

**Files:**
- Modify: `home/.chezmoiscripts/run_onchange_before_14_install_chrome_for_testing.sh.tmpl`

**Step 1: Read the current script**

Current content (6 lines of logic):

```bash
{{- if (eq .chezmoi.os "darwin") -}}
#!/bin/bash

set -eufo pipefail

if [[ -f /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Install Node.js LTS via mise
mise install node@lts

# Install Chrome for Testing using pnpm dlx
mise exec node@lts -- pnpm dlx @puppeteer/browsers install chrome@stable
{{ end }}
```

**Step 2: Remove the node install and mise exec wrapper**

Node is now globally available after script 11 runs. Replace with:

```bash
{{- if (eq .chezmoi.os "darwin") -}}
#!/bin/bash

set -eufo pipefail

# Add Homebrew to PATH for the current session (required on Apple Silicon)
if [[ -f /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Install Chrome for Testing (node available globally via mise after script 11)
pnpm dlx @puppeteer/browsers install chrome@stable
{{ end }}
```

Changes:
- Remove `mise install node@lts` (handled by script 11)
- Replace `mise exec node@lts -- pnpm dlx` with just `pnpm dlx` (node shims on PATH)

**Step 3: Verify the template renders**

Run: `chezmoi execute-template < home/.chezmoiscripts/run_onchange_before_14_install_chrome_for_testing.sh.tmpl`

Expected: A valid bash script with `pnpm dlx @puppeteer/browsers install chrome@stable` and no mise references.

**Step 4: Commit**

```bash
git add home/.chezmoiscripts/run_onchange_before_14_install_chrome_for_testing.sh.tmpl
git commit -m "refactor(chrome): simplify Chrome for Testing install

Node is now globally available via the unified mise tool installer
(script 11). Remove redundant mise install/exec node wrapper.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 5: Verify end-to-end with chezmoi diff

**Step 1: Run chezmoi diff to review all changes**

Run: `chezmoi diff --source-path home`

Expected:
- `~/.config/mise/config.toml` — new or updated with full tool list
- No references to deleted scripts in the diff
- Chrome for Testing script simplified

**Step 2: Verify no broken template references**

Run: `chezmoi execute-template '{{ .work_device }}' && chezmoi execute-template '{{ .personal_device }}'`

Expected: Both return `true` or `false` without errors — confirms template variables are accessible.

**Step 3: Prompt user to apply**

Tell the user: "Run `chezmoi apply` or `cma` to apply all changes. This will install the mise config and run the new install script."

Do NOT run `chezmoi apply` automatically — let the user decide when to apply.
