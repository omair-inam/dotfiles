---
name: publish-html
description: Publish an HTML file or a folder of static files to the OpenQuick platform at openquick.omair-bc7.workers.dev and get a shareable URL back. Use when asked to "publish", "deploy", "host", "put this online", "share this page", "get a link for this", or when a generated HTML report/dashboard/mockup should become a URL. Handles Cloudflare Access (Google) auth by opening the browser.
---

# Publish HTML to OpenQuick

Publishes static files to `https://openquick.omair-bc7.workers.dev/<site>/`.

The CLI is `oquick`, already on PATH. Source lives at `~/projects/openquick`.

## Step 1: auth preflight (always do this first)

Cloudflare Access guards the platform with Google SSO restricted to `@i.ai`. The token
lasts about 24 hours. Check it before deploying. A deploy with no cached token launches
the login itself, which then blocks until a human clicks Approve, hanging the command:

```bash
cloudflared access token -app https://openquick.omair-bc7.workers.dev 2>&1 | head -c 3
```

Output starting with `ey` is a valid token. Go to Step 2.

Anything else, such as "Unable to find token", means you need to log in. Run this in the
**background** so it cannot block:

```bash
cloudflared access login https://openquick.omair-bc7.workers.dev
```

Then tell the user a browser tab opened and they must click **Approve** on the "Access
Requested" screen. Wait for the command to exit, then re-check the token. Never click
Approve yourself. The user grants their own credentials.

Missing `cloudflared`? Install it with `brew install cloudflared`.

## Step 2: deploy

```bash
oquick deploy <path> [--name <site>]
```

`<path>` takes either form:

**A single file.** Deploys as a one-page site. An `.html` file becomes `index.html`, so it
renders at the site root. The default site name is the filename without its extension, so
`sales-report.html` publishes to `/sales-report/`.

**A folder.** Deploys every file under it, recursively. Include an `index.html` at the root
or the site URL renders nothing. The default site name is the folder name.

Site names must match `^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$`. Pass `--name` when the derived
name breaks that pattern or reads badly.

## Step 3: verify, then report the URL

A deploy prints the live URL. Confirm it serves before telling the user it worked:

```bash
TOK=$(cloudflared access token -app https://openquick.omair-bc7.workers.dev 2>/dev/null)
curl -s -o /dev/null -w '%{http_code}\n' -H "cf-access-token: $TOK" \
  https://openquick.omair-bc7.workers.dev/<site>/
```

`200` means live. Report the plain URL. Anyone in the `@i.ai` org opens it in a browser
without a token, because their own Google session satisfies Access.

## Rules that bite

- **Deploying to an existing site name overwrites it, with no confirmation.** Run
  `oquick list` first. If something you did not create holds the name, pick another or ask.
- **Assets need relative paths** (`./style.css`, not `/style.css`). The platform serves
  sites under a `/<site>/` prefix, so absolute paths resolve off the site and 404.
- The platform rejects single files over 25 MB, or over 95 MB once R2 is enabled.
- No build step runs on deploy. Ship what the browser needs.

## Other commands

| Command | Does |
|---|---|
| `oquick list` | All sites: name, file count, size, last updated |
| `oquick open <site>` | Open the site in the browser |
| `oquick delete <site>` | Delete a site and its data (prompts; `--yes` skips) |

## Fixing a broken auth state

A `302`, a `403`, or an HTML login page in a response means the Access token expired or
never existed. Re-run the Step 1 login.

A `401` saying "your local token does not match the worker" points at something else: the
bearer deploy token in `~/.config/openquick/config.json`. Fix that one with `oquick setup`.
