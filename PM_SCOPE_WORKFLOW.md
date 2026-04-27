# PM Scope Workflow

## Analyse a scope and break it into tickets

When the human says "analyse this scope", "break this down", or "create tickets from this scope" — follow this process:

---

### Step 1 — Read everything first

Before proposing anything, read:
- `Documents/0 PROJECT_CORE/` — understand the project and customer
- The scope folder in `Documents/2 Projects/YYMM <Name>/` — read `scope.md` and every ref file (wireframes, ER diagrams, photos)
- `Documents/3 Areas/` — note any brand, schema, or standards that apply

---

### Step 2 — Suggest teams

Before breaking down tickets, identify what disciplines the scope requires and suggest which teams to create. Check existing teams first with `list_teams()` — only suggest new ones.

Common teams and when to suggest them:

| Team      | Suggest when the scope involves…                                |
| --------- | --------------------------------------------------------------- |
| `ux`      | UI screens, user flows, wireframes, design specs, accessibility |
| `app`     | Backend logic, APIs, databases, business rules, integrations    |
| `web`     | Frontend implementation — HTML, CSS, JS, React, Vue             |
| `mobile`  | iOS or Android app screens and logic                            |
| `deploy`  | Infrastructure, CI/CD pipelines, servers, environment config    |
| `data`    | Databases, migrations, analytics, reporting, ETL                |
| `qa`      | Dedicated QA team for manual or automated testing               |
| `content` | Copywriting, translations, CMS content                          |

Present team suggestions before the ticket breakdown:

```
## Team Suggestions

Based on the scope, you'll need:

✅ ux       — 3 screens described in wireframes (already exists)
➕ app      — login API, JWT auth, password reset endpoints (needs to be created)
➕ deploy   — JWT secret config, environment setup (needs to be created)

Shall I scaffold `app` and `deploy` now, or do you want to handle that first?
```

- ✅ = team already exists (`list_teams()` returned it)
- ➕ = team needs to be created (`mkdir` + write `AGENTS.md`, plus the runtime files the human selects)

Wait for the human to confirm before scaffolding any new team or writing any ticket.

---

### Step 3 — Analyse the scope

Break the scope into logical units of work. Ask:
- What are the distinct deliverables?
- What must be built before something else can start? (dependencies)
- Which team owns each piece?
- What needs QA review vs what can auto-complete?
- What are the risks or unknowns worth flagging?

---

### Step 4 — Present the breakdown to the human first

Never create tickets without showing the plan first. Present it like this:

```
## Scope Breakdown — 2604 Login Redesign

### Proposed tickets (6 total)

**UX — 3 tickets**
1. [UX] Login page UI
   → Design the login form, error states, and mobile layout
   → Depends on: nothing — start here
   → need_qa: true

2. [UX] Forgot password flow
   → Design the email entry, confirmation, and reset screens
   → Depends on: #1 (shares design patterns)
   → need_qa: true

3. [UX] Design system tokens update
   → Add new colour tokens from brand-guidelines.md
   → Depends on: nothing — can run parallel
   → need_qa: false  (internal, low risk)

**App — 2 tickets**
4. [App] Auth API — login endpoint
   → POST /auth/login, JWT response, rate limiting
   → Depends on: #1 (UX spec must be final)
   → need_qa: true

5. [App] Auth API — password reset flow
   → POST /auth/forgot, POST /auth/reset, token expiry
   → Depends on: #2 (UX spec must be final)
   → need_qa: true

**Deploy — 1 ticket**
6. [Deploy] JWT secret rotation config
   → Environment variables, secret manager setup
   → Depends on: #4
   → need_qa: false

### Suggested order
Round 1 (parallel): tickets 1, 2, 3
Round 2 (parallel): tickets 4, 5  — after UX specs approved
Round 3: ticket 6

### Questions / risks
- No error state shown in wireframes for locked accounts — should I add a watch point?
- ER diagram not in 3 Areas/Database/ yet — is the schema finalised?

Confirm and I'll create all 6 tickets.
```

---

### Step 5 — Wait for human confirmation

Do not create any ticket until the human says yes (or asks to adjust). If they request changes — add, remove, reorder, change team — update the plan and confirm again before proceeding.

---

### Step 6 — Create and open tickets

Once confirmed, create all tickets then open them:

```python
# Create each ticket
create_ticket(team, title, goal, dos, donts, need_qa=...)

# Open all at once per team
open_ticket(ticket_id, by="pm-agent")   # repeat per ticket
# or
open_all_tickets(team, by="pm-agent")
```

Write `goal`, `dos`, and `donts` from the **actual scope content** — quote the spec, reference the wireframe, cite the standard. Never use generic placeholders.

**Ticket writing rules:**

| Field | How to write it |
|---|---|
| `goal` | One clear outcome. What does done look like? Link the source: `See: [[scope.md]]` |
| `dos` | Specific requirements pulled from the scope. Each line = one testable requirement |
| `donts` | Hard blockers — what the agent must not do, not change, not break |
| `watch_points` | QA focus — only fill if there's something specific QA should scrutinise |
| `need_qa` | `true` for user-facing or risky work. `false` for internal/config/low-risk tasks |
| `work_with_human` | `false` (default) autonomous. `true` — agent pauses after claiming, shows the spec, and waits for the human to guide the session; after each output the agent prompts "Say **submit** to close this ticket" — human types `submit` to trigger submit |
