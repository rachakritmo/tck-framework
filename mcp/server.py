#!/usr/bin/env python3
"""
TCK — Ticket MCP Server
Manages tickets in the TCK Obsidian vault.
All tickets live flat in <team>/Tickets/.
Status is tracked via YAML frontmatter — no file moves.
Teams are auto-discovered: any vault subfolder containing a Tickets/ directory is a team.
"""

import json
import os
import re
import shlex
import subprocess
import threading
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

VAULT_ROOT        = Path(__file__).parent.parent  # /Users/tong/chain
TICKET_LOGS_DIR   = VAULT_ROOT / "Ticket Logs"
PIDS_DIR          = VAULT_ROOT / ".pids"
CLAUDE_BIN        = Path.home() / ".local" / "bin" / "claude"
CODEX_BIN         = "codex"

VALID_STATUSES = ["Backlog", "Open", "InProgress", "QAReview", "Done", "ReOpen", "Escalated"]
VALID_RUNTIMES = ["claude", "codex"]
REOPEN_LIMIT = 4

mcp = FastMCP("ticket-mcp")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def tickets_dir(team: str) -> Path:
    return VAULT_ROOT / team / "Tickets"


def discover_teams() -> list[str]:
    """Return all team names by scanning for <team>/Tickets/ folders in the vault."""
    skip = {".obsidian", "Templates", "mcp", ".git"}
    teams = []
    for d in sorted(VAULT_ROOT.iterdir()):
        if d.is_dir() and d.name not in skip and not d.name.startswith("."):
            if (d / "Tickets").is_dir():
                teams.append(d.name)
    return teams


def validate_team(team: str) -> str | None:
    """Return error string if team is invalid, else None."""
    teams = discover_teams()
    if team not in teams:
        return f"unknown team '{team}'. Available teams: {teams}"
    return None


def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def find_ticket(ticket_id: str) -> tuple[str, Path] | None:
    """Find a ticket by ID across all discovered teams. Returns (team, path)."""
    for team in discover_teams():
        folder = tickets_dir(team)
        if not folder.exists():
            continue
        for f in folder.glob("*.md"):
            if f.stem.startswith(ticket_id):
                return team, f
    return None


def update_frontmatter(content: str, updates: dict) -> str:
    """Update YAML frontmatter fields in place."""
    def replacer(m):
        fm = m.group(1)
        for key, value in updates.items():
            fm = re.sub(
                rf"^({re.escape(key)}:\s*).*$",
                rf"\g<1>{value}",
                fm,
                flags=re.MULTILINE,
            )
        return f"---\n{fm}---"
    return re.sub(r"^---\n(.*?\n)---", replacer, content, count=1, flags=re.DOTALL)


def add_tag(content: str, tag: str) -> str:
    """Add a tag to the frontmatter tags list, creating the field if absent."""
    fm_match = re.match(r"^(---\n.*?\n---)", content, re.DOTALL)
    if not fm_match:
        return content
    fm_block = fm_match.group(1)
    if "tags:" in fm_block:
        # append to existing tags list
        updated = re.sub(
            r"^(tags:\s*\[)([^\]]*)\]",
            lambda m: f"{m.group(1)}{m.group(2) + ', ' if m.group(2).strip() else ''}{tag}]",
            fm_block,
            flags=re.MULTILINE,
        )
    else:
        # insert tags field before closing ---
        updated = fm_block.replace("\n---", f"\ntags: [{tag}]\n---", 1)
    return content.replace(fm_block, updated, 1)


def to_blockquote(text: str) -> str:
    """Convert multiline text to blockquote lines — each line prefixed with '> '."""
    return "\n".join(f"> {line}" if line.strip() else ">" for line in text.splitlines())


def append_log_block(
    content: str, entry_type: str, by_agent: str, text: str, status_update: str = ""
) -> str:
    """Append a callout log block. Multiline text is properly blockquoted."""
    ts = now_ts()
    body = to_blockquote(text)

    if entry_type == "escalated":
        num = len(re.findall(r"AI QA Audit Report #\d+", content)) + 1
        block = (
            f"\n> [!WARNING] ⚠️ AI QA Audit Report #{num}\n"
            f"> **Agent:** {by_agent}\n"
            f"> **Audit Results:**\n{body}\n"
            f"> **ts:** {ts}\n"
        )
    elif entry_type == "open":
        num = len(re.findall(r"AI Builder Feedback #\d+", content)) + 1
        block = (
            f"\n> [!EXAMPLE] 🎯 AI Builder Feedback #{num}\n"
            f"> **By:** {by_agent}\n"
            f"> **Action:**\n{body}\n"
            f"> **ts:** {ts}\n"
        )
    elif entry_type == "claim":
        num = len(re.findall(r"AI Builder Feedback #\d+", content)) + 1
        block = (
            f"\n> [!ABSTRACT] 🚀 AI Builder Feedback #{num}\n"
            f"> **Agent:** {by_agent}\n"
            f"> **Action:**\n{body}\n"
            f"> **ts:** {ts}\n"
        )
    elif entry_type == "builder":
        num = len(re.findall(r"AI Builder Feedback #\d+", content)) + 1
        block = (
            f"\n> [!INFO] 📥 AI Builder Feedback #{num}\n"
            f"> **Agent:** {by_agent}\n"
            f"> **Action:**\n{body}\n"
            f"> **ts:** {ts}\n"
        )
    elif entry_type == "auto_done":
        num = len(re.findall(r"AI Builder Feedback #\d+", content)) + 1
        block = (
            f"\n> [!CHECK] ✅ AI Builder Feedback #{num}\n"
            f"> **Agent:** {by_agent}\n"
            f"> **Action:**\n{body}\n"
            f"> **ts:** {ts}\n"
        )
    else:  # qa
        num = len(re.findall(r"AI QA Audit Report #\d+", content)) + 1
        is_fail = text.startswith("FAIL")
        is_pass = text.startswith("PASS")
        callout = "DANGER" if is_fail else "CHECK" if is_pass else "ABSTRACT"
        icon = "❌" if is_fail else "✅" if is_pass else "🔍"
        block = (
            f"\n> [!{callout}] {icon} AI QA Audit Report #{num}\n"
            f"> **Agent:** {by_agent}\n"
            f"> **Audit Results:**\n{body}\n"
            f"> **ts:** {ts}\n"
        )

    if status_update:
        block += f"> **🔃 Status Update:** `{status_update}`.\n"

    return content.rstrip() + "\n" + block


