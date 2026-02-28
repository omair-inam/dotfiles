# Replace asdf with mise for runtime version management

## Problem

The dotfiles use two runtime managers: `asdf` (Java, Python) and `mise` (Node.js via script 14). This split is confusing and redundant. mise is a faster, single-binary replacement that already handles Node.js in this repo. asdf should be removed entirely.

## Decision

Migrate all asdf-managed runtimes (Java, Python) to mise and remove every trace of asdf from the codebase. Replace the p10k `asdf` prompt segment with a custom `mise` segment based on the dagadbm community implementation.

## Scope

### Files changed

| File | Action |
|---|---|
| `home/.chezmoidata/packages.toml` | Remove `"asdf"` from common formulae |
| `home/dot_zshrc.tmpl` | Replace `asdf` with `mise` in OMZ plugins; remove manual `eval "$(mise activate zsh)"` block (plugin handles it); remove `export JAVA_HOME=$(asdf where java 2>/dev/null)`; remove stale pipx comment |
| `home/dot_p10k.zsh` | Remove `asdf` segment + ~140 lines of `POWERLEVEL9K_ASDF_*` config; add ~30-line `prompt_mise()` custom segment with per-tool colors |
| `home/.chezmoiscripts/run_onchange_before_12_install_java.sh.tmpl` | Replace `asdf plugin add java` / `asdf install java` with `mise install` / `mise use -g` |
| `home/.chezmoiscripts/run_onchange_before_13_install_python.tmpl` | Replace `asdf plugin/install/set` with `mise use -g python@3.13` |
| `CLAUDE.md` | Update script descriptions and zshrc description |
| `README.md` | Change "via asdf" to "via mise" |

### Not in scope

- macOS `/usr/libexec/java_home` symlinks (IntelliJ handles its own JDK discovery)
- Migrating any other tools to mise beyond Java and Python

## Script 12: Java install

Before:
```bash
asdf plugin add java
asdf install java adoptopenjdk-21.0.5+11.0.LTS
asdf install java temurin-24.0.2+12
```

After:
```bash
mise install java@adoptopenjdk-21
mise install java@temurin-24
mise use -g java@temurin-24
```

Both JDKs are installed; temurin-24 is set as the global default. `mise use -g` writes to `~/.config/mise/config.toml`.

## Script 13: Python install

Before:
```bash
asdf plugin add python
asdf install python 3.13.1
asdf set python 3.13.1
```

After:
```bash
mise use -g python@3.13
```

`mise use -g` installs and sets the global in one command. mise resolves `3.13` to the latest patch.

## zshrc changes

- **Plugins list**: `asdf` → `mise`. The mise OMZ plugin runs `eval "$(mise activate zsh)"` and sets up tab completions, so the manual activation block is removed.
- **JAVA_HOME**: The `export JAVA_HOME=$(asdf where java 2>/dev/null)` line is removed. mise's `activate` hook sets JAVA_HOME automatically when it detects a Java installation.
- **Stale pipx comment**: `# Created by pipx on 2024-06-23` removed (pipx was replaced by uv in a previous commit).

## p10k changes

**Removed**: `asdf` segment from `POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS` and the entire `POWERLEVEL9K_ASDF_*` configuration block (~140 lines, 572-710).

**Added**: Custom `prompt_mise()` function (based on dagadbm/dotfiles), appended before the closing brace of the p10k config. The function:

1. Calls `mise ls --local` to list project-level tool versions
2. Parses tool name + version from the output
3. Renders each tool as a p10k segment with per-tool foreground colors
4. Only shows versions for tools that have p10k icons defined

The final line substitutes `asdf` with `mise` in the right prompt elements array:
```zsh
typeset -g POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=("${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[@]/asdf/mise}")
```

Color scheme matches the previous asdf config (Ruby: 168, Python: 37, Go: 37, Node: 70, Java: 32, etc.).

Display is **local-only**: versions appear only when a project has a `.tool-versions` or `mise.toml` file.

## Alternatives considered

1. **Individual `*_version` segments**: Use p10k's built-in `java_version`, `node_version`, etc. Simpler but no Python version display and less unified.
2. **Hybrid (keep asdf for prompt)**: Install both tools — confusing, defeats the migration purpose.

## References

- [mise Java docs](https://mise.jdx.dev/lang/java.html)
- [mise OMZ plugin](https://github.com/ohmyzsh/ohmyzsh/blob/master/plugins/mise/mise.plugin.zsh)
- [p10k mise discussion](https://github.com/romkatv/powerlevel10k/issues/2212)
- [dagadbm p10k.mise.zsh](https://github.com/dagadbm/dotfiles/blob/master/zsh/p10k.mise.zsh)
