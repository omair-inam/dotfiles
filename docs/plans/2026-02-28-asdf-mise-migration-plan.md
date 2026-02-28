# asdf → mise Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove asdf entirely and replace it with mise for all runtime version management (Java, Python, Node.js).

**Architecture:** mise is already activated in `.zshrc` and manages Node.js. This plan migrates Java and Python to mise, removes all asdf traces, and replaces the p10k `asdf` prompt segment with a custom `mise` segment.

**Tech Stack:** chezmoi templates, zsh, Powerlevel10k, mise, Oh-My-Zsh

**Design doc:** `docs/plans/2026-02-28-asdf-mise-migration-design.md`

---

### Task 1: Rewrite Java install script to use mise

**Files:**
- Modify: `home/.chezmoiscripts/run_onchange_before_12_install_java.sh.tmpl`

**Step 1: Replace asdf commands with mise equivalents**

Replace lines 10-15 (the asdf plugin add + install block) with:

```bash
# install JDK 21 and JDK 24
mise install java@adoptopenjdk-21
mise install java@temurin-24

# set temurin-24 as the global default
mise use -g java@temurin-24
```

The full file should become:

```bash
#!/bin/bash
{{ if .work_device }}
set -eufo pipefail

# Add Homebrew to PATH for the current session (required on Apple Silicon)
if [[ -f /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# install JDK 21 and JDK 24
mise install java@adoptopenjdk-21
mise install java@temurin-24

# set temurin-24 as the global default
mise use -g java@temurin-24

{{ end }}
```

**Step 2: Verify**

Run: `grep -n asdf home/.chezmoiscripts/run_onchange_before_12_install_java.sh.tmpl`
Expected: No output (no asdf references remain)

**Step 3: Commit**

```
git add home/.chezmoiscripts/run_onchange_before_12_install_java.sh.tmpl
git commit -m "Migrate Java install script from asdf to mise"
```

---

### Task 2: Rewrite Python install script to use mise

**Files:**
- Modify: `home/.chezmoiscripts/run_onchange_before_13_install_python.tmpl`

**Step 1: Replace asdf commands with a single mise command**

Replace lines 10-15 (the asdf plugin add + install + set block) with:

```bash
# install and set Python 3.13 as global default
mise use -g python@3.13
```

The full file should become:

```bash
#!/bin/bash
{{ if .work_device }}
set -eufo pipefail

# Add Homebrew to PATH for the current session (required on Apple Silicon)
if [[ -f /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# install and set Python 3.13 as global default
mise use -g python@3.13

{{ end }}
```

**Step 2: Verify**

Run: `grep -n asdf home/.chezmoiscripts/run_onchange_before_13_install_python.tmpl`
Expected: No output (no asdf references remain)

**Step 3: Commit**

```
git add home/.chezmoiscripts/run_onchange_before_13_install_python.tmpl
git commit -m "Migrate Python install script from asdf to mise"
```

---

### Task 3: Remove asdf from Homebrew packages

**Files:**
- Modify: `home/.chezmoidata/packages.toml:52`

**Step 1: Delete the asdf formula line**

Remove this exact line (line 52):
```toml
            "asdf",                        # Version manager for multiple languages
```

**Step 2: Verify**

Run: `grep -n asdf home/.chezmoidata/packages.toml`
Expected: No output

**Step 3: Commit**

```
git add home/.chezmoidata/packages.toml
git commit -m "Remove asdf from Homebrew formulae"
```

---

### Task 4: Update zshrc — replace asdf plugin with mise, clean up

**Files:**
- Modify: `home/dot_zshrc.tmpl`

Four changes in this file, all independent:

**Step 1: Remove manual mise activation block (lines 27-28)**

Delete these two lines:
```
### mise — polyglot runtime manager
eval "$(mise activate zsh)"
```

The mise OMZ plugin (added in step 2) handles activation and also provides tab completions.

**Step 2: Replace `asdf` with `mise` in plugins list (line 108)**

Change:
```
  asdf
```
to:
```
  mise
```

