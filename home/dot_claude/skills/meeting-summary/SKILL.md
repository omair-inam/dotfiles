---
name: meeting-summary
description: Use when given meeting notes, a Google Doc URL, or a raw transcript and asked to produce a summary, action items, next steps, or Linear tickets from a meeting.
---

# Meeting Summary

## Overview

Produces structured meeting summaries from Google Docs, pasted transcripts, or raw notes. Optionally enriches with Slack context. Saves to `docs/notes/YYYY-mm-dd-<name>.md`.

## Workflow

```
1. Fetch source
   └─ Google Doc URL? → invoke gws-docs skill
      └─ Docs often have two tabs: Gemini summary (Tab 1) + raw transcript (Tab 2)
      └─ Read both tabs for full coverage

2. Generate structured summary (sections below)

3. Enrich with Slack (if asked or if Slack links appear in the doc)
   └─ Search by date and attendee usernames
   └─ Add inline links and missing context

4. Save to docs/notes/YYYY-mm-dd-<descriptive-name>.md
   └─ Include link back to source doc in a References section
```

## Standard Output Sections

| Section | Content |
|---------|---------|
| Meeting context | Date, attendees, purpose — as a metadata table |
| Key decisions | Numbered list of what was agreed or resolved |
| Action items | Table: Owner / Deliverable / Deadline |
| Key takeaways | Insights, risks, themes that emerged |
| Open questions | Unresolved items requiring follow-up or owner assignment |
| References | Source doc, related Slack threads/canvases, other links |

**Flag** anything ambiguous, incomplete, or contradicted by the transcript vs. the summary tab.

## Action-Forward Variant

When the user wants to turn notes into today's work instead of a narrative summary, output:

- **Priorities list** — Ordered, with reasoning. Flag time-sensitive, blocked, or dependent-on-others items.
- **Linear ticket table** — `| Title | Description | Priority | Assignee |` where Priority is Urgent / High / Medium.
- **Follow-ups** — Items that need owner assignment or clarification before a ticket can be created.

Use this variant when the user says "what should I work on today", "create tickets from this", or "identify priorities".

## Slack Enrichment

When asked to add Slack context:
1. Resolve attendee Slack usernames with `slack_search_users` from the attendee list; ask only for a name the lookup cannot find
2. Search around the meeting date for references to topics discussed
3. Include a **Slack References** table at the end: `| Resource | Link |`
4. Use Markdown links inline (e.g., `[thread](https://iai-hub.slack.com/archives/...)`)

## Team Context (IAI project)

| Person | Slack handle |
|--------|-------------|
| Ryan Cook (CEO) | @Ry |
| Kevin O'Neill (CTO) | @Kevin O'Neill |
| Irina Malkova (Advisor) | @Irina Malkova |
| Omair Inam (Engineer) | @Omair Inam |

Linear project: https://linear.app/i-ai/team/IAI/all  
Output location: `docs/notes/`