def parse_ticket(team: str, path: Path) -> dict:
    """Parse a ticket markdown file into a structured dict. Includes file_path so agents can read it directly."""
    content = path.read_text()

    # Frontmatter
    fm: dict = {}
    fm_match = re.match(r"^---\n(.*?\n)---", content, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).splitlines():
            m = re.match(r"^(\w+):\s*(.*)$", line)
            if m:
                fm[m.group(1)] = m.group(2).strip()

    # Tags
    tags_raw = fm.get("tags", "[]")
    tags = [t.strip().strip("\"'") for t in re.findall(r"[\w/.-]+", tags_raw)]

    # ticket_id + title
    title_m = re.search(r"#\s*🎫\s*Ticket:\s*\[([^\]]+)\]\s*(.+)", content)
    ticket_id = title_m.group(1).strip() if title_m else path.stem
    title = title_m.group(2).strip() if title_m else path.stem

    # Goal — raw markdown between ## 🎯 and next ### or ---
    goal_m = re.search(r"##\s*🎯.*?The Goal\n+(.*?)(?=###|---|\Z)", content, re.DOTALL)
    goal = goal_m.group(1).strip() if goal_m else ""

    # DOs — raw markdown between ### ✅ DO and ### ❌ DON'T DO
    dos_m = re.search(r"###\s*✅\s*DO\n+(.*?)(?=###\s*❌|---|\Z)", content, re.DOTALL)
    dos = dos_m.group(1).strip() if dos_m else ""

    # DON'Ts — raw markdown between ### ❌ DON'T DO and next --- or section
    donts_m = re.search(r"###\s*❌\s*DON'T DO\n+(.*?)(?=---|##|\Z)", content, re.DOTALL)
    donts = donts_m.group(1).strip() if donts_m else ""

    # Log entries — collect all callout types with position for ordering
    log_raw = []

    # Builder entries: EXAMPLE (open), ABSTRACT (claim), INFO (work)
    for m in re.finditer(
        r"> \[!(EXAMPLE|ABSTRACT|INFO)\][^\n]*AI Builder Feedback #(\d+)\n((?:>.*\n?)*)", content
    ):
        callout, num, body = m.group(1), int(m.group(2)), m.group(3)
        entry_type = "open" if callout == "EXAMPLE" else "claim" if callout == "ABSTRACT" else "builder"
        entry: dict = {"type": entry_type, "num": num}
        for field, pattern in [
            ("agent",   r"> \*\*(?:Agent|By):\*\*\s*(.+)"),
            ("summary", r"> \*\*Action:\*\*\n((?:> (?!\*\*(?:ts|Agent|By|Audit Results|🔃):\*\*).+\n?|>\n)*)"),
            ("ts",      r"> \*\*ts:\*\*\s*(.+)"),
        ]:
            fm_m = re.search(pattern, body)
            if fm_m:
                raw = fm_m.group(1).strip()
                entry[field] = re.sub(r"^> ?", "", raw, flags=re.MULTILINE).strip()
        log_raw.append((m.start(), entry))

    # QA entries: ABSTRACT (started), CHECK (pass), DANGER (fail), WARNING (escalated)
    for m in re.finditer(
        r"> \[!(ABSTRACT|CHECK|DANGER|WARNING)\][^\n]*AI QA Audit Report #(\d+)\n((?:>.*\n?)*)", content
    ):
        callout, num, body = m.group(1), int(m.group(2)), m.group(3)
        entry_type = (
            "qa_started"   if callout == "ABSTRACT" else
            "qa_pass"      if callout == "CHECK"    else
            "qa_fail"      if callout == "DANGER"   else
            "escalated"
        )
        entry = {"type": entry_type, "num": num}
        for field, pattern in [
            ("agent", r"> \*\*Agent:\*\*\s*(.+)"),
            ("notes", r"> \*\*Audit Results:\*\*\n((?:> (?!\*\*(?:ts|Agent|By|Action|🔃):\*\*).+\n?|>\n)*)"),
            ("ts",    r"> \*\*ts:\*\*\s*(.+)"),
        ]:
            fm_m = re.search(pattern, body)
            if fm_m:
                raw = fm_m.group(1).strip()
                entry[field] = re.sub(r"^> ?", "", raw, flags=re.MULTILINE).strip()
        log_raw.append((m.start(), entry))

    log = [e for _, e in sorted(log_raw, key=lambda x: x[0])]

    return {
        "ticket_id":    ticket_id,
        "team":         team,
        "status":       fm.get("status", "Backlog"),
        "title":        title,
        "goal":         goal,
        "dos":          dos,
        "donts":        donts,
        "log":          log,
        "tags":         tags,
        "reopen_count":   int(fm.get("reopen_count", 0)),
        "builder_tokens": int(fm.get("builder_tokens", 0)),
        "qa_tokens":      int(fm.get("qa_tokens", 0)),
        "need_qa":          fm.get("need_qa", "true").lower() == "true",
        "work_with_human":  fm.get("work_with_human", "false").lower() == "true",
        "created":          fm.get("created", ""),
        "updated":          fm.get("updated", ""),
        "file_name":        path.name,
    }


