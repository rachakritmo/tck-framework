# TICKET_AGENTS_RULES

Shared rules for all agents (builder + QA). Your `CLAUDE.md` covers your role, standards, and boundaries.

---

## Ticket Workflow

```
Backlog → Open → InProgress → QAReview → Done
                     │            ↓ (if issues found)
                     │         ReOpen → InProgress
                     │
                     └─(need_qa: false)→ Done   ← Auto-Done, skips QA
```

---

## MCP Tools

| Tool | Purpose |
|---|---|
| `create_ticket(team, title, goal, dos, donts, ticket_id?, watch_points?, need_qa?)` | Create a new ticket in Backlog |
| `list_tickets(team, status?)` | List tickets — returns `[{ ticket_id, title, status }]` |
| `get_ticket(ticket_id)` | Read full ticket details by ID |
| `get_next_ticket(team)` | Get the next Open or ReOpen ticket to work on |
| `execute_ticket(ticket_id, by_agent)` | Claim ticket: Open/ReOpen → InProgress + log entry |
| `submit_work(ticket_id, by_agent, summary, note?, tokens?)` | Submit work: InProgress → QAReview **or** Done (if `need_qa: false`) |
| `get_next_ticket_for_review(team)` | Get the next ticket waiting for QA |
| `start_review(ticket_id, by_agent)` | Claim ticket for review + log entry (stays in QAReview) |
| `review_pass(ticket_id, by_agent, notes, note?, tokens?)` | QA approved: QAReview → Done + log entry |
| `review_reopen(ticket_id, by_agent, issues, note?, tokens?)` | QA failed: QAReview → ReOpen + log entry |

---

## Submission Parameters

When calling `submit_work`, `review_pass`, or `review_reopen`, use the right format for each parameter:

| Parameter | Format | Written to | Example |
|---|---|---|---|
| `summary` / `notes` / `issues` | **Markdown** | Ticket audit log block (visible in Obsidian) | `"## What was done\n- Added rate limiting\n- Returns 429 with Retry-After"` |
| `note` | **Plain string** | Activity log table (one row, 60 char max) | `"Rate limit 429, Retry-After header set"` |
| `tokens` | **Integer** | Frontmatter `builder_tokens` / `qa_tokens` | `4200` |

- `summary` / `notes` / `issues` — write in full Markdown. This goes into the ticket's **Execution & Audit Log** callout block. Use headers, bullet lists, code blocks as needed.
- `note` — plain text, one line. This is the short entry in the activity log table. If omitted, falls back to the first line of `summary`/`notes`/`issues`.
- `Time` — **automatically calculated** by the server. No need to pass it. Measures time from `execute_ticket` → `submit_to_review` (builder) and `start_review` → `review_pass/reopen` (QA).

---

## Ticket Structure

| Section                 | Purpose                                                         |
| ----------------------- | --------------------------------------------------------------- |
| **The Goal**            | What needs to be built or designed and why                      |
| **DO**                  | Requirements and allowed behaviors — follow exactly             |
| **DON'T DO**            | Hard blockers — never implement what is listed here             |
| **Watch Points**        | QA focus areas called out by the PM                             |
| **AI Builder Feedback** | Logged automatically by `execute_ticket` and `submit_to_review` |
| **AI QA Audit Report**  | Logged automatically by `review_pass` and `review_reopen`       |

---

## Typical Agent Flow

```
# 1. Get next ticket
ticket = get_next_ticket(team="<your-team>")

# 2. Claim it — response includes reopen_count
ticket = execute_ticket(ticket["ticket_id"], by_agent="<your-agent>")
# ticket["reopen_count"] → 0 first round, 1 after first reopen, 2 after second, ...
suffix = "" if ticket["reopen_count"] == 0 else f"-r{ticket['reopen_count']}"

# 3. Read full spec from the ticket file
#    path → "Tickets/" + ticket["file_name"]

# 4. Do the work, then submit
#    summary = Markdown written into the ticket audit log
#    note    = plain string for the activity log table (60 char max)
#    submit_work routes automatically:
#      need_qa: true  → QAReview (QA agent picks it up next)
#      need_qa: false → Done immediately (Auto-Done, no QA step)

write f"TicketAttachments/<ticket_id>-summary{suffix}.md"

submit_work(ticket["ticket_id"], by_agent="<your-agent>",
            summary="## Summary\n- Did X\n- Decided Y because Z\n\nFull details: [[<ticket_id>-summary{suffix}]]",
            note="Short one-liner for the log",
            tokens=1234)

# --- QA side ---

# 5. Pick up the review — response includes reopen_count
ticket = get_next_ticket_for_review(team="<your-team>")
# ticket["reopen_count"] tells you which round this is
suffix = "" if ticket["reopen_count"] == 0 else f"-r{ticket['reopen_count']}"
start_review(ticket["ticket_id"], by_agent="<your-qa-agent>")

# 6. Pass or reopen
#    notes / issues = Markdown written into the ticket audit log
#    note           = plain string for the activity log table (60 char max)

write f"TicketAttachments/<ticket_id>-qa-report{suffix}.md"

review_pass(ticket["ticket_id"], by_agent="<your-qa-agent>",
            notes="## Audit\n- All DO items satisfied\n\nFull report: [[<ticket_id>-qa-report{suffix}]]",
            note="All checks passed",
            tokens=800)
# — or —
review_reopen(ticket["ticket_id"], by_agent="<your-qa-agent>",
              issues="## Issues\n- Missing error state\n\nFull report: [[<ticket_id>-qa-report{suffix}]]",
              note="Missing error state on empty input",
              tokens=800)
```

