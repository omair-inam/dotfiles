---
name: slite
description: Read, write, and edit docs in the IAI Slite workspace through the Slite MCP (`mcp__slite__*` tools), including attaching files and showing an HTML page inline in a doc. Use whenever Omair asks to find, read, create, update, or reorganize a Slite doc, wiki page, note, or collection, to attach an image, PDF, or HTML file to one, or pastes an `i-domain.slite.com` link.
---

# Slite

All Slite work goes through the Slite MCP. Its server instructions carry the workspace, Omair's user id, the personal channel id, and the sliteml format reference. Read those rather than guessing. "Doc" and "note" mean the same thing.

## Reading

- Default to `get-note` with `format: "sliteml"`. It carries the block IDs every partial edit needs. Use `md` for a compact read-only copy.
- Never request `format: "html"`. It returns about 2 MB per doc because it inlines Slite's stylesheet.
- For a long doc, pass `fullContent: false` and page with `cursor`, or fetch a section with `startBlockId`/`endBlockId`.
- Find docs with `search-notes`. Answer a question across the workspace with `ask-slite`. Walk a tree with `get-note-children`.

## Editing

- `update-note` with `sliteml` replaces the whole body. Use it only to rewrite a doc on purpose. For everything else, read the doc first, then use `append-blocks`, `modify-block`, `modify-range`, or `remove-blocks` with the block IDs from the read.
- Unknown tags are not rejected. `<iframe>` is dropped, and a made-up tag becomes an empty paragraph. After writing an unfamiliar block, check the `changedContent` in the response to see what was actually saved.
- Link another doc in this workspace with `<note-link note-id="..." title="...">`, not `<a>`.
- Keep every `<comment id="...">` tag exactly as read. Dropping one orphans a comment thread.
- To remove a doc, `archive-note` it. Do not delete docs.
- Test pages go in Omair's personal channel, which is where `create-note` puts a doc when no `parentNoteId` is given.

## Attaching a file

1. Get the exact byte size with `wc -c < file`.
2. Call `upload-file` with the `noteId`, the file name, the MIME type, and that size.
3. Upload the bytes to the returned `uploadUrl`, sending every header in `uploadHeaders`:

   ```shell
   curl -sS -o /dev/null -w '%{http_code}\n' -X PUT --data-binary @file \
     -H "Content-Type: <type>" -H "Content-Disposition: attachment" "<uploadUrl>"
   ```

   Expect `200`. The URL expires after an hour.
4. Insert the returned `<file .../>` block with `append-blocks`, or with `modify-block` to place it. Add `caption="..."` if wanted.

Uploads are limited to 20 per minute. An image that already has a public URL needs no upload. Write `<image url="..." />` instead.

## Showing HTML inline

An HTML file attached as above (`text/html`) renders in the Slite app as an interactive frame inside the doc, and its scripts run. This is the only way to show an HTML page inline.

These do not work:

- `<embed url="...">` renders as a link card, whether the URL is external or the uploaded file's own URL.
- `<iframe>` is dropped when saved.

## Checking how a doc looks

The `md` and `html` exports do not show how the app renders a doc. An inline HTML file appears there as a plain file link. The Chrome automation profile is not signed into Slite, so it cannot open docs either. To confirm how a doc looks, give Omair the doc URL and ask for a screenshot.
