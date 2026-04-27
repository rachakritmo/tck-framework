# PM Agent Management Guide

The PM can start, stop, and inspect team agents directly from MCP tools. The human chooses the runtime explicitly: **Codex** or **Claude**.

No `.tck.local.json` is used. There is no stored default runtime.

---

## Tools

| Tool | Purpose |
|---|---|
| `start_agent(team, runtime, drain=True)` | Open a Terminal window and launch the selected runtime |
| `get_agent_status(team, runtime)` | Check if that team/runtime agent is idle, busy, dead, or not running |
| `stop_agent(team, runtime)` | Gracefully shut down that team/runtime agent |
| `list_agents()` | Check all tracked team/runtime processes |

If the human says "start app" or "check ux" without naming a runtime, ask:

```text
Which runtime should I use: Codex or Claude?
```

---

## start_agent

```python
start_agent(team, runtime, drain=True)
```

Opens a new Terminal window at `<team>/` and starts the selected runtime.

| `runtime` | Behaviour |
|---|---|
| `"codex"` | Runs `codex --dangerously-bypass-approvals-and-sandbox` in the team workspace |
| `"claude"` | Runs `~/.local/bin/claude` in the team workspace |

| `drain` | Behaviour |
|---|---|
| `True` *(default)* | Agent gives its short startup greeting, then works Builder + QA for every ticket autonomously |
| `False` | Agent gives its short startup greeting, checks `Messages/inbox.md`, then waits for human input |

- If the selected team/runtime is already running, returns `"status": "already_running"` — no duplicate is launched.
- If the PID file exists but the process is dead, it cleans up and starts fresh.
- PID files are runtime-aware: `.pids/<team>-<runtime>-agent.pid`.

```python
start_agent("ux", "codex")
# → { "team": "ux", "runtime": "codex", "status": "starting", "mode": "drain", "pid_file": ".pids/ux-codex-agent.pid" }

start_agent("ux", "claude", drain=False)
# → { "team": "ux", "runtime": "claude", "status": "starting", "mode": "interactive", "pid_file": ".pids/ux-claude-agent.pid" }

start_agent("ux", "codex")
# called again while already running
# → { "team": "ux", "runtime": "codex", "pid": 12345, "status": "already_running" }
```

---

## get_agent_status

```python
get_agent_status(team, runtime)
```

Returns real-time status using CPU usage as the signal.

```python
get_agent_status("ux", "codex")
# → { "team": "ux", "runtime": "codex", "pid": 9801, "cpu": 0.0, "agent_status": "idle" }

get_agent_status("app", "claude")
# → { "team": "app", "runtime": "claude", "pid": 9900, "cpu": 72.4, "agent_status": "busy" }
```

| `agent_status` | Meaning |
|---|---|
| `idle` | Process alive, CPU near 0% — finished all tickets, waiting at the prompt |
| `busy` | Process alive, CPU above 5% — actively working a ticket |
| `dead` | PID file exists but process is gone — crashed or killed externally |
| `not_running` | No PID file — never started or cleanly stopped |
| `running_unknown` | Process exists but this environment cannot sample CPU for it |

---

## stop_agent

```python
stop_agent(team, runtime)
```

Sends `SIGTERM` to the selected team/runtime process and removes its PID file.

```python
stop_agent("ux", "codex")
# → { "team": "ux", "runtime": "codex", "pid": 12345, "status": "stopped" }
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
#     { "team": "app", "runtime": "codex",  "pid": 12346, "status": "running" },
#     { "team": "ux",  "runtime": "claude", "pid": 12345, "status": "dead"    }
#   ]
```

`"dead"` means the PID file exists but the process is gone — run `start_agent(team, runtime)` again to restart.

---

## Typical Flow

```python
# Open tickets
open_all_tickets("ux")

# Start the selected runtime — it drains the queue automatically
start_agent("ux", "codex")

# Check progress
get_agent_status("ux", "codex")
list_agents()

# Shut down when done
stop_agent("ux", "codex")
```

---

## When The Agent Goes Idle

The drain runs once on start. When the queue is empty the agent waits at the prompt and will not pick up new tickets automatically.

If new tickets arrive after the agent is idle, tell the human:

```text
The ux Codex agent is idle — all tickets are done.
If you open more tickets and want the agent to pick them up,
type this in the ux Codex Terminal window:

  Drain the ticket queue: Builder then QA, one ticket at a time.

Or call stop_agent("ux", "codex") and then start_agent("ux", "codex") to restart cleanly.
```

---

## Notes

- `start_agent` requires macOS — it uses `osascript` to open Terminal.
- Codex is resolved from `PATH` as `codex`.
- Claude is expected at `~/.local/bin/claude`.
- PID files are stored in `<project>/.pids/`.
- `stop_agent` sends `SIGTERM` — the agent finishes its current operation before exiting when the runtime handles termination gracefully.
