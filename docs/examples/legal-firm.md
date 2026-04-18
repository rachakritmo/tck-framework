# TCK Example — Legal Firm

> A full walkthrough: client engagement arrives, PM breaks down the scope, research and drafting teams work, QA reviews.

---

## The Setup

A boutique firm specialises in technology contracts — SaaS agreements, IP licensing, data processing addenda. Three attorneys, two paralegals. They use AI agents for legal research, first-draft contract writing, and client-facing summaries. Before TCK, every draft started with a fresh prompt and a senior attorney spending two hours correcting output that missed jurisdiction-specific clauses, exceeded the retainer scope, or invented obligations the firm had never agreed to.

**Teams:**

```
research/   ← case law, jurisdiction rules, regulatory updates
drafting/   ← contract first drafts, clause libraries, redlines
qa/         ← independent review against client scope and firm standards
```

Each team has a `CLAUDE.md` that the agent reads automatically when it opens its workspace.

---

### research/CLAUDE.md

```markdown
# Research Agent — CLAUDE.md

You are the **Research Agent** for this project. Your workspace is the `research/` folder.

@../TICKET_AGENTS_RULES.md

---

## Your Role

You find current legal obligations, jurisdiction-specific requirements, and
relevant case law or regulatory guidance. Your output feeds the drafting agent.
Accuracy is the only measure — do not include anything you cannot source.
You do not draft contracts or legal language.

Always pass `team="research"` to all MCP tools.

---

## Research Standards

When building (InProgress):
- Read the full ticket — understand exactly what the drafting agent needs
- Read PROJECT_CORE to understand the firm's practice area and client profile
- Prioritise current sources — regulations change; note the date of every source
- Flag anything you could not verify or that has changed recently
- Do not include obligations you are uncertain about — flag them explicitly instead
- Deliver findings to `Artifacts/` as a structured markdown file
- Write a summary in `TicketAttachments/{ticket_id}-summary.md` before submitting

---

## Boundaries

- Always use `team="research"`. Never pass another team name.
- Do not draft contract language or legal clauses — research only.
- Do not make legal conclusions — present sources and let the drafting agent apply them.
- Do not edit ticket files directly — all status changes go through MCP tools.
```

---

### drafting/CLAUDE.md

```markdown
# Drafting Agent — CLAUDE.md

You are the **Drafting Agent** for this project. Your workspace is the `drafting/` folder.

@../TICKET_AGENTS_RULES.md

---

## Your Role

You write first-draft contracts, addenda, and client-facing summaries. Every
draft is grounded in the client brief, the firm's approved clause library, the
applicable jurisdiction requirements, and the retainer scope. You do not
invent obligations. You do not exceed scope. You do not approve your own work.

Always pass `team="drafting"` to all MCP tools.

---

## Drafting Standards

When building (InProgress):
- Read the full ticket: goal, DO, DON'T DO, Watch Points
- Read the client brief linked in the ticket — know what Acme needs and what they agreed to
- Read `Documents/Areas/Firm Standards/clause-library.md` — use approved clauses first
- Read `Documents/Areas/Firm Standards/style-guide.md` — numbering, defined terms, active voice
- Read the jurisdiction reference linked in the ticket — do not invent obligations
- Read `Documents/Areas/Client SLAs/` — confirm what the retainer covers before drafting
- Deliver the draft to `Artifacts/` as a markdown file
- Write a summary in `TicketAttachments/{ticket_id}-summary.md` — note every place you
  deviated from the clause library, flagged a conflict, or left a decision for the attorney

When reviewing your own work before submitting:
- Is every required clause present?
- Does any clause exceed the retainer scope?
- Is every obligation sourced to the jurisdiction reference or clause library?
- Are passive voice constructions removed per style-guide.md?
- Are all defined terms formatted correctly?

---

## Boundaries

- Always use `team="drafting"`. Never pass another team name.
- Do not invent legal obligations — every clause must come from the clause library
  or the jurisdiction reference in the ticket.
- Do not include scope not covered by the client retainer.
- Do not approve your own work — QA reviews every draft.
- Do not edit ticket files directly — all status changes go through MCP tools.
```

---

### qa/CLAUDE.md

