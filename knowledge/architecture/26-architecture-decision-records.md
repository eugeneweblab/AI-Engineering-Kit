---
id: architecture/26-architecture-decision-records
topic: architecture
slug: architecture-decision-records
title: "Architecture Decision Records"
type: doc
order: 26
status: ready
tags: [architecture, architecture-decision-records, Accepted, OrderPlaced]
related: [architecture/25-documentation, architecture/27-architecture-review, architecture/28-best-practices, architecture/00-overview, architecture/30-engineering-principles]
when_to_use: "Read before making or reviewing a significant, hard-to-reverse architectural decision that future engineers will need the reasoning for."
---
# Architecture Decision Records

## Purpose

This document defines what an Architecture Decision Record (ADR) is, when to write one,
and how to structure it so the *reasoning* behind a decision survives longer than the
people who made it. An ADR is a short, immutable document capturing one significant
choice: the context, the decision, and the consequences. It is written so an agent can
produce an ADR that a future reader can trust, and can recognize when a change warrants
one.

ADRs are the history layer of [documentation](25-documentation.md): prose docs describe
the system as it is *now*; ADRs preserve *why* it became that way.

## Why It Matters

Architectural decisions are the expensive, hard-to-reverse ones — a database choice, a
service boundary, a sync-vs-async call. Six months later, someone finds that choice
"obviously wrong," reverses it, and rediscovers the constraint that made it necessary — at
the cost of a production incident. Without a record, every decision looks arbitrary and
gets relitigated. An ADR makes the constraints and trade-offs explicit and permanent, so a
future engineer can tell the difference between "this was a mistake" and "this was the best
option given constraints that may no longer hold." The record is cheap to write and
enormously expensive to lack.

## Core Principles

- **One decision per record.** An ADR captures a single choice with its own context and
  consequences. Bundling decisions makes each impossible to reference or supersede.
- **Records are immutable.** Once accepted, an ADR is never edited to reflect a new
  decision. To change course, write a new ADR that *supersedes* the old one and link them.
  The history is the point.
- **Capture the context, not just the conclusion.** The valuable part is the forces —
  constraints, alternatives, trade-offs — that made this choice reasonable *at the time*.
- **Write it when the decision is made, not after.** Reconstructed reasoning is
  rationalization. Capture the alternatives while they are still live.
- **Only significant, costly-to-reverse decisions need an ADR.** Routine choices do not.
  Over-documenting trivial decisions buries the important ones.

## Best Practices

- Use a lightweight, consistent template: **Title, Status, Context, Decision,
  Consequences.** Add *Alternatives Considered* — it is where most of the value lives.
- Number ADRs sequentially and immutably (`0012-use-event-bus-for-fulfilment.md`) and keep
  them in `docs/adr/` in the repo, reviewed in the PR that implements the decision.
- Use an explicit status lifecycle: `Proposed → Accepted → Deprecated / Superseded by NNNN`.
  A reader must be able to tell instantly whether an ADR is still in force.
- State consequences honestly, including the *negative* ones. An ADR that lists only
  benefits is marketing, not a record.
- Keep it short — one page. If it needs more, the decision is probably several decisions.
- Link ADRs to each other (supersedes / superseded-by) and from the relevant README so the
  history is navigable.
- Write in past-decision, plain language a newcomer can follow without tribal knowledge.

## Examples

**Good Example** — one decision, context, honest consequences, alternatives

```markdown
# 0012. Use an event bus for order fulfilment

Status: Accepted (2026-03-14)

## Context
The Order API must trigger fulfilment. Fulfilment is slow and occasionally down.
A synchronous call couples order acceptance to fulfilment availability, so an outage
would block customers from placing orders.

## Decision
The Order API publishes an `OrderPlaced` event to the bus. Fulfilment consumes it
asynchronously. The two services deploy and scale independently.

## Consequences
+ Orders succeed even when fulfilment is down; load is buffered by the bus.
- Fulfilment is now eventually consistent; the UI must not promise instant dispatch.
- We take on a message bus as new infrastructure to operate and monitor.

## Alternatives considered
- Synchronous HTTP call: simpler, but couples availability. Rejected.
- Shared database polling: no new infra, but tight coupling on schema. Rejected.
```

**Bad Example** — conclusion only, edited in place, no reasoning

```markdown
# Fulfilment

We use Kafka now.        <!-- no context: why? what was rejected? -->
                         <!-- Was edited over the old "we use HTTP" text, so the
                              history of WHY it changed is gone forever. -->
                         <!-- No status, no date, no consequences. Unciteable. -->
```

## Common Mistakes

- Editing an accepted ADR to reflect a new decision instead of writing a superseding one —
  this destroys the history the ADR exists to preserve.
- Recording only the decision, omitting the context and rejected alternatives — the reader
  cannot judge whether the reasoning still holds.
- Listing only upsides; hiding the negative consequences makes the record untrustworthy.
- Writing ADRs for trivial choices, drowning the decisions that actually matter.
- Storing ADRs in a wiki disconnected from the code and the PR that implemented them.
- Reconstructing an ADR months later, so it documents a rationalization, not the reasoning.

## Production Tips

- Add an `docs/adr/0000-record-architecture-decisions.md` as ADR-0 explaining the process
  itself, so the practice is self-documenting.
- Reference the ADR number in the PR and the code comment at the boundary it governs, so a
  reader lands on the reasoning from the code.
- Revisit `Accepted` ADRs during [architecture reviews](27-architecture-review.md); mark
  ones whose constraints no longer hold as candidates to supersede.

## AI Review Checklist

- Does the ADR capture exactly one significant, hard-to-reverse decision?
- Are Context, Decision, and Consequences all present, with alternatives considered?
- Are the negative consequences stated honestly, not just the benefits?
- Is the status explicit (Proposed/Accepted/Superseded), with links to related ADRs?
- Is the ADR immutable — is a change of course a new superseding record, not an edit?
- Does it live in the repo and get reviewed with the change it justifies?

## Related

- `knowledge/architecture/25-documentation.md`
- `knowledge/architecture/27-architecture-review.md`
- `knowledge/architecture/28-best-practices.md`
- `knowledge/architecture/30-engineering-principles.md`
- `knowledge/architecture/00-overview.md`
