#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# ///
"""Save every Rex session to a JSON snapshot, and restore it with each Claude Code conversation resumed.

  rexsnap.py save                      write a snapshot, print its path
  rexsnap.py restore [SNAPSHOT]        print the restore plan (dry run)
  rexsnap.py restore [SNAPSHOT] --apply [--only LABEL ...]
  rexsnap.py verify [SNAPSHOT]         check live state against a snapshot
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

SNAPSHOT_DIR = Path.home() / ".local/state/rex-snapshots"
LATEST = SNAPSHOT_DIR / "latest.json"
DEFAULT_CLAUDE_DIR = Path.home() / ".claude"
REX_FALLBACKS = [
    "~/Library/Application Support/com.superlogical.rex/RexServer/Versions/*/Rex Server.app/Contents/MacOS/rex",
    "/Applications/Rex*.app/Contents/Helpers/Rex Server.rex/Contents/MacOS/rex",
]
DEFAULT_WINDOW_LABEL = re.compile(r"^Window [0-9a-f]{8}$")
DEFAULT_BLOCK_LABEL = "shell"


@dataclass
class Claude:
    session_id: str
    name: str | None
    config_dir: str | None


@dataclass
class Block:
    label: str
    cwd: str
    foreground: str | None
    claude: Claude | None

    def command(self) -> list[str]:
        if self.claude is None:
            return [os.environ.get("SHELL", "/bin/zsh"), "-l"]
        resume = ["claude", "--resume", self.claude.session_id]
        if self.claude.config_dir:
            return ["env", f"CLAUDE_CONFIG_DIR={self.claude.config_dir}", *resume]
        return resume


@dataclass
class Split:
    direction: str
    ratio: float
    before: Node
    after: Node


type Node = Block | Split


@dataclass
class Window:
    label: str
    layout: Node


@dataclass
class Session:
    label: str
    active_window: int
    windows: list[Window]


def first_block(node: Node) -> Block:
    return node if isinstance(node, Block) else first_block(node.before)


def blocks(node: Node) -> list[Block]:
    return [node] if isinstance(node, Block) else blocks(node.before) + blocks(node.after)


def rex_bin() -> str:
    found = shutil.which("rex")
    if found:
        return found
    for pattern in REX_FALLBACKS:
        hits = sorted(glob.glob(os.path.expanduser(pattern)))
        if hits:
            return hits[-1]
    sys.exit("rex binary not found on PATH or in the Rex app bundles")


def rex(*args: str) -> dict:
    out = subprocess.run([rex_bin(), *args], check=True, capture_output=True, text=True).stdout
    return json.loads(out) if out.strip() else {}


def claude_for(pid: int) -> Claude | None:
    env = subprocess.run(["ps", "eww", "-o", "command=", "-p", str(pid)], capture_output=True, text=True).stdout
    m = re.search(r"\bCLAUDE_CONFIG_DIR=(\S+)", env)
    config_dir = m.group(1) if m else None
    pid_file = Path(config_dir or DEFAULT_CLAUDE_DIR) / "sessions" / f"{pid}.json"
    if not pid_file.exists():
        return None
    info = json.loads(pid_file.read_text())
    return Claude(info["sessionId"], info.get("name"), config_dir)


def read_block(sid: str, block_id: str, label: str) -> Block:
    proc = rex("block", "call", "-s", sid, "-b", block_id, "process")
    fg = proc.get("foreground") or proc.get("child") or {}
    claude = claude_for(fg["pid"]) if fg.get("pid") else None
    return Block(label, fg.get("cwd") or proc.get("home") or str(Path.home()), fg.get("argv0") or fg.get("name"), claude)


def read_layout(sid: str, node: dict, labels: dict[str, str]) -> Node:
    if "block_id" in node:
        return read_block(sid, node["block_id"], labels.get(node["block_id"], DEFAULT_BLOCK_LABEL))
    s = node["split"]
    return Split(s["direction"], s["ratio"], read_layout(sid, s["before"], labels), read_layout(sid, s["after"], labels))


def save() -> Path:
    sessions = []
    for ref in rex("ls", "--json")["sessions"]:
        listing = rex("window", "ls", "-s", ref["session_id"], "--json")
        windows = []
        for w in listing["windows"]:
            tiled = [layer for layer in w["layers"] if layer["kind"] == "tiled"]
            for layer in w["layers"]:
                if layer["kind"] != "tiled":
                    print(f"warning: {ref['label']}/{w['label']}: skipping {layer['kind']} layer", file=sys.stderr)
            labels = {b["block_id"]: b["label"] for layer in tiled for b in layer["blocks"]}
            windows.append(Window(w["label"], read_layout(ref["session_id"], tiled[0]["layout"], labels)))
        active = next(i for i, w in enumerate(listing["windows"]) if w["window_id"] == listing["active_window_id"])
        sessions.append(Session(ref["label"], active, windows))
    snapshot = {
        "version": 1,
        "captured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "rex": {"path": rex_bin(), "version": rex("whoami", "--json").get("rex_version")},
        "sessions": [asdict(s) for s in sessions],
    }
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOT_DIR / f"{datetime.now():%Y%m%d-%H%M%S}.json"
    path.write_text(json.dumps(snapshot, indent=2))
    shutil.copyfile(path, LATEST)
    for s in sessions:
        print(f"{s.label}: {len(s.windows)} window(s)")
        for w in s.windows:
            for b in blocks(w.layout):
                who = f"claude {b.claude.session_id}" if b.claude else (b.foreground or "shell")
                print(f"  {b.cwd}  {who}")
    return path


def parse_node(d: dict) -> Node:
    if "direction" in d:
        return Split(d["direction"], d["ratio"], parse_node(d["before"]), parse_node(d["after"]))
    claude = Claude(**d["claude"]) if d.get("claude") else None
    return Block(d["label"], d["cwd"], d.get("foreground"), claude)


def load(path: Path) -> list[Session]:
    data = json.loads(path.read_text())
    return [
        Session(s["label"], s["active_window"], [Window(w["label"], parse_node(w["layout"])) for w in s["windows"]])
        for s in data["sessions"]
    ]


class Runner:
    def __init__(self, apply: bool):
        self.apply = apply
        self.fake = 0

    def __call__(self, *args: str) -> dict:
        if not self.apply:
            print("  rex " + " ".join(_quote(a) for a in args))
            self.fake += 1
            return {"session_id": f"<session{self.fake}>", "window_id": f"<window{self.fake}>",
                    "block_ids": [f"<block{self.fake}>"],
                    "initial_windows": [{"window_id": f"<window{self.fake}>", "block_ids": [f"<block{self.fake}>"]}]}
        return rex(*args)


def _quote(arg: str) -> str:
    return arg if re.fullmatch(r"[\w@%+=:,./-]+", arg) else "'" + arg.replace("'", "'\\''") + "'"


def block_flags(b: Block) -> list[str]:
    flags = ["-c", b.cwd, "--keep-open", "--json"]
    return flags + (["--label", b.label] if b.label != DEFAULT_BLOCK_LABEL else [])


def build(run: Runner, sid: str, wid: str, node: Node, anchor: str) -> None:
    if isinstance(node, Block):
        return
    after = first_block(node.after)
    side = "right" if node.direction == "horizontal" else "below"
    pct = str(round((1 - node.ratio) * 100))
    created = run("run", "-s", sid, "-w", wid, "-b", anchor, "--split", side, "--ratio", pct, "--focus=false",
                  *block_flags(after), "--", *after.command())
    build(run, sid, wid, node.before, anchor)
    build(run, sid, wid, node.after, created["block_ids"][0])


def restore_session(run: Runner, s: Session) -> None:
    window_ids = []
    for i, w in enumerate(s.windows):
        head = first_block(w.layout)
        if i == 0:
            created = run("new", s.label, "-c", head.cwd, "--keep-open", "--json", "--", *head.command())
            sid = created["session_id"]
            first = created["initial_windows"][0]
            wid, bid = first["window_id"], first["block_ids"][0]
            if head.label != DEFAULT_BLOCK_LABEL:
                run("block", "rename", "-s", sid, bid, head.label)
        else:
            created = run("run", "-s", sid, "--focus=false", *block_flags(head), "--", *head.command())
            wid, bid = created["window_id"], created["block_ids"][0]
        if not DEFAULT_WINDOW_LABEL.match(w.label):
            run("window", "rename", "-s", sid, wid, w.label)
        build(run, sid, wid, w.layout, bid)
        window_ids.append(wid)
    run("window", "focus", "-s", sid, window_ids[s.active_window])


def restore(path: Path, apply: bool, only: list[str]) -> None:
    live = {s["label"] for s in rex("ls", "--json")["sessions"]}
    run = Runner(apply)
    for s in load(path):
        if only and s.label not in only:
            continue
        if s.label in live:
            print(f"skip {s.label}: a session with this label is already running")
            continue
        print(f"{'restoring' if apply else 'would restore'} {s.label}")
        restore_session(run, s)
    if apply:
        time.sleep(8)
        sys.exit(verify(path, only))
    print("\ndry run only; rerun with --apply")


def live_claude_ids() -> set[str]:
    ids = set()
    for pid_file in glob.glob(str(Path.home() / ".claude*/sessions/*.json")):
        try:
            os.kill(int(Path(pid_file).stem), 0)
        except (ValueError, ProcessLookupError, PermissionError):
            continue
        ids.add(json.loads(Path(pid_file).read_text())["sessionId"])
    return ids


def verify(path: Path, only: list[str]) -> int:
    live = {s["label"]: s["session_id"] for s in rex("ls", "--json")["sessions"]}
    running = live_claude_ids()
    problems = 0
    for s in load(path):
        if only and s.label not in only:
            continue
        if s.label not in live:
            print(f"MISSING session {s.label}")
            problems += 1
            continue
        count = len(rex("window", "ls", "-s", live[s.label], "--json")["windows"])
        if count != len(s.windows):
            print(f"WINDOWS {s.label}: expected {len(s.windows)}, found {count}")
            problems += 1
        for w in s.windows:
            for b in blocks(w.layout):
                if b.claude and b.claude.session_id not in running:
                    print(f"NOT RUNNING claude {b.claude.session_id} ({s.label})")
                    problems += 1
    print("verified: all sessions, windows, and Claude conversations are back" if not problems else f"{problems} problem(s)")
    return 1 if problems else 0


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("save")
    for name in ("restore", "verify"):
        sp = sub.add_parser(name)
        sp.add_argument("snapshot", nargs="?", type=Path, default=LATEST)
        sp.add_argument("--only", action="append", default=[], metavar="LABEL")
        if name == "restore":
            sp.add_argument("--apply", action="store_true")
    a = p.parse_args()
    if a.cmd == "save":
        print(save())
    elif a.cmd == "restore":
        restore(a.snapshot, a.apply, a.only)
    else:
        sys.exit(verify(a.snapshot, a.only))


if __name__ == "__main__":
    main()
