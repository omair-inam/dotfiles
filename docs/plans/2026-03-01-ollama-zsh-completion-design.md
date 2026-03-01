# Ollama ZSH Completion Design

**Date:** 2026-03-01
**Goal:** Add tab completion for the `ollama` CLI with zero shell startup cost.

---

## Context

Ollama (v0.17.4) has no built-in `completion` subcommand. A community-maintained ZSH completion script exists at [obeone/gist](https://gist.github.com/obeone/9313811fd61a7cbb843e0001a4434c58) that provides subcommand, flag, and dynamic model name completion.

The dotfiles already have `~/.zsh_completions/` in `fpath` (line 24 of `.zshrc`) with three script-generated completions (`_gh`, `_jwt`, `_op`). ZSH discovers completion files lazily, so adding a file to `fpath` costs nothing at startup.

## Approach

**Chezmoi-managed source file.** Add the completion script directly to the chezmoi source directory. Chezmoi deploys it alongside other managed dotfiles.

Alternatives considered and rejected:
- **Download script from gist:** Adds network dependency to `chezmoi apply`; gist URL could break. The existing `_gh`/`_jwt`/`_op` scripts generate from local binaries, not remote URLs.
- **Built-in `ollama completion`:** Does not exist as of v0.17.4.

## Changes

### 1. Add completion file

**New file:** `home/dot_zsh_completions/_ollama`

Import the gist completion script. Chezmoi maps this to `~/.zsh_completions/_ollama`.

**What it completes:**
- Subcommands: `serve`, `create`, `show`, `run`, `pull`, `push`, `list`, `cp`, `rm`, `help`
- Flags per subcommand (e.g., `--host`, `--timeout`)
- Dynamic model names via `ollama list` (for `show`, `run`, `pull`, `push`, `cp`, `rm`)

**Dynamic model lookup:** `_fetch_ollama_models()` runs `ollama list 2>/dev/null` at tab-complete time (not at startup). When the server is down, model completion returns nothing; subcommand and flag completion still work.

### 2. No `.zshrc` changes

`fpath=(~/.zsh_completions $fpath)` already exists. No plugins to add, no `source` lines, no `eval` calls.

## Startup Impact

**Zero.** ZSH loads completion functions lazily from `fpath` on first tab-complete, not at shell initialization.

## Verification

```zsh
# After chezmoi apply:
ollama <TAB>        # should list subcommands
ollama run <TAB>    # should list locally available models
ollama serve -<TAB> # should list flags
```
