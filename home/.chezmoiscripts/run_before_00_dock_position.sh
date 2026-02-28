#!/bin/bash

set -eufo pipefail

# Position dock based on number of active monitors
# - left when only one display is connected (maximize horizontal space)
# - bottom when multiple displays are connected (centered across screens)
display_count=$(system_profiler SPDisplaysDataType | grep -c "Online: Yes")
if [ "$display_count" -gt 1 ]; then
  defaults write com.apple.dock orientation -string bottom
else
  defaults write com.apple.dock orientation -string left
fi
