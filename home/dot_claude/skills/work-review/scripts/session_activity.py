# /// script
# requires-python = ">=3.14"
# ///
"""Summarize Claude Code session logs over a recent window.

Usage:
    session_activity.py [--hours 24] [--since YYYY-MM-DD] [--root DIR]

For each *main* session (subagent logs excluded) touched in the window, prints:
time span, project, git branch, line count, and the first real user message
(the "intent"). Useful for standup / weekly reviews and timesheets — it surfaces
work that never reached a PR or a meeting summary.
"""
import argparse
import datetime
import glob
import json
import os


def first_intent(path):
    """First genuine user message (skip tool results, system reminders, skill preambles)."""
    try:
        with open(path) as fh:
            for line in fh:
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if o.get("type") != "user":
                    continue
                c = o.get("message", {}).get("content")
                if isinstance(c, str):
                    t = c
                elif isinstance(c, list):
                    t = " ".join(
                        p.get("text", "") for p in c
                        if isinstance(p, dict) and p.get("type") == "text"
                    )
                else:
                    t = ""
                t = t.strip()
                if (t and not t.startswith("<")
                        and "Caveat" not in t[:30]
                        and "Base directory for this skill" not in t[:40]):
                    return t
    except OSError:
        return ""
    return ""


def meta(path):
    branch = first = last = None
    n = 0
    with open(path) as fh:
        for line in fh:
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            n += 1
            branch = o.get("gitBranch", branch)
            ts = o.get("timestamp")
            if ts:
                first = first or ts
                last = ts
    return branch, first, last, n


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hours", type=float, help="window size in hours (default 24)")
    ap.add_argument("--since", help="ISO date; overrides --hours")
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    a = ap.parse_args()

    if a.since:
        cutoff = datetime.datetime.fromisoformat(a.since).timestamp()
    else:
        cutoff = (datetime.datetime.now()
                  - datetime.timedelta(hours=a.hours or 24)).timestamp()

    rows = []
    for f in glob.glob(os.path.join(a.root, "*/*.jsonl")):
        if "/subagents/" in f:
            continue
        if os.path.getmtime(f) < cutoff:
            continue
        branch, first, last, n = meta(f)
        proj = os.path.basename(os.path.dirname(f))
        # Decode chezmoi/Claude's dash-encoded project path to something readable.
        proj = proj.replace("-Users-", "~/").replace("-", "/")
        rows.append(((first or "")[:16], (last or "")[5:16],
                     proj[-34:], (branch or "-")[:34], n, first_intent(f)[:140]))

    rows.sort()
    for first, last, proj, branch, n, intent in rows:
        print(f"{first}->{last} | {proj:<34} | {branch:<34} | {n:>4}l | {intent}")
    if not rows:
        print("(no sessions in window)")


if __name__ == "__main__":
    main()
