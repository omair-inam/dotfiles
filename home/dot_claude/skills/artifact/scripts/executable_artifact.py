#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# ///
"""Publish, read, list, and move claude.ai artifacts as any of Omair's Claude accounts, by alias.

Every artifact call runs in a headless `claude -p` launched by `cswap run <slot>`, so the
account named by the alias owns what it publishes, whichever account runs this script.
"""

import argparse
import functools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path

STATE_PATH = Path(
    os.environ.get("ARTIFACT_STATE", "~/.claude/artifacts.json")
).expanduser()
LEGACY_STATE_PATH = STATE_PATH.parent / "team-artifacts.json"

HEADLESS_FLAGS = [
    "--tools", "Artifact,Read",
    "--allowedTools", "Artifact,Read",
    "--strict-mcp-config",
    "--no-session-persistence",
    "--setting-sources", "project",
    "--output-format", "stream-json",
    "--verbose",
]  # fmt: skip

ALIAS_RE = re.compile(r"[a-z][a-z0-9-]{0,15}")
URL_RE = re.compile(r"https://claude\.ai/(?:code/)?artifact/[A-Za-z0-9-]+")
PUBLISHED_RE = re.compile(
    r"at (https://claude\.ai/\S+?) \(Version \d+, version id ([^)\s]+)\)"
)
READ_HEADER_RE = re.compile(r"^\[Artifact \S+ \(version ([^)\s]+)\) (.*)$", re.M)
LISTED_PATH_RE = re.compile(r'^- "(.+?)"\s{2}', re.M)
SAVED_DIR_RE = re.compile(r'^Files saved under "([^"]+)"', re.M)
SAVED_PATH_RE = re.compile(r'^- "(.+?)" saved \(', re.M)
ASSET_ID_RE = re.compile(r"\b[0-9a-f]{32}\b")
LOGIN_RE = re.compile(
    r"/login|authentication_error|OAuth token has expired|invalid_grant|401", re.I
)
PAGE = "index.html"
RAW_PAGE = ".published.html"
MAX_FILES = 255
PUBLISH_SKELETON_HEAD = (
    "<!doctype html><html><head><meta charset=utf8><meta name=viewport"
)
PUBLISH_SKELETON_BODY = "<body>\n"
PUBLISH_SKELETON_TAIL = "\n</body></html>"

UNREADABLE_REASONS = {
    "in another of the user's organizations": "it is in another organization",
    "was made by someone else": "someone else owns it, and a headless run cannot approve reading it",
    "couldn't check who made this artifact": "it does not exist, or this account cannot see it",
}

EXIT_CODES = {
    "not_configured": 2,
    "cswap_missing": 3,
    "logged_out": 4,
    "wrong_account": 5,
    "conflict": 6,
    "tool_failed": 7,
    "bad_input": 8,
    "account_missing": 9,
    "needs_input": 10,
    "not_readable": 11,
    "unknown_alias": 12,
}


@dataclass(frozen=True)
class Failure(Exception):
    kind: str
    message: str
    detail: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Account:
    alias: str
    email: str
    org_id: str
    org_name: str

    @property
    def label(self) -> str:
        return f"{self.alias} ({self.email}, {self.org_name})"


@dataclass(frozen=True)
class Record:
    url: str
    version: str
    published_at: str


