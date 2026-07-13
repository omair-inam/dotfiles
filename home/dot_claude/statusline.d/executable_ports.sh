#!/usr/bin/env bash
# Dev-server ports from this worktree's .ports / .ports.adk (see repo Makefiles)
input=$(cat)
dir=$(printf '%s' "$input" | jq -r '.workspace.current_dir // .cwd // empty')
[ -n "$dir" ] || exit 0
top=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) || top=$dir
out=""
if [ -r "$top/.ports" ]; then
    be=$(sed -n 's/^BACKEND_PORT=//p' "$top/.ports" | tr -d '"')
    fe=$(sed -n 's/^FRONTEND_PORT=//p' "$top/.ports" | tr -d '"')
    [ -n "$be" ] && out="be:$be"
    [ -n "$fe" ] && out="$out${out:+ }fe:$fe"
fi
if [ -r "$top/.ports.adk" ]; then
    adk=$(sed -n 's/^ADK_WEB_PORT=//p' "$top/.ports.adk" | tr -d '"')
    [ -n "$adk" ] && out="$out${out:+ }adk:$adk"
fi
printf '%s' "$out"