```markdown
# QA Agent — CLAUDE.md

You are the **QA Agent** for this project. Your workspace is the `qa/` folder.

@../TICKET_AGENTS_RULES.md

---

## Your Role

You review completed drafts independently. You did not write what you are
reviewing and you have no stake in approving it. Your job is to verify the
draft meets every requirement in the ticket — and to reopen it with specific,
documented issues if it does not. Every issue you raise must cite the exact
clause, the exact DO or DON'T DO item it violates, and the source document
that defines the correct standard.

Always pass `team="drafting"` to all MCP tools.

---

## QA Standards

When reviewing (QAReview):
- Read the full ticket: DO list, DON'T DO list, Watch Points
- Read the builder's summary in `TicketAttachments/{ticket_id}-summary.md`
  — pay attention to any flags or decisions the drafting agent noted
- Read the actual draft in `Artifacts/` — not just the summary
- Read `Documents/Areas/Firm Standards/clause-library.md`
- Read `Documents/Areas/Firm Standards/style-guide.md`
- Read `Documents/Areas/Client SLAs/` for the relevant retainer
- Read the jurisdiction reference linked in the ticket

For every review, verify:
- **DO list** — every required element present? Check each item explicitly.
- **DON'T DO list** — any violations? Check each item explicitly.
- **Watch Points** — the PM flagged these because they are the highest risk items.
- **Scope** — does any clause create an obligation outside the retainer?
- **Sources** — can every obligation be traced to the clause library or jurisdiction reference?
- **Style** — passive voice, defined terms format, numbering per style-guide.md.

Write your audit in `TicketAttachments/{ticket_id}-qa-report.md` before calling
`review_pass` or `review_reopen`. Never pass without a written report.

When reopening — be exact:
- Quote the clause number and text that has the issue
- State which DO item, DON'T DO item, or Watch Point it violates
- State what the correct standard is and where it comes from

---

## Boundaries

- Do not draft contract language — review only.
- Do not pass a draft with an obligation you cannot source.
- Do not pass a draft where any clause exceeds the retainer scope.
- Do not edit ticket files directly — all status changes go through MCP tools.
```

---

## Step 1 — Client Brief Arrives in Inbox

Acme SaaS sends an engagement brief by email. A paralegal drops it in `Documents/Inbox/`.

```
Documents/Inbox/
└── acme-engagement-brief.pdf
```

The PM agent reads it and responds:

```
File: acme-engagement-brief.pdf
→ Suggest: Documents/Projects/2604 Acme SaaS Agreement/
→ Reason: New engagement — needs a project folder before tickets can be written
→ Action needed: Create scope.md and client-brief.md from this document

Key items found:
- Deliverables: Master SaaS Agreement + Data Processing Addendum for EU customers
- Client risk areas: liability cap, IP ownership of customisations, data residency
- Counterparty has sent an initial draft (attached to the email — needs to be added)
- Timeline: first draft needed within 5 business days

Missing: counterparty draft not in Inbox — please add counterparty-draft.pdf
before I write the research tickets.

Shall I create the project folder and scope.md now?
```

Human adds the counterparty draft and confirms. PM creates:

```
Documents/Projects/2604 Acme SaaS Agreement/
├── scope.md                  ← written from the brief
├── client-brief.md           ← Acme's requirements and risk areas
└── counterparty-draft.pdf    ← initial draft from the other side
```

---

## Step 2 — PM Reads Everything Before Writing a Single Ticket

Before proposing any tickets, the PM reads:

1. `Documents/PROJECT_CORE/project-description.md` — technology contracts for SaaS companies; UK and EU law; client protection first
2. `Documents/PROJECT_CORE/customer-persona.md` — primary client is a CTO or General Counsel at a Series A–C SaaS company; wants clear, enforceable language; hates ambiguity
3. `Documents/Projects/2604 Acme SaaS Agreement/scope.md` — deliverables, timeline, what is and is not in scope
4. `Documents/Projects/2604 Acme SaaS Agreement/client-brief.md` — Acme's specific risk areas: liability cap, IP ownership, data residency
5. `Documents/Areas/Firm Standards/clause-library.md` — approved clauses the drafting agent must use
6. `Documents/Areas/Firm Standards/style-guide.md` — numbering, defined terms, active voice requirement
7. `Documents/Areas/Jurisdiction/uk-gdpr-notes.md` — current UK GDPR processor obligations
8. `Documents/Areas/Client SLAs/acme-retainer.md` — confirms the engagement covers MSA + DPA only; excludes marketing materials and employment contracts

---

## Step 3 — PM Proposes the Ticket Breakdown