def next_ticket_id(team: str) -> str:
    """Auto-generate the next ticket ID using yymm-001 format, resetting each month."""
    yymm = datetime.now().strftime("%y%m")
    prefix = f"TCK-{team.upper()}-{yymm}"
    folder = tickets_dir(team)
    max_num = 0
    if folder.exists():
        for f in folder.glob("*.md"):
            m = re.match(rf"^{re.escape(prefix)}-(\d+)", f.stem)
            if m:
                max_num = max(max_num, int(m.group(1)))
    return f"{prefix}-{max_num + 1:03d}"


def fmt_duration(seconds: int) -> str:
    """Format seconds as human-readable duration: 45s, 2m 3s."""
    if seconds <= 0:
        return ""
    if seconds < 60:
        return f"{seconds}s"
    return f"{seconds // 60}m {seconds % 60}s"


def truncate(text: str, max_len: int = 60) -> str:
    """Truncate to max_len chars, replacing newlines with spaces."""
    flat = text.strip().replace("\n", " ")
    return (flat[:max_len] + "…") if len(flat) > max_len else flat


def _get_marker(existing: str, ticket_id: str) -> str:
    """Return ●/○ marker by peeking at the first data row of an existing log.
    Handles both team logs (no team col) and ALL.md (has team col after #)."""
    if not existing:
        return "●"
    lines = existing.splitlines()
    sep_idx = next(
        (i for i, ln in enumerate(lines)
         if ln.startswith("|") and not any(c.isalpha() or c.isdigit() for c in ln)),
        None,
    )
    if sep_idx is None or sep_idx + 1 >= len(lines):
        return "●"
    top_row = lines[sep_idx + 1]
    # Optional team column between # and [[link]]: | ● | team | [[...]] | or | ● | [[...]] |
    m = re.match(r"\|\s*([●○])\s*\|(?:\s*\w+\s*\|)?\s*\[\[[^\|]+\|([^\]]+)\]\]", top_row)
    if not m:
        return "●"
    top_marker, top_tid = m.group(1), m.group(2).strip()
    if top_tid == ticket_id:
        return top_marker
    return "○" if top_marker == "●" else "●"


_log_lock = threading.Lock()


def _insert_log_row(log_file: Path, new_row: str, header: str, sep: str) -> None:
    """Write new_row to log_file newest-on-top, creating the file if needed.
    Thread-safe: uses a module-level lock to prevent concurrent write corruption."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with _log_lock:
        existing = log_file.read_text() if log_file.exists() else ""
        if not existing:
            log_file.write_text(f"{header}\n{sep}\n{new_row}\n")
            return
        lines = existing.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("|") and not any(c.isalpha() or c.isdigit() for c in line):
                lines.insert(i + 1, new_row)
                break
        else:
            lines.append(new_row)
        log_file.write_text("\n".join(lines) + "\n")


def append_activity_log(
    log_type: str, team: str, ticket_id: str, title: str,
    agent: str, action: str, note: str = "", tokens: int = 0, duration: int = 0
) -> None:
    """Append a row to both the team log and ALL.md, newest on top.
    Team logs live in Ticket Logs/<team>/. ALL.md lives at Ticket Logs/ALL.md."""
    TICKET_LOGS_DIR.mkdir(exist_ok=True)

    ts         = now_ts()
    safe_title = re.sub(r"[^\w\s-]", "", title).strip()
    file_stem  = f"{ticket_id} {safe_title}"
    note_short = truncate(note) if note.strip() else ""
    tokens_str = f"{tokens:,}" if tokens else ""
    time_str   = fmt_duration(duration)
    link       = f"[[{file_stem}\\|{ticket_id}]]"

    # --- Team log: Ticket Logs/<team>/TCK-<TEAM>-<type>.md ---
    team_log = TICKET_LOGS_DIR / team / f"TCK-{team.upper()}-{log_type}.md"
    team_existing = team_log.read_text() if team_log.exists() else ""
    team_marker   = _get_marker(team_existing, ticket_id)
    team_row      = f"| {team_marker} | {link} | {title} | {agent} | {action} | {tokens_str} | {time_str} | {note_short} | {ts} |"
    team_header   = "| # | Ticket ID | Ticket Name | Agent | Action | Tokens | Time | Note | Datetime |"
    team_sep      = "|---|---|---|---|---|---|---|---|---|"
    _insert_log_row(team_log, team_row, team_header, team_sep)

    # --- ALL.md: Ticket Logs/ALL.md (adds Team column) ---
    all_log      = TICKET_LOGS_DIR / "ALL.md"
    all_existing = all_log.read_text() if all_log.exists() else ""
    all_marker   = _get_marker(all_existing, ticket_id)
    all_row      = f"| {all_marker} | {team} | {link} | {title} | {agent} | {action} | {tokens_str} | {time_str} | {note_short} | {ts} |"
    all_header   = "| # | Team | Ticket ID | Ticket Name | Agent | Action | Tokens | Time | Note | Datetime |"
    all_sep      = "|---|---|---|---|---|---|---|---|---|---|"
    _insert_log_row(all_log, all_row, all_header, all_sep)


def atomic_write(path: Path, content: str) -> None:
    """Write content atomically — temp file + replace, so a crash never corrupts the target."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content)
    tmp.replace(path)


