# Agent Management — Technical Reference

How `start_agent`, `send_message`, `get_agent_status`, `stop_agent`, and `list_agents` work under the hood.

All five tools live in `mcp/server.py`. They manage Claude Code processes running in Terminal windows on macOS.

---

## Architecture Overview

```
PM Agent (Claude Desktop)
    │
    │  MCP call
    ▼
mcp/server.py  (FastMCP, runs as subprocess of Claude Desktop)
    │
    ├── osascript → Terminal.app → launch.sh → exec claude
    │                                               │
    │                                        .pids/ux-agent.pid
    │
    └── .pids/ux-agent.pid  ←  read by stop/status/list tools
```

Team agents are **separate OS processes** running in Terminal windows. The MCP server communicates with them through:
- **PID files** — track which process is the agent
- **OS signals** — check liveness (`signal 0`), stop (`SIGTERM`)
- **`ps` CPU sampling** — detect idle vs busy
- **`Messages/inbox.md`** — deliver messages from PM to agent

---

## Constants

```python
VAULT_ROOT = Path(__file__).parent.parent   # project root (chain/)
PIDS_DIR   = VAULT_ROOT / ".pids"           # PID and launch script files
CLAUDE_BIN = Path.home() / ".local" / "bin" / "claude"
```

---

## Helper: `_agent_cpu(pid) → float`

```python
def _agent_cpu(pid: int) -> float:
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
```

**What it does:** calls `ps` twice with a 0.5s gap and returns the higher reading.

**Why `ps -o %cpu=`:** the `=` after the column name suppresses the header line, so stdout is just the number. The `or "0"` guard handles the edge case where the process disappears between `os.kill(0)` check and `ps` call.

**Why two samples:** Claude Code's CPU usage is spiky — it bursts during LLM calls and tool execution, then drops briefly between steps. A single sample might catch a momentary idle dip mid-processing and wrongly classify a busy agent as idle. Taking `max()` of two samples 0.5s apart avoids false negatives.

**Why 5% threshold:** an agent sitting at the `>` prompt uses ~0% CPU (just an idle process waiting for stdin). Any active processing — LLM call, file read, MCP tool call — pushes well above 5%. The threshold has comfortable headroom in both directions.

**Used by:** `get_agent_status` (exposed as MCP tool) and `send_message` (internal wake decision).

---

## `start_agent(team)`

**Purpose:** open a Terminal window at the team workspace and launch Claude Code as the team agent.

```python
def start_agent(team: str) -> str:
    workspace = VAULT_ROOT / team
    pid_file  = PIDS_DIR / f"{team}-agent.pid"
    PIDS_DIR.mkdir(exist_ok=True)

    # 1. Guard — don't start a second instance
    if pid_file.exists():
        pid = int(pid_file.read_text().strip())
        try:
            os.kill(pid, 0)
            return json.dumps({"team": team, "pid": pid, "status": "already_running"})
        except ProcessLookupError:
            pid_file.unlink()  # stale PID — clean up

    # 2. Write launch script
    launch_file = PIDS_DIR / f"{team}-launch.sh"
    launch_file.write_text(
        f"#!/bin/bash\n"
        f"echo $$ > {pid_file}\n"
        f"exec {CLAUDE_BIN} 'Check Messages/inbox.md and start working on tickets.'\n"
    )
    launch_file.chmod(0o755)

    # 3. Open Terminal and run the launch script
    script = (
        f'tell application "Terminal" to do script '
        f'"cd {workspace} && {launch_file}"\n'
        f'tell application "Terminal" to activate'
    )
    subprocess.run(["osascript", "-e", script], check=True)

    return json.dumps({"team": team, "status": "starting", "pid_file": str(pid_file)})
```

### Step 1 — Duplicate guard

`os.kill(pid, 0)` sends signal 0 to the process. Signal 0 does not kill — it's purely a liveness check. If the process is alive, the call returns normally. If the process is dead, it raises `ProcessLookupError`.

- Alive → return `already_running`, do nothing
- Dead → `pid_file.unlink()` cleans up the stale file, then continue to launch

### Step 2 — Launch script

The launch script solves two problems at once:

**Problem A — Quoting.** The AppleScript `do script` command takes a double-quoted string. Embedding shell single quotes inside it (`sh -c 'echo $$ > file'`) creates quoting conflicts that cause parse errors. Writing the shell logic to a `.sh` file means the AppleScript string becomes `"cd /path && /path/launch.sh"` — no special characters at all.

**Problem B — TTY suspension.** Claude Code is an interactive terminal app that requires a TTY for input/output. Running it with `&` (background) triggers `SIGTTOU` — the OS suspends any background process that tries to write to the terminal. The fix is to run claude in the **foreground**.

