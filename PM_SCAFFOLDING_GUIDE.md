# PM Scaffolding Guide

## Create a new team

When the human asks to add a team, ask which runtime support they want:

```text
Which runtime should this team support: Codex, Claude, or both?
```

Recommended default when the human is unsure: **both**. This keeps Claude compatibility and makes the workspace ready for Codex.

Every team workspace is runtime-neutral at the ticket layer. Always create:

```text
mkdir <team>/Tickets/
mkdir <team>/Artifacts/
mkdir <team>/TicketAttachments/
mkdir <team>/Messages/
write <team>/AGENTS.md
```

Add runtime-specific files based on the human's choice:

```text
# Codex support
mkdir <team>/.codex/
write <team>/.codex/config.toml

# Claude support
mkdir <team>/.claude/
write <team>/CLAUDE.md
write <team>/.claude/settings.local.json
```

`AGENTS.md` is the primary instruction source. `CLAUDE.md` is only a Claude compatibility entrypoint and should point to `AGENTS.md`.

---

## Codex Config

Codex-enabled teams get `<team>/.codex/config.toml`:

```toml
# Codex team-agent autonomy profile.
# The MCP launcher also starts Codex with --dangerously-bypass-approvals-and-sandbox
# so this workspace can drain tickets without stopping for approvals.
approval_policy = "never"
sandbox_mode = "danger-full-access"
```

This is intentionally YOLO-style for team agents. Only put it inside isolated team workspaces that are expected to run autonomously.

---

## Claude Config

Claude-enabled teams get `<team>/.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Write(**)",
      "Edit(**)",
      "Bash(*)",
      "mcp__ticket-mcp__*"
    ]
  }
}
```

`Bash(*)` allows all shell commands. This is intentional because agents run in isolated team workspaces and need to run scripts, tool chains, and piped commands without stopping on every permission prompt.

---

## Team AGENTS.md Template

When scaffolding a new team, write `<team>/AGENTS.md` using this structure:

```markdown
# <Role> Agent — AGENTS.md

You are the **<Role> Agent** for this project. Your workspace is the `<team>/` folder.

@../TICKET_AGENTS_RULES.md

---

## Your Role

<What this agent does — 2-3 sentences covering domain, type of work, and ticket flow responsibility>

Always pass `team="<team>"` to all MCP tools.

---

## Startup Greeting

Follow the shared startup greeting rule in `TICKET_AGENTS_RULES.md`. Use this team-specific wording:

```text
I am the <Role> Agent for the <team> team. I am running inside the TCK Control Layer for AI Work, so I work through tickets, MCP state transitions, artifacts, and audit logs.

To have me process the queue, tell me:
Drain the ticket queue: Builder then QA, one ticket at a time.
```

---

## <Domain> Standards

When building (InProgress):
- <Standard 1>
- <Standard 2>
- ...

When reviewing (QA Audit):
- **DO list** — Every requirement satisfied?
- **DON'T DO list** — Any violations?
- **Artifacts** — Deliverables are in `Artifacts/`.
- **Reports** — Summaries and QA reports are in `TicketAttachments/`.
- <Domain-specific QA checks>

---

## Boundaries

- Always use `team="<team>"`. Never pass another team name.
- Do not modify the `Templates/` folder.
- Do not directly edit ticket lifecycle frontmatter such as `status`, `reopen_count`, or token counts — use MCP tools.
- Put actual deliverables in `Artifacts/`.
- Put notes, summaries, and QA reports in `TicketAttachments/`.
- <Any other hard limits specific to this team>
```

Tailor the standards section to the team's domain:

| Team domain | Standards focus |
|---|---|
| Frontend / UX | WCAG AA, design system tokens, all states (empty/loading/error/success) |
| Backend / API | Auth, input validation, OWASP Top 10, no hardcoded secrets |
| DevOps / Deploy | Idempotency, least-privilege IAM, rollback safety, no plaintext secrets |
| Data / ML | Schema validation, null handling, reproducibility, no PII leakage |
| QA / Test | Coverage targets, flaky-test policy, CI gate requirements |

---

## Team CLAUDE.md Compatibility File

When Claude support is selected, write `<team>/CLAUDE.md` as a pointer:

```markdown
# <Role> Agent — CLAUDE.md

This workspace uses `AGENTS.md` as the source of truth.

Read and follow:

@./AGENTS.md
```

Do not duplicate the full instructions in `CLAUDE.md`; duplicated instruction files drift.

---

## Start Instructions After Scaffolding

After scaffolding, tell the human how to run the selected runtime.

For Codex:

```text
✅ app/ workspace is ready for Codex.

To start the app agent with Codex:
1. Open Codex in <project>/app/
2. Confirm it reads AGENTS.md
3. Tell it:
   Drain the ticket queue: Builder then QA, one ticket at a time.

Or call start_agent("app", "codex") from the PM MCP tools.
```

For Claude:

```text
✅ app/ workspace is ready for Claude.

To start the app agent with Claude:
1. Open Claude Code in <project>/app/
2. Claude reads CLAUDE.md, which points to AGENTS.md
3. Tell it:
   Drain the ticket queue: Builder then QA, one ticket at a time.

Or call start_agent("app", "claude") from the PM MCP tools.
```

For both, provide both sets of instructions and ask which runtime they want to start first.