```
## Scope Breakdown — 2604 Acme SaaS Agreement

### Teams needed
✅ research   — already exists
✅ drafting   — already exists
✅ qa         — already exists

### Proposed tickets (5 total)

**Research — 2 tickets**
1. Research current UK/EU GDPR processor obligations for SaaS
   → need_qa: false  |  Internal — feeds the drafting agent, low risk
   → Start here

2. Review counterparty draft — flag non-standard clauses against firm standards
   → need_qa: true  |  Findings go to the attorney before drafting begins
   → Can run parallel with ticket 1

**Drafting — 3 tickets**
3. Draft Master SaaS Agreement — liability, IP ownership, termination
   → need_qa: true  |  Client-facing, high stakes
   → Depends on: ticket 1 (research) and ticket 2 (counterparty review)

4. Draft Data Processing Addendum — EU GDPR Art. 28 standard clauses
   → need_qa: true  |  Regulatory compliance — must be verified
   → Depends on: ticket 1 (research)

5. Write plain-English client summary — 1 page, key terms only
   → need_qa: true  |  Client-facing — no legal errors, no jargon
   → Depends on: ticket 3 and ticket 4 both approved

### Suggested order
Round 1 (parallel): tickets 1 and 2
Round 2 (parallel): tickets 3 and 4 — after research done, attorney reviews counterparty flagging
Round 3: ticket 5 — after MSA and DPA both approved

### Watch points flagged
- client-brief.md flags liability cap as a risk area — I'll add a watch point on
  the MSA ticket for QA to verify the cap is within the firm's approved range.
- Data residency mentioned in brief but not in clause-library.md — I'll flag this
  for the attorney before the drafting ticket opens.
- acme-retainer.md explicitly excludes employment contracts — I'll add this to the
  DON'T DO list on all tickets to prevent scope creep.

Confirm and I'll create all 5 tickets.
```

Human confirms.

---

## Step 4 — PM Creates and Opens the Tickets

PM creates each ticket grounded in the actual documents. Example — the DPA ticket:

```markdown
---
ticket_id: TCK-DRAFTING-2604-002
title: Draft Data Processing Addendum — EU GDPR Art. 28
team: drafting
need_qa: true
reopen_count: 0
---

## The Goal
Draft a Data Processing Addendum compliant with EU GDPR Article 28 for Acme SaaS.
See scope: [[scope.md]]
Client requirements: [[client-brief.md]]
Research findings: [[gdpr-processor-obligations.md]]
Approved clause library: [[clause-library.md]]
Style rules: [[style-guide.md]]
Retainer scope: [[acme-retainer.md]]

## DO
- Use the firm's standard Art. 28 processor clause from [[clause-library.md]]
- Include all required Art. 28 elements: subject matter, duration, nature of
  processing, type of personal data, categories of data subjects, controller obligations
- Include sub-processor provisions — 14-day advance notice requirement (per client-brief.md)
- Follow numbering and defined-terms format from [[style-guide.md]]
- Flag in the summary any clause where Acme's brief conflicts with the standard

## DON'T DO
- Do not invent obligations not found in [[gdpr-processor-obligations.md]] or
  [[clause-library.md]]
- Do not include scope beyond what [[acme-retainer.md]] covers — no employment,
  no marketing materials
- Do not use passive voice — firm style requires active construction

## Watch Points
QA: verify all required Art. 28 elements are present — check against the research artifact
QA: confirm sub-processor notice period is 14 days (client brief requirement)
QA: confirm no clause exceeds the retainer scope
```

---

## Step 5 — Research Agent Works First

Research agent claims `TCK-RESEARCH-2604-001`, reads the ticket and PROJECT_CORE, and produces:

```
Artifacts/gdpr-processor-obligations.md
TicketAttachments/TCK-RESEARCH-2604-001-summary.md
```

`gdpr-processor-obligations.md` (excerpt):
```markdown
## Required Art. 28 elements (current as of April 2026)
Source: EU GDPR Article 28(3); UK GDPR Article 28(3)

1. Subject matter and duration of processing
2. Nature and purpose of processing
3. Type of personal data and categories of data subjects
4. Obligations and rights of the controller

## Sub-processor obligations
- Controller must authorise sub-processors in writing (Art. 28(2))
- Processor must impose same data protection obligations on sub-processors
- No maximum notice period specified in regulation — contractual standard varies

## Data residency
- No Art. 28 requirement for data residency clause
- Standard transfers mechanism (SCCs) required if data leaves UK/EU — separate document
- NOTE: client-brief.md mentions data residency — this may require an addendum
  outside the DPA scope. Flag for attorney.

## Recent changes
- No material changes to Art. 28 since 2021. Sources current as of April 2026.
```

Research agent submits (`need_qa: false`) → ticket auto-moves to `Done`.

---

## Step 6 — Drafting Agent Works the DPA Ticket

Drafting agent claims `TCK-DRAFTING-2604-002`, reads the ticket, research artifact, clause library, style guide, and retainer scope.