---

## Artifacts

Actual deliverables produced by the agent go in `Artifacts/`. This is separate from `TicketAttachments/` which is for notes and reports only.

```
Artifacts/          ← output files: HTML, code, configs, specs
TicketAttachments/  ← agent notes: summaries, QA reports, decision logs
```

**Examples by team:**

| Team | Example artifact |
|---|---|
| ux | `Artifacts/welcome.html`, `Artifacts/login-spec.md` |
| app | `Artifacts/rate-limiter.py`, `Artifacts/auth-middleware.ts` |
| deploy | `Artifacts/pipeline.yml`, `Artifacts/nginx.conf` |

Link to the artifact from your `summary` so QA can find it:

```markdown
## Delivered
Built the welcome page.

Artifact: [[welcome.html]]
Full notes: [[TCK-UX-2604-005-summary]]
```

---

## Ticket Attachments

Agents can create files in `TicketAttachments/` and link to them from `summary`, `notes`, or `issues`. This keeps the audit log brief while preserving full detail.

**Naming convention:**

Every ticket object returned by MCP tools has a `reopen_count` property — use it to version your attachment filename so each round gets its own file.

```
ticket["reopen_count"]  →  0 = first round, 1 = after first reopen, 2 = after second, ...
```

| `reopen_count` | Builder file                | QA file                       |
| -------------- | --------------------------- | ----------------------------- |
| `0`            | `{ticket_id}-summary.md`    | `{ticket_id}-qa-report.md`    |
| `1`            | `{ticket_id}-summary-r1.md` | `{ticket_id}-qa-report-r1.md` |
| `2`            | `{ticket_id}-summary-r2.md` | `{ticket_id}-qa-report-r2.md` |

Example for `TCK-UX-2604-001` on second round (`reopen_count = 1`):

```
TicketAttachments/TCK-UX-2604-001-summary-r1.md
TicketAttachments/TCK-UX-2604-001-qa-report-r1.md
```

**Write path and link:**

Build the filename from `ticket_id` + `reopen_count`, write it to `TicketAttachments/`, then wiki-link it from your summary:

```
write path  →  TicketAttachments/{ticket_id}-summary{suffix}.md
wiki link   →  [[{ticket_id}-summary{suffix}]]
```

Example (`reopen_count = 0`):

```markdown
## What was done
Implemented avatar upload with circular crop preview.

Full details: [[TCK-UX-2604-001-summary]]
```

Example (`reopen_count = 1`):

```markdown
## What was done (r1 fix)
Corrected error state handling after QA reopen.

Full details: [[TCK-UX-2604-001-summary-r1]]
```

Obsidian resolves wiki links by filename — location in the vault doesn't matter.

**When to use attachments:**

Always write an attachment when your output is more than 3 lines. Keep `summary`/`notes`/`issues` to a brief overview + the wiki link.

- ✅ Write attachment — implementation notes, decisions, test results, QA audit checklist, generated code or config
- ✅ Write attachment — anything with headers, code blocks, or lists longer than 3 items
- ❌ Inline only — a single sentence outcome: `"Adjusted breakpoint from 768px to 767px"`

---

## Reading Ticket Files

Every MCP tool response includes a `file_name` field. Since your workspace opens at your team folder, the read path is always:

```
Tickets/<file_name>
```

Example:

```
ticket["file_name"] → "TCK-UX-2604-001 Login Page Redesign.md"
read path           → "Tickets/TCK-UX-2604-001 Login Page Redesign.md"
```

**Rules:**
- ✅ Read ticket files directly — full spec, references, images, and links are all there
- ❌ Never write, edit, move, or delete ticket files
- ❌ Never change `status`, `reopen_count`, or any frontmatter directly
- All state changes go through MCP tools only
