#!/usr/bin/env bash
# glob the version dir so a ponytail upgrade doesn't silently drop the badge
for pt in "$HOME"/.claude/plugins/cache/ponytail/ponytail/*/hooks/ponytail-statusline.sh; do
    [ -f "$pt" ] || continue
    badge=$(bash "$pt")
    [ -n "$badge" ] && printf '%s' "$badge"
done
exit 0
