# TCK —  Control Layer for AI Work
> *Structure for AI agents. Context for every decision. Quality on every output.*

**Author:** Rachakrit Monyanon
**Version:** April 2026

---

## Table of Contents

1. [The Problem](#1-the-problem)
2. [What TCK Is](#2-what-tck-is)
3. [Core Beliefs](#3-core-beliefs)
4. [The System at a Glance](#4-the-system-at-a-glance)
5. [PROJECT_CORE — The Brain of Every Project](#5-project_core--the-brain-of-every-project)
6. [Documents — The Knowledge Base](#6-documents--the-knowledge-base)
7. [Work Lifecycles](#7-work-lifecycles)
8. [The Ticket System](#8-the-ticket-system)
9. [MCP Tools Reference](#9-mcp-tools-reference)
10. [The PM Agent](#10-the-pm-agent)
11. [Team Agents](#11-team-agents)
12. [The QA System](#12-the-qa-system)
13. [Activity Logs](#13-activity-logs)
14. [Naming Conventions](#14-naming-conventions)
15. [Anti-Patterns](#15-anti-patterns)
16. [Conclusion](#16-conclusion)

---

## 1. The Problem

AI agents are fast. That is the problem.

Without context, an AI agent doesn't guess less — it guesses faster. Without structure, it produces confident output pointed in the wrong direction. Without a quality gate, that output reaches the customer before anyone notices.

This happens in software teams every day:

- A developer asks an AI agent to build a feature. The agent builds it correctly — against a requirement that was already changed in last week's meeting. The spec file was never updated. Nobody caught it until QA.

- A team asks an AI agent to fix a bug. The agent fixes it — and quietly changes an unrelated function it thought looked wrong. The change ships. The regression is found two weeks later in production.

- A team onboards a new AI agent mid-sprint. The agent has no memory of previous sessions. It asks no questions, makes assumptions about the architecture, and produces output that technically compiles and logically contradicts three previous decisions.

The common thread is not the AI. It is the absence of a system.

**Speed without structure produces wrong output faster.**

TCK is the system.

---

## 2. What TCK Is

**TCK (Ticket Control Kit)** is a structured workflow system for human-AI teams.

It gives every AI agent three things before it does any work:

1. **A role** — who it is, what it owns, and what it must never touch
2. **Context** — the project's purpose, the customer's needs, the standards that apply
3. **A ticket** — a precise, grounded specification of exactly what to do right now

And after the work is done, it gives a human or another agent one question to answer:

> Does this output meet everything the ticket asked for?

If yes — done. If no — reopened, fixed, reviewed again.

Every action is logged. Every decision is traceable. Every output is verified.

---

### Who TCK is built for

TCK was designed for software teams — the teams where wrong output has the highest cost and the fastest blast radius.

| Role | What TCK solves |
|---|---|
| **UX / Design** | Specs grounded in the actual brief, not assumptions. QA verifies every state was designed. |
| **Backend / API** | Requirements in the ticket, not in someone's head. No undocumented side effects. |
| **Frontend / Web** | Brand and design system constraints travel with every ticket. No deviation without a trace. |
| **DevOps / Deploy** | Infrastructure tickets with explicit DO/DON'T lists. Every change logged and reviewable. |
| **QA / Testing** | Independent review with documented pass/fail reasoning. Full audit trail per ticket. |

Every team speaks through the same ticket system. Every decision is traceable. Every output is verified.

---

### What makes TCK different

Most workflow tools manage tasks. TCK manages the **context behind the tasks**.

| | Traditional task tool | TCK |
|---|---|---|
| Agent knows its role | From a prompt, re-explained every session | From `CLAUDE.md` — read automatically on start |
| Agent knows the project | Doesn't — relies on the prompt | From `PROJECT_CORE` — always available |
| Work is grounded in documents | Manually copy-pasted into prompts | PM reads `Documents/` and writes tickets from actual content |
| Quality is verified | Optional, ad hoc | Independent QA agent — mandatory for every ticket |
| History is traceable | Partial | Full audit log — every action, every agent, every timestamp |

The result: agents that don't guess. Work that doesn't drift. Output that can be trusted.

---

## 3. Core Beliefs

Every rule in TCK exists because of a specific failure mode.

---

**Belief 1: Context before work.**

*The failure it prevents: fast, confident, wrong.*

An AI agent with no context about the project will optimise for a generic outcome. It will write for a generic user, build for a generic standard, and produce something that is technically fine and strategically irrelevant.

Before any agent touches a ticket, it reads the project's purpose and the customer's identity. This is not a formality. It is the difference between output that fits and output that doesn't.

---

**Belief 2: Documentation is the brain. AI agents are the hands.**

*The failure it prevents: the same mistake, every session.*

AI agents have no memory between sessions. Every conversation starts from zero. This is not a bug — it is the constraint the entire system is designed around.

```
PROJECT_CORE   → WHY this project exists and WHO it is for
Documents/     → WHAT the customer gave us and what we are building
Tickets/       → WHAT specifically to do right now
CLAUDE.md      → WHO this agent is and what it owns
```

When the documentation is right, the agent works right. When documentation is missing, the agent guesses. Every file in TCK exists to make guessing impossible.

---

**Belief 3: Every piece of work gets a ticket.**

*The failure it prevents: undocumented changes, lost context, broken traceability.*

No work happens outside the ticket system. Not a one-line fix. Not a quick content update. Not a small config change. Every ticket carries its full history: who worked on it, what they did, how long it took, and what the reviewer said.

This creates an unbroken chain of evidence. Any agent or human can open a ticket three months later and understand exactly what happened and why.

---

**Belief 4: Quality is a gate, not an afterthought.**

*The failure it prevents: wrong output reaching the customer.*

Every ticket that matters goes through an independent review before it is marked Done. The reviewer didn't build the work and has no bias toward approving it. They check the output against the ticket's requirements — and either pass it or send it back with documented issues.

Work is not done until the reviewer says it is done.

---

**Belief 5: Every agent owns exactly one domain.**

*The failure it prevents: everyone touching everything, no one responsible for anything.*

Each team owns one workspace. The PM does not execute work. Builders do not review their own output. Reviewers do not build. Boundaries are enforced by `CLAUDE.md` — the agent reads its role before reading its task.

Clear ownership is a form of quality control.

---

## 4. The System at a Glance

Every project using TCK has the same structure:

```
<project>/
├── CLAUDE.md                     ← PM Agent — reads this automatically on start
├── TICKET_AGENTS_RULES.md        ← Shared rules imported by all team agents
│
├── mcp/                          ← The ticket engine
│   ├── server.py                 ← MCP server — all ticket logic lives here
│   └── requirements.txt
│
├── Documents/                    ← The knowledge base — everything the PM reads
│   ├── 0 PROJECT_CORE/           ← What this project IS — read first, always
│   ├── 1 Inbox/                  ← Drop zone for unsorted files
│   ├── 2 Projects/               ← Active work — one folder per scope/bug/hotfix
│   ├── 3 Areas/                  ← Standards the team must follow
│   │   ├── Brand/                ← Logos, colours, fonts — used in every output
│   │   ├── Database/             ← Approved schema (if applicable)
│   │   ├── Design System/        ← Component rules, tokens, spacing
│   │   ├── API Contracts/        ← Endpoint specs, auth rules
│   │   ├── Coding Standards/     ← Language conventions, linting
│   │   └── SLAs/                 ← Client agreements, quality targets
│   ├── 4 Resources/              ← Reference only — external docs, research
│   └── 5 Archives/               ← Finished work, superseded standards
│
├── Ticket Logs/                  ← Auto-generated audit trail
│   ├── ALL.md                    ← Every action across all teams
│   └── <team>/
│       ├── TCK-<TEAM>-Builder.md
│       └── TCK-<TEAM>-QA.md
│
└── <team>/                       ← One folder per team (ux, app, content, etc.)
    ├── CLAUDE.md                 ← This team's role, standards, boundaries
    ├── Tickets/                  ← Ticket files managed by MCP
    ├── Artifacts/                ← Deliverables produced by the agent
    └── TicketAttachments/        ← Notes, summaries, QA reports
```

**The core rule:** Each team owns one workspace. The PM manages work via MCP tools — it never builds or reviews directly. Agents never edit ticket files — all state changes go through the MCP server.

---

## 5. PROJECT_CORE — The Brain of Every Project

Before any work begins, every member of the team — human and AI — must be able to answer:

> Why does this project exist? Who is it for? What does success look like?

These answers live in `Documents/0 PROJECT_CORE/`.

---

### What goes in PROJECT_CORE

```
Documents/0 PROJECT_CORE/
├── project-description.md    ← what this is, why it exists, what success looks like
├── customer-persona.md       ← who the audience is, what they need, what they hate
└── principles.md             ← optional — product rules that guide hard decisions
```

This folder is **stable**. It does not change every sprint. It evolves slowly as the project matures. It is the one thing every agent reads before every session.

---

### project-description.md

```markdown
# Project Description

## What is this project?
One paragraph — what it does and who it serves.

## Why does it exist?
The problem it solves. Why it matters.

## Who is it for?
Primary and secondary audience.

## What does success look like?
Measurable outcomes or clear user goals.

## What we are NOT doing
Explicit non-goals — prevents scope creep.
```

---

### customer-persona.md

```markdown
# Customer Personas

## Primary Persona — [Role or Name]
**Goals:** What they are trying to achieve
**Pain points:** What frustrates them today
**Behaviour:** How they interact with the work
**What they care about most:** Speed / accuracy / consistency / etc.

## Secondary Persona — [Role or Name]
...

## Decision Rule
When conflicts arise → ALWAYS prioritise the Primary Persona.
```

---

### principles.md (optional)

Standing rules that guide decisions when trade-offs must be made:

```markdown
# Principles

- Security over convenience — when in doubt, the safer implementation wins
- API contracts before implementation — agree on the interface before writing code
- No breaking changes without a migration path
- Readability is a feature — the next developer is the audience
```

---

### Why PROJECT_CORE matters for AI agents

| Without PROJECT_CORE | With PROJECT_CORE |
|---|---|
| Agent optimises for a generic outcome | Agent understands the project's actual purpose |
| Decisions are based on pattern-matching | Decisions are grounded in the real audience |
| Technically correct, strategically wrong | Built right for the right people |

The PM agent reads `Documents/0 PROJECT_CORE/` before every ticket creation session. Every team `CLAUDE.md` references it as the first source of truth.

---

## 6. Documents — The Knowledge Base

`Documents/` is the single source of truth for everything the PM agent reads. It is structured around the **PARA method** — a knowledge organisation system built on the idea that information has a different value depending on how actionable it is right now.

PARA sorts everything into four buckets: **Projects** (active work with an outcome), **Areas** (responsibilities with no end date), **Resources** (reference you might use someday), and **Archives** (everything finished). TCK extends this with two additions specific to AI agents: a foundational context layer (`PROJECT_CORE`) and a drop zone (`Inbox`) for unsorted input.

**Human's job:** Put files in the right folder — or drop them in `Inbox/` if unsure.  
**PM agent's job:** Read before writing any ticket. Never assume. Always check.

---

### Folder overview

```
Documents/
├── PROJECT_CORE/   ← what this project IS — read first, always
├── Inbox/          ← unsorted drop zone — clear before every session
├── Projects/       ← active work — one folder per scope, bug, or hotfix
├── Areas/          ← standards the team must follow on every ticket
├── Resources/      ← external reference — read, but not required to follow
└── Archives/       ← finished work and superseded standards
```

| Folder | PARA layer | When PM reads it |
|---|---|---|
| `PROJECT_CORE/` | Foundation (TCK addition) | Always first |
| `Inbox/` | Intake (TCK addition) | Before every session |
| `Projects/` | Projects | Always — source of every ticket |
| `Areas/` | Areas | Whenever a ticket touches a standard |
| `Resources/` | Resources | When background context helps |
| `Archives/` | Archives | Rarely — historical reference only |

---

### PROJECT_CORE

The foundation layer. Everything here defines what the project fundamentally is — its purpose, its audience, its non-negotiable principles. It does not change sprint to sprint. It is the one thing every agent reads before every session.

```
Documents/PROJECT_CORE/
├── project-description.md    ← what this is, why it exists, what success looks like
├── customer-persona.md       ← who the end users are and what they need
└── principles.md             ← optional — standing rules for hard decisions
```

This folder has no PARA equivalent. PARA assumes human memory bridges the gap between sessions. AI agents have no memory — `PROJECT_CORE` is that memory, externalised.

---

### Inbox — Drop Zone

The human drops anything here when unsure where it belongs — client emails, screenshots, exported Figma specs, meeting notes, requirements documents from a third party.

When the Inbox has files, the PM agent:
1. Reads each file
2. Suggests where it belongs and why
3. Asks for confirmation before moving
4. Flags anything that could become tickets

```
File: client-requirements-v2.pdf
→ Suggest: Projects/2604 Login Redesign/
→ Reason: "Updated login requirements — scope folder exists, file belongs there"
→ Could create tickets: Yes — mentions new SSO flow, password reset, and session timeout rules
```

The Inbox is cleared before any ticket session begins. If a file stays in Inbox, the PM agent cannot use it.

---

### Projects — Active Work

Every piece of active work gets its own folder. **No exceptions.** This maps directly to PARA's Projects layer: a project has a defined outcome and a finish line. When it is done, the folder moves to Archives.

**Naming pattern: `YYMM <Type> <Name>/`**

| Type | Prefix | Example |
|---|---|---|
| Scope / feature | *(none)* | `2604 Login Redesign/` |
| Bug | `BUG` | `2604 BUG Auth Token Expired/` |
| Hotfix | `FIX` | `2604 FIX DB Connection Pool/` |

**What goes inside:**

| File | Purpose |
|---|---|
| `scope.md` | What will be done, what will NOT be done, timeline |
| `bug-report.md` | Steps to reproduce, expected vs actual, severity |
| `fix-brief.md` | What broke, what the fix must do |
| Reference files | Wireframes, screenshots, specs — flat in the folder |

**When done:** move the entire folder to `Archives/`. Nothing is deleted.

---

### Areas — Standards That Must Be Followed

This is PARA's Areas layer: responsibilities with no end date. In TCK, Areas are **constraints** — things the team must follow on every ticket. They do not expire. Breaking them has consequences.

**The test:**

| Ask this | Areas | Resources |
|---|---|---|
| Must the team follow it? | Yes — it's a constraint | No — it's just reference |
| Does breaking it have consequences? | Yes | No |
| Does it apply to every ticket? | Yes | No |

**What belongs here:**

```
Documents/Areas/
├── Brand/              ← client logo, colours, fonts — used in every UI output
├── Database/           ← approved ER diagram and schema notes
├── Design System/      ← component rules, tokens, spacing
├── API Contracts/      ← endpoint specs, auth rules, request/response formats
├── Coding Standards/   ← language conventions, linting rules, patterns
└── SLAs/               ← client agreements, uptime targets, quality commitments
```

**Examples:**

| In Areas ✅ | In Resources ✅ |
|---|---|
| Client logo | Competitor logos for inspiration |
| Approved ER diagram | Database docs from a vendor |
| API contract | Framework documentation |
| Client SLA | Industry benchmark reports |

When the PM writes a ticket that touches a constraint, it links to the relevant Areas file:

```
Brand assets: [[brand-guidelines.md]]
Approved schema: [[er-diagram.png]]
API contract: [[api-v1.md]]
```

The constraint travels with the ticket. The builder agent reads it. The QA agent verifies against it.

---

### Resources — Reference Only

PARA's Resources layer: material you read but are not obligated to follow. Framework documentation, competitor research, design inspiration, vendor specs. Useful context — not a requirement.

If you find yourself thinking "we must use this" — it belongs in `Areas/`, not here.

---

### Archives — Finished Work

Completed project folders move here from `Projects/`. Superseded standards move here from `Areas/`. Nothing is deleted — everything is archived.

```
Documents/Archives/
├── 2603 Onboarding Redesign/    ← completed scope
└── Areas/Database/v1/           ← old schema after a migration
```

---

## 7. Work Lifecycles

Every piece of work follows a defined path from first contact to final archive.

---

### The Three Types

| Type | Triggered by | Urgency | Brief file |
|---|---|---|---|
| **Scope** | New project, campaign, or feature | Normal | `scope.md` |
| **Bug** | Something broken or wrong | Medium | `bug-report.md` |
| **Hotfix** | Critical issue needing immediate fix | High | `fix-brief.md` |

---

### Scope Lifecycle

```
Customer / client sends brief, requirements, or idea
              ↓
Human drops files in Documents/1 Inbox/
              ↓
PM reads Inbox → suggests destination → human confirms
              ↓
Scope folder created in Documents/2 Projects/YYMM Name/
  ├── scope.md
  └── refs (briefs, wireframes, photos)
              ↓
PM reads 0 PROJECT_CORE/ + scope folder + 3 Areas/
              ↓
PM suggests teams needed → human confirms
              ↓
PM scaffolds any new team workspaces (if needed)
              ↓
PM analyses scope → presents ticket breakdown → human confirms
              ↓
PM creates and opens tickets → teams work
              ↓
Each ticket: InProgress → QAReview → Done
              ↓
All tickets Done
              ↓
Move folder: 2 Projects/ → 5 Archives/
```

**Example — Software team, `2604 Login Redesign/`:**

```
Documents/2 Projects/2604 Login Redesign/
├── scope.md                  ← new login page, SSO, password reset, JWT auth
├── wireframe-login.png       ← client-provided UI mockup
└── wireframe-reset.png       ← forgot password flow
```

PM reads scope + wireframes + `3 Areas/Brand/` + `3 Areas/Database/` + `3 Areas/API Contracts/`.

PM proposes tickets:
```
TCK-UX-2604-001    Login page design — all states, mobile layout        need_qa: true
TCK-UX-2604-002    Forgot password flow — 3 screens, error states       need_qa: true
TCK-APP-2604-001   POST /auth/login — JWT response, rate limiting       need_qa: true
TCK-APP-2604-002   POST /auth/forgot + POST /auth/reset — token expiry  need_qa: true
TCK-DEPLOY-2604-001  JWT secret config — env vars, secret manager       need_qa: false
```

All pass QA → folder moves to `5 Archives/2604 Login Redesign/`.

---

### Bug Lifecycle

```
Something is wrong — reported by client, user, or team
              ↓
Human creates bug folder in Documents/2 Projects/
  └── YYMM BUG Name/
      ├── bug-report.md
      └── screenshot (if available)
              ↓
PM reads bug-report.md + relevant 3 Areas/ standards
              ↓
PM creates ONE ticket → opens it
              ↓
Builder claims → reads report → fixes → submits
              ↓
QA verifies fix meets requirements → pass or reopen
              ↓
Ticket Done → folder moves to 5 Archives/
```

**Example — Software team, `2604 BUG Auth Token Expired/`:**

`bug-report.md`:
```markdown
# Bug Report — JWT Tokens Expiring Too Early

## What happened
Users are being logged out after ~5 minutes instead of the expected 60 minutes.
Reported by 3 clients on 2026-04-17. Started after the 2604 Login Redesign deploy.

## Expected
JWT access token valid for 60 minutes (configured in ENV: JWT_EXPIRY=3600)

## Actual
Tokens expire in ~5 minutes. Suspect ENV var set to 300 instead of 3600 in prod.

## Severity
High — affects all authenticated users in production

## Steps to reproduce
1. Log in via POST /auth/login
2. Wait 6 minutes
3. Make any authenticated request → 401 Unauthorized

## Steps to fix
Verify JWT_EXPIRY in production environment. Correct value and redeploy.
```

PM creates:
```
TCK-APP-2604-003  [BUG] Fix JWT_EXPIRY misconfiguration in prod   need_qa: true
```

---

### Hotfix Lifecycle

```
Critical issue — immediate action needed
              ↓
Human creates hotfix folder in Documents/2 Projects/
  └── YYMM FIX Name/
      └── fix-brief.md
              ↓
PM reads fix-brief.md → creates ONE ticket immediately
  → need_qa decision:
      need_qa: false  → Auto-Done (simple, low-risk, speed matters)
      need_qa: true   → QA reviews (touches critical content or logic)
              ↓
Builder claims → fixes → submits
              ↓
Auto-Done OR QA passes
              ↓
Ticket Done → folder moves to 5 Archives/
```

**Example — `2604 FIX DB Connection Pool/`:**

`fix-brief.md`:
```markdown
# Hotfix — Production DB Connection Pool Exhausted

## What broke
API returning 503 errors under load since 14:30.
Sentry shows "connection pool exhausted" across all app instances.

## Root cause
Connection pool max set to 5 in production config. Should be 20.
Change was never applied when we migrated to the new DB host last sprint.

## Impact
~30% of API requests failing. Revenue impact confirmed by ops team.

## Fix
Update DB_POOL_MAX from 5 to 20 in production environment config.
Restart app instances after applying. Do NOT touch any application code.

## Do NOT
Do not change DB_POOL_MIN or DB_TIMEOUT — those are correct.
Do not restart the DB server itself.
```

PM creates:
```
TCK-DEPLOY-2604-002  [FIX] Set DB_POOL_MAX=20 in production config   need_qa: false
```

`need_qa: false` — single config value, no logic change, speed is critical.

---

### Lifecycle Summary

```
Documents/2 Projects/         → work happens →    Documents/5 Archives/
─────────────────────────────────────────────────────────────────────────
2604 Login Redesign/                               2604 Login Redesign/
  scope.md           → 5 tickets, all Done    →     scope.md

2604 BUG Auth Token Expired/                       2604 BUG Auth Token Expired/
  bug-report.md      → 1 ticket, QA pass      →     bug-report.md

2604 FIX DB Connection Pool/                       2604 FIX DB Connection Pool/
  fix-brief.md       → 1 ticket, Auto-Done    →     fix-brief.md
```

Every piece of work starts with a folder. Every piece of work ends with that folder in Archives. Nothing is deleted.

---

## 8. The Ticket System

Tickets are how all work is tracked, executed, and reviewed. The ticket engine is an MCP server (`mcp/server.py`) that runs automatically via Claude Desktop.

---

### Ticket Lifecycle

```
Backlog → Open → InProgress → QAReview → Done
               │                 ↓ (if issues found)
               │              ReOpen → InProgress
               │
               └──(need_qa: false)──→ Done   ← Auto-Done, no review needed
```

| Status | Meaning |
|---|---|
| `Backlog` | Created but not yet ready to start |
| `Open` | Ready — agent can claim it |
| `InProgress` | Claimed by a builder agent — work in progress |
| `QAReview` | Work submitted — waiting for independent review |
| `Done` | Accepted — either QA-approved or Auto-Done |
| `ReOpen` | QA found issues — back to the builder |

---

### Ticket Structure

```markdown
---
ticket_id: TCK-APP-2604-001
title: POST /auth/login — JWT auth endpoint
team: app
status: Open
need_qa: true
reopen_count: 0
---

## The Goal
Build the login API endpoint. Returns a signed JWT on success.
See full spec: [[scope.md]]
API contract: [[api-v1.md]]
Approved schema: [[er-diagram.png]]

## DO
- POST /auth/login — accepts email + password, returns signed JWT
- JWT expiry: 3600 seconds (read from ENV: JWT_EXPIRY)
- Rate limit: max 5 failed attempts per IP per 15 minutes — return 429 with Retry-After header
- Return 401 for invalid credentials — do not reveal whether email or password was wrong
- Hash passwords with bcrypt (cost factor 12) — never store plaintext

## DON'T DO
- Do not return the user's password hash in any response
- Do not hardcode JWT_SECRET — must read from environment variable
- Do not skip input validation — sanitise email and password before any DB query

## Watch Points
QA: verify rate limiting fires correctly at attempt 6
QA: confirm JWT_SECRET is not present in any log output
```

---

### The `need_qa` Flag

| Value | Route | Use when |
|---|---|---|
| `true` | → QAReview → pass or reopen → Done | User-facing features, API endpoints, security logic, anything risky |
| `false` | → Done immediately (Auto-Done) | Config changes, env vars, internal tooling, low-risk tasks |

---

### The `reopen_count`

Every QA reopen increments `reopen_count`. Agents use it to version their attachment files so each round has its own record:

| `reopen_count` | Builder file | QA file |
|---|---|---|
| `0` | `{ticket_id}-summary.md` | `{ticket_id}-qa-report.md` |
| `1` | `{ticket_id}-summary-r1.md` | `{ticket_id}-qa-report-r1.md` |
| `2` | `{ticket_id}-summary-r2.md` | `{ticket_id}-qa-report-r2.md` |

---

### Artifacts vs TicketAttachments

```
Artifacts/           ← the actual deliverable: code, spec, config, design file
TicketAttachments/   ← agent notes: summary of what was done, QA reports, decisions
```

---

## 9. MCP Tools Reference

All ticket operations go through the MCP server. Agents never edit ticket files directly.

| Tool | Purpose |
|---|---|
| `create_ticket(team, title, goal, dos, donts, ticket_id?, watch_points?, need_qa?)` | Create ticket in Backlog |
| `list_tickets(team, status?)` | List tickets for a team |
| `get_ticket(ticket_id)` | Read full ticket details |
| `get_next_ticket(team)` | Get next Open or ReOpen ticket |
| `execute_ticket(ticket_id, by_agent)` | Claim ticket → InProgress |
| `submit_work(ticket_id, by_agent, summary, note?, tokens?)` | Submit → QAReview or Done |
| `get_next_ticket_for_review(team)` | Get next ticket awaiting review |
| `start_review(ticket_id, by_agent)` | Claim for review (stays QAReview) |
| `review_pass(ticket_id, by_agent, notes, note?, tokens?)` | Approve → Done |
| `review_reopen(ticket_id, by_agent, issues, note?, tokens?)` | Reject → ReOpen |
| `open_ticket(ticket_id, by)` | Move Backlog → Open |
| `open_all_tickets(team, by)` | Open all Backlog tickets for a team |
| `list_teams()` | List all teams in the project |

---

### Submission parameters

| Parameter | Format | Goes to | Example |
|---|---|---|---|
| `summary` / `notes` / `issues` | **Markdown** | Ticket audit log | `"## What was done\n- Built POST /auth/login\n- Rate limiting: 429 after 5 attempts"` |
| `note` | **Plain text** | Activity log row (60 char max) | `"JWT auth done, rate limiting 429 confirmed"` |
| `tokens` | **Integer** | Frontmatter | `3800` |

Time is **automatically calculated** — no need to pass it.

---

## 10. The PM Agent

The PM Agent runs at the project root. It is the entry point for all work. It reads documents, suggests teams, analyses scopes, writes tickets, and keeps work moving.

**The PM agent does not build and does not review.** That belongs to team agents.

---

### Before creating any ticket

1. Read `Documents/0 PROJECT_CORE/` — understand the project and audience
2. Check `Documents/1 Inbox/` — clear it before starting
3. Read the relevant folder in `Documents/2 Projects/` — the scope, bug report, or fix brief
4. Scan `Documents/3 Areas/` — note any brand, standard, or constraint that applies
5. Write `goal`, `dos`, and `donts` from the **actual documents** — never from assumption
6. Wiki-link source documents in the ticket so agents can find them:

```
See full brief: [[scope.md]]
Brand voice: [[brand-voice.md]]
Approved schema: [[er-diagram.png]]
```

---

### Suggesting teams

Before writing any ticket, check what disciplines the scope requires:

| Team | Suggest when the project involves… |
|---|---|
| `ux` | UI screens, user flows, wireframes, design specs |
| `app` | Backend logic, APIs, databases, business rules |
| `web` | Frontend — HTML, CSS, JS, React, Vue |
| `deploy` | Infrastructure, CI/CD, servers, environment config |
| `data` | Databases, migrations, analytics, ETL |
| `mobile` | iOS or Android app screens and logic |
| `qa` | Dedicated testing, manual or automated |

Check existing teams with `list_teams()` first. Present suggestions before creating anything:

```
## Team Suggestions

✅ ux      — already exists
➕ app     — login API, JWT auth, password reset endpoints (needs scaffolding)
➕ deploy  — JWT secret config, environment setup (needs scaffolding)

Shall I scaffold app/ and deploy/ now?
```

---

### Scaffolding a new team

```
mkdir <team>/Tickets/
mkdir <team>/Artifacts/
mkdir <team>/TicketAttachments/
write  <team>/CLAUDE.md
```

Then give the human clear instructions:

```
✅ app/ workspace is ready.

To start the app agent:
1. Open a new Claude Code window
2. Set the folder to: <project>/app/
3. That window is now your app agent.
```

> The PM cannot launch agents. Each agent is a separate Claude Code window opened by the human. Agents communicate through the ticket system — not directly with each other.

---

### Scope analysis and ticket breakdown

When the human says "analyse this scope" or "break this down into tickets":

**Step 1** — Read everything (PROJECT_CORE + scope folder + Areas)
**Step 2** — Suggest teams needed
**Step 3** — Analyse: deliverables, dependencies, risks, `need_qa` per ticket
**Step 4** — Present the full breakdown — never create tickets without showing the plan first

```
## Scope Breakdown — 2604 Login Redesign

### Proposed tickets (5 total)

**UX — 2 tickets**
1. [UX] Login page design — all states, mobile layout
   → need_qa: true  |  Start here — app tickets depend on the UX spec

2. [UX] Forgot password flow — 3 screens, error states
   → need_qa: true  |  Can run parallel with #1

**App — 2 tickets**
3. [App] POST /auth/login — JWT response, rate limiting
   → need_qa: true  |  Depends on: #1 (UX spec must be final)

4. [App] POST /auth/forgot + POST /auth/reset — token expiry
   → need_qa: true  |  Depends on: #2

**Deploy — 1 ticket**
5. [Deploy] JWT secret config — env vars, secret manager setup
   → need_qa: false  |  Depends on: #3

### Suggested order
Round 1 (parallel): tickets 1, 2
Round 2 (parallel): tickets 3, 4 — after UX specs approved
Round 3: ticket 5

### Questions / risks
- ER diagram not in 3 Areas/Database/ yet — is the schema finalised?
- No locked-account error state in wireframes — should I add a watch point?

Confirm and I'll create all 5 tickets.
```

**Step 5** — Wait for confirmation before creating anything
**Step 6** — Create and open tickets

---

### Ticket writing rules

| Field | How to write it |
|---|---|
| `goal` | One clear outcome. What does done look like? Link the source doc. |
| `dos` | Specific requirements from the scope — each line = one testable requirement |
| `donts` | Hard blockers — what must not be done, changed, or broken |
| `watch_points` | QA focus — specific things the reviewer must check |
| `need_qa` | `true` for creative, client-facing, or risky work. `false` for simple/internal tasks |

---

## 11. Team Agents

Each team agent runs in its own Claude Code window opened at `<project>/<team>/`. It reads `CLAUDE.md` automatically on start.

---

### Team workspace

```
<team>/
├── CLAUDE.md             ← role, standards, and boundaries for this team
├── Tickets/              ← ticket files managed by MCP
├── Artifacts/            ← deliverables: code, specs, configs, design files
└── TicketAttachments/    ← notes, summaries, QA reports
```

---

### CLAUDE.md structure per team

```markdown
# <Role> Agent — CLAUDE.md

You are the **<Role> Agent** for this project. Your workspace is the `<team>/` folder.

@../TICKET_AGENTS_RULES.md

## Your Role
2–3 sentences: what this agent does, what it produces, what it is responsible for.

Always pass `team="<team>"` to all MCP tools.

## Standards

When working (InProgress):
- Standard 1
- Standard 2

When reviewing (QA):
- DO list — every requirement met?
- DON'T DO list — any violations?
- Domain-specific checks

## Boundaries
- Always use `team="<team>"`. Never pass another team name.
- Do not modify the Templates/ folder.
```

---

### Builder agent flow

```python
# 1. Get next ticket
ticket = get_next_ticket(team="<your-team>")

# 2. Claim it — execute_ticket is the lock
#    If two agents race, only one succeeds — the other retries
ticket = execute_ticket(ticket["ticket_id"], by_agent="<your-agent>")
suffix = "" if ticket["reopen_count"] == 0 else f"-r{ticket['reopen_count']}"

# 3. Read the full ticket file
#    path → "Tickets/" + ticket["file_name"]
#    Read it — the goal, DO list, DON'T DO list, watch points, source links

# 4. Do the work

# 5. Write attachment
#    path → TicketAttachments/{ticket_id}-summary{suffix}.md

# 6. Submit
submit_work(ticket["ticket_id"], by_agent="<your-agent>",
            summary="## What was done\n- ...\n\nFull notes: [[{ticket_id}-summary{suffix}]]",
            note="One line for the log (60 char max)",
            tokens=1234)
# need_qa: true  → goes to QAReview
# need_qa: false → Auto-Done
```

---

## 12. The QA System

Every ticket with `need_qa: true` must pass an independent review before it is Done. The QA agent did not build the work and has no bias toward approving it.

---

### QA agent flow

```python
# 1. Pick up the review
ticket = get_next_ticket_for_review(team="<your-team>")
suffix = "" if ticket["reopen_count"] == 0 else f"-r{ticket['reopen_count']}"
start_review(ticket["ticket_id"], by_agent="<your-qa-agent>")

# 2. Read the ticket — check DO list, DON'T DO list, Watch Points
#    Read the builder's summary in TicketAttachments/
#    Check the Artifact in Artifacts/

# 3. Write QA report
#    path → TicketAttachments/{ticket_id}-qa-report{suffix}.md

# 4a. Pass
review_pass(ticket["ticket_id"], by_agent="<your-qa-agent>",
            notes="## Audit\n- All requirements met\n\nReport: [[{ticket_id}-qa-report{suffix}]]",
            note="All checks passed",
            tokens=400)

# 4b. Reopen
review_reopen(ticket["ticket_id"], by_agent="<your-qa-agent>",
              issues="## Issues\n- Rate limiting fires at attempt 4, not 5\n\nReport: [[{ticket_id}-qa-report{suffix}]]",
              note="Rate limit threshold off by one — reopen",
              tokens=400)
```

---

### QA checklist principles

| Check | What to verify |
|---|---|
| DO list | Every requirement satisfied? |
| DON'T DO list | Any violations? |
| Watch Points | PM's specific QA focus areas |
| Artifact | Does the deliverable exist in `Artifacts/`? |
| Scope | Nothing added beyond what the ticket asked for? |

---

### When QA reopens

- Ticket moves `QAReview` → `ReOpen`
- Builder picks it up via `get_next_ticket` (ReOpen tickets included)
- Builder claims with `execute_ticket` — `reopen_count` increments
- Builder creates versioned attachment (`-r1`, `-r2`, etc.)
- Builder re-submits → QA reviews again

Every round is fully documented. No history is overwritten.

---

## 13. Activity Logs

Every action in TCK is automatically logged. No manual entry required.

---

### Log files

| File | Contains |
|---|---|
| `Ticket Logs/ALL.md` | Every action across all teams |
| `Ticket Logs/<team>/TCK-<TEAM>-Builder.md` | All builder actions for the team |
| `Ticket Logs/<team>/TCK-<TEAM>-QA.md` | All QA actions for the team |

---

### Log row format

```
| ○ | app | TCK-APP-2604-001 | POST /auth/login endpoint | app-agent | Submitted | 3800 | 22m | JWT auth, rate limiting, 429 on breach | 2026-04-18 10:24:57 |
```

| Column     | Value                                                            |
| ---------- | ---------------------------------------------------------------- |
| Status dot | Visual grouping — rows sharing the same ticket ID get the same dot symbol, making it easy to scan which log entries belong together |
| Team       | Which team                                                       |
| Ticket ID  | Wiki-linked to ticket file                                       |
| Title      | Ticket name                                                      |
| Agent      | Who performed the action                                         |
| Action     | Claimed / Submitted / QA Started / QA Pass / QA Fail / Auto-Done |
| Tokens     | Token count for this action                                      |
| Time       | Duration (auto-calculated)                                       |
| Note       | One-line summary (60 char max)                                   |
| Datetime   | Timestamp                                                        |

---

### What gets logged automatically

| Event | Logged |
|---|---|
| `execute_ticket` | Builder log + ALL |
| `submit_work` | Builder log + ALL |
| `start_review` | QA log + ALL |
| `review_pass` | QA log + ALL |
| `review_reopen` | QA log + ALL |
| `open_ticket` | ALL |

---

## 14. Naming Conventions

---

### Documents/ folders

| What | Pattern | Example |
|---|---|---|
| Scope folder | `YYMM Name/` | `2604 Login Redesign/` |
| Bug folder | `YYMM BUG Name/` | `2604 BUG Auth Token Expired/` |
| Hotfix folder | `YYMM FIX Name/` | `2604 FIX DB Connection Pool/` |

---

### Ticket IDs

| What | Pattern | Example |
|---|---|---|
| Ticket ID | `TCK-<TEAM>-YYMM-NNN` | `TCK-APP-2604-001` |
| Team name | lowercase | `ux`, `app`, `web`, `deploy` |
| Agent name | `<team>-agent`, `<team>-qa` | `app-agent`, `app-qa` |

---

### Attachment files

| `reopen_count` | Builder file | QA file |
|---|---|---|
| `0` | `{ticket_id}-summary.md` | `{ticket_id}-qa-report.md` |
| `1` | `{ticket_id}-summary-r1.md` | `{ticket_id}-qa-report-r1.md` |

---

### General rules

- Ticket files — never edit directly, always use MCP tools
- Artifacts — name clearly: `login-page-spec.md`, `auth-middleware.ts`, `db-migration-2604.sql`
- TicketAttachments — follow `{ticket_id}-{type}{suffix}.md` exactly
- No spaces in artifact or attachment filenames

---

## 15. Anti-Patterns

---

### ❌ Skipping PROJECT_CORE

**What it looks like:** PM jumps straight to tickets. "We know what we're building."

**Why it breaks things:** Every agent decision is a guess. Builders optimise for the wrong audience. Output is technically fine and strategically wrong.

**The rule:** PM reads `Documents/0 PROJECT_CORE/` before every ticket creation session.

---

### ❌ Writing tickets without reading the source documents

**What it looks like:** PM writes tickets from memory or assumption instead of reading the scope file.

**Why it breaks things:** `goal`, `dos`, and `donts` become generic. Agents make wrong decisions. QA has no clear criteria.

**The rule:** Every ticket field must be grounded in an actual document. If you can't cite a source, you don't have enough information to write the ticket yet.

---

### ❌ Editing ticket files directly

**What it looks like:** Someone opens a `.md` ticket file and manually changes the status field.

**Why it breaks things:** MCP server state becomes inconsistent. Logs are skipped. Timestamps are wrong. The audit trail is broken.

**The rule:** All state changes go through MCP tools only.

---

### ❌ Creating a new ticket instead of reopening

**What it looks like:** QA fails. Instead of `review_reopen`, someone creates a fresh ticket: "Fix rate limiting bug."

**Why it breaks things:** History splits across two tickets. The original requirements and context are in the old ticket. The fix is in the new one. Neither tells the full story.

**The rule:** When QA fails, use `review_reopen`. The original ticket carries the full history.

---

### ❌ Submitting without an attachment

**What it looks like:** Builder calls `submit_work` with a one-line summary and no attachment file.

**Why it breaks things:** The QA agent has nothing to read. They cannot verify the work without seeing what was done and what was delivered.

**The rule:** Always write `TicketAttachments/{ticket_id}-summary{suffix}.md` before submitting. If the output is more than 3 lines, it goes in the attachment.

---

### ❌ Keeping files out of Documents/

**What it looks like:** Customer sends a brand brief over email. Human reads it but doesn't put it in Documents/.

**Why it breaks things:** The PM agent cannot read email. It reads `Documents/`. If the file isn't there, the information doesn't exist for the agent.

**The rule:** Everything the customer sends — briefs, logos, specs, feedback — goes into Documents/. If unsure where, drop it in `1 Inbox/`.

---

### At a glance

| Anti-pattern | Rule violated |
|---|---|
| Skipping PROJECT_CORE | Context before work |
| Tickets without source documents | Grounded tickets only |
| Editing ticket files directly | MCP-only state changes |
| New ticket instead of reopening | Preserve full history |
| No attachment on submission | QA needs evidence |
| Files not in Documents/ | PM reads Documents/ — nothing else |

---

## 16. Conclusion

TCK is built on one insight: **AI agents do not need better prompts. They need better environments.**

Software teams feel this more acutely than anyone. A missing spec file becomes a wrong feature. An unchecked side effect becomes a production regression. An agent with no memory of the last sprint makes the same architectural mistake twice. The cost is real: developer time, client trust, and release confidence.

TCK addresses the environment, not the agent. It gives every AI agent a role, a knowledge base, a grounded ticket, and an independent reviewer. It records every action automatically. It prevents the most common failures before they happen — not by making agents smarter, but by making the system around them impossible to misuse.

---

### What TCK gives a software team

| Capability | What it prevents |
|---|---|
| `PROJECT_CORE` — project purpose and customer context, always available | Agents optimising for the wrong outcome |
| `Documents/` — structured knowledge base, PM reads before every ticket | Tickets written from memory or assumption |
| PM Agent — analyses scopes, suggests teams, writes grounded tickets | Generic requirements that leave agents guessing |
| MCP ticket engine — automated lifecycle, full audit trail | Undocumented changes, lost context, broken traceability |
| Independent QA gate — pass or reopen with documented reasoning | Wrong output reaching the customer |
| Auto-Done — `need_qa: false` for low-risk work | QA overhead on changes that don't warrant it |
| Activity logs — tokens, time, agent, timestamp — automatic | No visibility into what was done and when |

---

### Beyond software

TCK was built to solve a software problem. But the problem it solves is not exclusive to software.

Consider a marketing agency running campaigns with AI agents. The agent writes copy — but the client's tone of voice guide was in an email that nobody put into the system. The output is technically good and completely off-brand. The client pushes back. The team rewrites it. Nobody documented why. Next campaign, the same mistake happens again.

Or a design studio using AI to produce UI kits. The agent delivers components — but the approved brand guidelines changed two weeks ago and the file in the shared drive was never updated. The wrong logo ships in the deliverable. QA was skipped because "it was just an update."

Or a consultancy where AI agents draft client reports. No one defined what the engagement scope actually covers. The agent includes analysis the client didn't ask for and omits the section they did. The report goes out. The client is confused. There is no ticket trail, no audit log, no record of what was asked for and what was delivered.

These are not software failures. They are the same three failures TCK was built to prevent: an agent without context, work without structure, output without verification.

TCK is a control kit. The ticket system, the PM Agent, the Documents knowledge base, and the QA gate are patterns — not software constructs. Any team that uses AI agents to execute knowledge work can apply them. The kit does not change. The industry does.

**See it applied:**
- [[TCK Example — Design Studio]] — full walkthrough: brief arrives, PM breaks down the scope, design team works, QA reviews
- [[TCK Example — Content Creator]] — a YouTube creator using TCK for sponsored video production
- [[TCK Example — Legal Firm]] — a boutique law firm using TCK for contract drafting and review

---

### The one thing to remember

> Put your context in Documents/.
> Let the PM agent read it.
> Let the agents do the work.
> Let QA verify the output.

That is TCK.

---

*TCK — Ticket Control Kit*
*Structure for AI agents. Context for every decision. Quality on every output.*

*Version April 2026 — Rachakrit Monyanon*
