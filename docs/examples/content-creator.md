# TCK Example — Content Creator

> A full walkthrough: sponsor brief arrives, PM breaks down the scope, research and script teams work, QA reviews.

---

## The Setup

A creator runs a tech review channel — 180,000 subscribers, two sponsors per month, one long-form video and three Shorts per week. They use AI agents for research, scripting, and short-form writing. Before TCK, every video was a fresh prompt with no memory of the channel's voice, the audience's expectations, or the sponsor's restrictions.

**Teams:**

```
research/   ← finds product details, competitor coverage, audience questions
script/     ← writes video scripts, hooks, sponsor segments
short/      ← writes Short captions and hooks from the main script
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

You find facts, real use cases, known limitations, and honest audience opinions
about the product being reviewed. Your output feeds the script agent — accuracy
and specificity matter more than volume. You do not write scripts or captions.

Always pass `team="research"` to all MCP tools.

---

## Research Standards

When building (InProgress):
- Read the full ticket before researching — understand what the script team needs
- Read PROJECT_CORE to understand the audience (what they care about, what they hate)
- Prioritise: real user experiences over marketing claims, specific benchmarks over general praise
- Flag claims you could not verify — do not include them as facts
- Deliver findings to `Artifacts/` as a structured markdown file
- Write a summary in `TicketAttachments/{ticket_id}-summary.md` before submitting

---

## Boundaries

- Always use `team="research"`. Never pass another team name.
- Do not write scripts, captions, or any video content — research only.
- Do not edit ticket files directly — all status changes go through MCP tools.
```

---

### script/CLAUDE.md

```markdown
# Script Agent — CLAUDE.md

You are the **Script Agent** for this project. Your workspace is the `script/` folder.

@../TICKET_AGENTS_RULES.md

---

## Your Role

You write video scripts — hooks, body, sponsor segments, and CTAs. Every script
is grounded in the research ticket output, the channel's brand voice, and the
sponsor's approved claims. You do not publish. You do not approve your own work.

Always pass `team="script"` to all MCP tools.

---

## Script Standards

When building (InProgress):
- Read the full ticket: goal, DO, DON'T DO, Watch Points
- Read the research artifact from `Artifacts/` — the script must be grounded in it
- Read `Documents/Areas/Brand/brand-voice.md` — tone, banned phrases, style rules
- Read `Documents/Areas/Channel Standards/format.md` — hook timing, sponsor window, end card
- Read the sponsor brief linked in the ticket — every sponsor claim must come from it
- Write the script to `Artifacts/` as a markdown file
- Write a summary in `TicketAttachments/{ticket_id}-summary.md` — note any decisions
  made about the sponsor segment or any claims you couldn't fit naturally

When reviewing your own work before submitting:
- Is the hook in the first 8 seconds?
- Is the sponsor segment within the 3:30–4:00 window?
- Does every sponsor claim appear in the brief?
- Are there any banned phrases from brand-voice.md?
- Does it end with an audience question?

---

## Boundaries

- Always use `team="script"`. Never pass another team name.
- Do not approve your own work — QA reviews every script.
- Do not make sponsor claims not found in the brief.
- Do not edit ticket files directly — all status changes go through MCP tools.
```

---

### short/CLAUDE.md

