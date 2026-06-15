---
name: promptsmith
description: Turn a one-off prompt into a reusable, robust one. Use when the user wants to "make this prompt generic/reusable", "use this every day/week/Monday", "improve this prompt", or "turn this into a skill/recurring task". Applies relative dates, a verification Gate for prerequisites, enumerate-don't-assume, and a constrained output spec.
---

# promptsmith — make a prompt reusable & robust

Take a single-use prompt and generalize it so it runs correctly every time.

## Transformations

1. **Relative, not absolute dates.** Replace fixed dates with relatives —
   "yesterday", "the most recent Friday", "the last 7 days up to today". This is
   the single biggest reusability lever; it also handles holidays/long weekends.
2. **Add a Gate for hard prerequisites.** Rules are guidance; a **gate demands
   proof of passage**. Add a Step-0 that verifies required access/state with an
   *observable* check (run the command, show output) and STOPs with remediation
   if it fails. **Gate only the true dependencies** — match the gate's weight to
   what the task actually needs; an over-broad gate trains the user to click past
   it. (See: Rules and Gates, blog.fsck.com/2026/04/07/rules-and-gates/.)
3. **Enumerate, don't assume.** If the task targets "the meetings this week" or
   "my open PRs", instruct it to list and select, not assume a fixed count or id.
4. **Constrain the output, not just the input.** Replace "show me X" with the
   shape you want: a prioritized shortlist, lead with #1, one line of why + any
   blocker. This forces triage instead of a dump.
5. **Bake in tool gotchas** discovered in use (e.g. pipe `2>/dev/null` for `gws`;
   notes vs transcript live in separate doc tabs).
6. **Add a mode/argument** if one prompt should serve several variants
   (e.g. `daily | weekly | monday`) — pass the variant as an argument rather than
   maintaining near-duplicate prompts.

## Output

- Return the rewritten prompt in a code block.
- Add a short **what-changed** table (original → improved, with the why).
- If the user wants it permanent, offer to persist it: a recurring task, or a
  skill via `superpowers:writing-skills` / `skill-creator`. (If it touches
  dotfiles, author it under chezmoi, not directly in `~`.)