@dataclass
class State:
    default: str | None = None
    accounts: dict[str, Account] = field(default_factory=dict)
    artifacts: dict[str, dict[str, Record]] = field(default_factory=dict)
    moves: dict[str, dict[str, str]] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "State":
        if STATE_PATH.exists():
            raw = json.loads(STATE_PATH.read_text())
            return cls(
                default=raw.get("default"),
                accounts={
                    alias: Account(alias=alias, **acc)
                    for alias, acc in raw.get("accounts", {}).items()
                },
                artifacts={
                    path: {org: Record(**rec) for org, rec in by_org.items()}
                    for path, by_org in raw.get("artifacts", {}).items()
                },
                moves=raw.get("moves", {}),
            )
        if LEGACY_STATE_PATH.exists():
            legacy = json.loads(LEGACY_STATE_PATH.read_text()).get("artifacts", {})
            migrated = cls(
                artifacts={
                    path: {
                        rec["org_id"]: Record(
                            rec["url"], rec["version"], rec["published_at"]
                        )
                    }
                    for path, rec in legacy.items()
                }
            )
            migrated.save()
            return migrated
        return cls()

    def save(self) -> None:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        body = {
            "default": self.default,
            "accounts": {
                alias: {k: v for k, v in asdict(acc).items() if k != "alias"}
                for alias, acc in self.accounts.items()
            },
            "artifacts": {
                path: {org: asdict(rec) for org, rec in by_org.items()}
                for path, by_org in sorted(self.artifacts.items())
            },
            "moves": self.moves,
        }
        fd, tmp = tempfile.mkstemp(dir=STATE_PATH.parent, prefix=".artifacts.")
        with os.fdopen(fd, "w") as f:
            json.dump(body, f, indent=2)
            f.write("\n")
        os.replace(tmp, STATE_PATH)

    def account(self, alias: str | None) -> Account:
        if not self.accounts:
            raise Failure(
                "not_configured",
                f"No accounts saved in {STATE_PATH}. Run `setup` first.",
            )
        name = alias or self.default
        if name not in self.accounts:
            raise Failure(
                "unknown_alias",
                f"No account has the alias {name!r}. Known aliases: {', '.join(self.accounts)}.",
            )
        return self.accounts[name]

    def by_org(self, org_id: str) -> Account:
        for acc in self.accounts.values():
            if acc.org_id == org_id:
                return acc
        raise Failure(
            "unknown_alias",
            f"No alias is set for organization {org_id}. Rerun `setup` to give it one.",
        )

    def owner_candidates(self) -> list[Account]:
        default = self.account(None)
        return [default, *(acc for acc in self.accounts.values() if acc != default)]


@dataclass(frozen=True)
class Call:
    input: dict
    text: str
    is_error: bool

    def matches(self, action: str, **fields: object) -> bool:
        return self.input.get("action", "publish") == action and all(
            self.input.get(k) == v for k, v in fields.items()
        )


@dataclass(frozen=True)
class Site:
    """A local page plus its supporting files, keyed by published path, sources relative to root."""

    root: Path
    page: Path
    files: dict[str, str]
    multi_file: bool

    @classmethod
    def at(cls, path: Path) -> "Site":
        if path.is_file() and path.suffix in (".html", ".htm"):
            return cls(path.parent, path, {}, multi_file=False)
        if path.is_dir() and (path / PAGE).is_file():
            files = {
                rel: rel
                for f in sorted(path.rglob("*"))
                if f.is_file()
                and not any(part.startswith(".") for part in f.relative_to(path).parts)
                and (rel := f.relative_to(path).as_posix()) != PAGE
            }
            if len(files) >= MAX_FILES:
                raise Failure(
                    "bad_input",
                    f"{path} holds {len(files) + 1} files. One publish takes at most {MAX_FILES}.",
                )
            return cls(path, path / PAGE, files, multi_file=True)
        raise Failure(
            "bad_input",
            f"{path} is neither an .html file nor a directory with {PAGE} at its root.",
        )


@dataclass(frozen=True)
class Download:
    account: Account
    url: str
    version: str
    role: str
    out: Path
    paths: list[str]
    assets: list[str]
    passed_over: dict[str, str] = field(default_factory=dict)


def cswap(
    *args: str, env: dict[str, str] | None = None, cwd: Path | None = None
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["cswap", *args],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            env=env,
            cwd=cwd,
            timeout=900,
        )
    except FileNotFoundError:
        raise Failure(
            "cswap_missing", "cswap is not on PATH. Install claude-swap, then rerun."
        )


@functools.cache
def cswap_listing() -> dict:
    out = cswap("list", "--json")
    if out.returncode != 0:
        raise Failure(
            "tool_failed", f"`cswap list --json` failed: {out.stderr.strip()}"
        )
    return json.loads(out.stdout)


def auth_status(slot: int) -> dict:
    out = cswap("run", str(slot), "--", "auth", "status")
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        raise Failure(
            "tool_failed",
            f"`cswap run {slot} -- auth status` did not answer: {(out.stderr or out.stdout).strip()}",
        )