```markdown
# Short Agent — CLAUDE.md

You are the **Short Agent** for this project. Your workspace is the `short/` folder.

@../TICKET_AGENTS_RULES.md

---

## Your Role

You write YouTube Shorts hooks and captions adapted from the main video script.
Each Short takes one angle from the long-form script and distils it into a
standalone 60-second concept. You do not rewrite the full script — you extract
and sharpen.

Always pass `team="short"` to all MCP tools.

---

## Short Standards

When building (InProgress):
- Read the ticket — it tells you which angle to cover and links to the main script
- Read `Documents/Areas/Brand/brand-voice.md` — Shorts use the same voice rules
- Each Short must work without watching the main video — no "as I mentioned"
- Hook must land in the first 3 seconds — strong opinion or surprising fact
- End with a single CTA — subscribe, comment, or link in bio (ticket specifies which)
- Deliver to `Artifacts/` as a markdown file named `short-{n}-{topic}.md`

---

## Boundaries

- Always use `team="short"`. Never pass another team name.
- Do not include sponsor content in Shorts unless the ticket explicitly says so.
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

You review completed scripts and Shorts independently. You did not write what
you are reviewing and you have no stake in approving it. Your job is to verify
the output meets every requirement in the ticket — and to reopen it with specific,
documented issues if it does not.

Always pass `team="script"` to all MCP tools when reviewing script tickets.
Use `team="short"` when reviewing Short tickets.

---

## QA Standards

When reviewing (QAReview):
- Read the full ticket: DO list, DON'T DO list, Watch Points
- Read the builder's summary in `TicketAttachments/{ticket_id}-summary.md`
- Read the actual artifact in `Artifacts/` — not just the summary
- For script tickets: read the sponsor brief linked in the ticket
- For script tickets: check `Documents/Areas/Brand/brand-voice.md` ban list
- For script tickets: check `Documents/Areas/Channel Standards/format.md`

For every review, verify:
- **DO list** — every requirement satisfied? Check each item explicitly.
- **DON'T DO list** — any violations? Check each item explicitly.
- **Watch Points** — the PM flagged these for a reason. Extra attention required.
- **Sponsor claims** — every claim in the script must exist word-for-word in the brief.
- **Banned phrases** — check the full ban list, not just memory.

Write your audit in `TicketAttachments/{ticket_id}-qa-report.md` before calling
`review_pass` or `review_reopen`. Never pass without a written report.

When reopening:
- Quote the exact line in the script that has the issue
- Reference the exact brief, DO item, or ban list entry that it violates

---

## Boundaries

- Do not write scripts, captions, or any content — review only.
- Do not approve a script with an unverified sponsor claim.
- Do not edit ticket files directly — all status changes go through MCP tools.
```

---

## Step 1 — Sponsor Brief Arrives in Inbox

The sponsor sends a brief over email. The creator drops it in `Documents/Inbox/`.

```
Documents/Inbox/
└── notion-sponsor-brief-april.pdf
```

The PM agent reads it and responds:

```
File: notion-sponsor-brief-april.pdf
→ Suggest: Documents/Projects/2604 Notion AI Review/
→ Reason: April sponsor brief — needs a project folder for this video
→ Action needed: Create scope.md, then I can break it down

Key items found in the brief:
- Approved claims: 3 feature talking points, 1 pricing line
- Restrictions: do not compare directly to competitors by name
- Deliverables requested by sponsor: 1 long-form integration + 3 Shorts mentions

Shall I create the project folder and scope.md now?
```

Human confirms. PM creates:

```
Documents/Projects/2604 Notion AI Review/
├── scope.md                          ← written from the brief
└── notion-sponsor-brief-april.pdf    ← moved from Inbox
```

---

## Step 2 — PM Reads Everything Before Writing a Single Ticket

Before proposing any tickets, the PM reads:

1. `Documents/PROJECT_CORE/project-description.md` — tech reviews for working professionals 28–40; honest, no hype, always compare alternatives
2. `Documents/PROJECT_CORE/customer-persona.md` — primary audience is Sam, 34, software engineer; wants to know if something is worth buying; hates vague benchmarks and sponsored spin
3. `Documents/Projects/2604 Notion AI Review/scope.md` — deliverables, sponsor requirements, video length
4. `Documents/Areas/Brand/brand-voice.md` — direct, specific, no stock phrases, always cite the source of a claim
5. `Documents/Areas/Channel Standards/format.md` — hook in first 8 seconds, sponsor slot at 3:30–4:00, end card asks one question

---

## Step 3 — PM Proposes the Ticket Breakdown