def err(msg: str) -> str:
    return json.dumps({"error": msg})


def validate_runtime(runtime: str) -> str | None:
    """Return error string if runtime is invalid, else None."""
    if runtime not in VALID_RUNTIMES:
        return f"runtime required: one of {VALID_RUNTIMES}"
    return None


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def list_teams() -> str:
    """
    List all available teams in the vault (any folder containing a Tickets/ subfolder).

    Returns: [{ team, tickets_path }]
    """
    teams = discover_teams()
    return json.dumps([
        {"team": t, "tickets_path": str(tickets_dir(t))}
        for t in teams
    ], indent=2)


@mcp.tool()
def create_ticket(
    team: str,
    title: str,
    goal: str,
    dos: str,
    donts: str,
    ticket_id: str = "",
    watch_points: str = "",
    need_qa: bool = True,
    work_with_human: bool = False,
) -> str:
    """
    Create a new ticket in the team's Tickets folder with status Backlog.
    All content fields accept Markdown — use any formatting (bold, lists, code blocks, etc).
    ticket_id is optional — auto-generated (e.g. TCK-APP-2604-001) if not provided.
    watch_points is optional — leave blank if no special QA focus.
    need_qa defaults to true — set to false to skip QA and auto-complete on submit_work.
    work_with_human defaults to false — set to true so the agent pauses and works interactively
    with the human instead of executing autonomously.

    Args:
        team:             team name (e.g. "ux", "app", "deploy") — auto-discovered from vault
        title:            Short descriptive title
        goal:             Markdown — what needs to be achieved and why
        dos:              Markdown — requirements and allowed behaviors
        donts:            Markdown — constraints and prohibited behaviors
        ticket_id:        Optional. Auto-generated if not provided.
        watch_points:     Optional Markdown — what QA should pay special attention to.
        need_qa:          Optional. Default true. Set false to skip QA — ticket auto-completes on submit_work.
        work_with_human:  Optional. Default false. Set true — agent pauses and collaborates with
                          the human rather than working autonomously. Human drives the session;
                          when they say "ok" the agent calls submit_work.

    Returns: Ticket object | Error
    """
    if e := validate_team(team):
        return err(e)

    if not ticket_id:
        ticket_id = next_ticket_id(team)

    ts = now_ts()
    watch_text = watch_points.strip() if watch_points.strip() else "_No special QA focus — review against the DO / DON'T list._"
    safe_title = re.sub(r"[^\w\s-]", "", title).strip()
    filename = f"{ticket_id} {safe_title}.md"
    dest = tickets_dir(team) / filename
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        return err(f"ticket already exists: {filename}")

    dest.write_text(f"""---
status: Backlog
reopen_count: 0
builder_tokens: 0
qa_tokens: 0
need_qa: {"true" if need_qa else "false"}
work_with_human: {"true" if work_with_human else "false"}
created: {ts}
updated: {ts}
tags: [tck, team/{team}]
---

# 🎫 Ticket: [{ticket_id}] {title}

## 🎯 1. The Goal

{goal}

### ✅ DO

{dos}

### ❌ DON'T DO

{donts}

---

## 👀 2. Watch Points (For QA)

{watch_text}

---

## 🛠️ 3. Execution & Audit Log

""")

    return json.dumps(parse_ticket(team, dest), indent=2)


@mcp.tool()
def list_tickets(team: str, status: str = "") -> str:
    """
    List tickets for a team, optionally filtered by status property.

    Args:
        team: team name (e.g. "ux", "app", "deploy") — auto-discovered from vault
        status: Optional — Backlog, Open, InProgress, QAReview, Done, ReOpen, Escalated

    Returns: [{ ticket_id, title, status }] | Error
    """
    if e := validate_team(team):
        return err(e)
    if status and status not in VALID_STATUSES:
        return err(f"unknown status '{status}'. Valid: {VALID_STATUSES}")

    folder = tickets_dir(team)
    if not folder.exists():
        return json.dumps([])

    results = []
    for f in sorted(folder.glob("*.md")):
        content = f.read_text()
        fm_m = re.match(r"^---\n(.*?\n)---", content, re.DOTALL)
        ticket_status = ""
        if fm_m:
            s_m = re.search(r"^status:\s*(.+)$", fm_m.group(1), re.MULTILINE)
            ticket_status = s_m.group(1).strip() if s_m else ""

        if status and ticket_status != status:
            continue

        title_m = re.search(r"#\s*🎫\s*Ticket:\s*\[([^\]]+)\]\s*(.+)", content)
        results.append({
            "ticket_id": title_m.group(1).strip() if title_m else f.stem,
            "title":     title_m.group(2).strip() if title_m else f.stem,
            "status":    ticket_status,
        })

    return json.dumps(results, indent=2)


@mcp.tool()
def get_ticket(ticket_id: str) -> str:
    """
    Get full details of a ticket by ID.

    Args:
        ticket_id: e.g. "TCK-UX-001"

    Returns: Ticket object | Error
    """
    result = find_ticket(ticket_id)
    if not result:
        return err(f"ticket '{ticket_id}' not found")
    team, path = result
    return json.dumps(parse_ticket(team, path), indent=2)


