#!/bin/bash

set -eufo pipefail

# Position dock based on number of active monitors
# - left when only one display is connected (maximize horizontal space)
# - bottom when multiple displays are connected (centered across screens)
display_count=$(system_profiler SPDisplaysDataType | grep -c "Online: Yes")
if [ "$display_count" -gt 1 ]; then
  want=bottom
else
  want=left
fi

current=$(defaults read com.apple.dock orientation 2>/dev/null || echo "")
if [ "$current" != "$want" ]; then
  defaults write com.apple.dock orientation -string "$want"
  killall Dock
fi
