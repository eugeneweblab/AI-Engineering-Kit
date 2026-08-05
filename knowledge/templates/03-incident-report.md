---
id: templates/03-incident-report
topic: templates
slug: incident-report
title: "Incident Report Template"
type: template
order: 3
status: ready
tags: [templates, incident-report, "@ana", "@dev", CheckoutErrorRateHigh, TypeScript]
related: [templates/02-architecture-decision-record, playbooks/01-site-down, security/26-incident-response, workflows/06-investigate-production-bug, tools/29-observability-tools]
when_to_use: "Copy after a user-visible failure, once service is restored and the timeline is still accurate."
---
# Incident Report Template

## Purpose

An incident report turns an outage into something the team can learn from. Its audience is
the engineer who hits a similar failure in a year — not management, and not the people who
were already in the room.

Write it within a few days, while the timeline is still reconstructable from logs and
memory. Store under `docs/incidents/`, numbered and dated.

---

## The Principle: Blameless

The report names systems, not people. Not because blame is impolite, but because it is
inaccurate: if one person's mistake could take production down, the system permitted it —
and that is the finding worth recording.

Write "the deploy skipped the migration check" rather than "Sam forgot to run migrations".
The first has a fix; the second has an apology.

---

## The Template

```markdown
# INC-2026-07-14: Checkout unavailable for 34 minutes

- **Severity:** SEV2
- **Detected:** 2026-07-14 14:12 UTC (alert: checkout success rate)
- **Resolved:** 2026-07-14 14:46 UTC
- **Duration:** 34 minutes
- **Author:** @dev

## Impact

Who was affected, how many, and what they experienced. Quantify where you can, and say so
where you cannot.

## Timeline

All times UTC. Include detection, each significant action, and what was believed at the
time — including the wrong hypotheses. Those are the most useful lines in the document.

| Time | Event |
|---|---|
| 14:05 | <the change or trigger, often before anyone noticed> |
| 14:12 | <detection: alert, or a customer report> |
| 14:19 | <first hypothesis, and what ruled it out> |
| 14:41 | <what actually fixed it> |
| 14:46 | <confirmed recovered> |

## Root cause

The chain, not the last link. Keep asking "and why was that possible?" until the answer is
a system property rather than an action.

## Detection

How it was found, and how long that took. If a customer reported it before monitoring did,
that is a finding in its own right.

## Resolution

What restored service, and whether it was a fix or a mitigation.

## What went well

Genuinely — the parts of the response worth keeping. This is not padding; it identifies
which controls earned their cost.

## What did not

Where the response was slower or harder than it should have been.

## Action items

| Action | Type | Owner | Issue |
|---|---|---|---|
| <specific, testable change> | Prevent / Detect / Mitigate | @who | #123 |
```

---

## Writing the Root Cause

The first answer is almost never the root cause. Keep going:

> The checkout page returned 500.
> — *Why?* The pricing service timed out.
> — *Why?* It was waiting on a database query that normally takes 8ms.
> — *Why?* The query lost its index during a migration that rebuilt the table.
> — *Why?* The migration recreated the table without the index, and nothing verified index
>   parity afterwards.
> — *Why?* Migrations are reviewed for correctness of data, not for schema-object parity.

The last line is the actionable one. Stopping at "the query was slow" produces an action
item to add a timeout — useful, but it leaves the same class of failure available.

---

## Action Items That Work

Every action item should be a specific, verifiable change with an owner and a ticket. Sort
them by category, because the categories have different value:

- **Prevent** — makes this class of failure impossible. Most valuable, usually hardest.
- **Detect** — finds it faster next time. Almost always worth doing.
- **Mitigate** — reduces the blast radius when it recurs.

"Be more careful with migrations" is not an action item. "Add a post-migration check that
compares index definitions against the schema snapshot, failing the deploy on mismatch" is.

An incident with no action items is either a genuinely unpreventable external failure — say
so explicitly — or a report that stopped asking why too early.

---

## Common Mistakes

- **Naming individuals.** It suppresses the reporting that makes the process work.
- **A timeline written from the fix backwards**, hiding the wrong turns. The dead ends are
  where the detection gaps show.
- **Root cause = the last thing that broke.** Keep going up the chain.
- **Vague action items** with no owner, no ticket, and no way to tell if they happened.
- **Writing it weeks later**, when the timeline is a reconstruction.
- **Skipping the report because the fix was trivial.** A one-line fix for a 40-minute outage
  is a detection problem worth its own finding.

---

## Examples

**Good Example** — a timeline, a cause, and actions with owners

```markdown
# Incident 2026-08-04: checkout 500s for legacy plans

**Impact** 2% of checkout requests failed for 72 minutes. 431 customers
affected; 0 orders lost (all retried successfully after the fix).
**Detected by** Error-rate alert, 14:12 — 2 minutes after onset.

## Timeline (UTC)
14:10  Deploy 8f2c1a9 reaches production.
14:12  CheckoutErrorRateHigh fires.
14:15  First status update posted.
14:22  Rolled back to 7c1a9f2. Error rate returns to baseline.
14:50  Cause identified: `plan.discountPercent` made required; legacy rows null.
15:24  Fix deployed with a regression test. Incident closed.

## Cause
8f2c1a9 changed `discountPercent` from optional to required in the pricing code.
Rows created before 2024 have it null. No test covered a legacy plan, and the
staging database had been reseeded without legacy rows in March.

## Why it was not caught earlier
Staging data no longer represents production. The type change was correct in
TypeScript terms; the database was the source of the null.

## Actions
- [ ] Seed staging with a representative legacy row — @ana — 2026-08-11
- [ ] Add a nullability check to the migration review checklist — @ben — 2026-08-08
- [x] Regression test for null discountPercent — @ana — done in 9f3c2d1
```

**Bad Example** — a summary with no timeline and no follow-through

```markdown
# Incident report

The site was down for a while this afternoon due to a bad deploy. We rolled it
back and everything is working now. We should be more careful with deploys.

Action items: be more careful.
```

No times, so nobody can tell whether detection or response was the slow part. No cause, so the
same class of failure is not prevented. "Be more careful" has no owner and no date, which means
it will not happen.

---

## Related

- `knowledge/templates/02-architecture-decision-record.md`
- `knowledge/playbooks/01-site-down.md`
- `knowledge/security/26-incident-response.md`
- `knowledge/workflows/06-investigate-production-bug.md`
- `knowledge/tools/29-observability-tools.md`