@mcp.tool()
def get_next_ticket(team: str) -> str:
    """
    Return the next Open ticket for a builder agent (lowest ID first).

    Args:
        team: team name (e.g. "ux", "app", "deploy") — auto-discovered from vault

    Returns: Ticket object | null | Error
    """
    if e := validate_team(team):
        return err(e)

    folder = tickets_dir(team)
    if not folder.exists():
        return json.dumps(None)

    open_tickets, reopen_tickets = [], []
    for f in sorted(folder.glob("*.md")):
        content = f.read_text()
        fm_m = re.match(r"^---\n(.*?\n)---", content, re.DOTALL)
        if fm_m:
            s_m = re.search(r"^status:\s*(.+)$", fm_m.group(1), re.MULTILINE)
            s = s_m.group(1).strip() if s_m else ""
            if s == "Open":
                open_tickets.append(f)
            elif s == "ReOpen":
                reopen_tickets.append(f)

    # Open takes priority over ReOpen
    candidates = open_tickets or reopen_tickets
    if not candidates:
        return json.dumps(None)

    return json.dumps(parse_ticket(team, candidates[0]), indent=2)


@mcp.tool()
def get_next_ticket_for_review(team: str) -> str:
    """
    Return the next QAReview ticket for a QA agent (lowest ID first).

    Args:
        team: team name (e.g. "ux", "app", "deploy") — auto-discovered from vault

    Returns: Ticket object | null | Error
    """
    if e := validate_team(team):
        return err(e)

    folder = tickets_dir(team)
    if not folder.exists():
        return json.dumps(None)

    candidates = []
    for f in sorted(folder.glob("*.md")):
        content = f.read_text()
        fm_m = re.match(r"^---\n(.*?\n)---", content, re.DOTALL)
        if fm_m:
            s_m = re.search(r"^status:\s*(.+)$", fm_m.group(1), re.MULTILINE)
            if s_m and s_m.group(1).strip() == "QAReview":
                candidates.append(f)

    if not candidates:
        return json.dumps(None)

    return json.dumps(parse_ticket(team, candidates[0]), indent=2)


@mcp.tool()
def open_ticket(ticket_id: str, by: str) -> str:
    """
    Move a ticket from Backlog to Open, making it available for agents to pick up.
    Writes a log entry recording who opened it.

    Args:
        ticket_id: e.g. "TCK-UX-001"
        by: Who is opening the ticket (PM, orchestrator, agent name, etc.)

    Returns: Updated Ticket object | Error
    """
    result = find_ticket(ticket_id)
    if not result:
        return err(f"ticket '{ticket_id}' not found")
    team, path = result
    ticket = parse_ticket(team, path)

    if ticket["status"] != "Backlog":
        return err(f"ticket is '{ticket['status']}', expected 'Backlog'")

    content = path.read_text()
    content = update_frontmatter(content, {"status": "Open", "updated": now_ts()})
    content = append_log_block(content, "open", by, "Ticket moved to Open and ready for execution.", "Open")
    atomic_write(path, content)

    append_activity_log("Builder", team, ticket["ticket_id"], ticket["title"], by, "Opened")

    return json.dumps(parse_ticket(team, path), indent=2)


@mcp.tool()
def execute_ticket(ticket_id: str, by_agent: str) -> str:
    """
    Claim an Open ticket and set it to InProgress. Writes a history log entry.

    Args:
        ticket_id: e.g. "TCK-UX-001"
        by_agent: Agent identifier

    Returns: Updated Ticket object | Error
    """
    result = find_ticket(ticket_id)
    if not result:
        return err(f"ticket '{ticket_id}' not found")
    team, path = result
    ticket = parse_ticket(team, path)

    if ticket["status"] not in ("Open", "ReOpen"):
        return err(f"ticket is '{ticket['status']}', expected 'Open' or 'ReOpen'")

    prev_status   = ticket["status"]
    reopen_count  = ticket["reopen_count"]

    content = path.read_text()
    content = update_frontmatter(content, {"status": "InProgress", "updated": now_ts()})
    content = append_log_block(content, "claim", by_agent, "Ticket claimed and execution started.", "InProgress")
    atomic_write(path, content)

    if prev_status == "ReOpen":
        action = f"Claimed (ReOpen r{reopen_count})"
    else:
        action = "Claimed"
    append_activity_log("Builder", team, ticket["ticket_id"], ticket["title"], by_agent, action)

    return json.dumps(parse_ticket(team, path), indent=2)


