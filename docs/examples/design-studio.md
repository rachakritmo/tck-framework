# TCK Example — Design Studio

> A full walkthrough: client brief arrives, PM breaks down the scope, designers work, QA reviews.

---

## The Setup

A design studio takes on a brand identity project for a fintech startup. The client needs a logo, a colour system, a typography scale, and a component library starter kit. Two designers on the job — one senior, one junior.

**Teams:**

```
design/   ← produces all visual deliverables
qa/       ← independent review against client brief and brand standards
```

Each team has a `CLAUDE.md` that the agent reads automatically when it opens its workspace.

---

### design/CLAUDE.md

```markdown
# Design Agent — CLAUDE.md

You are the **Design Agent** for this project. Your workspace is the `design/` folder.

@../TICKET_AGENTS_RULES.md

---

## Your Role

You produce visual brand deliverables — logos, colour systems, typography scales,
and component specifications. You work from tickets written by the PM Agent.
Every ticket tells you what to build, what constraints apply, and which source
documents to read before you start.

Always pass `team="design"` to all MCP tools.

---

## Design Standards

When building (InProgress):
- Read the full ticket before producing anything — goal, DO, DON'T DO, Watch Points
- Read every linked document in the ticket (scope, brand guidelines, client brief)
- Check `Documents/Areas/Brand/` for studio quality standards that apply to every job
- Deliver artifacts to `Artifacts/` — named clearly: `colour-system.md`, `logo-primary.svg`
- Write a summary in `TicketAttachments/{ticket_id}-summary.md` before submitting
- Document every significant decision — why a colour was chosen, why a typeface was rejected

When reviewing your own work before submitting:
- Does the deliverable satisfy every item in the DO list?
- Does it violate anything in the DON'T DO list?
- Does it match the brief direction (not just technically correct — directionally right)?
- Are WCAG contrast ratios documented if colour is involved?
- Is the artifact file present and named correctly?

---

## Boundaries

- Always use `team="design"`. Never pass another team name.
- Do not review your own submitted work — that belongs to the QA agent.
- Do not edit ticket files directly — all status changes go through MCP tools.
- Do not produce deliverables outside the scope defined in the ticket.
```

---

### qa/CLAUDE.md

```markdown
# QA Agent — CLAUDE.md

You are the **QA Agent** for this project. Your workspace is the `qa/` folder.

@../TICKET_AGENTS_RULES.md

---

## Your Role

You review completed design work independently. You did not build what you are
reviewing and you have no stake in approving it. Your job is to verify the output
meets every requirement in the ticket — and to reopen it with documented issues
if it does not.

Always pass `team="design"` to all MCP tools.

---

## QA Standards

When reviewing (QAReview):
- Read the full ticket: DO list, DON'T DO list, Watch Points
- Read the builder's summary in `TicketAttachments/{ticket_id}-summary.md`
- Read the actual artifact in `Artifacts/` — not just the summary
- Check `Documents/Areas/Brand/brand-guidelines.md` for studio standards
- Check `Documents/Areas/Client SLAs/` for what the engagement covers

For every review, verify:
- **DO list** — is every requirement satisfied? Check each item explicitly.
- **DON'T DO list** — any violations? Check each item explicitly.
- **Watch Points** — the PM flagged these for a reason. Give them extra attention.
- **Artifact** — does it exist? Is it named correctly? Is it complete?
- **Scope** — did the agent add anything the ticket didn't ask for?

Write your audit in `TicketAttachments/{ticket_id}-qa-report.md` before calling
`review_pass` or `review_reopen`. Never pass without a written report.

When reopening:
- List every issue specifically — not "colour doesn't look right" but
  "neutral-300 (#C4C4C4) on white (#FFFFFF) fails WCAG AA at 1.6:1 — minimum 4.5:1 required"
- Reference the exact DO or DON'T DO item that was violated

---

## Boundaries

- Always use `team="design"`. Never pass another team name.
- Do not build or produce deliverables — review only.
- Do not approve work that has unresolved Watch Points.
- Do not edit ticket files directly — all status changes go through MCP tools.
```

---

## Step 1 — Brief Arrives in Inbox

The client sends a brand brief PDF over email. The human drops it in `Documents/Inbox/`.