**Step 3: Remove JAVA_HOME export (line 214)**

Delete this line:
```
export JAVA_HOME=$(asdf where java 2>/dev/null)
```

mise's `activate` hook sets JAVA_HOME automatically.

**Step 4: Remove stale pipx comment (line 221)**

Delete this line:
```
# Created by `pipx` on 2024-06-23 20:44:40
```

Keep the `export PATH="$PATH:$HOME/.local/bin"` line below it — uv uses that path.

**Step 5: Verify**

Run: `grep -n asdf home/dot_zshrc.tmpl`
Expected: No output

Run: `grep -n 'mise activate' home/dot_zshrc.tmpl`
Expected: No output (plugin handles it now)

Run: `grep -n 'mise' home/dot_zshrc.tmpl`
Expected: One match — the `mise` plugin in the plugins list

**Step 6: Commit**

```
git add home/dot_zshrc.tmpl
git commit -m "Replace asdf OMZ plugin with mise, remove manual activation and JAVA_HOME"
```

---

### Task 5: Update p10k — remove asdf segment and config, add mise segment

**Files:**
- Modify: `home/dot_p10k.zsh`

Three changes:

**Step 1: Replace `asdf` with `mise` in the right prompt elements (line 53)**

Change:
```
    asdf                    # asdf version manager (https://github.com/asdf-vm/asdf)
```
to:
```
    mise                    # mise runtime versions (https://mise.jdx.dev)
```

**Step 2: Remove the entire POWERLEVEL9K_ASDF_* config block (lines 572-710)**

Delete everything from:
```
  ###############[ asdf: asdf version manager (https://github.com/asdf-vm/asdf) ]###############
```
through to (and including):
```
  # typeset -g POWERLEVEL9K_ASDF_JULIA_SHOW_ON_UPGLOB='*.foo|*.bar'
```

This is approximately 140 lines. The next section after it starts with:
```
  ##########[ nordvpn: nordvpn connection status, linux only (https://nordvpn.com/) ]###########
```

**Step 3: Add the custom prompt_mise() function and colors**

Insert the following block at line 1649 (after the "User-defined prompt segments" comment block, before the "Transient prompt" section). Specifically, insert after:
```
  # typeset -g POWERLEVEL9K_EXAMPLE_VISUAL_IDENTIFIER_EXPANSION='⭐'
```

and before:
```
  # Transient prompt works similarly to the builtin transient_rprompt option.
```

Insert this block:

```zsh
  ###############[ mise: mise runtime versions (https://mise.jdx.dev) ]###############
  function prompt_mise() {
    local plugins=("${(@f)$(mise ls --local 2>/dev/null | awk '!/\(symlink\)/ && $3!="~/.tool-versions" && $3!="~/.config/mise/config.toml" {print $1, $2}')}")
    local plugin
    for plugin in ${(k)plugins}; do
      local parts=("${(@s/ /)plugin}")
      local tool=${(U)parts[1]}
      local version=${parts[2]}

      local icon_var="POWERLEVEL9K_${tool}_ICON"
      if [[ -n "${(P)icon_var}" ]] || [[ -n "${icons[${tool}_ICON]}" ]]; then
        p10k segment -r -i "${tool}_ICON" -s $tool -t "$version"
      fi
    done
  }

  typeset -g POWERLEVEL9K_MISE_FOREGROUND=66
  typeset -g POWERLEVEL9K_MISE_RUBY_FOREGROUND=168
  typeset -g POWERLEVEL9K_MISE_PYTHON_FOREGROUND=37
  typeset -g POWERLEVEL9K_MISE_GOLANG_FOREGROUND=37
  typeset -g POWERLEVEL9K_MISE_NODEJS_FOREGROUND=70
  typeset -g POWERLEVEL9K_MISE_RUST_FOREGROUND=37
  typeset -g POWERLEVEL9K_MISE_DOTNET_CORE_FOREGROUND=134
  typeset -g POWERLEVEL9K_MISE_FLUTTER_FOREGROUND=38
  typeset -g POWERLEVEL9K_MISE_LUA_FOREGROUND=32
  typeset -g POWERLEVEL9K_MISE_JAVA_FOREGROUND=32
  typeset -g POWERLEVEL9K_MISE_PERL_FOREGROUND=67
  typeset -g POWERLEVEL9K_MISE_ERLANG_FOREGROUND=125
  typeset -g POWERLEVEL9K_MISE_ELIXIR_FOREGROUND=129
  typeset -g POWERLEVEL9K_MISE_POSTGRES_FOREGROUND=31
  typeset -g POWERLEVEL9K_MISE_PHP_FOREGROUND=99
  typeset -g POWERLEVEL9K_MISE_HASKELL_FOREGROUND=172
  typeset -g POWERLEVEL9K_MISE_JULIA_FOREGROUND=70
```

