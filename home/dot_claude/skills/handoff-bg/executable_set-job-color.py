#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# ///
"""Set a background session's color: set-job-color.py <short-id> <color>

Colors: red blue green yellow purple orange pink cyan.
Writes `color` into ~/.claude/jobs/<short-id>/state.json, the same field
`/color` sets. Every other writer merges onto a re-read, so this survives.
"""

import json
import os
import sys
import time
from pathlib import Path

COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    short_id, color = sys.argv[1], sys.argv[2]
    if color not in COLORS:
        print(f"unknown color {color!r}; pick from {sorted(COLORS)}", file=sys.stderr)
        return 2

    root = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    state = root / "jobs" / short_id / "state.json"

    # The session writes state.json itself at startup; wait for it.
    for _ in range(50):
        if state.exists():
            break
        time.sleep(0.2)
    else:
        print(f"no state file at {state}", file=sys.stderr)
        return 1

    data = json.loads(state.read_text())
    data["color"] = color
    tmp = state.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data))
    os.replace(tmp, state)
    print(f"{short_id} -> {color}")
    return 0


def demo() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        job = Path(d) / "jobs" / "abc12345"
        job.mkdir(parents=True)
        (job / "state.json").write_text(json.dumps({"name": "x", "state": "working"}))
        os.environ["CLAUDE_CONFIG_DIR"] = d
        sys.argv = ["set-job-color.py", "abc12345", "cyan"]
        assert main() == 0
        after = json.loads((job / "state.json").read_text())
        assert after["color"] == "cyan", after
        assert after["name"] == "x", "must merge, not replace"
        sys.argv = ["set-job-color.py", "abc12345", "chartreuse"]
        assert main() == 2
        print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        raise SystemExit(main())
