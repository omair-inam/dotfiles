# pstack overrides

Rules that adjust pstack skills without editing the plugin. User instructions outrank skill text, so where these conflict with a skill, these win. Sections are keyed by the skill they adjust. Keep each entry to the rule and the command. Plugin files are never edited and upstream PRs are not an option; a lesson that cannot be written as a rule here does not get applied.

## GitHub status reads (babysit, opening-a-pr, shipping)

The `gh` token from the 1Password plugin is a fine-grained personal access token. GitHub does not grant the Checks permission to that token type at all, whatever the REST docs say (github.com/orgs/community/discussions/129512). Only a GitHub App or a classic PAT can read check runs.

- Never put `statusCheckRollup` in a `gh pr view --json` field list, and never run `gh pr checks`. One denied field fails the whole query.
- Red or green comes from `gh pr view <n> --json mergeStateStatus`. `UNSTABLE` or `BLOCKED` means something is red.
- CI detail comes from the Actions API: `gh run list --branch <branch> --json databaseId,name,status,conclusion,headSha`, then `gh run view <id> --json jobs`, `gh run view <id> --log-failed`, and `gh run watch <id> --exit-status` to block until a run ends.
- Never trust `repos/<o>/<r>/commits/<sha>/status`. It omits GitHub Actions and reports `success` on a commit whose workflow failed.
- Scripts and the pstack watcher do not see the shell function. Check `GH_TOKEN` first: when it is already exported (`I-AI-Corp/iai-explorer`'s `.envrc`, checked out at `~/projects/iv-living-archive`, does this and the SessionStart hook loads it), run `gh` directly with no `op` call. Only when it is unset, run `export GH_TOKEN=$(op plugin run -- gh auth token)` once, never as a per-command prefix.

## babysit

- Before giving the `watch-pr` watcher a PR, confirm the token can see run data with one `gh run list --branch <branch>`. Run the watcher under `timeout 60`. If it prints nothing, use the Actions API commands above; the watcher retries a 403 as if it were transient and hangs.
- A CI failure in code the diff never touched has two causes: a stale base, or drift already merged on trunk. Tell them apart by running the failing check against `origin/main` with the repo's pinned tool version. Trunk drift gets its own PR from `origin/main` in the same session. A stale base gets reported for rebase. Neither gets a retry.

## opening-a-pr

- A pre-commit hook failing on a file the diff never touched means trunk is broken. Fix it in the same session, on its own branch from `origin/main`, as its own PR. Never `--no-verify`. Never hand the diff back to the user as a note to act on.
- Before reporting a PR as opened or updated, read its status once: `gh pr view <n> --json mergeStateStatus` and `gh run list --branch <branch>`. Report red with the reason. "Opening a PR does not start a babysit" governs the loop, not this one read.
- Images in a PR comment or description go through `gh pr comment <n> --body-file <md> --attach <file>` (one `--attach` per image, body references the local path); `gh` uploads to `github.com/user-attachments/` and rewrites the reference, so the image survives the branch being deleted at merge. Never link `raw.githubusercontent.com` (private repo, the proxy cannot read it) or a branch-pinned `blob/` path (404 after merge). After posting, `gh api` the comment and confirm every reference is a `user-attachments` URL before reporting it done.
- Superseding a PR means disarming it, not annotating it: convert the old PR to draft (`gh pr ready <n> --undo`) and remove its `Closes <ticket>` keyword, so whichever PR merges first cannot close the ticket with the refuted change.

## feature

- When the ticket prescribes a mechanism (which component detects, which layer decides) rather than a behavior, treat the naming as a hypothesis. Measure it on a labeled set as a blocking gate before `architect`, and measure at least one component the ticket did not name. A prior PR that built the named mechanism without measuring whether it fires is not evidence.
- In the throughput checkpoint, a new key that crosses a serialization boundary makes the transport layer a blocking first unit, owned by someone, before either side fans out. Grep every site that gates on a sibling key; both halves can be fully green while the feature is dead on screen.
- Verify a measured change against the committed code, not the prototype; a monkeypatched probe number drifts once the schema is real. Measure the negative class as well as the positive one (what the change now does to inputs it should ignore), and replicate before calling a single-run delta noise.

## how

- Before spawning explorers, read the repo's CLAUDE.md skill table and load any repo skill it maps to the paths the change will touch (for iv-living-archive: `iai:agents`, `iai:feature-flags`, `iai:memory-subsystem`, and the rest). The skill carries constraints greps do not surface and costs less than one explorer.

## trunk claims (every skill)

- Before saying trunk lacks something, run `git fetch origin -q` and compare against `origin/main`, never local `main`. Check for an open PR or an unmerged local branch that supplies it before calling it absent.

## create-verification-skill

- Write the generated skill where the host repo keeps its skills. When the repo has a convention (for example real files under `.agents/skills/<name>/` with a symlink from `.claude/skills/`), follow it instead of the skill's default path.
- The proof run in step 4 is performed by a fresh agent that did not write the skill and reads only the skill files. It exercises every helper the skill ships against the real app, not only one mapped feature.
- After editing a skill inside a worktree, confirm the path the loader resolves from the main checkout is the edited copy. Copying a skill directory forks it.

## reflect

- Locate transcripts with a command that survives zsh, where an unmatched glob is a fatal error: `find ~/.claude/projects/<encoded-cwd> -maxdepth 3 -name '*.jsonl' -print0 | xargs -0 ls -t | head -10`. Quote every glob-shaped argument (`--include='*.tsx'`).
- Add a `Scope` column to the synthesizer's Accepted table with one of three values. `local`: a fact about this machine or its accounts, goes to `~/.claude/CLAUDE.md`. `override`: a rule for a pstack skill, goes to this file. `repo`: a fact about the codebase, goes to the project's `CLAUDE.md` or a project skill. Plugin files are not a routing target.
