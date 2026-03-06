#!/usr/bin/env uv run
import json
import re
import sys

# Block git commit commands that disable GPG signing.
# Commits in this environment are signed via 1Password SSH;
# bypassing signing is never intentional.
BLOCK_PATTERNS = [
    (
        r"--no-gpg-sign",
        "Unsigned commits are not allowed. Remove --no-gpg-sign to sign via 1Password SSH.",
    ),
    (
        r"-c\s+commit\.gpgsign=false",
        "Unsigned commits are not allowed. Remove -c commit.gpgsign=false to sign via 1Password SSH.",
    ),
]


def strip_message_content(cmd: str) -> str:
    """Remove commit message content so flags inside messages don't false-positive.

    Strips:
    - Heredoc bodies (<<'EOF' ... EOF  or  <<EOF ... EOF)
    - Inline -m "..." or -m '...' arguments
    """
    # Strip heredoc bodies (content between <<'DELIM' or <<DELIM and the delimiter)
    cmd = re.sub(r"<<'?(\w+)'?.*?\n.*?\1", "", cmd, flags=re.DOTALL)
    # Strip -m "..." (double-quoted message)
    cmd = re.sub(r'''-m\s+"[^"]*"''', "-m MSG", cmd)
    # Strip -m '...' (single-quoted message)
    cmd = re.sub(r"""-m\s+'[^']*'""", "-m MSG", cmd)
    return cmd


try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
command = tool_input.get("command", "")

# Only inspect Bash commands containing "git commit" (or "git ... commit")
if tool_name != "Bash" or not command or not re.search(r"\bgit\b.*\bcommit\b", command):
    sys.exit(0)

# Strip message content to avoid false positives from flags mentioned in commit messages
command_flags = strip_message_content(command)

# Check for signing bypass attempts
for pattern, message in BLOCK_PATTERNS:
    if re.search(pattern, command_flags):
        print(f"BLOCKED: {message}", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
