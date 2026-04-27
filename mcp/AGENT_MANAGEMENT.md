# Agent Management — Technical Reference

How `mcp/server.py` starts, tracks, monitors, and stops team agents.

---

## Constants

| Constant | Value | Purpose |
|---|---|---|
| `CLAUDE_BIN` | `~/.local/bin/claude` | Path to Claude Code binary |
| `CODEX_BIN` | `codex` (resolved from PATH) | Codex binary name |
| `VALID_RUNTIMES` | `["claude", "codex"]` | Accepted runtime values |
| `PIDS_DIR` | `<vault>/.pids/` | Folder for all PID and launch files |
| `DRAIN_PROMPT` | `"Give your short startup greeting from AGENTS.md, then drain the ticket queue: Builder then QA, one ticket at a time."` | Sent to agent on `drain=True` |
| `INTERACTIVE_PROMPT` | `"Give your short startup greeting from AGENTS.md, then check Messages/inbox.md and wait for human instructions."` | Sent to agent on `drain=False` |

---

## Files Written Per Agent

Every team/runtime pair gets two files in `.pids/`:

| File | Example | Purpose |
|---|---|---|
| `<team>-<runtime>-agent.pid` | `ux-claude-agent.pid` | Holds the agent process PID |
| `<team>-<runtime>-launch.sh` | `ux-claude-launch.sh` | Shell script that captures PID and execs the agent |

### Launch script contents

```bash
#!/bin/bash
echo $$ > /path/to/ux-claude-agent.pid
exec /home/user/.local/bin/claude "Give your short startup greeting..."
```

- `echo $$` — writes the shell's own PID before replacing it
- `exec` — replaces the shell process in-place (same PID, same TTY)
- The agent inherits the PID captured by `echo $$`

---

## MCP Tools

### `start_agent(team, runtime, drain=True)`

Starts an agent for a team/runtime pair in a new Terminal window.

**Flow:**
1. Validate `team` and `runtime`
2. Check for existing PID file → if alive, return `already_running`
3. If PID file exists but process is dead → delete stale PID file
4. Write launch script to `.pids/<team>-<runtime>-launch.sh`
5. Run AppleScript: `tell Terminal to do script "cd <workspace> && <launch.sh>"`
6. Return `{ team, runtime, status: "starting", mode, pid_file }`

**Runtime dispatch:**

| `runtime` | Binary | Extra flags |
|---|---|---|
| `"claude"` | `~/.local/bin/claude` | none |
| `"codex"` | `codex` | `--dangerously-bypass-approvals-and-sandbox` |

**`drain` parameter:**

| Value | Prompt sent to agent |
|---|---|
| `True` *(default)* | `DRAIN_PROMPT` — agent greets then drains queue autonomously |
| `False` | `INTERACTIVE_PROMPT` — agent greets, checks inbox, waits for human |

**Returns:**
```json
{ "team": "ux", "runtime": "claude", "status": "starting", "mode": "drain", "pid_file": "/path/.pids/ux-claude-agent.pid" }
```

**Already running:**
```json
{ "team": "ux", "runtime": "claude", "pid": 12345, "status": "already_running" }
```

---

### `stop_agent(team, runtime)`

Sends `SIGTERM` (signal 15) to the agent process and removes the PID file.

**Flow:**
1. Validate `team` and `runtime`
2. Read PID from `.pids/<team>-<runtime>-agent.pid`
3. `os.kill(pid, 15)` — graceful shutdown
4. Unlink PID file

**Returns:**

| Case | Response |
|---|---|
| Stopped successfully | `{ team, runtime, pid, status: "stopped" }` |
| Process already gone | `{ team, runtime, pid, status: "was_not_running" }` (PID file still cleaned up) |
| Permission denied | `{ error: "permission denied..." }` |
| No PID file | `{ error: "no running agent found..." }` |

---

### `get_agent_status(team, runtime)`

Reports real-time agent status using CPU as the activity signal.

**Flow:**
1. Validate `team` and `runtime`
2. Check PID file exists → if not, return `not_running`
3. `os.kill(pid, 0)` — liveness check (no signal sent)
4. Sample CPU twice via `ps -p <pid> -o %cpu=`, 0.5s apart, take `max()`
5. `cpu > 5.0%` → `busy`, else → `idle`

**Returns:**
```json
{ "team": "ux", "runtime": "claude", "pid": 9801, "cpu": 72.4, "agent_status": "busy" }
```

**`agent_status` values:**

| Value | Meaning |
|---|---|
| `idle` | Process alive, CPU ≈ 0% — finished work, waiting at prompt |
| `busy` | Process alive, CPU > 5% — actively processing a ticket |
| `dead` | PID file exists but process is gone — crashed or killed |
| `not_running` | No PID file — never started or cleanly stopped |
| `running_unknown` | Process exists but CPU cannot be sampled (permission) |

---

### `list_agents()`

Reads all files in `.pids/` matching `*-agent.pid` and checks liveness.

**PID file naming:** `<team>-<runtime>-agent.pid`
- Parsed with regex `^(.+)-(claude|codex)-agent$`
- Legacy PID files (no runtime in name) are tagged `runtime: "legacy"`

**Returns:**
```json
[
  { "team": "app", "runtime": "codex",  "pid": 12346, "status": "running" },
  { "team": "ux",  "runtime": "claude", "pid": 12345, "status": "dead"    }
]
```

| `status` | Meaning |
|---|---|
| `running` | `os.kill(pid, 0)` succeeded |
| `dead` | `ProcessLookupError` — process is gone |
| `running_unknown` | `PermissionError` — exists but cannot signal |

---

## Internal Helpers

| Function | Purpose |
|---|---|
| `_runtime_pid_file(team, runtime)` | Returns `Path(.pids/<team>-<runtime>-agent.pid)` |
| `_runtime_launch_file(team, runtime)` | Returns `Path(.pids/<team>-<runtime>-launch.sh)` |
| `_agent_cpu(pid)` | Samples CPU twice via `ps`, 0.5s apart, returns `max()` |
| `_applescript_string(value)` | Escapes `\` and `"` for safe embedding in AppleScript string |
| `_get_runtime_agent_status(team, runtime)` | Core logic for `get_agent_status` |
| `_launch_terminal_agent(team, runtime, command, drain)` | Core logic for all `start_agent` calls |
| `_start_claude_agent(team, drain)` | Calls `_launch_terminal_agent` with Claude binary |
| `_start_codex_agent(team, drain)` | Calls `_launch_terminal_agent` with Codex + YOLO flag |
| `_stop_runtime_agent(team, runtime)` | Core logic for `stop_agent` |
| `validate_runtime(runtime)` | Returns error string if runtime not in `VALID_RUNTIMES` |

---

## Platform Notes

- **macOS only** — `start_agent` uses `osascript` to open Terminal windows
- `stop_agent` uses `os.kill(pid, 15)` — POSIX, works on macOS and Linux
- `get_agent_status` uses `ps -p <pid> -o %cpu=` — macOS/Linux; Windows syntax differs
- Windows support is planned — will require replacing `osascript`, `ps`, and signal handling

---

## Typical Flow

```python
# 1. Start agent — drains queue automatically
start_agent("ux", "claude")
# → { status: "starting", mode: "drain" }

# 2. Monitor progress
get_agent_status("ux", "claude")
# → { agent_status: "busy", cpu: 68.2 }

# 3. Check all teams at once
list_agents()
# → [{ team: "ux", runtime: "claude", status: "running" }, ...]

# 4. Shut down when done
stop_agent("ux", "claude")
# → { status: "stopped" }
```