But foreground means the shell that started it is blocked — you can't capture the PID with `$!` (which only works for background processes). The solution is `exec`:

```bash
echo $$ > pidfile   # write current shell's PID to file
exec claude '...'   # replace this shell with claude in-place
```

`exec` replaces the current process image with `claude` — same PID, same TTY, same file descriptors. The PID written by `echo $$` remains the correct PID for the claude process because `exec` never creates a new process.

**The initial prompt** is passed as a claude argument: `exec claude 'Check Messages/inbox.md...'`. Claude Code accepts an opening message as a positional argument — it starts in interactive mode with that as the first user turn, so the agent immediately reads its inbox and starts working without waiting for human input.

### Step 3 — osascript

`osascript -e` executes an AppleScript expression. `Terminal.app`'s `do script` command opens a new terminal tab and runs the given shell command inside it. `activate` brings Terminal to the foreground.

The two statements are passed as a single `-e` string with a newline between them — AppleScript treats newlines as statement separators.

---

## `get_agent_status(team)`

**Purpose:** return real-time status of an agent — `idle`, `busy`, `dead`, or `not_running`.

```python
def get_agent_status(team: str) -> str:
    pid_file = PIDS_DIR / f"{team}-agent.pid"

    if not pid_file.exists():
        return json.dumps({"team": team, "agent_status": "not_running"})

    pid = int(pid_file.read_text().strip())
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return json.dumps({"team": team, "pid": pid, "agent_status": "dead"})

    cpu = _agent_cpu(pid)
    agent_status = "busy" if cpu > 5.0 else "idle"

    return json.dumps({"team": team, "pid": pid, "cpu": round(cpu, 1), "agent_status": agent_status})
```

**Decision tree:**

```
pid file exists?
    No  → not_running
    Yes → os.kill(pid, 0)
              raises ProcessLookupError → dead
              returns normally          → alive
                  cpu > 5%  → busy
                  cpu ≤ 5%  → idle
```

**`dead` vs `not_running`:** `dead` means the PID file exists but the process is gone — a crash or unclean shutdown. `not_running` means there is no PID file — the agent was never started or was stopped cleanly by `stop_agent`.

**Returns:**
```json
{ "team": "ux", "pid": 9801, "cpu": 0.0, "agent_status": "idle" }
{ "team": "app", "pid": 9900, "cpu": 72.4, "agent_status": "busy" }
{ "team": "ux", "pid": 9801, "agent_status": "dead" }
{ "team": "ux", "agent_status": "not_running" }
```

---

## `send_message(team, message)`

**Purpose:** write a message to the agent's inbox and wake it immediately if idle.

```python
def send_message(team: str, message: str) -> str:
    inbox = VAULT_ROOT / team / "Messages" / "inbox.md"
    inbox.parent.mkdir(exist_ok=True)

    ts = now_ts()
    content = f"## Message from PM — {ts}\n\n{message.strip()}\n"

    # Append if unread content already exists
    if inbox.exists() and inbox.read_text().strip():
        inbox.write_text(inbox.read_text().rstrip() + "\n\n---\n\n" + content)
    else:
        inbox.write_text(content)

    # Wake decision
    pid_file = PIDS_DIR / f"{team}-agent.pid"
    wake_status = "not_running"

    if pid_file.exists():
        pid = int(pid_file.read_text().strip())
        try:
            os.kill(pid, 0)
            cpu = _agent_cpu(pid)

            if cpu > 5.0:
                wake_status = "agent_busy_message_queued"
            else:
                os.kill(pid, 15)       # SIGTERM
                pid_file.unlink()
                time.sleep(1)          # wait for process to exit
                # relaunch via existing launch script
                subprocess.run(["osascript", "-e", relaunch_script], check=True)
                wake_status = "agent_restarted"

        except ProcessLookupError:
            wake_status = "not_running"

    return json.dumps({...,"wake_status": wake_status})
```

### Inbox write — append safety

`inbox.read_text().strip()` checks whether the file has actual content (not just whitespace). If yes, the new message is appended with a `---` separator. This handles the case where the PM sends multiple messages before the agent reads any of them — nothing is overwritten.

### Wake decision

After writing, `send_message` checks CPU via `_agent_cpu`:

| CPU | Action | `wake_status` |
|---|---|---|
| > 5% | Do nothing — agent is mid-ticket, will read inbox after finishing | `agent_busy_message_queued` |
| ≤ 5% | SIGTERM → wait 1s → relaunch via existing launch script | `agent_restarted` |
| Process dead | Do nothing — message waits for next `start_agent` | `not_running` |

