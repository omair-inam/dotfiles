# /// script
# requires-python = ">=3.14"
# ///
"""Extract text from a "Notes by Gemini" Google Doc via the gws CLI.

Usage:
    extract_gemini_doc.py <documentId> [--tab notes|transcript|all] [--out PATH]

Prints the requested tab(s) as plain text to stdout (or to --out).

Handles the two gotchas that bite every time:
  1. Gemini keeps the notes and the full transcript in *separate tabs* of the
     same doc, so a plain body read misses the transcript.
  2. `gws` prints "Using keyring backend: keyring" to stderr; we read stdout
     only so it can't corrupt JSON parsing.
"""
import argparse
import json
import subprocess
import sys


def walk(elements):
    """Flatten a Docs body content tree (paragraphs + nested tables) to text."""
    out = []
    for e in elements:
        if "paragraph" in e:
            out.append("".join(
                r.get("textRun", {}).get("content", "")
                for r in e["paragraph"].get("elements", [])
            ))
        elif "table" in e:
            for row in e["table"].get("tableRows", []):
                for cell in row.get("tableCells", []):
                    out.append(walk(cell.get("content", [])))
    return "".join(out)


def find_tab(tabs, title):
    """Depth-first search for a tab by (case-insensitive) title."""
    for t in tabs:
        if t.get("tabProperties", {}).get("title", "").lower() == title.lower():
            return t
        hit = find_tab(t.get("childTabs", []), title)
        if hit:
            return hit
    return None


def tab_text(tab):
    return walk(tab.get("documentTab", {}).get("body", {}).get("content", []))


def fetch(doc_id):
    params = json.dumps({"documentId": doc_id, "includeTabsContent": True})
    p = subprocess.run(
        ["gws", "docs", "documents", "get", "--params", params, "--format", "json"],
        capture_output=True, text=True,
    )
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        sys.exit(
            "ERROR: could not parse gws output. stderr:\n"
            f"{p.stderr.strip()}\n"
            "(If this is an auth/invalid_rapt error, run: gws auth login)"
        )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("document_id")
    ap.add_argument("--tab", default="all", choices=["notes", "transcript", "all"])
    ap.add_argument("--out", help="write to this file instead of stdout")
    a = ap.parse_args()

    doc = fetch(a.document_id)
    tabs = doc.get("tabs", [])
    wanted = ["Notes", "Transcript"] if a.tab == "all" else [a.tab.capitalize()]

    sections = []
    for title in wanted:
        tab = find_tab(tabs, title)
        if tab:
            sections.append(f"===== {title} =====\n{tab_text(tab)}")
        elif not tabs and title == "Notes":
            # Older docs have no tabs; fall back to the root body.
            sections.append(
                "===== Notes (no tabs) =====\n"
                + walk(doc.get("body", {}).get("content", []))
            )
        else:
            sections.append(f"===== {title} =====\n(not found)")

    text = "\n\n".join(sections)
    if a.out:
        with open(a.out, "w") as f:
            f.write(text)
        print(f"wrote {len(text)} chars to {a.out}")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
