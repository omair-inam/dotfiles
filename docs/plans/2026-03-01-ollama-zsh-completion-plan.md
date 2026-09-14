# Ollama ZSH Completion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add tab completion for the `ollama` CLI via a chezmoi-managed completion file with zero startup cost.

**Architecture:** Drop a `_ollama` ZSH completion file into the chezmoi source directory at `home/dot_zsh_completions/_ollama`. Chezmoi deploys it to `~/.zsh_completions/_ollama`, which is already in `fpath`. No `.zshrc` changes needed.

**Tech Stack:** ZSH completion system, chezmoi

**Design doc:** `docs/plans/2026-03-01-ollama-zsh-completion-design.md`

---

### Task 1: Create the completion file

**Files:**
- Create: `home/dot_zsh_completions/_ollama`

**Step 1: Create the directory and file**

Create `home/dot_zsh_completions/_ollama` with the following content (sourced from [obeone's gist](https://gist.github.com/obeone/9313811fd61a7cbb843e0001a4434c58), MIT licensed):

```zsh
#compdef ollama

# Ollama ZSH completion
# Source: https://gist.github.com/obeone/9313811fd61a7cbb843e0001a4434c58
# License: MIT
# Principal contributions by ChatGPT ZSH Expert and obeone.

# Function to fetch and return model names from 'ollama list'
_fetch_ollama_models() {
    local -a models
    local output="$(ollama list 2>/dev/null | sed 's/:/\\:/g')"
    if [[ -z "$output" ]]; then
        _message "no models available or 'ollama list' failed"
        return 1
    fi
    models=("${(@f)$(echo "$output" | awk 'NR>1 {print $1}')}")
    if [[ ${#models} -eq 0 ]]; then
        _message "no models found"
        return 1
    fi
    _describe 'model names' models
}

# Main completion function
_ollama() {
    local -a commands

    _arguments -C \
        '1: :->command' \
        '*:: :->args'

    case $state in
        command)
            commands=(
                'serve:Start ollama'
                'create:Create a model from a Modelfile'
                'show:Show information for a model'
                'run:Run a model'
                'pull:Pull a model from a registry'
                'push:Push a model to a registry'
                'list:List models'
                'cp:Copy a model'
                'rm:Remove a model'
                'help:Help about any command'
            )
            _describe -t commands 'ollama command' commands
        ;;
        args)
            case $words[1] in
                serve)
                    _arguments \
                        '--host[Specify the host and port]:host and port:' \
                        '--origins[Set allowed origins]:origins:' \
                        '--models[Path to the models directory]:path:_directories' \
                        '--keep-alive[Duration to keep models in memory]:duration:'
                ;;
                create)
                    _arguments \
                        '-f+[Specify the file name]:file:_files'
                ;;
                show)
                    _arguments \
                        '--license[Show license of a model]' \
                        '--modelfile[Show Modelfile of a model]' \
                        '--parameters[Show parameters of a model]' \
                        '--system[Show system message of a model]' \
                        '--template[Show template of a model]' \
                        '*::model:->model'
                    if [[ $state == model ]]; then
                        _fetch_ollama_models
                    fi
                ;;
                run)
                    _arguments \
                        '--format[Specify the response format]:format:' \
                        '--insecure[Use an insecure registry]' \
                        '--nowordwrap[Disable word wrap]' \
                        '--verbose[Show verbose output]' \
                        '*::model and prompt:->model_and_prompt'
                    if [[ $state == model_and_prompt ]]; then
                        _fetch_ollama_models
                        _message "enter prompt"
                    fi
                ;;
                pull|push)
                    _arguments \
                        '--insecure[Use an insecure registry]' \
                        '*::model:->model'
                    if [[ $state == model ]]; then
                        _fetch_ollama_models
                    fi
                ;;
                list)
                    _message "no additional arguments for list"
                ;;
                cp)
                    _arguments \
                        '1:source model:_fetch_ollama_models' \
                        '2:target model:_fetch_ollama_models'
                ;;
                rm)
                    _arguments \
                        '*::models:->models'
                    if [[ $state == models ]]; then
                        _fetch_ollama_models
                    fi
                ;;
                help)
                    _message "no additional arguments for help"
                ;;
            esac
        ;;
    esac
}

_ollama
```

**Step 2: Verify chezmoi sees the new file**

Run: `chezmoi managed | grep ollama`
Expected: `home/dot_zsh_completions/_ollama` appears in output (or `.zsh_completions/_ollama`)

**Step 3: Dry-run chezmoi apply**

Run: `chezmoi diff`
Expected: Shows `_ollama` as a new file to be created at `~/.zsh_completions/_ollama`

**Step 4: Apply**

Run: `chezmoi apply -v`
Expected: `~/.zsh_completions/_ollama` is created

**Step 5: Verify the file is deployed**

Run: `ls -la ~/.zsh_completions/_ollama`
Expected: File exists with correct content

**Step 6: Commit**

```bash
git add home/dot_zsh_completions/_ollama
git commit -m "feat(zsh): add Ollama tab completion

Chezmoi-managed ZSH completion for the ollama CLI. Completes
subcommands, flags, and dynamic model names (via ollama list).
Zero shell startup cost — loaded lazily on first tab-complete.

Source: https://gist.github.com/obeone/9313811fd61a7cbb843e0001a4434c58"
```

### Task 2: Manual verification in a fresh shell

**Step 1: Open a new terminal tab/window**

This ensures the completion system picks up the new file from `fpath`.

**Step 2: Test subcommand completion**

Type: `ollama ` then press Tab
Expected: List of subcommands (`serve`, `create`, `show`, `run`, `pull`, `push`, `list`, `cp`, `rm`, `help`)

**Step 3: Test flag completion**

Type: `ollama serve --` then press Tab
Expected: List of flags (`--host`, `--origins`, `--models`, `--keep-alive`)

**Step 4: Test dynamic model completion**

Type: `ollama run ` then press Tab
Expected: List of locally available models (from `ollama list`)

**Step 5: Verify startup time is unaffected**

Run: `time zsh -i -c exit`
Expected: No regression from baseline (should be well under 500ms per optimization design)
