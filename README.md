# TCK — Ticket Control Kit

*Structure for AI agents. Context for every decision. Quality on every output.*

TCK is a structured workflow system for human-AI teams. The PM agent reads your documents, breaks work into grounded tickets, and routes them through builders and QA — with every action logged and every decision traceable.

---

## How It Works

- Tickets are Markdown files stored flat in `<team>/Tickets/`
- Status is tracked via Obsidian **frontmatter properties** (`status:`) — no folder moves
- Tags are written automatically: `tck` (system) + `team/<name>` (ownership) + `escalated` (circuit breaker)
- All agent interactions go through the **`ticket-mcp` MCP server**
- Activity logs are written to `Ticket Logs/` — one Builder log and one QA log per team
- Obsidian **Bases** provides a Kanban board view grouped by `status`

---

## Folder Structure

```
<project>/
├── mcp/
│   ├── server.py                     # MCP server — all ticket logic lives here
│   └── requirements.txt
├── Documents/                        # Customer docs — briefs, specs, notes, reference
│   ├── 0 PROJECT_CORE/               # Foundational files: project description, customer personas
│   ├── 1 Inbox/                      # Drop anything here — PM will help categorise
│   ├── 2 Projects/                   # Every piece of work gets a folder (YYMM [BUG|FIX] Name/)
│   │   ├── 2604 Login Redesign/      # scope.md + wireframes, photos, refs
│   │   ├── 2604 BUG Login Crash/     # bug-report.md + screenshots, logs
│   │   └── 2604 FIX Cart Rounding/   # fix-brief.md + any refs
│   ├── 3 Areas/                      # Standards the team MUST follow — no end date, breaking = consequences
│   │   ├── Brand/                    # Customer logo, colours, fonts — required in every UI ticket
│   │   ├── Database/                 # Approved ER diagram + schema notes — all dev tickets must match
│   │   ├── Design System/            # Component rules, tokens, spacing
│   │   ├── API Contracts/            # Endpoint specs, auth rules, versioning
│   │   ├── Coding Standards/         # Language conventions, patterns, linting
│   │   └── SLAs/                     # Client agreements, uptime targets, response times
│   ├── 4 Resources/                  # Reference only — external docs, research, inspiration (no obligation)
│   └── 5 Archives/                   # Finished scopes, old specs, superseded standards
├── Templates/
│   └── Ticket Template.md            # Reference template for manually created tickets
├── Ticket Logs/                      # Activity logs — auto-created
│   ├── ALL.md                        # Every entry across all teams (with Team column)
│   ├── ux/
│   │   ├── TCK-UX-Builder.md
│   │   └── TCK-UX-QA.md
│   ├── app/
│   │   ├── TCK-APP-Builder.md
│   │   └── TCK-APP-QA.md
│   └── deploy/
│       ├── TCK-DEPLOY-Builder.md
│       └── TCK-DEPLOY-QA.md
├── AGENTS.md                         # PM Agent identity — open Codex here to act as PM
├── CLAUDE.md                         # Claude compatibility pointer to AGENTS.md
├── TICKET_AGENTS_RULES.md            # Shared rules imported by all team AGENTS.md files
├── ux/
│   ├── AGENTS.md                     # UX Agent identity, standards, boundaries
│   ├── CLAUDE.md                     # Claude compatibility pointer
│   ├── Tickets/                      # Ticket specs — written by humans in Obsidian
│   ├── Artifacts/                    # Agent deliverables: HTML, specs, design files
│   └── TicketAttachments/            # Agent notes: summaries, QA reports, decision logs
├── app/
│   ├── AGENTS.md                     # Developer Agent identity, standards, boundaries
│   ├── CLAUDE.md                     # Claude compatibility pointer
│   ├── Tickets/
│   ├── Artifacts/                    # Agent deliverables: code, scripts, configs
│   └── TicketAttachments/
├── deploy/
│   ├── AGENTS.md                     # DevOps Agent identity, standards, boundaries
│   ├── CLAUDE.md                     # Claude compatibility pointer
│   ├── Tickets/
│   ├── Artifacts/                    # Agent deliverables: pipeline configs, infra files
│   └── TicketAttachments/
└── README.md
```

> **Adding a new team:** create `<teamname>/Tickets/` — the MCP server and log system auto-discover it.

---

## Agent Setup

