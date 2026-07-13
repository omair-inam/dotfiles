#!/usr/bin/env bash
# Self-check for statusline.d scripts. Run: bash ~/.claude/statusline.d/test_statusline_d.sh
set -u
d=$(cd "$(dirname "$0")" && pwd)
fails=0
check() {
    if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: expected [$2] got [$3]"; fails=$((fails+1)); fi
}
payload() { printf '{"cwd":"%s","workspace":{"current_dir":"%s"}}' "$1" "$1"; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

repo="$tmp/myrepo"
git init -q -b main "$repo"
git -C "$repo" -c user.email=t@t -c user.name=t commit -q --allow-empty -m x
git -C "$repo" worktree add -q -b iai-1-fix "$repo/.worktrees/iai-1-fix"
git -C "$repo" worktree add -q -b feature/other "$repo/.worktrees/wt2"

# --- whereami.sh ---
check "main checkout"          "myrepo main"                 "$(payload "$repo" | bash "$d/whereami.sh")"
check "worktree, branch==name" "myrepo⧸iai-1-fix"            "$(payload "$repo/.worktrees/iai-1-fix" | bash "$d/whereami.sh")"
check "worktree, branch diff"  "myrepo⧸wt2 feature/other"    "$(payload "$repo/.worktrees/wt2" | bash "$d/whereami.sh")"
check "non-git dir"            "$(basename "$tmp")"          "$(payload "$tmp" | bash "$d/whereami.sh")"
check "empty payload"          ""                            "$(printf '{}' | bash "$d/whereami.sh")"

[ "$fails" -eq 0 ] && echo "ALL OK" || { echo "$fails failing"; exit 1; }