```
Documents/Inbox/
└── fintech-brand-brief.pdf
```

The PM agent reads it and responds:

```
File: fintech-brand-brief.pdf
→ Suggest: Documents/Projects/2604 Fintech Brand Identity/
→ Reason: New scope — needs a project folder before tickets can be written
→ Action needed: Create scope.md from this brief, then I can break it down

Key deliverables I found in the brief:
- Primary logo + reversed variant
- Colour palette (primary, secondary, neutral, semantic)
- Typography scale (headings, body, captions)
- Component library starter: buttons, inputs, cards, badges

Shall I create the project folder and scope.md now?
```

Human confirms. PM creates:

```
Documents/Projects/2604 Fintech Brand Identity/
├── scope.md                 ← written from the brief
└── fintech-brand-brief.pdf  ← moved from Inbox
```

---

## Step 2 — PM Reads Everything Before Writing a Single Ticket

Before proposing any tickets, the PM reads:

1. `Documents/PROJECT_CORE/project-description.md` — the studio specialises in fintech and healthcare; precision and trust are the recurring themes
2. `Documents/PROJECT_CORE/customer-persona.md` — clients are CTOs and founders who care about looking credible to investors, not trendy
3. `Documents/Projects/2604 Fintech Brand Identity/scope.md` — the deliverables, the timeline, what is and is not in scope
4. `Documents/Areas/Brand/brand-guidelines.md` — the studio's own quality standards for delivered brand work
5. `Documents/Areas/Client SLAs/standard-retainer.md` — confirms this engagement covers brand identity only, not marketing materials

---

## Step 3 — PM Proposes the Ticket Breakdown

```
## Scope Breakdown — 2604 Fintech Brand Identity

### Teams needed
✅ design   — already exists
✅ qa       — already exists

### Proposed tickets (5 total)

**Design — 4 tickets**

1. Logo design — primary mark + reversed variant
   → Deliver: SVG + PNG at 3 sizes. Light and dark background versions.
   → need_qa: true  |  Client-facing, high stakes — must pass QA

2. Colour system — primary, secondary, neutral, semantic tokens
   → Deliver: colour-system.md with hex values, usage rules, WCAG contrast ratios
   → need_qa: true  |  Accessibility requirements make this a QA candidate

3. Typography scale — heading, body, caption levels
   → Deliver: typography-scale.md with font, size, weight, line-height per level
   → need_qa: true

4. Component library starter — buttons, inputs, cards, badges
   → Deliver: component-library.fig (Figma file) + component-notes.md
   → need_qa: true  |  Must be consistent with colour and typography tickets

### Suggested order
Round 1: ticket 1 (logo) and ticket 2 (colour) in parallel
Round 2: ticket 3 (typography) — can start after colour is approved
Round 3: ticket 4 (components) — depends on colour + typography both done

### Watch points flagged
- Brief says "trustworthy and modern" — no further guidance. I'll add a watch point
  for QA to verify the logo doesn't read as generic fintech.
- WCAG contrast ratios not mentioned in brief. I'm adding it to the colour ticket's
  DO list as a studio standard from Areas/Brand/brand-guidelines.md.
- Figma file delivery format is the studio standard — brief didn't specify, but
  Areas/Client SLAs/standard-retainer.md confirms this is the default.

Confirm and I'll create all 4 tickets.
```

Human confirms.

---

## Step 4 — PM Creates and Opens the Tickets

PM creates each ticket with requirements pulled directly from the scope and Areas documents. Example:

```markdown
---
ticket_id: TCK-DESIGN-2604-002
title: Colour system — primary, secondary, neutral, semantic tokens
team: design
need_qa: true
reopen_count: 0
---

## The Goal
Define the full colour system for the Fintech Brand Identity.
See scope: [[scope.md]]
Studio brand standards: [[brand-guidelines.md]]

## DO
- Deliver a colour-system.md file with named tokens and hex values
- Include: primary (2 shades), secondary (2 shades), neutral scale (6 shades),
  semantic colours (success, warning, error, info)
- Every colour used on text must pass WCAG AA contrast ratio (4.5:1 minimum)
- Document intended usage for each token (e.g. "primary-600 = CTA button background")
- Palette must read as trustworthy and credible — avoid neon, pastels, or
  colours associated with consumer-facing fintech (avoid Robinhood green,
  Revolut gradient)

## DON'T DO
- Do not deliver fewer than 12 named tokens
- Do not skip contrast ratio documentation
- Do not use colours from previous client projects

## Watch Points
QA: verify contrast ratios are documented and correct
QA: sanity check palette against "trustworthy, not trendy" brief direction
```

