# TCK — PM Agent Setup Guide

This guide gets you from zero to a working PM agent. Follow every step in order.

---

## What You Need

| Tool | Why | Get it |
|---|---|---|
| **Python 3.10+** | Runs the MCP server | [python.org](https://python.org) |
| **Claude Desktop** | Hosts the MCP server; PM agent talks through it | [claude.ai/download](https://claude.ai/download) |
| **Claude Code** | The PM agent itself (and each team agent) | Installed via `npm install -g @anthropic-ai/claude-code` |
| **Obsidian** | Read and write ticket specs, view the Kanban board | [obsidian.md](https://obsidian.md) |

---

## Step 1 — Get the vault

Clone or copy the project folder to your machine. Note the full path — you'll need it in the next steps.

```bash
git clone <repo-url> ~/chain
```

---

## Step 2 — Install Python dependencies

```bash
cd ~/chain/mcp
pip3 install -r requirements.txt
```

Verify it works:

```bash
python3 ~/chain/mcp/server.py
```

It should exit cleanly with no errors. If you see `ModuleNotFoundError`, run `pip3 install mcp` and try again.

---

## Step 3 — Find your Python path

You need the **full path** to your Python binary for Claude Desktop. Don't guess — run this:

**Mac / Linux**
```bash
which python3
```

**Windows (PowerShell)**
```powershell
(Get-Command python).Source
```

Common results:

| Setup | Typical path |
|---|---|
| Mac — Homebrew | `/opt/homebrew/bin/python3` |
| Mac — system | `/usr/bin/python3` |
| Mac — pyenv | `~/.pyenv/shims/python3` |
| Linux | `/usr/bin/python3` |
| Windows — installer | `C:\Users\<you>\AppData\Local\Programs\Python\Python311\python.exe` |
| Windows — Microsoft Store | `C:\Users\<you>\AppData\Local\Microsoft\WindowsApps\python.exe` |

---

## Step 4 — Register the MCP server in Claude Desktop

Open the Claude Desktop config file:

| OS | Path |
|---|---|
| Mac | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

Add this — replace the paths with your actual Python path and vault location:

**Mac / Linux**
```json
{
  "mcpServers": {
    "ticket-mcp": {
      "command": "/opt/homebrew/bin/python3",
      "args": ["/Users/yourname/chain/mcp/server.py"]
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
      "args": ["C:\\chain\\mcp\\server.py"]
    }
  }
}
```

> **Important:** Use the exact Python path from Step 3. Claude Desktop does not inherit your shell's `PATH`.

---

## Step 5 — Restart Claude Desktop

Fully quit Claude Desktop (not just close the window) and relaunch it.

**Verify it connected:** A **hammer icon** appears in the Claude Desktop chat input bar. Click it — you should see tools listed under `ticket-mcp`.

If the hammer icon is missing, see [Troubleshooting](#troubleshooting) below.

---

## Step 6 — Open the vault in Obsidian

1. Open Obsidian → **Open folder as vault**
2. Select the `chain/` folder (the project root)
3. Enable the **Bases** core plugin:
   Settings → Core plugins → Bases → toggle **on**

Obsidian is your interface for reading tickets, viewing attached images, and navigating wiki links.

---

## Step 7 — Open Claude Code as the PM agent

Open a terminal, navigate to the **project root**, and launch Claude Code:

```bash
cd ~/chain
claude
```

Because `chain/` contains `CLAUDE.md` (the PM agent identity file), Claude Code will read it automatically and adopt the PM agent role.

**Verify it loaded:** Ask Claude Code:
> "What is your role?"

It should describe itself as the PM Agent, explain it manages the ticket system, and mention that it reads `Documents/` before creating tickets.

---

## Step 8 — Verify the MCP connection from the PM agent

Inside Claude Code, ask:

> "List all teams"

Claude Code will call `list_teams()` via the MCP server. You should see the existing teams returned (e.g., `ux`, `app`, `deploy`).

If this fails, the MCP server is not connected — check Step 4 and Step 5.

---

## Step 9 — Start team agents

Each team agent is a **separate Codex or Claude runtime window** opened at the team's folder.

```bash
# Codex
cd ~/chain/ux
codex --dangerously-bypass-approvals-and-sandbox

# Claude
cd ~/chain/ux
~/.local/bin/claude
```

Because `ux/AGENTS.md` exists, the Codex window becomes the UX agent automatically. Claude reads `ux/CLAUDE.md`, which points to `ux/AGENTS.md`. The team instructions import `TICKET_AGENTS_RULES.md` and define the UX-specific standards and boundaries.

Open one window per team:

| Team | Folder | Command |
|---|---|---|
| UX | `chain/ux/` | `cd ~/chain/ux && codex --dangerously-bypass-approvals-and-sandbox` |
| App | `chain/app/` | `cd ~/chain/app && codex --dangerously-bypass-approvals-and-sandbox` |
| Deploy | `chain/deploy/` | `cd ~/chain/deploy && codex --dangerously-bypass-approvals-and-sandbox` |

You can also ask the PM to start an agent through MCP, for example `start_agent("ux", "codex")` or `start_agent("ux", "claude")`.

---

## Recommended Window Layout

Run all of these simultaneously:

| Window | Tool | Folder | Purpose |
|---|---|---|---|
| 1 | **Obsidian** | `chain/` | View tickets, attach images, read specs |
| 2 | **Codex or Claude** | `chain/` | PM agent — create and manage tickets |
| 3 | **Codex or Claude** | `chain/ux/` | UX agent |
| 4 | **Codex or Claude** | `chain/app/` | App agent |

---

## First Run — Create a Ticket

Once everything is set up, test the full loop in the PM agent window:

```
Create a ticket for the ux team:
- Title: Test ticket
- Goal: Verify the ticket system is working end-to-end
- DO: Create the ticket and open it
- DON'T: Add any real requirements

Then open it so the UX agent can pick it up.
```

Switch to the UX agent window and ask it to pick up its next ticket. Watch it claim the ticket, do the work, and submit it.

---

## Messaging Team Agents

The PM can send a message to any team agent while it is running. The message lands in the agent's inbox and the agent reads it at the start of its next turn.

In the PM agent window:

```
Send a message to the ux team: "Stop current work — pick up TCK-UX-2604-007 first, client is waiting."
```

The PM calls `send_message("ux", "...")` which writes to `ux/Messages/inbox.md`.

The UX agent reads this at the top of its next session, acts on the instruction, then clears the file.

**When to use it:**
- Redirect priorities mid-session ("Pick up this ticket first")
- Push context the agent needs ("The spec changed — re-read this file")
- Unblock a stalled agent ("Ignore that QA reopen — the requirement was dropped")

**How it stacks:** If the agent hasn't read the inbox yet, new messages are appended — nothing is lost.

---

## Adding a New Team

Ask the PM agent:

```
Scaffold a new team called "web" for frontend development.
```

The PM agent will:
1. Ask whether the team should support Codex, Claude, or both
2. Create `web/Tickets/`, `web/Artifacts/`, `web/TicketAttachments/`, and `web/Messages/`
3. Write `web/AGENTS.md` — tailored to frontend work
4. Add `.codex/config.toml` and/or `.claude/settings.local.json` based on the selected runtime support
5. Give you the runtime-specific command to start the web agent

Then open a new Codex or Claude window at `chain/web/` to start the agent, or ask the PM to call `start_agent("web", "codex")` or `start_agent("web", "claude")`.

---

## Troubleshooting

**Hammer icon missing in Claude Desktop**
- Check the JSON config for syntax errors — no trailing commas, balanced brackets
- Use the exact Python path from `which python3` / `(Get-Command python).Source`
- Confirm `server.py` exists at the path in `args`
- Fully quit Claude Desktop (menu → Quit, not just close) and relaunch

**`ModuleNotFoundError: No module named 'mcp'`**
- The Python binary in the config is not the one you ran `pip install` with
- Run `pip3 install -r requirements.txt` using the exact Python binary in your config:
  ```bash
  /opt/homebrew/bin/python3 -m pip install -r ~/chain/mcp/requirements.txt
  ```

**PM agent doesn't know its role**
- Codex or Claude must be opened at the **project root** (`chain/`) — not a subfolder
- Confirm `chain/AGENTS.md` exists and starts with `# TCK — PM Agent`
- For Claude, confirm `chain/CLAUDE.md` points to `AGENTS.md`
- Reset the runtime session to reload context

**`unknown team` error from MCP tools**
- `mcp/server.py` must be inside the vault root (`chain/mcp/server.py`)
- Do not move `server.py` to a different location

**Team agent picks up wrong tickets**
- Confirm the runtime is opened at the correct team folder (e.g., `chain/ux/`)
- Each agent folder has its own `AGENTS.md` which sets `team="ux"` in all MCP calls

**Windows: path errors in the config**
- Use double backslashes `\\` in JSON, or forward slashes `/` — both work
- Example: `"C:/chain/mcp/server.py"` is valid

---

## File Reference

```
chain/
├── AGENTS.md                   ← PM agent identity — open Codex here
├── CLAUDE.md                   ← Claude compatibility pointer to AGENTS.md
├── TICKET_AGENTS_RULES.md      ← shared rules imported by all team agents
├── PM_DOCUMENTS_GUIDE.md       ← how the PM reads and uses Documents/
├── PM_SCAFFOLDING_GUIDE.md     ← how the PM scaffolds new team workspaces
├── PM_SCOPE_WORKFLOW.md        ← how the PM breaks a scope into tickets
├── SETUP.md                    ← this file
├── README.md                   ← full system reference
├── mcp/
│   ├── server.py               ← MCP server — all ticket logic lives here
│   └── requirements.txt        ← Python dependencies (just `mcp`)
├── Documents/                  ← customer briefs, specs, reference material
├── ux/
│   ├── AGENTS.md               ← UX agent identity — open Codex here
│   ├── CLAUDE.md               ← Claude compatibility pointer to AGENTS.md
│   ├── .codex/
│   │   └── config.toml         ← Codex autonomy profile
│   ├── .claude/
│   │   └── settings.local.json ← pre-authorised permissions (no prompts)
│   ├── Tickets/
│   ├── Artifacts/
│   ├── TicketAttachments/
│   └── Messages/
│       └── inbox.md            ← PM writes here to message the UX agent
├── app/                        ← same structure as ux/
└── deploy/                     ← same structure as ux/
```
