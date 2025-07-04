#!/bin/bash

# PreToolUse hook to enforce ripgrep usage instead of Glob and Grep

# Read the tool name from the arguments passed by Claude Code
TOOL_NAME="$3"

# Check if the tool is Glob or Grep
if [[ "$TOOL_NAME" == "Glob" ]] || [[ "$TOOL_NAME" == "Grep" ]]; then
    # Return JSON response to block the tool and provide feedback
    cat <<EOF
{
  "approved": false,
  "feedback": "⚠️  Tool '$TOOL_NAME' is blocked by policy. Please use ripgrep (rg) via the Bash tool instead.\n\nExamples:\n- For file pattern matching: Use 'rg --files | rg <pattern>' via Bash\n- For content search: Use 'rg <pattern>' via Bash\n- For advanced searches: Use 'rg -i <pattern>' (case-insensitive), 'rg -l <pattern>' (files only), etc.\n\nRipgrep is faster and more efficient than Glob/Grep tools."
}
EOF
    exit 0
fi

# If it's not Glob or Grep, allow the tool to proceed
echo '{"approved": true}'
exit 0