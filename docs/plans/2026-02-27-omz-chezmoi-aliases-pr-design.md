# OMZ Chezmoi Plugin Aliases PR Design

## Context

Add aliases to the existing chezmoi plugin in ohmyzsh/ohmyzsh. The plugin currently only has completion. The PR targets the upstream repo via the user's fork at `omairinam:omair-inam/ohmyzsh.git`.

## Approach

Append 14 aliases to `plugins/chezmoi/chezmoi.plugin.zsh` and update `plugins/chezmoi/README.md`. Follow OMZ conventions: alphabetical sort, `cm` prefix, 3-column README table.

## Alias Set (14 aliases)

| Alias  | Command                | Description                                            |
| :----- | :--------------------- | :----------------------------------------------------- |
| `cm`   | `chezmoi`              | The base chezmoi command                               |
| `cma`  | `chezmoi add`          | Add a file to the source state                         |
| `cmap` | `chezmoi apply`        | Update the destination to match the target state       |
| `cmcd` | `chezmoi cd`           | Launch a shell in the source directory                 |
| `cmd`  | `chezmoi diff`         | Print the diff between target state and destination    |
| `cme`  | `chezmoi edit`         | Edit the source state of a target                      |
| `cmg`  | `chezmoi git`          | Run git in the source directory                        |
| `cmi`  | `chezmoi init`         | Set up the source directory                            |
| `cmia` | `chezmoi init --apply` | Set up the source directory and apply in one step      |
| `cmm`  | `chezmoi merge`        | Three-way merge for a file                             |
| `cmma` | `chezmoi merge-all`    | Three-way merge for all modified files                 |
| `cmra` | `chezmoi re-add`       | Re-add modified files                                  |
| `cmst` | `chezmoi status`       | Show the status of targets                             |
| `cmu`  | `chezmoi update`       | Pull and apply changes from the remote                 |

## Files Changed (in OMZ repo)

1. `plugins/chezmoi/chezmoi.plugin.zsh` — append alias block after completion code
2. `plugins/chezmoi/README.md` — rewrite with alias table

## PR Details

- **Branch:** `feat/chezmoi-aliases`
- **Commit:** `feat(chezmoi): add aliases for common chezmoi commands`
- **Target:** `ohmyzsh/ohmyzsh` `master` branch via fork
- **AI disclosure:** Claude Code assisted with alias design, transparently noted in PR

## Design Decisions

1. **`cm` prefix:** Zero collisions across all OMZ plugins. Clearly evokes "chezmoi."
2. **Conservative set (14 not 25):** Omitted flag variants and maintenance commands per OMZ guidelines favoring broadly useful aliases.
3. **Alphabetical sort by alias name:** Matches git plugin convention.
4. **3-column README table:** Matches molecule plugin format (Alias | Command | Description).
