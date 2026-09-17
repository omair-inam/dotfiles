---
name: pr-watch
description: Manually-started loop that tends my open GitHub PRs in the current repo. When a PR flips Draft to Ready, runs unslop on prose surfaces and /code-review with fixes, then keeps CI green, addresses review comments, and resolves conflicts until merge. Re-fires itself via ScheduleWakeup.
---

# pr-watch

You are one pass of a standing loop. Do the pass, then schedule the next
wakeup (or stop). The tending itself follows poteto-mode's Babysit playbook
(`pstack:poteto-mode`, `playbooks/babysit.md`); this skill owns only the state
file and the pacing. Design spec:
`docs/superpowers/specs/2026-07-13-pr-watch-loop-design.md` (iv-living-archive).

## How to start

The standing loop is started with `/loop /pr-watch` (no interval — dynamic
mode gives this skill ScheduleWakeup for self-pacing). A bare `/pr-watch`
is a single pass: run it normally but do not schedule a wakeup; instead end
by telling the user to start `/loop /pr-watch` if they want the standing
loop. `dry-run` and `stop` are one-shots either way.

## Arguments

- _(none)_ — normal pass.
- `dry-run` — perform every read, report every action you WOULD take, write
  nothing (no commits, pushes, `gh pr edit`, or state-file writes), and do
  not schedule a wakeup.
- `stop` — call `ScheduleWakeup` with `stop: true`, confirm to the user, end.

## State

File: `~/.claude/pr-watch/<owner>-<repo>.json`. Derive owner/repo from
`gh repo view --json owner,name -q '.owner.login + "-" + .name'`.
`mkdir -p ~/.claude/pr-watch` if missing. Schema, keyed by PR number:

```json
{
  "742": {
    "lastSeenSha": "abc123",
    "readyPipelineRanAtSha": "abc123",
    "lastReviewCommentId": 987654,
    "lastCiConclusion": "success",
    "parkedPush": false
  }
}
```

The file answers one question: has the loop handled this before? Live PR
state comes from GitHub on each pass.

## Each pass

1. Read the state file (missing file = empty state).
2. One listing call:
   `gh pr list --author "@me" --state open --json number,isDraft,headRefOid,headRefName,title,body,url,mergeable,mergeStateStatus,reviewDecision`
   (do NOT request `statusCheckRollup` — the 1Password `gh` token lacks
   Checks read scope and the whole call degrades into GraphQL errors).
   For CI status on Ready PRs, per PR:
   - `gh run list --branch <headRefName> --json name,status,conclusion,headSha`
     and keep only rows where `headSha` == the PR's `headRefOid` (Actions CI);
   - `gh api repos/{owner}/{repo}/commits/<headRefOid>/status -q .state`
     (external statuses: Terrateam, previews).
3. Zero open PRs → narrate that, `ScheduleWakeup` with `stop: true`, end.
4. **First run** (no state file): baseline. Record every current PR in
   state as-is (Ready PRs get `readyPipelineRanAtSha` = current SHA so the
   pipeline does NOT fire on pre-existing Ready PRs). Then run incremental
   care on every Ready PR and report what it found.
5. **Draft → Ready transition** (state says draft or no
   `readyPipelineRanAtSha`; GitHub says not draft): run the Ready pipeline.
6. **Already-Ready PRs**: run incremental care.
7. Update state, narrate a short summary, schedule the next wakeup
   (see Pacing).

## Ready pipeline (once per PR, keyed by head SHA)

1. **Isolate.** `git fetch origin` then
   `git worktree add .worktrees/<headRefName> <headRefName>` (reuse if it
   exists). Run `direnv allow` there if `.envrc` exists.
2. **unslop, prose only.** Invoke the unslop skill; apply it to the PR
   title, PR body, and changed `.md` files in the diff. Code files are out
   of scope. Update title/body via `gh pr edit`. unslop rewrites rather than
   scores, so keep edits conservative here: fix the tells it names and leave
   the author's phrasing otherwise. Its rule-26 word ban does not apply to
   this codebase's real vocabulary (`substrate`, `surface`, `harness`,
   `scaffolding`, `primitive` name actual modules). Narrate every prose
   change you push.
3. **/code-review** on the diff vs `origin/main`. Fix CONFIRMED findings.
   Skip speculative ones.
4. **Diff hygiene.** `git diff origin/main --stat`. Flag files unrelated to
   the PR's task in your narration. Never remove them yourself.
5. **Metadata.** Title contains a Linear ID (`IAI-NN`); body contains
   `Closes IAI-NN` and the AI-assistance header blockquote. Fix what you
   can infer via `gh pr edit`; flag what you can't.
6. **Commit and push, once.** The pre-commit hook runs the tests. On a
   1Password/Touch ID failure: set `parkedPush: true`, tell the user, and
   do NOT retry until they confirm — then retry once.
7. Record `readyPipelineRanAtSha` = the head SHA you just pushed (or the
   SHA you reviewed, if there was nothing to fix).

## Incremental care (already-Ready PRs, every pass)

- `parkedPush` is true and the user has since confirmed → retry the push
  once.
- CI red (a failed Actions run for the head SHA, or commit status
  `failure`) → `gh run view <id> --log-failed`, fix the root cause in the
  worktree, commit, push.
- Review comments with id > `lastReviewCommentId` → address in code where
  warranted; reply via `gh api repos/{owner}/{repo}/pulls/{n}/comments/{id}/replies`
  with the AI-assistance header.
- `mergeable: CONFLICTING` or `mergeStateStatus: BEHIND` → merge
  `origin/main` into the branch. Merge, never rebase.
- Merged or closed → drop from state; `git worktree remove` if the tree is
  clean.

## Hard limits

- Never force-push. Never push to main. Never delete flagged unrelated
  files. Never re-run the full ready pipeline on ordinary new commits.
- Never launch `/code-review ultra` (user-billed). For a diff over ~800
  changed lines, run the ordinary review anyway and note the size in the report.
- At most one fix-push per PR per pass.
- On any 1Password auth failure, follow the parked-push protocol above —
  no auth retry loops.

## Pacing

Always `ScheduleWakeup` with `prompt: "/pr-watch"` and a reason naming the
specific wait:

| Waiting on | Delay | Example reason |
|---|---|---|
| CI running on a push this loop made | ~480s | "CI running on #742 after fix push" |
| Open PRs, all quiet | 1200–1800s | "3 PRs open, all quiet; next sweep in 25m" |

## Narration

End every pass with a short summary: what you found, pushed, parked, or
flagged. A quiet pass gets one line.