**Why restart instead of inject input:** there is no safe way to write to an interactive process's stdin from outside without a shared TTY or named pipe set up at process creation time. Restarting is clean — the new session starts with the kickoff prompt, reads the inbox as its first action, and picks up where the old session left off (ticket state is in the MCP server, not in the agent's memory).

**Why `time.sleep(1)` before relaunch:** `SIGTERM` is asynchronous — the process may still be running for a brief period after the signal is sent. Waiting 1 second gives it time to exit cleanly before a new Terminal tab is opened. Without the wait, the new launch script might write a new PID to the file before the old process reads it, causing a race condition.

---

## `stop_agent(team)`

**Purpose:** gracefully shut down a running agent and clean up its PID file.

```python
def stop_agent(team: str) -> str:
    pid_file = PIDS_DIR / f"{team}-agent.pid"

    if not pid_file.exists():
        return err(f"no running agent found for team '{team}'")

    pid = int(pid_file.read_text().strip())
    try:
        os.kill(pid, 15)   # SIGTERM
        pid_file.unlink()
        return json.dumps({"team": team, "pid": pid, "status": "stopped"})
    except ProcessLookupError:
        pid_file.unlink()
        return json.dumps({"team": team, "pid": pid, "status": "was_not_running"})
```

**`SIGTERM` (signal 15) vs `SIGKILL` (signal 9):**

| Signal | Behaviour |
|---|---|
| `SIGTERM` (15) | Sent to the process — it can catch it, finish current work, flush buffers, then exit. Claude Code handles it gracefully. |
| `SIGKILL` (9) | Immediate forced termination by the OS — process has no chance to clean up. Not used here. |

**Both branches unlink the PID file:** whether the process was alive (stopped now) or already dead (stale PID file), the file is removed. This leaves `.pids/` in a clean state.

---

## `list_agents()`

**Purpose:** survey all known agents across all teams.

```python
def list_agents() -> str:
    PIDS_DIR.mkdir(exist_ok=True)
    results = []

    for pid_file in sorted(PIDS_DIR.glob("*-agent.pid")):
        team = pid_file.stem.replace("-agent", "")
        pid  = int(pid_file.read_text().strip())
        try:
            os.kill(pid, 0)
            status = "running"
        except ProcessLookupError:
            status = "dead"

        results.append({"team": team, "pid": pid, "status": status})

    return json.dumps(results, indent=2)
```

**Team name extraction:** PID files are named `<team>-agent.pid`. `pid_file.stem` gives `ux-agent`, then `.replace("-agent", "")` gives `ux`. This means team names are implicit in the filename — no separate registry needed.

**`running` vs `dead`:** `list_agents` does not use `_agent_cpu` — it only checks process liveness, not activity. Use `get_agent_status` if you need `idle` vs `busy` for a specific team.

**`PIDS_DIR.mkdir(exist_ok=True)`:** called at the top so `glob` doesn't fail if the directory was never created (no agent has ever been started).

---

## Data Flow Summary

```
start_agent("ux")
    │
    ├── writes  .pids/ux-launch.sh      (bash script: echo $$, exec claude)
    ├── writes  .pids/ux-agent.pid      (written BY launch.sh at runtime)
    └── runs    osascript → Terminal → launch.sh → exec claude '...'


send_message("ux", "...")
    │
    ├── writes  ux/Messages/inbox.md    (PM message, timestamped)
    └── reads   .pids/ux-agent.pid
                    │
                    ├── os.kill(pid, 0)     alive?
                    ├── _agent_cpu(pid)     idle?
                    │       idle → SIGTERM + relaunch
                    │       busy → leave running, message queued
                    └── ProcessLookupError → not_running


stop_agent("ux")
    │
    ├── reads   .pids/ux-agent.pid
    ├── sends   SIGTERM to pid
    └── unlinks .pids/ux-agent.pid


get_agent_status("ux")
    │
    ├── reads   .pids/ux-agent.pid
    ├── os.kill(pid, 0)     alive check
    └── _agent_cpu(pid)     idle / busy


list_agents()
    │
    └── glob .pids/*-agent.pid
            └── os.kill(pid, 0) per file → running / dead
```

---

## Files Written by the System

```
chain/
└── .pids/
    ├── ux-agent.pid       ← PID of the running ux claude process
    ├── ux-launch.sh       ← bootstrap script for ux agent
    ├── app-agent.pid
    └── app-launch.sh

chain/ux/
└── Messages/
    └── inbox.md           ← PM writes here; agent reads and clears
```

`.pids/` is gitignored — it contains runtime state only.