def relogin_steps(slot: int, who: str, email: str, org_name: str) -> str:
    active = cswap_listing().get("activeAccountNumber")
    back = (
        f"`cswap switch {active}`"
        if active and active != slot
        else "a switch back to your usual default account"
    )
    return (
        f"Log {who} back in. Run `cswap run {slot}`, type /login and sign in as {email} "
        f"(organization {org_name}), then exit. Then run `cswap switch {slot}` followed by {back}. "
        "The switch is what copies the new login into cswap's stored copy; without it the next "
        "`cswap run` reseeds the profile from the old, dead login."
    )


@functools.cache
def session(account: Account) -> tuple[int, str | None]:
    """The account's current cswap slot and subscription, after confirming it is logged in as itself."""
    slot = next(
        (
            a["number"]
            for a in cswap_listing()["accounts"]
            if (a.get("email"), a.get("organizationUuid"))
            == (account.email, account.org_id)
        ),
        None,
    )
    if slot is None:
        raise Failure(
            "account_missing",
            f"cswap holds no account for {account.label}. Add it back to cswap (log in to it and run `cswap add`), "
            "then rerun.",
        )
    status = auth_status(slot)
    if not status.get("loggedIn"):
        raise Failure(
            "logged_out",
            relogin_steps(slot, account.alias, account.email, account.org_name),
        )
    if (status.get("email"), status.get("orgId")) != (account.email, account.org_id):
        raise Failure(
            "wrong_account",
            f"cswap slot {slot} is listed as {account.label} but is logged in as {status.get('email')} "
            f"({status.get('orgName')}). Nothing was done. Log the slot back in as {account.email}, or rerun `setup`.",
        )
    return slot, status.get("subscriptionType")


def run_as(account: Account, prompt: str, cwd: Path) -> list[Call]:
    """Run one headless claude as the account and return its Artifact calls, in order."""
    slot, _ = session(account)
    env = {**os.environ, "CLAUDE_CODE_ARTIFACT": "1"}
    out = cswap("run", str(slot), "--", "-p", prompt, *HEADLESS_FLAGS, env=env, cwd=cwd)
    inputs: dict[str, dict] = {}
    calls: list[Call] = []
    final: dict = {}
    for line in out.stdout.splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        body = msg.get("message") if msg.get("type") in ("assistant", "user") else None
        for block in (body or {}).get("content") or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") == "Artifact":
                inputs[block["id"]] = block.get("input") or {}
            if (
                block.get("type") == "tool_result"
                and block.get("tool_use_id") in inputs
            ):
                content = block.get("content")
                if isinstance(content, list):
                    content = "\n".join(part.get("text", "") for part in content)
                calls.append(
                    Call(
                        inputs[block["tool_use_id"]],
                        content or "",
                        bool(block.get("is_error")),
                    )
                )
        if msg.get("type") == "result":
            final = msg
    if final.get("is_error") or not final:
        detail = final.get("result") or out.stderr.strip() or "no result"
        if LOGIN_RE.search(detail):
            raise Failure(
                "logged_out",
                relogin_steps(slot, account.alias, account.email, account.org_name),
            )
        raise Failure(
            "tool_failed", f"Headless claude as {account.alias} failed: {detail}"
        )
    return calls


def exact_calls(*calls: dict) -> str:
    steps = " ".join(f"{i}) {json.dumps(call)}" for i, call in enumerate(calls, 1))
    return (
        "Make exactly these Artifact tool calls, in order, each with exactly the JSON input shown, and no other "
        f"Artifact call: {steps} The local files are final: do not edit them. Reply DONE."
    )


def find(calls: list[Call], action: str, **fields: object) -> Call | None:
    return next((c for c in calls if c.matches(action, **fields)), None)


def unreadable_reason(text: str) -> str:
    return next(
        (why for marker, why in UNREADABLE_REASONS.items() if marker in text),
        text.strip().splitlines()[0][:200],
    )