### Recommended Multi-Window Layout

The intended workflow uses three tools open simultaneously:

| Window | Tool | Opens at | Role |
|---|---|---|---|
| 1 | **Obsidian** | `<project>/` (vault root) | Human writes tickets, attaches images, adds links |
| 2 | **Codex or Claude** | `<project>/` | PM agent — creates and opens tickets |
| 3 | **Codex or Claude** | `<project>/ux/` | UX agent — reads specs, does the work, submits via MCP |

Each team gets its own agent-runtime window opened at that team's folder. Multiple agents can run in parallel across different windows.

---

### How an Agent Knows Its Role

When Codex opens inside a team folder, it reads that folder's `AGENTS.md`. When Claude opens inside a team folder, it reads `CLAUDE.md`, which points to `AGENTS.md`. Each team `AGENTS.md` contains:

```
@../TICKET_AGENTS_RULES.md   ← shared: workflow, MCP tools, agent flow, file reading rules
```

followed by team-specific content:

- Which team the agent belongs to (`team="ux"`)
- What kind of work it does (UX, engineering, DevOps)
- Team-specific quality standards
- Boundaries (what it must not touch)

The `@` directive brings in the shared rules so the agent gets the common workflow and its own team identity in one load. The folder you open in determines the agent's identity.

---

### Read vs Write — The Core Rule

| Action | How |
|---|---|
| **Read ticket spec** | Directly from `Tickets/<ticket_id>*.md` |
| **Change ticket state** | MCP tools only — never touch the file |

Ticket files are the **spec** — humans write them in Obsidian with full Markdown: images, links, Figma references, wiki links to other notes. Agents read these files to get full context.

The MCP server is the **state machine** — the only way to change `status`, log entries, or token counts.

```
Human (Obsidian)        Agent runtime in team folder
      │                           │
      │  writes rich spec         │  reads Tickets/*.md for full context
      ▼                           │  ──────────────────────────────────
  Ticket file  ◄─────────────────┘
                                  │  calls MCP tools for state changes
                                  ▼
                            ticket-mcp server
```

---

### Agent Flow — Step by Step

**1. Get the next ticket**
```
ticket = get_next_ticket(team="ux")
```

**2. Read the full ticket file for context**
```
# Tickets/ folder is in the working directory
# Find: Tickets/TCK-UX-2604-001 Login Page Redesign.md
# Read it — see images, Figma links, design refs, all PM notes
```

**3. Claim it**
```
execute_ticket(ticket_id, by_agent="ux-agent")
```

**4. Do the work, then submit**
```
submit_work(
    ticket_id, by_agent="ux-agent",
    summary="What was done...",
    note="Short one-liner for the log",
    tokens=4200
)
# need_qa: true  → goes to QAReview (default)
# need_qa: false → goes directly to Done (Auto-Done, no QA step)
```

**5. QA agent picks it up**
```
ticket = get_next_ticket_for_review(team="ux")
start_review(ticket_id, by_agent="ux-qa")

review_pass(ticket_id, by_agent="ux-qa", notes="...", tokens=1500)
# or
review_reopen(ticket_id, by_agent="ux-qa", issues="...", tokens=1500)
```

---

### Writing Rich Ticket Specs in Obsidian

Since agents read the full ticket file, the PM can include anything Obsidian supports:

```markdown
## 🎯 1. The Goal

Redesign the login page for better accessibility.

**Current state:**
![[login-current.png]]

**Reference design:**
![[login-figma-mockup.png]]

**Links:**
- [Figma file](https://figma.com/...)
- [[UX/Components/Form Fields]]
- [WCAG AA contrast checker](https://webaim.org/resources/contrastchecker/)

### ✅ DO
- Follow design system tokens for colors and spacing
- Add visible focus states on all inputs

### ❌ DON'T DO
- Don't use placeholder text as labels
```

The agent reads this file after `get_next_ticket` and sees everything — no information is lost.

---

## Setup on a New Machine

### 1. Prerequisites