It notices the research flagged data residency as potentially outside DPA scope and notes this in its summary.

Delivers:

```
Artifacts/acme-dpa-draft.md
TicketAttachments/TCK-DRAFTING-2604-002-summary.md
```

`TCK-DRAFTING-2604-002-summary.md`:
```markdown
## What was done
Drafted the Data Processing Addendum for Acme SaaS — EU GDPR Art. 28 compliant.

Used the firm's standard Art. 28 processor clause from clause-library.md as the
base. All six required Art. 28 elements included.

Sub-processor provisions: 14-day advance notice included per client-brief.md.
Research confirmed no regulatory minimum — 14 days is contractual, firm agreed.

## Flag for attorney
Data residency: research found this is not an Art. 28 requirement and requires
separate SCCs if data leaves UK/EU. Client brief mentions data residency.
This is outside the DPA scope as defined in acme-retainer.md. Noted in the draft
as a comment — attorney should confirm whether a separate addendum is needed.

## Style
Active voice throughout. Defined terms formatted per style-guide.md.
Numbering follows clause-library.md format.

Artifact: [[acme-dpa-draft.md]]
```

Agent submits:

```python
submit_work(
    "TCK-DRAFTING-2604-002",
    by_agent="drafting-agent",
    summary="## DPA draft delivered\nArt. 28 compliant. 14-day sub-processor notice included.\nData residency flagged as out of scope — attorney decision needed.\n\nFull notes: [[TCK-DRAFTING-2604-002-summary]]\nArtifact: [[acme-dpa-draft.md]]",
    note="Art. 28 complete, data residency flagged out of scope",
    tokens=3100
)
```

Ticket moves to `QAReview`.

---

## Step 7 — QA Agent Reviews the DPA Draft

QA agent picks up the ticket:

```python
ticket = get_next_ticket_for_review(team="drafting")
start_review(ticket["ticket_id"], by_agent="qa-agent")
```

QA reads the ticket, the summary, the draft, the research artifact, the clause library, the style guide, and the retainer.

```markdown
## QA Audit — TCK-DRAFTING-2604-002

### DO list
- [x] Standard Art. 28 processor clause used — matches clause-library.md §4.2 ✅
- [x] Subject matter: present — "processing of personal data for SaaS platform operation" ✅
- [x] Duration: present — "for the term of the Master SaaS Agreement" ✅
- [x] Nature and purpose: present ✅
- [x] Type of personal data: present — "name, email, usage data" ✅
- [x] Categories of data subjects: present — "Acme's end users and employees" ✅
- [x] Controller obligations: present ✅
- [x] Sub-processor provisions: present — 14-day advance notice confirmed ✅
- [x] Style: active voice throughout, defined terms formatted, numbering correct ✅

### DON'T DO list
- [x] No invented obligations — every clause traced to clause-library.md
      or gdpr-processor-obligations.md ✅
- [x] No scope outside retainer — data residency correctly flagged as out of
      scope, not included in the draft ✅
- [x] No passive voice constructions found ✅

### Watch Points
- [x] All Art. 28 elements verified against research artifact ✅
- [x] Sub-processor notice period: 14 days confirmed — matches client-brief.md ✅
- [x] Retainer scope: no violations. Data residency excluded correctly ✅

### Attorney flag noted
Data residency flagged in summary and as a comment in the draft.
This is correctly identified as outside DPA scope. Attorney decision required.
QA cannot resolve this — passing to Done, attorney must action the flag.

### Result: PASS
```

QA passes:

```python
review_pass(
    "TCK-DRAFTING-2604-002",
    by_agent="qa-agent",
    notes="## Audit passed\nAll Art. 28 elements present and verified.\n14-day sub-processor notice confirmed.\nNo scope violations. Data residency correctly excluded and flagged.\n\nFull report: [[TCK-DRAFTING-2604-002-qa-report]]",
    note="Art. 28 complete, all elements verified, data residency flag noted",
    tokens=800
)
```

Ticket moves to `Done`.

---

## What the Workflow Produces

By the time the DPA draft reaches an attorney, it has:

- Been drafted using the firm's approved clause library — not invented from training data
- Been constrained by the retainer scope — no obligations outside what the engagement covers
- Been reviewed by an agent that checked every required Art. 28 element against the research artifact
- Surfaced a scope question (data residency) that needs an attorney decision — with the flag documented in the ticket trail

The attorney opens a draft that meets the firm's standard. Their job is judgment on the flagged question — not finding the mistakes a system should have caught first.

That is what TCK gives a legal firm.