def page_header(calls: list[Call], url: str) -> tuple[str, str]:
    """The live version and the account's role (owner or writer) from a plain read, or Failure not_readable."""
    read = find(calls, "read", url=url)
    if read is None:
        raise Failure("tool_failed", f"The headless run never read {url}.")
    m = READ_HEADER_RE.search(read.text)
    role = m and (
        "owner"
        if "owned by you" in m.group(2)
        else "writer"
        if "writer" in m.group(2)
        else None
    )
    if read.is_error or not role:
        raise Failure(
            "not_readable",
            unreadable_reason(read.text)
            if read.is_error
            else "only a summary came back",
        )
    return m.group(1), role


def listed_paths(calls: list[Call], url: str) -> list[str]:
    listing = find(calls, "list", scope="files", url=url)
    if listing is None or listing.is_error:
        raise Failure(
            "tool_failed",
            f"Could not list the files of {url}: {listing.text if listing else 'not called'}",
        )
    return LISTED_PATH_RE.findall(listing.text)


def unwrap(page: str) -> str:
    if page.startswith(PUBLISH_SKELETON_HEAD) and page.endswith(PUBLISH_SKELETON_TAIL):
        return page[
            page.index(PUBLISH_SKELETON_BODY) + len(PUBLISH_SKELETON_BODY) : -len(
                PUBLISH_SKELETON_TAIL
            )
        ]
    return page


def download(
    account: Account, url: str, out: Path, with_assets: bool = False
) -> Download:
    """Save every published file of the artifact into out, with index.html unwrapped so out is publishable."""
    steps = [
        f"1) {json.dumps({'action': 'read', 'url': url})}. If it fails, stop and reply DONE.",
        f"2) {json.dumps({'action': 'list', 'scope': 'files', 'url': url})}.",
        f'3) {{"action": "read", "url": "{url}", "paths": [...]}} with paths set to "index.html" plus every '
        "other path call 2 listed, exactly as listed. Do not pass out_dir.",
    ]
    if with_assets:
        steps.append(
            f"4) {json.dumps({'action': 'list', 'scope': 'assets', 'url': url})}. It may fail; that is fine."
        )
    prompt = f"Make these Artifact tool calls in order, and no other Artifact call. {' '.join(steps)} Reply DONE."
    calls = run_as(account, prompt, out)
    version, role = page_header(calls, url)
    paths = sorted({PAGE, *listed_paths(calls, url)})
    fetched = next(
        (c for c in calls if c.matches("read", url=url) and c.input.get("paths")), None
    )
    saved_dir = fetched and SAVED_DIR_RE.search(fetched.text)
    if not saved_dir:
        raise Failure(
            "tool_failed",
            f"Could not download the files of {url}: {fetched.text[:600] if fetched else 'not called'}",
        )
    if missing := set(paths) - set(SAVED_PATH_RE.findall(fetched.text)):
        raise Failure(
            "tool_failed",
            f"These files of {url} were not downloaded: {sorted(missing)}. {fetched.text[:600]}",
        )
    for rel in paths:
        dest = (out / rel).resolve()
        if not dest.is_relative_to(out):
            raise Failure(
                "tool_failed",
                f"{url} publishes a path outside its own folder: {rel!r}. Nothing more was saved.",
            )
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path(saved_dir.group(1)) / rel, dest)
    raw = (out / PAGE).read_text()
    (out / RAW_PAGE).write_text(raw)
    (out / PAGE).write_text(unwrap(raw))
    assets = find(calls, "list", scope="assets", url=url)
    found = (
        sorted(set(ASSET_ID_RE.findall(assets.text)))
        if assets and not assets.is_error
        else []
    )
    return Download(account, url, version, role, out, paths, found)


def download_from_owner(
    state: State, url: str, out: Path, alias: str | None, with_assets: bool = False
) -> Download:
    if alias:
        try:
            return download(state.account(alias), url, out, with_assets)
        except Failure as f:
            if f.kind != "not_readable":
                raise
            raise Failure("not_readable", f"{alias} cannot open {url}: {f.message}.")
    tried: dict[str, str] = {}
    for account in state.owner_candidates():
        try:
            return replace(download(account, url, out, with_assets), passed_over=tried)
        except Failure as f:
            if f.kind not in (
                "not_readable",
                "logged_out",
                "wrong_account",
                "account_missing",
            ):
                raise
            tried[account.alias] = f.message
    raise Failure(
        "not_readable",
        f"No saved account can open {url}. "
        + " ".join(f"{a}: {why}." for a, why in tried.items()),
        {"tried": tried},
    )