| Requirement | Version | Mac/Linux check | Windows check |
|---|---|---|---|
| Python | 3.10+ | `python3 --version` | `python --version` |
| pip | any | `pip3 --version` | `pip --version` |
| Obsidian | latest | [obsidian.md](https://obsidian.md) | [obsidian.md](https://obsidian.md) |
| Claude Desktop | latest | [claude.ai/download](https://claude.ai/download) | [claude.ai/download](https://claude.ai/download) |

### 2. Copy the vault

Clone or copy the `<project>/` folder to your machine. The vault can live anywhere — just note the full path.

**Mac / Linux**
```bash
git clone <repo-url> ~/<project>
```

**Windows (PowerShell)**
```powershell
git clone <repo-url> C:\<project>
```

### 3. Install Python dependencies

**Mac / Linux**
```bash
cd ~/<project>/mcp
pip3 install -r requirements.txt
```

**Windows (PowerShell)**
```powershell
cd C:\<project>\mcp
pip install -r requirements.txt
```

Verify it works:

**Mac / Linux**
```bash
python3 ~/<project>/mcp/server.py
```
**Windows**
```powershell
python C:\<project>\mcp\server.py
```

Both should exit cleanly with no import errors.

### 4. Find your Python path

The Claude Desktop config needs the **full path** to your Python binary.

**Mac / Linux**
```bash
which python3
```

**Windows (PowerShell)**
```powershell
where.exe python
# or
(Get-Command python).Source
```

Common paths by environment:

| OS / Environment | Command | Typical path |
|---|---|---|
| Mac — Homebrew | `which python3` | `/opt/homebrew/bin/python3` |
| Mac — system | `which python3` | `/usr/bin/python3` |
| Mac — pyenv | `which python3` | `~/.pyenv/shims/python3` |
| Linux | `which python3` | `/usr/bin/python3` |
| Windows — installer | `where.exe python` | `C:\Users\<you>\AppData\Local\Programs\Python\Python311\python.exe` |
| Windows — Microsoft Store | `where.exe python` | `C:\Users\<you>\AppData\Local\Microsoft\WindowsApps\python.exe` |
| Windows — pyenv-win | `where.exe python` | `C:\Users\<you>\.pyenv\pyenv-win\shims\python.exe` |

### 5. Register the MCP server in Claude Desktop

Open (or create) the config file:

| OS | Path |
|---|---|
| Mac | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

**Mac / Linux**
```json
{
  "mcpServers": {
    "ticket-mcp": {
      "command": "/opt/homebrew/bin/python3",
      "args": ["/Users/yourname/<project>/mcp/server.py"]
    }
  }
}
```

**Windows**
```json
{
  "mcpServers": {
    "ticket-mcp": {
      "command": "C:\\Users\\yourname\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
      "args": ["C:\\<project>\\mcp\\server.py"]
    }
  }
}
```

> **Windows tip:** Use double backslashes `\\` in JSON paths, or forward slashes `/` — both work.

### 6. Open the vault in Obsidian

1. Open Obsidian → **Open folder as vault**
2. Select the `<project>/` folder
3. Enable **Bases** core plugin: Settings → Core plugins → Bases → toggle on

### 7. Restart Claude Desktop

After saving the config, fully quit and relaunch Claude Desktop. A **hammer icon** in the chat input confirms the MCP server is connected.

### 8. Verify

In a Claude Desktop chat, ask:

> "List all teams using ticket-mcp"

You should see `ux`, `app`, `deploy` returned.

---

## Ticket Workflow

```
Backlog ──► Open ──► InProgress ──► QAReview ──► Done
                          │              │
                          │ (need_qa:    ▼ (QA fail)
                          │  false)   ReOpen ──► InProgress
                          ▼              │
                         Done            ▼ (fail > 4 times)
                      (Auto-Done)    Escalated 🔒
```

| Status | Meaning |
|---|---|
| `Backlog` | Created, not yet ready to work |
| `Open` | Ready for an agent to pick up |
| `InProgress` | Agent is actively working |
| `QAReview` | Work submitted, awaiting QA |
| `Done` | QA approved ✅ |
| `ReOpen` | QA failed, needs rework ❌ |
| `Escalated` | Failed QA more than 4 times — requires human intervention ⚠️ |

---

## Ticket Frontmatter

Every ticket is created with the following frontmatter fields:

```yaml
---
status: Backlog
reopen_count: 0
builder_tokens: 0
qa_tokens: 0
need_qa: true
created: 2026-04-17 17:00:00
updated: 2026-04-17 17:00:00
tags: [tck, team/app]
---
```

| Field | Description |
|---|---|
| `status` | Current workflow status |
| `reopen_count` | Number of times QA has failed the ticket |
| `builder_tokens` | Total tokens used by builder agents across all submissions |
| `qa_tokens` | Total tokens used by QA agents across all reviews |
| `need_qa` | `true` (default) — requires QA review. `false` — auto-completes to Done on `submit_work` |
| `created` / `updated` | Timestamps with seconds |

---

## Ticket Sections

Every ticket has 3 sections:

| Section | Filled by | When |
|---|---|---|
| **1. The Goal** — objective, DO, DON'T DO | PM / creator | At creation |
| **2. Watch Points (For QA)** — what QA should pay special attention to | PM | Before `open_ticket` — leave placeholder if nothing special |
| **3. Execution & Audit Log** | MCP server | Automatically on each status transition |

---

## Ticket Tags

Every ticket carries tags set automatically at creation:

| Tag | Meaning |
|---|---|
| `tck` | Identifies the file as a system ticket — filter all tickets across all teams |
| `team/ux` | Team ownership — filter by team |
| `team/app` | |
| `team/deploy` | |
| `escalated` | Added by circuit breaker — filter blocked tickets needing human review |

**In Obsidian Tags panel:**
- `#tck` → every ticket in the system
- `#team/ux` → only UX tickets
- `#escalated` → all blocked tickets

New teams get `team/<name>` automatically — no code changes needed.

---

## MCP Tools Reference

### Discovery

| Tool | Description |
|---|---|
| `list_teams()` | List all teams auto-discovered from the vault |
| `list_tickets(team, status?)` | List tickets, optionally filtered by status |
| `get_ticket(ticket_id)` | Get full ticket details by ID |
| `get_next_ticket(team)` | Get the next `Open` ticket (falls back to `ReOpen`) |
| `get_next_ticket_for_review(team)` | Get the next `QAReview` ticket |

### Messaging

| Tool | Description |
|---|---|
| `send_message(team, message)` | Write a message to a team agent's inbox (`<team>/Messages/inbox.md`). The agent reads it at the start of its next session, acts on it, then clears it. If the inbox already has an unread message, the new one is appended — nothing is overwritten. |

Use `send_message` to redirect priorities, send context mid-session, or unblock an agent without waiting for a ticket update.

```python
# Examples
send_message("ux", "Stop current work — pick up TCK-UX-2604-007 first, client is waiting.")
send_message("app", "The auth spec changed. Re-read Documents/2 Projects/2604 Login Redesign/scope.md before continuing.")
send_message("ux", "QA reopen on TCK-UX-2604-003 can be ignored — that requirement was dropped by the client.")
```

### Workflow

| Tool | Transition | Who |
|---|---|---|
| `create_ticket(team, title, goal, dos, donts, ticket_id?, watch_points?, need_qa?)` | → `Backlog` | PM / orchestrator |
| `open_ticket(ticket_id, by)` | `Backlog` → `Open` | PM / orchestrator |
| `open_all_tickets(team, by?)` | All `Backlog` → `Open` | PM / orchestrator |
| `execute_ticket(ticket_id, by_agent)` | `Open`/`ReOpen` → `InProgress` | Builder agent |
| `submit_work(ticket_id, by_agent, summary, note?, tokens?)` | `InProgress` → `QAReview` or `Done` | Builder agent |
| `start_review(ticket_id, by_agent)` | stays `QAReview` | QA agent |
| `review_pass(ticket_id, by_agent, notes, note?, tokens?)` | `QAReview` → `Done` | QA agent |
| `review_reopen(ticket_id, by_agent, issues, note?, tokens?)` | `QAReview` → `ReOpen` | QA agent |

**Optional parameters:**
- `note` — short one-liner for the activity log (truncated to 60 chars). Falls back to `summary`/`notes`/`issues` if omitted.
- `tokens` — token count used for the task or review. Accumulated into `builder_tokens` / `qa_tokens` on the ticket frontmatter.

### Ticket IDs

Auto-generated in `TCK-<TEAM>-YYMM-SEQ` format. Sequence resets each month.

| Team | Example ID |
|---|---|
| ux | `TCK-UX-2604-001` |
| app | `TCK-APP-2604-001` |
| deploy | `TCK-DEPLOY-2604-001` |

### Example: Creating a Blank Ticket to Fill in Manually

Paste this into Claude Desktop chat — replace `app` and the title:

```
Create a blank ticket in the app team with title "Your Title Here".
Use placeholder text for the goal, dos, and donts so I can fill them in manually in Obsidian.
Do not open it yet.
```

Claude Desktop will create the ticket in `Backlog` status. Open the file in Obsidian and edit:
- **The Goal** — describe what needs to be achieved
- **DO** — list requirements and allowed behaviors
- **DON'T DO** — list constraints and prohibited behaviors
- **Watch Points (For QA)** — optional, fill in anything QA should pay special attention to before opening

When ready, open it for agents with:
```
Open ticket TCK-APP-2604-001
```

### Example: Creating a Full Ticket in Claude Desktop

Paste this into Claude Desktop chat:

```
Create a ticket for the app team:
- Title: User Profile API
- Goal: Build a GET /api/profile endpoint that returns the authenticated user's name, email, and avatar URL
- DO: require JWT auth, return 401 if missing or invalid, return consistent JSON field names
- DON'T: expose password hash or sensitive fields, allow unauthenticated access, add extra endpoints, modify the user record

Then open it so agents can pick it up.
```

Claude Desktop will call `create_ticket(...)` then `open_ticket(...)` automatically.

---

## Typical Agent Loop

### Builder Agent
```
ticket = get_next_ticket(team="app")
if not ticket: stop — nothing to work on

execute_ticket(ticket_id, by_agent="app-agent")
# ... do the work ...
submit_work(
    ticket_id, by_agent="app-agent",
    summary="Detailed description of what was done...",
    note="Short one-liner for the log",
    tokens=4200
)
# Automatically routes based on ticket's need_qa field:
#   need_qa: true  → QAReview
#   need_qa: false → Done (Auto-Done)
```

### QA Agent
```
ticket = get_next_ticket_for_review(team="app")
if not ticket: stop — nothing to review

start_review(ticket_id, by_agent="app-qa")
# ... review the work ...

# if approved:
review_pass(
    ticket_id, by_agent="app-qa",
    notes="All checks passed. No issues found.",
    note="Short one-liner for the log",
    tokens=1500
)

# if issues found:
review_reopen(
    ticket_id, by_agent="app-qa",
    issues="What failed and why.",
    note="Short one-liner for the log",
    tokens=1500
)
```

---

## Activity Logs

Every tool call appends a row to both `Ticket Logs/<team>/TCK-<TEAM>-Builder.md` (or QA) and `Ticket Logs/ALL.md`. Logs are newest-on-top.

**Team log format:**

| # | Ticket ID | Ticket Name | Agent | Action | Tokens | Time | Note | Datetime |
|---|---|---|---|---|---|---|---|---|
| ● | [[TCK-UX-2604-006 Login Page\|TCK-UX-2604-006]] | Login Page | ux-agent | Submitted | 3,850 | 1m 12s | login.html built, WCAG AA | 2026-04-18 09:00:01 |
| ● | [[TCK-UX-2604-006 Login Page\|TCK-UX-2604-006]] | Login Page | ux-agent | Claimed | | | | 2026-04-18 08:58:49 |

**ALL.md format** (adds Team column):

| # | Team | Ticket ID | Ticket Name | Agent | Action | Tokens | Time | Note | Datetime |
|---|---|---|---|---|---|---|---|---|---|
| ● | ux | [[TCK-UX-2604-006 Login Page\|TCK-UX-2604-006]] | Login Page | ux-agent | Submitted | 3,850 | 1m 12s | login.html built, WCAG AA | 2026-04-18 09:00:01 |
| ○ | app | [[TCK-APP-2604-001 Auth API\|TCK-APP-2604-001]] | Auth API | app-agent | Submitted | 2,940 | 45s | JWT RS256, refresh token | 2026-04-18 08:55:10 |

- **`#` column** — `●`/`○` alternates each time the ticket ID changes, for visual grouping
- **Ticket ID** — wiki link to the ticket file, clickable in Obsidian
- **Tokens** — blank for `Opened`/`Claimed`/`QA Started`; populated on `Submitted`, `QA Pass`, `QA Fail`
- **Time** — automatically calculated by the server (builder: `execute_ticket` → `submit_work`; QA: `start_review` → `review_pass/reopen`)
- **Action values:** `Opened`, `Claimed`, `Claimed (ReOpen r1)`, `Submitted`, `Auto-Done`, `QA Started`, `QA Pass`, `QA Fail (r1)`, `Escalated`

---

## Circuit Breaker

If a ticket is reopened more than **4 times**, the next `review_reopen` call automatically:
- Sets `status: Escalated` — ticket is frozen, no agent can claim it
- Adds `escalated` to the tags list
- Writes a `⚠️` warning log entry
- Requires human intervention to resolve

---

## Audit Log Callout Colors

Every status transition is logged as a callout block in the ticket file using Obsidian callout syntax:

| Event | Callout type | Color |
|---|---|---|
| Ticket opened (`Backlog → Open`) | `[!EXAMPLE]` | Purple |
| Ticket claimed (`Open/ReOpen → InProgress`) | `[!ABSTRACT]` | Teal |
| Work submitted (`InProgress → QAReview`) | `[!INFO]` | Blue |
| Auto-Done (`InProgress → Done`, `need_qa: false`) | `[!CHECK] ✅ AI Builder Feedback` | Green |
| QA started | `[!ABSTRACT]` | Teal |
| QA passed (`QAReview → Done`) | `[!CHECK]` | Green |
| QA failed (`QAReview → ReOpen`) | `[!DANGER]` | Red |
| Escalated (circuit breaker) | `[!WARNING]` | Yellow |

Colors are rendered natively by Obsidian — no plugins or CSS required.

---

## Obsidian Bases Board

To create a Kanban board view for a team:

1. Right-click `<team>/Tickets/` in the file explorer → **New base**
2. Name it e.g. `TCK Board`
3. Add a **Filter** → `tags` contains `tck`
4. Add **Columns** (properties to display on each card):
   - `status`
   - `reopen_count`
   - `builder_tokens`
   - `qa_tokens`
   - `tags`
5. Click **Group by** → select `status`
6. Switch to **Board** view

Columns map to workflow stages automatically via the `status` property.

---

## Adding a New Team

**Mac / Linux**
```bash
mkdir -p ~/<project>/<teamname>/Tickets
```

**Windows**
```powershell
New-Item -ItemType Directory -Path C:\<project>\<teamname>\Tickets -Force
```

Then:
1. Create `AGENTS.md` in the new team folder — copy an existing one as a template. Keep the `@../TICKET_AGENTS_RULES.md` import line; update only the role, standards, and boundaries sections
2. Add `CLAUDE.md` as a pointer to `AGENTS.md` if Claude support is needed
3. Create `Artifacts/`, `TicketAttachments/`, and `Messages/` folders alongside `Tickets/`
4. Add `.codex/config.toml` and/or `.claude/settings.local.json` for the selected runtimes
5. Restart the MCP host if needed
6. The new team appears in `list_teams()` automatically
7. New tickets get `tags: [tck, team/<teamname>]` automatically — no code changes needed
8. Activity logs `TCK-<TEAMNAME>-Builder.md` and `TCK-<TEAMNAME>-QA.md` are created automatically on first use

---

## Troubleshooting

**Hammer icon not showing in Claude Desktop**
- Check the config JSON is valid — no trailing commas, correct brackets
- Mac/Linux: confirm path with `which python3`
- Windows: confirm path with `where.exe python`
- Confirm the server file exists at the path in `args`
- Fully quit Claude Desktop (not just close the window) and relaunch

**`ModuleNotFoundError: mcp`**
- The Python binary in the config is not the one you ran `pip install` with
- Fix: use the exact Python path from `which python3` / `where.exe python` after installing dependencies

**`unknown team` error from MCP tools**
- The vault path in `server.py` is derived from `__file__` — so the folder structure must be intact
- `<project>/mcp/server.py` must sit inside the vault root — do not move `server.py` outside the vault

**Windows: `python` not found in config**
- Use the full absolute path to `python.exe` — Claude Desktop does not inherit your shell `PATH`
- Find it with: `(Get-Command python).Source` in PowerShell

**Tickets not showing in Obsidian Tags panel**
- Obsidian re-indexes on startup — close and reopen the vault
- Or: open the command palette → **Reload app without saving**

**Activity log rows appearing at the bottom instead of top**
- Obsidian may have reformatted the separator row (`|---|` → `| --- |`)
- The server handles this automatically — separator detection is spacing-insensitive
- If it persists, restart the MCP server so it picks up the latest code