@mcp.tool()
def submit_work(ticket_id: str, by_agent: str, summary: str, note: str = "", tokens: int = 0) -> str:
    """
    Mark work complete. Routes automatically based on the ticket's need_qa field:
    - need_qa: true  → status becomes QAReview (default flow)
    - need_qa: false → status becomes Done immediately (Auto-Done, no QA step)

    Args:
        ticket_id: e.g. "TCK-UX-001"
        by_agent: Agent identifier
        summary: Detailed description of what was done (written into ticket log)
        note: Short one-liner for the activity log (optional — truncated to 60 chars)
        tokens: Token count used for this task (optional — accumulated in builder_tokens)

    Returns: Updated Ticket object | Error
    """
    result = find_ticket(ticket_id)
    if not result:
        return err(f"ticket '{ticket_id}' not found")
    team, path = result
    ticket = parse_ticket(team, path)

    if ticket["status"] != "InProgress":
        return err(f"ticket is '{ticket['status']}', expected 'InProgress'")

    new_builder_tokens = ticket["builder_tokens"] + tokens
    started  = datetime.strptime(ticket["updated"], "%Y-%m-%d %H:%M:%S")
    duration = int((datetime.now() - started).total_seconds())
    content  = path.read_text()

    if not ticket["need_qa"]:
        # Skip QA — auto-complete to Done
        content = update_frontmatter(content, {"status": "Done", "updated": now_ts(), "builder_tokens": new_builder_tokens})
        auto_done_text = f"{summary}\n\n_QA not required — ticket auto-completed on submit._"
        content = append_log_block(content, "auto_done", by_agent, auto_done_text, "Done")
        atomic_write(path, content)
        append_activity_log("Builder", team, ticket["ticket_id"], ticket["title"], by_agent, "Auto-Done", note or summary, tokens, duration)
    else:
        # Normal flow — send to QA
        content = update_frontmatter(content, {"status": "QAReview", "updated": now_ts(), "builder_tokens": new_builder_tokens})
        content = append_log_block(content, "builder", by_agent, summary, "QAReview")
        atomic_write(path, content)
        append_activity_log("Builder", team, ticket["ticket_id"], ticket["title"], by_agent, "Submitted", note or summary, tokens, duration)

    return json.dumps(parse_ticket(team, path), indent=2)


@mcp.tool()
def start_review(ticket_id: str, by_agent: str) -> str:
    """
    Claim a QAReview ticket and log that review has started.
    Status stays QAReview — no transition.

    Args:
        ticket_id: e.g. "TCK-UX-001"
        by_agent: QA agent identifier

    Returns: Updated Ticket object | Error
    """
    result = find_ticket(ticket_id)
    if not result:
        return err(f"ticket '{ticket_id}' not found")
    team, path = result
    ticket = parse_ticket(team, path)

    if ticket["status"] != "QAReview":
        return err(f"ticket is '{ticket['status']}', expected 'QAReview'")

    content = path.read_text()
    content = update_frontmatter(content, {"updated": now_ts()})
    content = append_log_block(content, "qa", by_agent, "QA review started.")
    atomic_write(path, content)

    append_activity_log("QA", team, ticket["ticket_id"], ticket["title"], by_agent, "QA Started")

    return json.dumps(parse_ticket(team, path), indent=2)


@mcp.tool()
def review_pass(ticket_id: str, by_agent: str, notes: str, note: str = "", tokens: int = 0) -> str:
    """
    QA approved — set ticket to Done.

    Args:
        ticket_id: e.g. "TCK-UX-001"
        by_agent: QA agent identifier
        notes: Detailed review notes (written into ticket log)
        note: Short one-liner for the activity log (optional — truncated to 60 chars)
        tokens: Token count used for this review (optional — accumulated in qa_tokens)

    Returns: Updated Ticket object | Error
    """
    result = find_ticket(ticket_id)
    if not result:
        return err(f"ticket '{ticket_id}' not found")
    team, path = result
    ticket = parse_ticket(team, path)

    if ticket["status"] != "QAReview":
        return err(f"ticket is '{ticket['status']}', expected 'QAReview'")

    new_qa_tokens = ticket["qa_tokens"] + tokens
    started  = datetime.strptime(ticket["updated"], "%Y-%m-%d %H:%M:%S")
    duration = int((datetime.now() - started).total_seconds())
    content  = path.read_text()
    content  = update_frontmatter(content, {"status": "Done", "updated": now_ts(), "qa_tokens": new_qa_tokens})
    clean_notes = re.sub(r"^(PASS|FAIL)\s*[—\-]\s*", "", notes, flags=re.IGNORECASE).strip()
    content  = append_log_block(content, "qa", by_agent, f"PASS — {clean_notes}", "Done")
    atomic_write(path, content)

    append_activity_log("QA", team, ticket["ticket_id"], ticket["title"], by_agent, "QA Pass", note or notes, tokens, duration)

    return json.dumps(parse_ticket(team, path), indent=2)


@mcp.tool()
def review_reopen(ticket_id: str, by_agent: str, issues: str, note: str = "", tokens: int = 0) -> str:
    """
    QA failed — set ticket to ReOpen and increment reopen_count.
    Escalates automatically if reopen_count exceeds the limit (circuit breaker).

    Args:
        ticket_id: e.g. "TCK-UX-001"
        by_agent: QA agent identifier
        issues: Detailed description of what failed and needs to be fixed (written into ticket log)
        note: Short one-liner for the activity log (optional — truncated to 60 chars)
        tokens: Token count used for this review (optional — accumulated in qa_tokens)

    Returns: Updated Ticket object | Error
    """
    result = find_ticket(ticket_id)
    if not result:
        return err(f"ticket '{ticket_id}' not found")
    team, path = result
    ticket = parse_ticket(team, path)

    if ticket["status"] != "QAReview":
        return err(f"ticket is '{ticket['status']}', expected 'QAReview'")

    content = path.read_text()
    new_count     = ticket["reopen_count"] + 1
    new_qa_tokens = ticket["qa_tokens"] + tokens
    started       = datetime.strptime(ticket["updated"], "%Y-%m-%d %H:%M:%S")
    duration      = int((datetime.now() - started).total_seconds())

    # Circuit breaker — escalate instead of reopening past the limit
    if new_count > REOPEN_LIMIT:
        content = update_frontmatter(content, {"status": "Escalated", "updated": now_ts(), "reopen_count": new_count, "qa_tokens": new_qa_tokens})
        content = add_tag(content, "escalated")
        content = append_log_block(
            content, "escalated", by_agent,
            f"ESCALATED — Reopen limit ({REOPEN_LIMIT}) exceeded. Requires human intervention. Last issue: {issues}",
            "Escalated",
        )
        atomic_write(path, content)
        append_activity_log("QA", team, ticket["ticket_id"], ticket["title"], by_agent, "Escalated", note or issues, tokens, duration)
        return json.dumps(parse_ticket(team, path), indent=2)

    content = update_frontmatter(content, {"status": "ReOpen", "updated": now_ts(), "reopen_count": new_count, "qa_tokens": new_qa_tokens})
    clean_issues = re.sub(r"^(PASS|FAIL)\s*[—\-]\s*", "", issues, flags=re.IGNORECASE).strip()
    content = append_log_block(content, "qa", by_agent, f"FAIL — {clean_issues}", "ReOpen")
    atomic_write(path, content)

    append_activity_log("QA", team, ticket["ticket_id"], ticket["title"], by_agent, f"QA Fail (r{new_count})", note or issues, tokens, duration)

    return json.dumps(parse_ticket(team, path), indent=2)