def publish_site(
    account: Account, site: Site, url: str | None, icon: str, published: list[str]
) -> tuple[str, str]:
    """Publish the site as the account, new or in place at url, removing published paths the site no longer has."""
    files: dict[str, str | None] = dict(site.files)
    if url and site.multi_file:
        files |= {
            path: None for path in published if path != PAGE and path not in site.files
        }
    publish: dict = {"action": "publish", "file_path": str(site.page)}
    publish |= {"url": url} if url else {"icon": icon}
    if files:
        publish["files"] = files
    reads = [{"action": "read", "url": url}] if url else []
    if url and site.multi_file:
        reads.append({"action": "list", "scope": "files", "url": url})
    calls = run_as(account, exact_calls(*reads, publish), site.root)
    done = find(calls, "publish")
    m = done and PUBLISHED_RE.search(done.text)
    if not m:
        raise Failure(
            "tool_failed",
            f"The headless run finished without a confirmed publish. {done.text[:800] if done else ''}",
        )
    if url and m.group(1) != url:
        raise Failure(
            "tool_failed",
            f"Expected an update to {url} but the publish landed at {m.group(1)}.",
        )
    return m.group(1), m.group(2)


def live_state(
    account: Account, url: str, site: Site, cwd: Path
) -> tuple[str, list[str]]:
    reads = [{"action": "read", "url": url}]
    if site.multi_file:
        reads.append({"action": "list", "scope": "files", "url": url})
    calls = run_as(account, exact_calls(*reads), cwd)
    version, _ = page_header(calls, url)
    return version, listed_paths(calls, url) if site.multi_file else []


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def out_dir(arg: str | None) -> Path:
    path = Path(arg or tempfile.mkdtemp(prefix="artifact-")).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def cmd_setup(args, state: State) -> dict:
    listing = cswap_listing()
    by_slot = {a["number"]: a for a in listing["accounts"]}
    if not args.alias:
        saved = {
            (acc.email, acc.org_id): alias for alias, acc in state.accounts.items()
        }
        accounts = [
            {
                "number": a["number"],
                "email": a.get("email"),
                "org_name": a.get("organizationName"),
                "org_id": a.get("organizationUuid"),
                "active": a["number"] == listing.get("activeAccountNumber"),
                "alias": (
                    alias := saved.get((a.get("email"), a.get("organizationUuid")))
                ),
                "default": alias is not None and alias == state.default,
            }
            for a in listing["accounts"]
        ]
        raise Failure(
            "needs_input",
            "Ask Omair, for every account, for a short lowercase alias or to exclude it, and which alias is the "
            "default. Then run `setup --alias <name>=<number> ... --default <name>`.",
            {"accounts": accounts},
        )
    pairs = [entry.partition("=") for entry in args.alias]
    if bad := [
        name
        for name, eq, slot in pairs
        if not (eq and ALIAS_RE.fullmatch(name) and slot.isdigit())
    ]:
        raise Failure(
            "bad_input",
            f"Each --alias must be <name>=<number>, name lowercase, at most 16 characters: {bad}.",
        )
    names = [name for name, _, _ in pairs]
    slots = [int(slot) for _, _, slot in pairs]
    if len(set(names)) != len(names) or len(set(slots)) != len(slots):
        raise Failure(
            "bad_input", "Each alias and each account number may appear only once."
        )
    if args.default not in names:
        raise Failure(
            "bad_input", f"--default must be one of the aliases: {', '.join(names)}."
        )
    if unknown := [s for s in slots if s not in by_slot]:
        raise Failure(
            "bad_input",
            f"cswap has no account numbered {unknown}. Run `setup` with no flags to list them.",
        )
    accounts = {
        name: Account(
            name,
            by_slot[slot]["email"],
            by_slot[slot]["organizationUuid"],
            by_slot[slot]["organizationName"],
        )
        for name, slot in zip(names, slots)
    }
    subscriptions = {name: session(acc)[1] for name, acc in accounts.items()}
    state.accounts, state.default = accounts, args.default
    state.save()
    return {
        "saved": {
            name: {**asdict(acc), "subscription": subscriptions[name]}
            for name, acc in accounts.items()
        },
        "default": args.default,
        "state": str(STATE_PATH),
    }