**Step 4: Verify**

Run: `grep -n asdf home/dot_p10k.zsh`
Expected: No output

Run: `grep -n 'prompt_mise\|MISE' home/dot_p10k.zsh`
Expected: Multiple matches — the new function and color definitions

**Step 5: Commit**

```
git add home/dot_p10k.zsh
git commit -m "Replace p10k asdf segment with custom mise prompt segment"
```

---

### Task 6: Update documentation

**Files:**
- Modify: `CLAUDE.md`
- Modify: `README.md`

**Step 1: Update CLAUDE.md script descriptions**

Line 35 — change:
```
* `01_mac_setup` — Dock prefs, NVM dir, macOS updates (work only)
```
to:
```
* `01_mac_setup` — Dock prefs, macOS updates (work only)
```

Line 37 — change:
```
* `11_install_python` — pipx, poetry
```
to:
```
* `11_install_python` — uv tool management
```

Line 38 — change:
```
* `12_install_java` — asdf java plugin, JDK 21/24 (work only)
```
to:
```
* `12_install_java` — mise java, JDK 21/24 (work only)
```

Line 39 — change:
```
* `13_install_python` — asdf python plugin, Python 3.13.1 (work only)
```
to:
```
* `13_install_python` — mise python, Python 3.13 (work only)
```

Line 50 — change:
```
* `dot_zshrc.tmpl` — main shell config (Oh-My-Zsh, Powerlevel10k, asdf, nvm, pyenv, fzf)
```
to:
```
* `dot_zshrc.tmpl` — main shell config (Oh-My-Zsh, Powerlevel10k, mise, fzf)
```

**Step 2: Update README.md**

Line 72 — change:
```
- For work devices: enable automatic macOS updates, install Java 21 + 24 and Python 3.13.1 via asdf
```
to:
```
- For work devices: enable automatic macOS updates, install Java 21 + 24 and Python 3.13 via mise
```

Line 71 — change:
```
- Install pipx
```
to:
```
- Configure uv tool management
```

**Step 3: Verify**

Run: `grep -rn asdf CLAUDE.md README.md`
Expected: No output

**Step 4: Commit**

```
git add CLAUDE.md README.md
git commit -m "Update docs: replace asdf/pipx references with mise/uv"
```

---

### Task 7: Final verification

**Step 1: Full-codebase asdf audit**

Run: `grep -rn 'asdf\|ASDF' --include='*.tmpl' --include='*.toml' --include='*.zsh' --include='*.md' .`

Expected: Only matches in:
- `docs/plans/` (design/plan documents — these are historical records, leave them)
- `migration-kit-backup/` (archive — leave it)
- `.worktrees/` (stale worktree — leave it)

No matches in `home/`, `CLAUDE.md`, or `README.md`.

**Step 2: Verify commit log**

Run: `git log --oneline -6`

Expected: 6 new commits in order:
1. Migrate Java install script from asdf to mise
2. Migrate Python install script from asdf to mise
3. Remove asdf from Homebrew formulae
4. Replace asdf OMZ plugin with mise, remove manual activation and JAVA_HOME
5. Replace p10k asdf segment with custom mise prompt segment
6. Update docs: replace asdf/pipx references with mise/uv
