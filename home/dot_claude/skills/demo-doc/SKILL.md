---
name: demo-doc
description: Create a proof-of-work demo markdown document using showboat and rodney. Use when asked to "create a demo doc", "document this feature with showboat/rodney", or "use showboat and rodney to demo X". Also applies when finishing an implementation task and the user asks to document it.
---

# demo-doc

`showboat` builds markdown files that mix commentary with real captured command output — the document is both readable and re-runnable. `rodney` automates a headless Chrome browser for navigation, interaction, and screenshots.

## Workflow

1. Run `uvx showboat --help` and `uvx rodney --help` to learn the current CLI options
2. Verify dev servers are up: `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000`
   - Start if needed (e.g. `make dev-bg`) before proceeding
3. Initialize the document: `uvx showboat init docs/<name>.md "<Title>"`
   - If the file already exists, delete it first
4. Build the document section by section (see Structure below)
6. Stop Chrome and dev servers when done

## Document structure

Sensible default — adapt based on what was asked to demo:

- **Root Cause / Context** — why the problem existed or what the feature does
- **The Change** — `uvx showboat exec ... bash "git diff <file>"` to capture the real diff
- **Tests** — capture real test output (e.g. `cd frontend && npm test 2>&1 | tail -8`)
- **DOM / API Proof** *(optional)* — use `rodney js` to verify live state in the running app
- **Screenshots** — embed with `uvx showboat image docs/<name>.md <path-to-png>`

## showboat commands

```bash
uvx showboat init <file> "<Title>"          # Create document
uvx showboat note <file> "commentary"       # Add a prose block
uvx showboat exec <file> bash "command"     # Run command, capture output
uvx showboat image <file> path/to/img.png   # Embed image (plain path — see Pitfalls)
uvx showboat pop <file>                     # Remove last entry (use after a failed exec)
```

`exec` prints captured output to stdout. Read it and `pop` if the command failed before adding the next entry.

## rodney workflow

```bash
uvx rodney start                              # Launch headless Chrome
uvx rodney open "http://localhost:3000"       # Navigate
uvx rodney waitload                           # Wait for page load
uvx rodney input '[aria-label="X"]' "text"   # Type into an element
uvx rodney js "expression"                    # Evaluate JavaScript
uvx rodney screenshot -w 1280 -h 800 out.png # Capture screenshot
uvx rodney stop                               # Quit Chrome
```

Screenshots saved by rodney are embedded into the showboat document with `showboat image`.

## Remote publishing

None. Never set `SHOWBOAT_REMOTE_URL`; demo docs stay local. To share results, post the whole doc (image references rewritten to hosted URLs) to the relevant ticket.

## Pitfalls

- **`showboat image` requires a plain file path** — the `![alt](path)` markdown-reference form is shell-fragile; use `uvx showboat image doc.md path/img.png` instead
- **`showboat init` fails if the file exists** — delete it first with `rm`
- **`pop` on prose removes the whole trailing prose run** — every consecutive paragraph since the last code block counts as one entry, not just the last paragraph. Check the doc's tail before popping.
- **rodney session state persists** — if Chrome wasn't cleanly stopped, run `uvx rodney stop` before `uvx rodney start`
- **Auth-gated pages** — after navigating, check `uvx rodney url`; if redirected to login, fill the form before screenshots
- **Dev server must be up** before opening rodney; verify with `curl` first