def cmd_check(args, state: State) -> dict:
    accounts = [state.account(args.alias)] if args.alias else state.owner_candidates()
    results, failures = {}, []
    for acc in accounts:
        try:
            slot, subscription = session(acc)
            results[acc.alias] = {
                "ok": True,
                "slot": slot,
                "subscription": subscription,
                **asdict(acc),
            }
        except Failure as f:
            results[acc.alias] = {"ok": False, "error": f.kind, "message": f.message}
            failures.append(f)
    if failures:
        raise Failure(
            failures[0].kind,
            f"{len(failures)} of {len(accounts)} accounts failed the check.",
            results,
        )
    return {"ok": results, "default": state.default}


def cmd_publish(args, state: State) -> dict:
    source = Path(args.path).expanduser().resolve()
    site = Site.at(source)
    account = state.account(args.to)
    record = state.artifacts.get(str(source), {}).get(account.org_id)
    url = args.url or (record.url if record else None)
    published: list[str] = []
    if url:
        live, published = live_state(account, url, site, site.root)
        if record and record.url == url and live != record.version and not args.force:
            raise Failure(
                "conflict",
                f"{url} is at version {live}, but this path last published version {record.version}. Someone "
                "changed it since (a teammate, or an edit in the browser). Nothing was published. Run `read <path> "
                f"--from {account.alias} --rebase`, merge the change into the local files, then publish again. Or "
                "pass --force to overwrite the change.",
            )
    published_url, version = publish_site(account, site, url, args.icon, published)
    state.artifacts.setdefault(str(source), {})[account.org_id] = Record(
        published_url, version, now()
    )
    state.save()
    return {
        "url": published_url,
        "version": version,
        "owner": account.label,
        "files": 1 + len(site.files),
        "new": not url,
        "sharing": "Sharing settings carry over from earlier versions."
        if url
        else "Private until shared. Open the link, use Share, and choose the organization.",
    }


def cmd_read(args, state: State) -> dict:
    out = out_dir(args.out)
    match = URL_RE.search(args.target)
    if match:
        if args.rebase:
            raise Failure(
                "bad_input",
                "--rebase needs the local path that was published, not a link.",
            )
        got = download_from_owner(state, match.group(0), out, args.from_)
    else:
        source = str(Path(args.target).expanduser().resolve())
        records = state.artifacts.get(source, {})
        preferred = (
            state.account(args.from_).org_id
            if args.from_
            else state.account(None).org_id
        )
        org = (
            preferred
            if preferred in records
            else next(iter(records))
            if len(records) == 1
            else None
        )
        if org is None:
            raise Failure(
                "bad_input",
                f"{args.target} is neither an artifact link nor a path published to that account. "
                "Pass a link, or --from with the account it was published to.",
            )
        got = download_from_owner(state, records[org].url, out, state.by_org(org).alias)
        if args.rebase:
            records[org] = Record(
                records[org].url, got.version, records[org].published_at
            )
            state.save()
    return {
        "url": got.url,
        "read_as": got.account.alias,
        "owner": got.account.label if got.role == "owner" else None,
        "role": got.role,
        "version": got.version,
        "out": str(out),
        "page": str(out / PAGE),
        "published_page": str(out / RAW_PAGE),
        "files": got.paths,
        "passed_over": got.passed_over,
    }


