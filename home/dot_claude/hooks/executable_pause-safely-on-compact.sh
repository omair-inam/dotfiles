#!/bin/sh
# PreCompact and SessionStart(compact) hook: run pstack's pause-safely playbook
# before a compaction, then point the compacted session at the resume note.
#
# PreCompact hooks cannot add context for Claude, so the playbook runs in a
# headless `claude -p` that reads the conversation from the transcript. The
# SessionStart hook that fires after compaction hands Claude the note's path.
#
# Every failure exits 1: Claude Code shows stderr and compaction still runs.
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"

[ -n "$PAUSE_SAFELY_HOOK" ] && exit 0
command -v jq >/dev/null 2>&1 || { echo "pause-safely: jq not found" >&2; exit 1; }

input=$(cat)
field() { printf '%s' "$input" | jq -r ".$1 // empty"; }
session_id=$(field session_id)
[ -n "$session_id" ] || { echo "pause-safely: no session_id in hook input" >&2; exit 1; }

dir=/tmp/claude-resume
note="$dir/$session_id.md"

case "$(field hook_event_name)" in
SessionStart)
  [ -s "$note" ] || exit 0
  echo "Before this compaction, the pstack pause-safely playbook wrote a resume note for this session at $note. It records the intent, progress, verified state, next steps, key files, and gotchas from before the compaction."
  exit 0
  ;;
PreCompact) ;;
*) exit 0 ;;
esac

playbook=$(ls -d "$HOME"/.claude/plugins/cache/cursor-plugins/pstack/*/skills/poteto-mode/playbooks/pause-safely.md 2>/dev/null | sort -V | tail -1)
[ -n "$playbook" ] || { echo "pause-safely: pstack playbook not found" >&2; exit 1; }
transcript=$(field transcript_path)
[ -r "$transcript" ] || { echo "pause-safely: cannot read transcript $transcript" >&2; exit 1; }
cwd=$(field cwd)
cd "${cwd:-.}" || exit 1

mkdir -p "$dir"
rm -f "$note"
excerpt="$dir/$session_id.transcript.md"
# Since the last compaction (its summary included): user text, assistant text,
# and one line per tool call. Tool results and thinking are dropped to fit.
jq -rs '
  (map(.type == "system" and .subtype == "compact_boundary") | indices(true) | last // -1) as $b
  | .[($b + 1):][]
  | select((.type == "user" or .type == "assistant") and (.isSidechain | not) and (.isMeta | not))
  | .type as $who
  | (.message.content | if type == "string" then [{type: "text", text: .}] else . end)[]
  | if .type == "text" then "\n## \($who)\n\(.text)"
    elif .type == "tool_use" then "- tool \(.name): \(.input | tojson | .[0:300])"
    else empty end
' "$transcript" | tail -c 600000 > "$excerpt" || { echo "pause-safely: transcript extraction failed" >&2; exit 1; }

prompt="Claude Code session $session_id, working in $cwd, is about to be compacted (trigger: $(field trigger)). Its conversation since the last compaction is in $excerpt, oldest first. Read it in parts.

Read the pause-safely playbook at $playbook and follow it on that session's behalf. The session is idle between turns, so step 1 is already met and there are no subagents to cancel. Write the resume note to $note, replacing any older one. If the current branch is the repository's default branch, or a commit fails, do not commit. List the uncommitted files in the note instead.

Reply with one line naming the note path and any commit you made."

PAUSE_SAFELY_HOOK=1 claude -p "$prompt" \
  --model opus \
  --setting-sources project,local \
  --permission-mode dontAsk \
  --allowedTools Read Write Glob Grep 'Bash(git:*)' \
  --add-dir "$dir" \
  --no-session-persistence \
  >&2 || { echo "pause-safely: headless claude failed" >&2; exit 1; }

[ -s "$note" ] || { echo "pause-safely: no resume note written to $note" >&2; exit 1; }
