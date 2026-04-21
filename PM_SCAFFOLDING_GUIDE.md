# PM Scaffolding Guide

## Create a new team

When the human asks to add a team, scaffold the full workspace and write a `CLAUDE.md` tailored to that team's domain:

```
mkdir <team>/Tickets/
mkdir <team>/Artifacts/
mkdir <team>/TicketAttachments/
mkdir <team>/Messages/
mkdir <team>/.claude/
write  <team>/CLAUDE.md                    ← see Team CLAUDE.md template below
write  <team>/.claude/settings.local.json  ← pre-authorise permissions so agent runs without prompts
```

**`settings.local.json` must always be created.** Without it the agent stops to ask permission on every file write and tool call, breaking autonomous operation.

Write it with this content — adjust the `Bash` entries to match the team's domain:

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

`Bash(*)` allows all shell commands. This is intentional — agents run in isolated team workspaces and need to run piped commands, scripts, and tool chains without being interrupted for permission prompts on every step.

**Important — the PM cannot start agents.** After scaffolding, always give the human the exact instruction to start the agent:

```
✅ app/ workspace is ready.

To start the app agent:
1. Open a new Claude Code window
2. Set the folder to: <project>/app/
3. That window is now your app agent — it will pick up tickets automatically.
```

If multiple teams were just scaffolded, list all of them:

```
✅ All workspaces ready. Open one Claude Code window per team:

  app     → <project>/app/
  deploy  → <project>/deploy/

Each window = one agent. They work independently and communicate through tickets.
```

**Why the PM can't start agents:**
- Each agent is a separate Claude Code window opened by the human
- Agents don't talk to each other directly — they communicate through the ticket system
- The PM sets everything up; the human opens the windows

---

## Team CLAUDE.md Template

When scaffolding a new team, write `<team>/CLAUDE.md` using this structure:

```markdown
# <Role> Agent — CLAUDE.md

You are the **<Role> Agent** for this project. Your workspace is the `<team>/` folder.

@../TICKET_AGENTS_RULES.md

---

## Your Role

<What this agent does — 2-3 sentences covering domain, type of work, and ticket flow responsibility>

Always pass `team="<team>"` to all MCP tools.

---

## <Domain> Standards

When building (InProgress):
- <Standard 1>
- <Standard 2>
- ...

When reviewing (QA Audit):
- **DO list** — Every requirement satisfied?
- **DON'T DO list** — Any violations?
- <Domain-specific QA checks>

---

## Boundaries

- Always use `team="<team>"`. Never pass another team name.
- Do not modify the `Templates/` folder.
- <Any other hard limits specific to this team>
```

Tailor the standards section to the team's domain — examples:

| Team domain | Standards focus |
|---|---|
| Frontend / UX | WCAG AA, design system tokens, all states (empty/loading/error/success) |
| Backend / API | Auth, input validation, OWASP Top 10, no hardcoded secrets |
| DevOps / Deploy | Idempotency, least-privilege IAM, rollback safety, no plaintext secrets |
| Data / ML | Schema validation, null handling, reproducibility, no PII leakage |
| QA / Test | Coverage targets, flaky-test policy, CI gate requirements |