def cmd_move(args, state: State) -> dict:
    if args.from_ and args.from_ == (args.to or state.default):
        raise Failure(
            "bad_input",
            f"The source and the target are both {args.from_}. Name two different accounts.",
        )
    target = state.account(args.to)
    match = URL_RE.search(args.target)
    if not match:
        raise Failure("bad_input", f"{args.target} is not a claude.ai artifact link.")
    source_url = match.group(0)
    got = download_from_owner(
        state, source_url, out_dir(None), args.from_, with_assets=True
    )
    if got.account == target:
        raise Failure(
            "bad_input",
            f"{source_url} already belongs to {target.alias}. Name a different target with --to.",
        )
    copy = Site.at(got.out)
    copy_url = state.moves.get(source_url, {}).get(target.org_id)
    published: list[str] = []
    if copy_url:
        try:
            published = live_state(target, copy_url, copy, got.out)[1]
        except Failure as f:
            if f.kind != "not_readable":
                raise
            copy_url = None  # the earlier copy was deleted, so make a new one
    url, version = publish_site(target, copy, copy_url, "page", published)
    state.moves.setdefault(source_url, {})[target.org_id] = url
    state.save()
    slot, _ = session(got.account)
    in_session_account = slot == cswap_listing().get("activeAccountNumber")
    return {
        "source": {
            "url": source_url,
            "alias": got.account.alias,
            "owner": got.account.label,
            "version": got.version,
        },
        "copy": {
            "url": url,
            "alias": target.alias,
            "owner": target.label,
            "version": version,
            "new": not copy_url,
        },
        "files": got.paths,
        "passed_over": got.passed_over,
        "not_moved": {"assets": got.assets} if got.assets else {},
        "source_is_active_account": in_session_account,
        "next_steps": (
            f"The copy is private: open {url}, use Share, and choose the organization. The source still exists. "
            + (
                "It belongs to the account this session runs on, so this session's own delete tool can remove it "
                "once Omair confirms."
                if in_session_account
                else f"Omair must delete it on claude.ai while signed in as {got.account.label}."
            )
        ),
    }


def cmd_list(args, state: State) -> dict:
    account = state.account(args.account)
    calls = run_as(
        account,
        exact_calls({"action": "list", "scope": args.scope, "limit": args.limit}),
        Path.cwd(),
    )
    return {
        "account": account.label,
        "listing": "\n".join(c.text for c in calls),
        "local_records": {
            path: by_org[account.org_id].url
            for path, by_org in state.artifacts.items()
            if account.org_id in by_org
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("setup", help="list cswap accounts, or save aliases for them")
    p.add_argument("--alias", action="append", default=[], metavar="NAME=NUMBER")
    p.add_argument("--default")
    p = sub.add_parser(
        "check", help="confirm one alias, or all, is logged in as itself"
    )
    p.add_argument("alias", nargs="?")
    p = sub.add_parser(
        "publish",
        help="publish an .html file, or a directory with index.html, as an account",
    )
    p.add_argument("path")
    p.add_argument("--to", help="alias to publish as (default: the default alias)")
    p.add_argument(
        "--url",
        help="update this existing artifact of that account instead of the recorded one",
    )
    p.add_argument("--icon", default="page")
    p.add_argument(
        "--force",
        action="store_true",
        help="overwrite a version someone else published",
    )
    p = sub.add_parser("read", help="download every published file of an artifact")
    p.add_argument("target", help="artifact link, or a local path this tool published")
    p.add_argument(
        "--from",
        dest="from_",
        help="alias to read as (default: the first alias that owns it)",
    )
    p.add_argument("--out", help="directory to save into")
    p.add_argument(
        "--rebase",
        action="store_true",
        help="record the live version as the base for the next publish",
    )
    p = sub.add_parser(
        "move", help="copy an artifact to another account as a new artifact"
    )
    p.add_argument("target", help="artifact link")
    p.add_argument(
        "--from", dest="from_", help="alias that owns it (default: detected)"
    )
    p.add_argument("--to", help="alias to copy it to (default: the default alias)")
    p = sub.add_parser("list", help="list artifacts an account can open")
    p.add_argument("--account", help="alias (default: the default alias)")
    p.add_argument("--scope", default="mine", choices=["mine", "shared", "all"])
    p.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    handler = {
        "setup": cmd_setup,
        "check": cmd_check,
        "publish": cmd_publish,
        "read": cmd_read,
        "move": cmd_move,
        "list": cmd_list,
    }[args.cmd]
    try:
        print(json.dumps(handler(args, State.load()), indent=2))
    except Failure as f:
        print(json.dumps({"error": f.kind, "message": f.message, **f.detail}, indent=2))
        sys.exit(EXIT_CODES[f.kind])


if __name__ == "__main__":
    main()
