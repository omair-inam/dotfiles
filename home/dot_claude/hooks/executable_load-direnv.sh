#!/bin/sh
# SessionStart hook: load this checkout's .envrc into the Claude Code session.
#
# Claude's Bash tool runs non-interactive shells, so the direnv shell hook never
# fires and .envrc (service-account token, gh shim, IAI_GH_DIRECT) is skipped.
# `direnv export` runs the real direnv stdlib and emits quoted `export` lines,
# which $CLAUDE_ENV_FILE applies to every later Bash call.
#
# Every early exit is 0: engineers without direnv, without an allowed .envrc, or
# without a service-account token keep exactly today's behaviour (interactive
# 1Password prompts) — nothing new fails.
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

[ -n "$CLAUDE_ENV_FILE" ] || exit 0
# Global and project settings may both register this hook; the second run finds
# the first one's output and skips the three op calls.
grep -q '^export DIRENV_DIR=' "$CLAUDE_ENV_FILE" 2>/dev/null && exit 0
command -v direnv >/dev/null 2>&1 || exit 0
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
[ -f .envrc ] || exit 0

# Not yet `direnv allow`ed: say so once instead of silently doing nothing.
if ! direnv status 2>/dev/null | grep -q 'Found RC allowed 0'; then
  echo "direnv: .envrc not allowed — run 'direnv allow' to load repo env into Claude sessions" >&2
  exit 0
fi

out=$(direnv export bash 2>/dev/null) || exit 0
[ -n "$out" ] && printf '%s\n' "$out" >> "$CLAUDE_ENV_FILE"
exit 0
