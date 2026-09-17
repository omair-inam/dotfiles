#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# ///
"""Audit git worktrees and emit a categorized markdown report.

Read-only: never runs `git worktree remove`, `git branch -d`, or any
destructive command. Outputs markdown to stdout; errors to stderr.

Run from inside any checkout of the target repository:

    audit_worktrees.py [--repo PATH]

Requires `git` and `gh` on PATH. If `gh` auth fails, the script aborts
with a non-zero exit code rather than guessing PR state.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Worktree:
    path: Path
    branch: str | None  # None for detached HEAD
    head: str
    is_main: bool = False
    is_bare: bool = False
    is_detached: bool = False

    # Populated later
    pr_number: int | None = None
    pr_state: str = "NO_PR"  # MERGED | CLOSED | OPEN | NO_PR | ERROR
    pr_title: str = ""
    pr_url: str = ""
    pr_merged_at: str = ""
    pr_updated_at: str = ""
    has_uncommitted: bool = False
    uncommitted_summary: str = ""
    unpushed_count: int = 0
    has_upstream: bool = True
    last_commit_date: str = ""
    last_commit_subject: str = ""
    notes: list[str] = field(default_factory=list)


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> str:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\nstderr: {result.stderr.strip()}"
        )
    return result.stdout


def parse_worktrees(porcelain: str) -> list[Worktree]:
    """Parse `git worktree list --porcelain` output.

    Each block is separated by a blank line and starts with `worktree <path>`.
    """
    worktrees: list[Worktree] = []
    current: dict[str, str] = {}

    def flush() -> None:
        if not current:
            return
        path = Path(current["worktree"])
        is_bare = "bare" in current
        is_detached = "detached" in current
        branch = None
        if "branch" in current:
            # branch lines look like "refs/heads/foo"; strip the prefix
            ref = current["branch"]
            branch = ref.removeprefix("refs/heads/")
        worktrees.append(
            Worktree(
                path=path,
                branch=branch,
                head=current.get("HEAD", ""),
                is_bare=is_bare,
                is_detached=is_detached,
            )
        )
        current.clear()

    for raw in porcelain.splitlines():
        line = raw.rstrip()
        if not line:
            flush()
            continue
        # Lines are either "key value" or single-word flags ("bare", "detached")
        if " " in line:
            key, value = line.split(" ", 1)
            current[key] = value
        else:
            current[line] = "true"
    flush()
    return worktrees


def ensure_gh_auth() -> None:
    """Verify `gh auth status` succeeds; raise otherwise."""
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "gh CLI is not authenticated. Run `gh auth login` "
            "(or `ghinit` / `ghinitdna`) and re-run this command.\n"
            f"gh stderr: {result.stderr.strip()}"
        )


def lookup_pr(branch: str, repo_dir: Path) -> dict | None:
    """Return the most recent PR matching `branch`, or None.

    Picks `MERGED` > `OPEN` > `CLOSED` if multiple exist, since a merged
    PR is the most informative about the branch's terminal state.
    """
    out = run(
        [
            "gh",
            "pr",
            "list",
            "--head",
            branch,
            "--state",
            "all",
            "--json",
            "number,state,title,mergedAt,updatedAt,url",
            "--limit",
            "20",
        ],
        cwd=repo_dir,
        check=False,
    )
    try:
        prs = json.loads(out) if out.strip() else []
    except json.JSONDecodeError:
        return None
    if not prs:
        return None
    priority = {"MERGED": 0, "OPEN": 1, "CLOSED": 2}
    prs.sort(key=lambda p: (priority.get(p.get("state", ""), 9), p.get("number", 0)))
    return prs[0]


def gather_git_status(wt: Worktree) -> None:
    """Fill in uncommitted/unpushed/last-commit fields on `wt`."""
    if wt.is_bare or wt.is_detached or not wt.path.exists():
        return

    porcelain = run(
        ["git", "-C", str(wt.path), "status", "--porcelain"], check=False
    )
    if porcelain.strip():
        wt.has_uncommitted = True
        lines = porcelain.strip().splitlines()
        wt.uncommitted_summary = f"{len(lines)} file(s)"

    # Unpushed commits relative to upstream. If no upstream, mark for note.
    upstream = run(
        [
            "git",
            "-C",
            str(wt.path),
            "rev-parse",
            "--abbrev-ref",
            "--symbolic-full-name",
            "@{u}",
        ],
        check=False,
    ).strip()
    if not upstream:
        wt.has_upstream = False
    else:
        count = run(
            ["git", "-C", str(wt.path), "rev-list", "--count", "@{u}..HEAD"],
            check=False,
        ).strip()
        try:
            wt.unpushed_count = int(count) if count else 0
        except ValueError:
            wt.unpushed_count = 0

    wt.last_commit_date = run(
        ["git", "-C", str(wt.path), "log", "-1", "--format=%cs"], check=False
    ).strip()
    wt.last_commit_subject = run(
        ["git", "-C", str(wt.path), "log", "-1", "--format=%s"], check=False
    ).strip()


def categorize(worktrees: list[Worktree]) -> dict[str, list[Worktree]]:
    buckets: dict[str, list[Worktree]] = {
        "safe_merged": [],
        "safe_closed": [],
        "needs_attention": [],
        "active_open": [],
        "active_no_pr": [],
        "unusual": [],
    }
    for wt in worktrees:
        if wt.is_main or wt.is_bare:
            continue
        if wt.is_detached or wt.branch is None:
            wt.notes.append("detached HEAD — no branch to match against PRs")
            buckets["unusual"].append(wt)
            continue

        clean = not wt.has_uncommitted and wt.unpushed_count == 0

        if wt.pr_state == "MERGED" and clean:
            buckets["safe_merged"].append(wt)
        elif wt.pr_state == "CLOSED" and not wt.has_uncommitted:
            buckets["safe_closed"].append(wt)
        elif wt.pr_state in ("MERGED", "CLOSED"):
            buckets["needs_attention"].append(wt)
        elif wt.pr_state == "OPEN":
            buckets["active_open"].append(wt)
        else:
            buckets["active_no_pr"].append(wt)
    return buckets


def fmt_pr_link(wt: Worktree) -> str:
    if wt.pr_number:
        return f"PR #{wt.pr_number}"
    return ""


def render(buckets: dict[str, list[Worktree]], total_audited: int) -> str:
    lines: list[str] = []

    def section(title: str, items: list[Worktree], render_item):
        lines.append(f"### {title}")
        if not items:
            lines.append("")
            lines.append("_None._")
            lines.append("")
            return
        lines.append("")
        for wt in items:
            lines.append(f"- {render_item(wt)}")
        lines.append("")

    def render_safe_merged(wt: Worktree) -> str:
        merged = wt.pr_merged_at[:10] if wt.pr_merged_at else "?"
        return (
            f"`{wt.path}` — branch `{wt.branch}` — "
            f"PR #{wt.pr_number} merged {merged}"
        )

    def render_safe_closed(wt: Worktree) -> str:
        return (
            f"`{wt.path}` — branch `{wt.branch}` — "
            f"PR #{wt.pr_number} closed without merging — "
            "**confirm with user before removing** (work was abandoned)"
        )

    def render_needs_attention(wt: Worktree) -> str:
        loss: list[str] = []
        if wt.has_uncommitted:
            loss.append(f"uncommitted changes ({wt.uncommitted_summary})")
        if wt.unpushed_count > 0:
            loss.append(f"{wt.unpushed_count} unpushed commit(s)")
        if not wt.has_upstream:
            loss.append("no upstream tracking branch")
        loss_str = "; ".join(loss) or "unknown loss"
        return (
            f"`{wt.path}` — branch `{wt.branch}` — "
            f"PR #{wt.pr_number} {wt.pr_state.lower()} — would lose: {loss_str}"
        )

    def render_active_open(wt: Worktree) -> str:
        updated = wt.pr_updated_at[:10] if wt.pr_updated_at else "?"
        title = wt.pr_title or "(no title)"
        return (
            f"`{wt.path}` — branch `{wt.branch}` — "
            f"PR #{wt.pr_number} \"{title}\" — last activity {updated}"
        )

    def render_active_no_pr(wt: Worktree) -> str:
        date = wt.last_commit_date or "?"
        subj = wt.last_commit_subject or "(no commits)"
        extras = []
        if wt.has_uncommitted:
            extras.append(f"uncommitted ({wt.uncommitted_summary})")
        if wt.unpushed_count > 0:
            extras.append(f"{wt.unpushed_count} unpushed")
        elif not wt.has_upstream:
            extras.append("no upstream")
        suffix = f" — {'; '.join(extras)}" if extras else ""
        return (
            f"`{wt.path}` — branch `{wt.branch}` — last commit {date}: "
            f"\"{subj}\"{suffix}"
        )

    def render_unusual(wt: Worktree) -> str:
        notes = "; ".join(wt.notes) or "see git worktree list"
        return f"`{wt.path}` — {notes}"

    section(
        "Safe to close (PR merged, no uncommitted work)",
        buckets["safe_merged"],
        render_safe_merged,
    )
    section(
        "Safe to close (PR closed without merging)",
        buckets["safe_closed"],
        render_safe_closed,
    )
    section(
        "Needs attention before closing",
        buckets["needs_attention"],
        render_needs_attention,
    )
    section("Active (PR open)", buckets["active_open"], render_active_open)
    section("Active (no PR yet)", buckets["active_no_pr"], render_active_no_pr)
    if buckets["unusual"]:
        section("Unusual / skipped", buckets["unusual"], render_unusual)

    safe = len(buckets["safe_merged"]) + len(buckets["safe_closed"])
    needs = len(buckets["needs_attention"])
    active = len(buckets["active_open"]) + len(buckets["active_no_pr"])
    summary = (
        f"**{total_audited} worktrees audited — "
        f"{safe} safe to close, {needs} need attention, {active} active.**"
    )
    lines.append(summary)
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Path to a checkout of the repository (default: cwd).",
    )
    args = parser.parse_args()

    repo = args.repo.resolve()

    try:
        # Resolve the canonical main worktree (top-level of the common dir).
        main_path = Path(
            run(["git", "-C", str(repo), "rev-parse", "--show-toplevel"]).strip()
        ).resolve()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    try:
        ensure_gh_auth()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    porcelain = run(["git", "-C", str(repo), "worktree", "list", "--porcelain"])
    worktrees = parse_worktrees(porcelain)

    total_audited = 0
    for wt in worktrees:
        if wt.path.resolve() == main_path:
            wt.is_main = True
            continue
        if wt.is_bare:
            continue
        total_audited += 1

        # PR lookup
        if wt.branch:
            try:
                pr = lookup_pr(wt.branch, main_path)
                if pr is None and wt.path.name != wt.branch:
                    # Fallback: try the worktree directory name
                    pr = lookup_pr(wt.path.name, main_path)
                    if pr is not None:
                        wt.notes.append(
                            f"matched PR via directory name `{wt.path.name}`"
                        )
                if pr:
                    wt.pr_number = pr.get("number")
                    wt.pr_state = pr.get("state", "NO_PR")
                    wt.pr_title = pr.get("title", "")
                    wt.pr_url = pr.get("url", "")
                    wt.pr_merged_at = pr.get("mergedAt") or ""
                    wt.pr_updated_at = pr.get("updatedAt") or ""
            except RuntimeError as exc:
                wt.pr_state = "ERROR"
                wt.notes.append(f"PR lookup failed: {exc}")

        gather_git_status(wt)

        # Note any worktree outside the conventional `.worktrees/` directory.
        try:
            rel = wt.path.resolve().relative_to(main_path)
            if not str(rel).startswith(".worktrees/"):
                wt.notes.append(f"outside `.worktrees/` (at `{rel}`)")
        except ValueError:
            wt.notes.append("outside the main repo tree")

    buckets = categorize(worktrees)
    sys.stdout.write(render(buckets, total_audited))
    return 0


if __name__ == "__main__":
    sys.exit(main())