---

## Step 5 — Design Agent Works the Ticket

The design agent claims `TCK-DESIGN-2604-002`:

```
execute_ticket("TCK-DESIGN-2604-002", by_agent="design-agent")
```

It reads the ticket, reads `[[scope.md]]` and `[[brand-guidelines.md]]`, produces the colour system, and writes:

```
Artifacts/colour-system.md
TicketAttachments/TCK-DESIGN-2604-002-summary.md
```

`TCK-DESIGN-2604-002-summary.md`:
```markdown
## What was done
Defined a 14-token colour system for the Fintech Brand Identity.

Palette direction: deep navy primary, slate secondary, clean neutrals,
standard semantic colours. Avoided consumer-fintech associations.
All text colour combinations pass WCAG AA.

## Tokens delivered
- primary-500 / primary-700
- secondary-400 / secondary-600
- neutral-100 through neutral-900 (6 stops)
- semantic: success, warning, error, info

## Contrast ratios
All documented in [[colour-system.md]] — minimum 4.5:1 confirmed on all text uses.

Artifact: [[colour-system.md]]
```

Agent submits:

```python
submit_work(
    "TCK-DESIGN-2604-002",
    by_agent="design-agent",
    summary="## Colour system delivered\n14 tokens, WCAG AA confirmed.\n\nFull notes: [[TCK-DESIGN-2604-002-summary]]\nArtifact: [[colour-system.md]]",
    note="14 tokens, WCAG AA contrast confirmed on all text uses",
    tokens=2100
)
```

Ticket moves to `QAReview`.

---

## Step 6 — QA Agent Reviews

The QA agent picks up the ticket:

```python
ticket = get_next_ticket_for_review(team="design")
start_review(ticket["ticket_id"], by_agent="qa-agent")
```

QA reads:
- The ticket — DO list, DON'T DO list, Watch Points
- `[[TCK-DESIGN-2604-002-summary.md]]` — what the designer said they did
- `[[colour-system.md]]` — the actual deliverable

QA runs through the checklist:

```markdown
## QA Audit — TCK-DESIGN-2604-002

### DO list
- [x] colour-system.md delivered with named tokens and hex values
- [x] 14 tokens (exceeds minimum of 12)
- [x] primary, secondary, neutral, semantic all present
- [x] Usage documentation included for each token
- [x] WCAG AA contrast ratios documented

### DON'T DO list
- [x] No fewer than 12 tokens — 14 delivered ✅
- [x] Contrast ratios documented ✅
- [x] No colours from previous projects (checked against studio reference) ✅

### Watch Points
- [x] Contrast ratios verified independently — minimum 4.5:1 confirmed ✅
- [x] Palette direction: deep navy + slate reads trustworthy, not trendy ✅
      No consumer-fintech colour associations found

### Result: PASS
```

QA writes the report and passes:

```python
review_pass(
    "TCK-DESIGN-2604-002",
    by_agent="qa-agent",
    notes="## Audit passed\nAll DO items satisfied. WCAG AA confirmed independently.\nPalette reads credible — passes brief direction check.\n\nFull report: [[TCK-DESIGN-2604-002-qa-report]]",
    note="All checks passed — WCAG AA confirmed, palette direction approved",
    tokens=600
)
```

Ticket moves to `Done`.

---

## What the Workflow Produces

By the time the colour system reaches the client, it has:

- Been written against requirements pulled from the actual brief — not a prompt
- Been checked against the studio's brand standards from `Areas/`
- Been reviewed by an independent agent who did not build it
- Left a full audit trail: who worked on it, what they checked, what they found

If the client comes back three months later and asks why a specific colour was chosen, the answer is in the ticket. If a junior designer joins the team, the standards are in `Areas/` — not in someone's head.

That is what TCK gives a design studio.