```
## Scope Breakdown — 2604 Notion AI Review

### Teams needed
✅ research  — already exists
✅ script    — already exists
✅ short     — already exists
✅ qa        — already exists

### Proposed tickets (5 total)

**Research — 1 ticket**
1. Research Notion AI — real use cases, known limitations, audience questions
   → need_qa: false  |  Internal — feeds the script, low risk

**Script — 1 ticket**
2. Write 12-min script — hook, honest review, sponsor segment at 3:30
   → need_qa: true  |  Sponsor claims must be verified before the creator sees it
   → Depends on: ticket 1 (research must be done first)

**Short — 3 tickets**
3. Short #1 — "Is Notion AI worth it?" — strong opinion hook
   → need_qa: true  |  Depends on: ticket 2 (script must be approved first)

4. Short #2 — Top 3 use cases from the review, 60 seconds
   → need_qa: true  |  Depends on: ticket 2

5. Short #3 — One thing Notion AI still can't do
   → need_qa: true  |  Depends on: ticket 2

### Suggested order
Round 1: ticket 1 (research)
Round 2: ticket 2 (script) — after research done
Round 3: tickets 3, 4, 5 in parallel — after script approved

### Watch points flagged
- Sponsor brief says "do not compare to competitors by name" — I'll add this to
  the script DON'T DO list and flag it as a QA watch point.
- Brand voice bans "game changer", "next level", "revolutionise" — adding to
  script and Short tickets explicitly.
- research/CLAUDE.md instructs the agent to flag unverified claims — QA should
  check the research artifact for any flagged items before reviewing the script.

Confirm and I'll create all 5 tickets.
```

Human confirms.

---

## Step 4 — PM Creates and Opens the Tickets

PM creates each ticket grounded in the actual documents. Example — the script ticket:

```markdown
---
ticket_id: TCK-SCRIPT-2604-001
title: Write 12-min script — Notion AI Review
team: script
need_qa: true
reopen_count: 0
---

## The Goal
Write the main video script for the Notion AI review.
See scope: [[scope.md]]
Research findings: [[notion-ai-research.md]]
Brand voice: [[brand-voice.md]]
Format rules: [[format.md]]
Sponsor brief: [[notion-sponsor-brief-april.pdf]]

## DO
- Hook in the first 8 seconds — use the strongest finding from the research
- Sponsor segment at 3:30–4:00 — natural transition, approved claims only
- Cover at least one real limitation — the audience trusts honest reviews
- Cite the source of any performance or feature claim
- End with one question to the audience (comment prompt)

## DON'T DO
- Do not use "game changer", "next level", "revolutionise", or any phrase
  on the ban list in [[brand-voice.md]]
- Do not name competitors directly — sponsor brief prohibits this
- Do not make any Notion claim not found in [[notion-sponsor-brief-april.pdf]]
- Do not exceed 1,900 words

## Watch Points
QA: verify every sponsor claim appears in the brief verbatim
QA: check full ban list in brand-voice.md — not just the obvious phrases
QA: confirm no competitor names appear in the script
```

---

## Step 5 — Research Agent Works First

Research agent claims `TCK-RESEARCH-2604-001`, reads the ticket and PROJECT_CORE, and produces:

```
Artifacts/notion-ai-research.md
TicketAttachments/TCK-RESEARCH-2604-001-summary.md
```

`notion-ai-research.md` (excerpt):
```markdown
## Verified use cases
- Meeting notes → action items: confirmed in Notion AI docs, 3 user reviews on Reddit
- Database summarisation: confirmed, works on tables up to ~500 rows (tested by Linus Tech Tips, April 2026)

## Known limitations
- Cannot reference content across multiple pages in one query (confirmed missing feature as of April 2026)
- Slow on large databases — noticeable lag above 1,000 rows (user reports on Notion subreddit)

## Unverified claims (do not use)
- "Saves 2 hours per week" — sponsor talking point, no independent source found
```

Research agent submits (`need_qa: false`) → ticket auto-moves to `Done`.

---

## Step 6 — Script Agent Works the Ticket

