# PM Agent Management Guide

The PM can start, stop, and inspect team agents directly from MCP tools.

---

## Tools

| Tool | Purpose |
|---|---|
| `start_agent(team)` | Open a Terminal window and launch the agent — it drains the ticket queue automatically |
| `get_agent_status(team)` | Check if the agent is idle, busy, dead, or not running |
| `stop_agent(team)` | Gracefully shut down a running agent |
| `list_agents()` | Check which agents are running and their process status |

---

## start_agent

```python
start_agent(team, drain=True)
```

Opens a new Terminal window at `<team>/` and starts the Claude agent.

| `drain` | Behaviour |
|---|---|
| `True` *(default)* | Agent starts with the drain prompt — works Builder + QA for every ticket autonomously |
| `False` | Agent starts in interactive mode — waits at `>` for human input |

- If the agent is **already running**, returns `"status": "already_running"` — no duplicate is launched.
- If the PID file exists but the process is dead, it cleans up and starts fresh.

```python
start_agent("ux")
# → { "team": "ux", "status": "starting", "mode": "drain", "pid_file": ".pids/ux-agent.pid" }

start_agent("ux", drain=False)
# → { "team": "ux", "status": "starting", "mode": "interactive", "pid_file": ".pids/ux-agent.pid" }

start_agent("ux")   # called again while already running
# → { "team": "ux", "pid": 12345, "status": "already_running" }
```

---

## get_agent_status

```python
get_agent_status(team)
```

Returns real-time status using CPU usage as the signal.

```python
get_agent_status("ux")
# → { "team": "ux", "pid": 9801, "cpu": 0.0, "agent_status": "idle" }

get_agent_status("app")
# → { "team": "app", "pid": 9900, "cpu": 72.4, "agent_status": "busy" }
```

| `agent_status` | Meaning |
|---|---|
| `idle` | Process alive, CPU ≈ 0% — finished all tickets, waiting at `>` prompt |
| `busy` | Process alive, CPU > 5% — actively working a ticket |
| `dead` | PID file exists but process is gone — crashed or killed externally |
| `not_running` | No PID file — never started or cleanly stopped |

---

## stop_agent

```python
stop_agent(team)
```

Sends `SIGTERM` (graceful shutdown) to the agent process and removes the PID file.

- If the process is already dead, it cleans up the PID file and returns `"status": "was_not_running"`.

```python
stop_agent("ux")
# → { "team": "ux", "pid": 12345, "status": "stopped" }
```

---

## list_agents

```python
list_agents()
```

Reads all PID files under `.pids/` and checks whether each process is alive.

```python
list_agents()
# → [
#     { "team": "app", "pid": 12346, "status": "running" },
#     { "team": "ux",  "pid": 12345, "status": "dead"    }
#   ]
```

`"dead"` means the PID file exists but the process is gone — run `start_agent` again to restart.

---

## Typical Flow

```python
# Open tickets
open_all_tickets("ux")

# Start agent — it drains the queue automatically
start_agent("ux")

# Check progress — agent does Builder first, then QA
get_agent_status("ux")   # busy while working, idle when done
list_agents()            # overview of all teams

# Shut down when done
stop_agent("ux")
```

---

## When the Agent Goes Idle

The drain runs **once on start**. When the queue is empty the agent stops working and waits at the `>` prompt — it will not pick up new tickets automatically.

**If new tickets arrive after the agent is idle:**
- The PM cannot push work to an idle agent
- Tell the human: *"The agent has finished its queue and is now idle. To process new tickets, type a message in the agent's Terminal window."*
- The human types directly in the Terminal to give the agent its next instruction

**Suggested message to give the human:**
```
The ux agent is idle — all tickets are done.
If you open more tickets and want the agent to pick them up,
type this in the ux Terminal window:

  Drain the ticket queue: Builder then QA, one ticket at a time.
```

To avoid this, `stop_agent` after the queue is empty. Next time tickets are ready, `start_agent` launches fresh with the drain prompt.

---

## Notes

- `start_agent` requires macOS — it uses `osascript` to open Terminal.
- The agent binary is expected at `~/.local/bin/claude`.
- PID files are stored in `<project>/.pids/` — auto-created if the folder doesn't exist.
- `stop_agent` sends `SIGTERM` — the agent finishes its current operation before exiting.