@mcp.tool()
def open_all_tickets(team: str, by: str = "pm-agent") -> str:
    """
    Open all Backlog tickets for a team in one call.
    Used by PM after human has reviewed and approved all tickets in Obsidian.

    Args:
        team: team name (e.g. "ux", "app", "deploy")
        by: Who is opening the tickets (default: "pm-agent")

    Returns: List of opened ticket IDs | Error
    """
    if e := validate_team(team):
        return err(e)

    folder = tickets_dir(team)
    if not folder.exists():
        return json.dumps([])

    opened = []
    for f in sorted(folder.glob("*.md")):
        content = f.read_text()
        fm_m = re.match(r"^---\n(.*?\n)---", content, re.DOTALL)
        if not fm_m:
            continue
        s_m = re.search(r"^status:\s*(.+)$", fm_m.group(1), re.MULTILINE)
        if not s_m or s_m.group(1).strip() != "Backlog":
            continue

        content = update_frontmatter(content, {"status": "Open", "updated": now_ts()})
        content = append_log_block(content, "open", by, "Ticket opened and ready for execution.", "Open")
        atomic_write(f, content)

        title_m = re.search(r"#\s*🎫\s*Ticket:\s*\[([^\]]+)\]\s*(.+)", content)
        tid   = title_m.group(1).strip() if title_m else f.stem
        tname = title_m.group(2).strip() if title_m else f.stem
        opened.append(tid)
        append_activity_log("Builder", team, tid, tname, by, "Opened")

    return json.dumps({"opened": opened, "count": len(opened)}, indent=2)


# ---------------------------------------------------------------------------
# Agent Management Tools
# ---------------------------------------------------------------------------

def _agent_cpu(pid: int) -> float:
    """Sample CPU usage of a process twice and return the higher value."""
    import time
    def sample(pid):
        r = subprocess.run(
            ["ps", "-p", str(pid), "-o", "%cpu="],
            capture_output=True, text=True
        )
        return float(r.stdout.strip() or "0")
    cpu1 = sample(pid)
    time.sleep(0.5)
    cpu2 = sample(pid)
    return max(cpu1, cpu2)


def _runtime_pid_file(team: str, runtime: str) -> Path:
    """Return the PID file path for one team/runtime pair."""
    return PIDS_DIR / f"{team}-{runtime}-agent.pid"


def _runtime_launch_file(team: str, runtime: str) -> Path:
    """Return the launch script path for one team/runtime pair."""
    return PIDS_DIR / f"{team}-{runtime}-launch.sh"


