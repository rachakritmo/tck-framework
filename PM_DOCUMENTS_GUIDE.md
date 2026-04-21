# PM Documents Guide

`Documents/` is the single source of truth for everything about this project.

**Human's job:** Put files in the right folder (or drop in `1 Inbox/` if unsure).  
**PM agent's job:** Read those files before writing any ticket — never assume, always check.

---

## Folder Overview

```
Documents/
├── 0 PROJECT_CORE/   ← what this project IS — read this first, always
├── 1 Inbox/          ← unsorted drop zone — human puts anything here
├── 2 Projects/       ← active work — one folder per scope / bug / hotfix
├── 3 Areas/          ← standards the team MUST follow — brand, schema, contracts
├── 4 Resources/      ← reference only — external docs, research, inspiration
└── 5 Archives/       ← finished work — completed scopes, old specs, old decisions
```

---

## 0 PROJECT_CORE — Always Read First

Foundational files that define what this project is. Read before anything else.

```
0 PROJECT_CORE/
├── project-description.md   ← what the product does, who it's for, the vision
└── customer-persona.md      ← who the end users are, their goals and pain points
```

The PM agent reads these **before every ticket creation session** to stay grounded in the project's purpose.

---

## 1 Inbox — Drop Zone

The human drops anything here when unsure where it belongs — emails, screenshots, files from a customer meeting, random notes.

**PM agent behaviour when Inbox has files:**
1. Read each file
2. Suggest where it belongs + one-line reason
3. Ask the human to confirm before moving
4. If a file could become tickets, say so

```
File: customer-feedback-april.md
→ Suggest: 2 Projects/2604 Login Redesign/
→ Reason: "Feedback on the login flow currently in scope."
→ Could create tickets: Yes — mentions broken back button and missing error state
```

---

## 2 Projects — Active Work

Every active scope, bug, and hotfix gets its own folder here. **No exceptions — always create a folder.**

**Folder naming pattern: `YYMM <Type> <Name>/`**

| Work type | Prefix | Folder name example |
|---|---|---|
| Scope / feature | *(none)* | `2604 Login Redesign/` |
| Bug | `BUG` | `2604 BUG Login Crash/` |
| Hotfix | `FIX` | `2604 FIX Cart Rounding/` |

**What goes inside:**

| File | Purpose |
|---|---|
| `scope.md` | Scope of work — deliverables, what's in and out, timeline |
| `bug-report.md` | Bug — steps to reproduce, expected vs actual, severity |
| `fix-brief.md` | Hotfix — what broke, what the fix must do |
| `wireframe-*.png` | Wireframes, mockups, UI references from the customer |
| `er-diagram.png` | ER diagram while it's still being designed (move to Areas when approved) |
| `screenshot-*.png` | Error screenshots, customer-provided examples |

**Rules:**
- Always create the folder first — even if there are no attachments yet
- Every folder must have at least one brief file (`scope.md`, `bug-report.md`, or `fix-brief.md`)
- Keep refs flat inside the folder — no subfolders unless there are 10+ files
- **When work is done:** move the entire folder to `5 Archives/`

**Example:**
```
2 Projects/
├── 2604 Login Redesign/
│   ├── scope.md
│   ├── wireframe-login.png
│   └── wireframe-forgot-password.png
├── 2604 BUG Login Crash/
│   ├── bug-report.md
│   └── screenshot-error.png
└── 2604 FIX Cart Rounding/
    └── fix-brief.md
```

---

## 3 Areas — Standards the Team Must Follow

Everything in `3 Areas/` is a **constraint** — the team is responsible for upholding it on every ticket. It has no end date. Breaking it has consequences with the customer or the codebase.

**The test: Areas vs Resources**

| Ask this | Areas ✅ | Resources ✅ |
|---|---|---|
| Must the team follow it? | Yes — it's a constraint | No — it's just reference |
| Does breaking it have consequences? | Yes | No |
| Does it apply across all tickets? | Yes | No |
| Examples | Customer logo, ER schema, SLA, coding standards | React docs, competitor screenshots, design inspiration |

**Folder structure:**

```
3 Areas/
├── Brand/                   ← customer-provided brand assets — used in every UI ticket
│   ├── logo.png             ← primary logo
│   ├── logo-dark.png        ← dark / reversed variant
│   ├── logo-icon.png        ← icon / favicon variant
│   └── brand-guidelines.md  ← colours, fonts, usage rules (if provided)
├── Database/                ← approved schema — all dev tickets must match this
│   ├── er-diagram.png       ← finalised ER diagram
│   └── schema-notes.md      ← table descriptions, relationships, naming rules
├── Design System/           ← UI component rules, spacing, tokens
│   └── design-system.md
├── API Contracts/           ← endpoint specs, request/response formats, auth rules
│   └── api-v1.md
├── Coding Standards/        ← language conventions, patterns, linting rules
│   └── standards.md
└── SLAs/                    ← client agreements, uptime targets, response times
    └── sla.md
```

**Key rules:**
- Customer logo, icon, font, colour palette → always `3 Areas/Brand/`
- ER diagram while designing → `2 Projects/<scope>/` → once approved, **move to `3 Areas/Database/`**
- Agents building UI tickets must check `3 Areas/Brand/` for logo and colours
- Agents building backend tickets must check `3 Areas/Database/` for the approved schema

---

## 4 Resources — Reference Only

External material the team reads but does not own or maintain. No obligation to follow it — it's context.

```
4 Resources/
├── react-docs-notes.md       ← framework reference
├── competitor-analysis.md    ← research
└── design-inspiration/       ← mood boards, screenshots from other products
```

If you find yourself thinking "we must use this" — it belongs in `3 Areas/`, not here.

---

## 5 Archives — Finished Work

When a project folder in `2 Projects/` is done, move it here. When a standard in `3 Areas/` is superseded, move the old version here.

Nothing is deleted — everything is archived.

```
5 Archives/
├── 2603 Onboarding Redesign/   ← completed scope
└── 3 Areas/Database/v1/        ← old schema after a migration
```

---

## Before Creating Any Ticket

1. Read `Documents/0 PROJECT_CORE/` — know what the project is and who the customer is
2. Check `Documents/1 Inbox/` — clear it before moving on
3. Read the relevant folder in `Documents/2 Projects/` — the scope, bug report, or fix brief
4. Scan `Documents/3 Areas/` — note any brand, schema, or standard the ticket must respect
5. Write `goal`, `dos`, and `donts` from the **actual documents** — never use generic placeholders
6. Wiki-link source documents in the ticket goal so agents can find them:

```
See full spec: [[scope.md]]
Brand assets: [[brand-guidelines.md]]
Approved schema: [[er-diagram.png]]
```
