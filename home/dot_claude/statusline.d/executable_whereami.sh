#!/usr/bin/env bash
# Session identity: repo⧸worktree [branch-if-differs] | repo branch | dir basename
input=$(cat)
dir=$(printf '%s' "$input" | jq -r '.workspace.current_dir // .cwd // empty')
[ -n "$dir" ] || exit 0
if ! top=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null); then
    printf '%s' "$(basename "$dir")"
    exit 0
fi
gitdir=$(git -C "$dir" rev-parse --absolute-git-dir)
common=$(git -C "$dir" rev-parse --path-format=absolute --git-common-dir)
branch=$(git -C "$dir" branch --show-current)
name=$(basename "$top")
if [ "$gitdir" != "$common" ]; then
    # linked worktree: common dir is <main-repo>/.git
    repo=$(basename "$(dirname "$common")")
    out="${repo}⧸${name}"
    [ -n "$branch" ] && [ "$branch" != "$name" ] && out="$out $branch"
else
    [ -n "$branch" ] || branch=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null)
    out="$name $branch"
fi
printf '%s' "$out"
