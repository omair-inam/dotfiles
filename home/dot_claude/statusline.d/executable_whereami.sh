#!/usr/bin/env bash
# Current directory, $HOME as ~.
input=$(cat)
dir=$(printf '%s' "$input" | jq -r '.workspace.current_dir // .cwd // empty')
[ -n "$dir" ] || exit 0
tilde='~'
printf '%s' "${dir/#$HOME/$tilde}"