def _applescript_string(value: str) -> str:
    """Escape a shell command so it can be embedded in an AppleScript string."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _get_runtime_agent_status(team: str, runtime: str) -> str:
    """Get status for one team/runtime agent process."""
    if e := validate_team(team):
        return err(e)
    if e := validate_runtime(runtime):
        return err(e)

    pid_file = _runtime_pid_file(team, runtime)

    if not pid_file.exists():
        return json.dumps({"team": team, "runtime": runtime, "agent_status": "not_running"})

    pid = int(pid_file.read_text().strip())
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return json.dumps({"team": team, "runtime": runtime, "pid": pid, "agent_status": "dead"})
    except PermissionError:
        return json.dumps({"team": team, "runtime": runtime, "pid": pid, "agent_status": "running_unknown"})

    cpu = _agent_cpu(pid)
    agent_status = "busy" if cpu > 5.0 else "idle"

    return json.dumps({"team": team, "runtime": runtime, "pid": pid, "cpu": round(cpu, 1), "agent_status": agent_status})


DRAIN_PROMPT = (
    "Give your short startup greeting from AGENTS.md, then drain the ticket queue: "
    "Builder then QA, one ticket at a time."
)
INTERACTIVE_PROMPT = (
    "Give your short startup greeting from AGENTS.md, then check Messages/inbox.md "
    "and wait for human instructions."
)


def _launch_terminal_agent(team: str, runtime: str, command: list[str], drain: bool) -> str:
    """Launch a runtime agent in Terminal and track it with a runtime-specific PID file."""
    if e := validate_team(team):
        return err(e)
    if e := validate_runtime(runtime):
        return err(e)

    workspace = VAULT_ROOT / team
    pid_file  = _runtime_pid_file(team, runtime)
    PIDS_DIR.mkdir(exist_ok=True)

    # Check if already running
    if pid_file.exists():
        pid = int(pid_file.read_text().strip())
        try:
            os.kill(pid, 0)
            return json.dumps({"team": team, "runtime": runtime, "pid": pid, "status": "already_running"})
        except ProcessLookupError:
            pid_file.unlink()
        except PermissionError:
            return json.dumps({"team": team, "runtime": runtime, "pid": pid, "status": "already_running"})

    prompt = DRAIN_PROMPT if drain else INTERACTIVE_PROMPT
    launch_file = _runtime_launch_file(team, runtime)
    agent_cmd = shlex.join([*command, prompt])
    launch_file.write_text(
        f"#!/bin/bash\n"
        f"echo $$ > {shlex.quote(str(pid_file))}\n"
        f"exec {agent_cmd}\n"
    )
    launch_file.chmod(0o755)

    shell_cmd = f"cd {shlex.quote(str(workspace))} && {shlex.quote(str(launch_file))}"
    script = (
        f'tell application "Terminal" to do script '
        f'"{_applescript_string(shell_cmd)}"\n'
        f'tell application "Terminal" to activate'
    )
    subprocess.run(["osascript", "-e", script], check=True)

    mode = "drain" if drain else "interactive"
    return json.dumps({"team": team, "runtime": runtime, "status": "starting", "mode": mode, "pid_file": str(pid_file)})


def _start_claude_agent(team: str, drain: bool = True) -> str:
    """Start a Claude Code agent for a team."""
    return _launch_terminal_agent(team, "claude", [str(CLAUDE_BIN)], drain)


def _start_codex_agent(team: str, drain: bool = True) -> str:
    """Start a Codex agent for a team in autonomous YOLO mode."""
    return _launch_terminal_agent(team, "codex", [CODEX_BIN, "--dangerously-bypass-approvals-and-sandbox"], drain)


def _stop_runtime_agent(team: str, runtime: str) -> str:
    """Stop one team/runtime agent process."""
    if e := validate_team(team):
        return err(e)
    if e := validate_runtime(runtime):
        return err(e)

    pid_file = _runtime_pid_file(team, runtime)

    if not pid_file.exists():
        return err(f"no running {runtime} agent found for team '{team}'")

    pid = int(pid_file.read_text().strip())

    try:
        os.kill(pid, 15)  # SIGTERM — graceful shutdown
        pid_file.unlink()
        return json.dumps({"team": team, "runtime": runtime, "pid": pid, "status": "stopped"})
    except ProcessLookupError:
        pid_file.unlink()
        return json.dumps({"team": team, "runtime": runtime, "pid": pid, "status": "was_not_running"})
    except PermissionError:
        return err(f"permission denied stopping {runtime} agent for team '{team}'")


@mcp.tool()
def get_agent_status(team: str, runtime: str) -> str:
    """
    Get the current status of a team agent for a selected runtime.

    Uses CPU usage as the signal:
      - ~0% CPU → idle (waiting at the prompt)
      - >5% CPU  → busy (actively processing a ticket)

    Args:
        team: team name (e.g. "ux", "app")
        runtime: agent runtime — "codex" or "claude"

    Returns: { team, runtime, pid, cpu, agent_status } | Error
      agent_status: "idle" | "busy" | "dead" | "not_running" | "running_unknown"
    """
    return _get_runtime_agent_status(team, runtime)


@mcp.tool()
def start_agent(team: str, runtime: str, drain: bool = True) -> str:
    """
    Start a team agent for a selected runtime by opening a Terminal window.
    Saves the agent PID to .pids/<team>-<runtime>-agent.pid.

    Args:
        team: team name (e.g. "ux", "app")
        runtime: agent runtime — "codex" or "claude"
        drain: True (default) — agent starts with a prompt to drain the ticket queue automatically.
               False — agent starts in interactive mode, waiting for human input.

    Returns: { team, runtime, status, mode } | Error
    """
    if runtime == "claude":
        return _start_claude_agent(team, drain)
    if runtime == "codex":
        return _start_codex_agent(team, drain)
    return err("runtime required: codex or claude")


@mcp.tool()
def stop_agent(team: str, runtime: str) -> str:
    """
    Stop a running team agent by terminating its process.

    Args:
        team: team name (e.g. "ux", "app")
        runtime: agent runtime — "codex" or "claude"

    Returns: { team, runtime, pid, status } | Error
    """
    return _stop_runtime_agent(team, runtime)


@mcp.tool()
def list_agents() -> str:
    """
    List all known team agents and their running status.

    Returns: [{ team, runtime, pid, status }]
    """
    PIDS_DIR.mkdir(exist_ok=True)
    results = []

    for pid_file in sorted(PIDS_DIR.glob("*-agent.pid")):
        m = re.match(r"^(.+)-(claude|codex)-agent$", pid_file.stem)
        if m:
            team, runtime = m.group(1), m.group(2)
        else:
            team, runtime = pid_file.stem.replace("-agent", ""), "legacy"
        pid  = int(pid_file.read_text().strip())
        try:
            os.kill(pid, 0)
            status = "running"
        except ProcessLookupError:
            status = "dead"
        except PermissionError:
            status = "running_unknown"

        results.append({"team": team, "runtime": runtime, "pid": pid, "status": status})

    return json.dumps(results, indent=2)


if __name__ == "__main__":
    mcp.run()