Script agent claims `TCK-SCRIPT-2604-001`, reads the ticket, research artifact, brand voice, format rules, and sponsor brief. It notices the research flagged "saves 2 hours per week" as unverified and does not use it in the sponsor segment.

Delivers:

```
Artifacts/notion-ai-review-script.md
TicketAttachments/TCK-SCRIPT-2604-001-summary.md
```

`TCK-SCRIPT-2604-001-summary.md`:
```markdown
## What was done
Wrote 1,740-word script for the Notion AI review.

Hook: "I've been using Notion AI for 30 days on real client work. Here's what
it's actually good at — and the one thing it still can't do."

Sponsor segment at 3:32 — natural transition from the use cases section.
Used three approved claims from the brief. Omitted "saves 2 hours per week"
— research flagged it as unverified and the brief allows omission.

Limitations section at 9:00 — cross-page query limitation and large database lag,
both sourced from research artifact.

End card: "What do you use for meeting notes — drop it in the comments."

Artifact: [[notion-ai-review-script.md]]
```

Agent submits:

```python
submit_work(
    "TCK-SCRIPT-2604-001",
    by_agent="script-agent",
    summary="## Script delivered\n1,740 words. Sponsor at 3:32, 3 approved claims used.\nOmitted unverified time-saving claim.\n\nFull notes: [[TCK-SCRIPT-2604-001-summary]]\nArtifact: [[notion-ai-review-script.md]]",
    note="1,740 words, sponsor at 3:32, unverified claim omitted",
    tokens=2800
)
```

Ticket moves to `QAReview`.

---

## Step 7 — QA Agent Reviews the Script

QA agent picks up the ticket:

```python
ticket = get_next_ticket_for_review(team="script")
start_review(ticket["ticket_id"], by_agent="qa-agent")
```

QA reads the ticket, the summary, the script, the sponsor brief, and the brand voice ban list.

```markdown
## QA Audit — TCK-SCRIPT-2604-001

### DO list
- [x] Hook in first 8 seconds — "I've been using Notion AI for 30 days..." lands at 0:00 ✅
- [x] Sponsor segment at 3:30–4:00 — starts at 3:32, ends at 3:58 ✅
- [x] Real limitation covered — cross-page query and database lag, both sourced ✅
- [x] Claims cited — database summarisation sourced to Linus Tech Tips April 2026 ✅
- [x] End card question — "What do you use for meeting notes?" ✅

### DON'T DO list
- [x] Ban list phrases checked — none found ✅
- [x] No competitor names — Notion is the only product named ✅
- [x] Sponsor claims verified against brief:
      Claim 1: "AI-powered meeting summaries" — in brief ✅
      Claim 2: "Works inside your existing Notion workspace" — in brief ✅
      Claim 3: "Available on all plans" — in brief ✅
- [x] Word count: 1,740 — under 1,900 limit ✅

### Watch Points
- [x] All sponsor claims verified verbatim against brief ✅
- [x] Full ban list checked (22 phrases) — none present ✅
- [x] No competitor names in script or sponsor segment ✅

### Result: PASS
```

QA passes:

```python
review_pass(
    "TCK-SCRIPT-2604-001",
    by_agent="qa-agent",
    notes="## Audit passed\nAll DO items satisfied. All 3 sponsor claims verified against brief.\nBan list clean. No competitor names. Word count within limit.\n\nFull report: [[TCK-SCRIPT-2604-001-qa-report]]",
    note="All checks passed — sponsor claims verified, ban list clean",
    tokens=700
)
```

Ticket moves to `Done`. Short tickets are now unblocked.

---

## What the Workflow Produces

By the time the script reaches the creator, it has:

- Been written from research the agent produced — not from the agent's training data assumptions
- Been constrained by the sponsor brief, the brand voice, and the channel format — all read from Documents, not re-explained in a prompt
- Been reviewed by an agent that checked every sponsor claim against the actual brief document

The creator reads a script that is on-brand, on-format, and legally safe. Their job is creative judgment — not catching the mistakes a system should have prevented.

That is what TCK gives a content creator.
