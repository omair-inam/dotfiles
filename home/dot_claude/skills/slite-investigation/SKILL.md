---
name: slite-investigation
description: Add a new page to, or update an existing page in, the Investigations collection in Slite (Research channel), with a short summary, the collection's fields, and the full HTML report shown inline. Use when Omair asks to publish, upload, add, log, or file an investigation, eval, latency teardown, decision report, or Claude artifact to Slite or to "Investigations", or to update, refresh, or correct an investigation page there.
---

# Slite investigations

Follow the **slite** skill (`~/.claude/skills/slite/SKILL.md`) for every Slite read, edit, and file upload. This skill adds what is specific to the Investigations collection.

## The collection

- [Investigations](https://i-domain.slite.com/app/docs/1y-Q1Oc2p_V9SE), note id `1y-Q1Oc2p_V9SE`, in the Research channel. Each row is one investigation page.
- Read `get-note` with `format: "collection"` before writing fields. It gives the column ids and every existing row.
- **Area** takes one of: Latency, Cost, Model eval, Infrastructure, Agent behavior.
- **Outcome** takes one of: Decided, Shipped, Open, Superseded. Leave it blank when you cannot confirm it.
- **Date** is the date the investigation was about, as `YYYY-MM-DD`.
- **Linear ticket** is the ticket id the report itself names, such as `IAI-2004`. Leave it blank if the report names none. Never guess an id.
- **Source artifact** is the claude.ai artifact URL.
- **Finding** is one or two sentences with the headline number.

A system explainer that describes how something works now, with no question and answer, belongs in the Architecture channel, not here. Say so instead of filing it.

## Page body

```
**Question.** <the question the investigation answered>

**Method.** <optional, one or two sentences>

**Answer.** <the answer>

**Key numbers.**

- <number with its unit and what it measures>

**Status.** <optional: open PRs, decisions still needed>

**Note on the report below.** <only when precheck reported a problem>

**Links.** Linear <a url="https://linear.app/i-ai/issue/IAI-N">IAI-N</a>. PRs <a url="https://github.com/I-AI-Corp/iai-explorer/pull/N">#N</a>. Source <a url="<artifact url>">Claude artifact</a>.

## Full report

<file .../>
```

Use only numbers that appear in the report. Link a related investigation page with `<note-link>`.

## Getting the report

1. Save the artifact's page with the Artifact tool: `action: "read"`, `url`, `path: "index.html"`, and `out_dir` set to a new folder in the scratchpad. This saves the file without loading it into context. If it answers "artifact not found" for an artifact Omair owns, Claude Code is signed in to a different claude.ai account. Ask him to switch accounts or send the HTML file.
2. Pull the question, answer, numbers, ticket ids, and PR numbers from the saved file with `grep` or a tag-stripping script. For a large report, delegate this to a subagent and have it quote the text each ticket id comes from.
3. Run `uv run ~/.claude/skills/slite-investigation/scripts/precheck.py <file>`. Add a "Note on the report below" line for each problem it reports.
4. Leave out a report, or a supporting file it links to, that holds prompt text, trace payloads, or patron data. Ask Omair first if you are unsure.

## Setting Outcome

- Check the ticket with Linear `get_issue` and each PR with `gh pr view <n> --json state`.
- Shipped means the PRs are merged or the ticket is Done for the change the report describes.
- Open means PRs are open, decisions are pending, or the ticket is in progress.
- A Done ticket whose title is about different work does not prove the fix shipped. Leave Outcome blank and say so in the reply.

## Creating a page

1. Read the collection and confirm no row already covers this investigation. If one does, update it instead.
2. `create-note` with `parentNoteId: "1y-Q1Oc2p_V9SE"`, the artifact's title, `fields`, and the body up to and including `## Full report`.
3. Attach the HTML with the slite skill's upload steps, `contentType: "text/html"`, then `append-blocks` the returned `<file>` block.
4. Read the collection again and confirm the row's fields.

## Updating a page

1. Find the row in the collection read, or with `search-notes` and `parentNoteId: "1y-Q1Oc2p_V9SE"`.
2. `get-note` in sliteml for its block ids.
3. Change summary text with `modify-block`. Change fields with `update-note` and `fields` only. Never pass `sliteml` to `update-note` here, because it replaces the whole body.
4. For a newer version of the report, save and precheck it as above, upload it, and `modify-block` the existing `<file>` block's id with the new `<file>` block.
5. Recheck Outcome when tickets or PRs may have moved.

## Reply

Give the page URL, the fields you set, any field left blank and why, and any precheck note. Ask Omair for a screenshot of the page, because the inline report cannot be checked from here.
