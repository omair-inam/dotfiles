# /// script
# requires-python = ">=3.14"
# ///
"""Report what will break when an HTML report is shown inline in a Slite doc.

Usage:
    precheck.py <file.html> [<file.html> ...]
"""

import re
import sys
from pathlib import Path

RUNTIME = re.compile(r"window\.claude")
REF = re.compile(r'(?:src|href)="([^"#$][^"]*)"')
EXTERNAL = ("http:", "https:", "data:", "mailto:", "javascript:")


def check(path: Path) -> list[str]:
    html = path.read_text(errors="replace")
    problems = []
    if not html.lstrip().lower().startswith("<!doctype html"):
        problems.append("no <!doctype html>: not a standalone page")
    if RUNTIME.search(html):
        problems.append("uses window.claude: database, user or ask features will not work in Slite")
    local = sorted({m for m in REF.findall(html) if not m.startswith(EXTERNAL)})
    if local:
        shown = ", ".join(local[:5]) + (" ..." if len(local) > 5 else "")
        problems.append(f"{len(local)} relative links or assets will not resolve: {shown}")
    return problems


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    for arg in sys.argv[1:]:
        path = Path(arg)
        problems = check(path)
        print(f"{path} ({path.stat().st_size} bytes)")
        for p in problems or ["ok"]:
            print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
