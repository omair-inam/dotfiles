---
name: browser-automation
description: "Browser automation using Claude in Chrome for web tasks requiring a browser window. Use when user asks to open/navigate websites, fill forms, click elements, test web apps, debug with console logs, extract web data, automate multi-site workflows, interact with authenticated apps (Google Docs, Gmail, Notion), record browser GIFs, or any task requiring visual browser interaction. Triggers on phrases like 'go to', 'open in browser', 'check website', 'fill out form', 'test the UI', 'scrape', 'automate', 'record a demo'."
---

# Browser Automation

Automate browser tasks using Claude in Chrome MCP tools.

## Prerequisites Check

Before browser actions, verify:

1. **Connection**: Run `/chrome` to check status
2. **Tab context**: Call `mcp__claude-in-chrome__tabs_context_mcp` first to get available tabs
3. **New tab**: Create with `mcp__claude-in-chrome__tabs_create_mcp` for each new task

## Core Workflow

```
1. tabs_context_mcp (get tab IDs)
      ↓
2. tabs_create_mcp OR use existing tab
      ↓
3. navigate (go to URL)
      ↓
4. read_page / find / computer screenshot (understand page)
      ↓
5. Actions: computer click/type, form_input, javascript_tool
      ↓
6. Verify results
```

## Tool Quick Reference

| Tool | Purpose |
|------|---------|
| `tabs_context_mcp` | Get available tabs (call FIRST) |
| `tabs_create_mcp` | Create new tab |
| `navigate` | Go to URL, back/forward |
| `read_page` | Get accessibility tree (DOM structure) |
| `find` | Find elements by natural language |
| `computer` | Click, type, scroll, screenshot, wait |
| `form_input` | Set form values by ref ID |
| `javascript_tool` | Execute JS in page context |
| `get_page_text` | Extract article/text content |
| `read_console_messages` | Read console.log/error output |
| `read_network_requests` | Monitor XHR/Fetch requests |
| `gif_creator` | Record browser actions as GIF |
| `upload_image` | Upload screenshots to file inputs |
| `resize_window` | Set browser dimensions |

## Action Patterns

### Navigation

```python
# Always get context first
tabs_context_mcp(createIfEmpty=True)
tabs_create_mcp()  # New tab for task
navigate(url="example.com", tabId=TAB_ID)
```

### Finding & Clicking Elements

```python
# Method 1: Natural language find
find(query="login button", tabId=TAB_ID)
# Returns ref IDs like "ref_1", "ref_2"

# Method 2: Read accessibility tree
read_page(tabId=TAB_ID, filter="interactive")

# Click by coordinates (from screenshot)
computer(action="screenshot", tabId=TAB_ID)
computer(action="left_click", coordinate=[x, y], tabId=TAB_ID)

# Click by ref ID
computer(action="left_click", ref="ref_1", tabId=TAB_ID)
```

### Form Filling

```python
# Find input, then fill
find(query="email input", tabId=TAB_ID)
form_input(ref="ref_3", value="user@example.com", tabId=TAB_ID)

# Or type directly after clicking
computer(action="left_click", ref="ref_3", tabId=TAB_ID)
computer(action="type", text="user@example.com", tabId=TAB_ID)
```

### Debugging

```python
# Console errors (use pattern filter)
read_console_messages(tabId=TAB_ID, pattern="error|warning")

# Network requests
read_network_requests(tabId=TAB_ID, urlPattern="/api/")
```

### Recording GIFs

```python
gif_creator(action="start_recording", tabId=TAB_ID)
computer(action="screenshot", tabId=TAB_ID)  # Capture initial frame
# ... perform actions ...
computer(action="screenshot", tabId=TAB_ID)  # Capture final frame
gif_creator(action="stop_recording", tabId=TAB_ID)
gif_creator(action="export", download=True, filename="demo.gif", tabId=TAB_ID)
```

## Critical Rules

1. **NO JavaScript dialogs**: `alert()`, `confirm()`, `prompt()` block the extension. If triggered, user must dismiss manually.

2. **Always screenshot before clicking**: Coordinates come from visual inspection.

3. **Filter console output**: Always provide `pattern` parameter to avoid noise.

4. **Explicit permission required** for:
   - Downloading files
   - Submitting forms (irreversible actions)
   - Financial transactions
   - Sending emails/messages
   - Publishing content

5. **NEVER enter**:
   - Passwords (direct user to enter themselves)
   - Credit card numbers
   - SSN/passport numbers
   - API keys in shared documents

6. **Verify tab exists**: If tool errors with "tab doesn't exist", call `tabs_context_mcp` to refresh.

## Common Issues

| Problem | Solution |
|---------|----------|
| Extension not detected | Run `/chrome`, select "Reconnect" |
| Tab unresponsive | Create new tab, try again |
| Modal blocking | User dismisses dialog, then continue |
| Element not found | Take screenshot, use coordinates |
| Page not loading | Wait, retry, check network |

## Plan Presentation

For multi-step browser tasks, present plan to user via `update_plan`:

```python
update_plan(
    domains=["github.com", "docs.google.com"],
    approach=[
        "Navigate to GitHub repo",
        "Extract recent commit messages",
        "Open Google Doc and add summary"
    ]
)
```
