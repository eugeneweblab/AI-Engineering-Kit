---
id: architecture/27-architecture-review
topic: architecture
slug: architecture-review
title: "Architecture Review"
type: doc
order: 27
status: ready
tags: [architecture, architecture-review]
related: [architecture/26-architecture-decision-records, architecture/28-best-practices, architecture/99-ai-review-checklist, architecture/25-documentation, architecture/100-common-antipatterns]
when_to_use: "Read before running or participating in a review of a proposed design, a significant change, or an existing system's architecture."
---
# Architecture Review

## Purpose

This document defines how to review an architecture: a proposed design, a significant
change, or an existing system. It covers what to examine, in what order, and how to give
feedback that improves the design instead of just blocking it. It is written so an agent
can conduct or participate in a review that catches expensive mistakes *before* they are
built.

A code review checks whether the code is correct. An architecture review checks whether
the *shape* is right — the boundaries, the coupling, the failure modes, the ability to
change later. It catches the mistakes that code review cannot, because by the time there
is code, the expensive decision is already made.

## Why It Matters

The cost of fixing a design flaw grows by orders of magnitude the later it is caught. A
wrong service boundary noticed in a review is a whiteboard edit; the same boundary noticed
after six months of code is a multi-quarter migration. Architecture review is the cheapest
possible place to catch these — before the commitment. It is also where institutional
knowledge transfers: the constraints, the past failures, the "we tried that" that a
newcomer or an agent cannot know. A review that only rubber-stamps, or that only blocks
without teaching, wastes that leverage.

## Core Principles

- **Review the design before the code, not after.** The point of a review is to change the
  decision while it is still cheap. A review of already-built architecture is damage
  assessment, not prevention.
- **Evaluate against explicit requirements and constraints.** "Good" is meaningless in the
  abstract. Judge the design against its actual load, latency, consistency, and change
  requirements — nothing more, nothing less.
- **Attack the failure modes.** The most valuable review question is "what happens when
  this dependency is down / slow / returns garbage?" Happy paths rarely need a review.
- **Feedback proposes, it does not just reject.** Every objection should come with the
  trade-off it is protecting and, where possible, an alternative. A block without a reason
  is noise.
- **Judge for changeability, not perfection.** The winning design is rarely the most
  elegant; it is the one that is cheapest to be wrong about and easiest to evolve.

## Best Practices

- Require a short written proposal *before* the review: the problem, the constraints, the
  proposed design (with a diagram), and the alternatives considered — ideally the draft of
  an [ADR](26-architecture-decision-records.md). No proposal, no review.
- Review in a fixed order so nothing is skipped: **requirements → boundaries & coupling →
  data ownership & consistency → failure modes → operability → security → cost of change.**
- Push back on scope creep in the design itself — a review should catch a system solving
  problems it does not yet have (speculative generality) as readily as one that ignores
  real requirements.
- Timebox and right-size: a reversible, low-blast-radius decision needs a lightweight
  review; an irreversible, system-wide one needs a thorough one. Match rigor to stakes.
- Separate blocking concerns ("this will lose data") from preferences ("I'd name it
  differently") explicitly, so the author knows what must change versus what is optional.
- Capture the outcome as an ADR, including decisions the review *changed* — the reasoning
  is the durable artifact, not the meeting.
- Include someone who will *operate* the system, not only those who will build it.

## Examples

**Good Example** — a review comment that catches a failure mode and proposes a fix

```text
Boundary/consistency concern (blocking):
The checkout service writes to the Orders DB *and* calls the Payments API in the
same request, treating both as one transaction. But they are two systems — if the
process dies after the DB write and before payment, we have an unpaid order and no
way to reconcile.

Why it matters: this is a dual-write with no atomicity; it will silently corrupt
state under normal failure, not just rare ones.

Proposed alternative: persist the order as PENDING, then drive payment via an
outbox/event so the retry is durable. Trade-off: eventual consistency on order
status, which the UI already tolerates. See pattern in 12-integration-patterns.
```

**Bad Example** — a review that blocks without reasoning or teaches nothing

```text
LGTM I guess.                         <!-- rubber stamp: adds no signal -->
-- or --
No. Don't use Kafka here.             <!-- blocks with no reason, no alternative,
                                           no requirement it's protecting. The author
                                           learns nothing and will argue, not improve. -->
Why not just make it a monolith?      <!-- reopens settled scope with no constraint -->
```

## Common Mistakes

- Reviewing the architecture only after it is built, when feedback can no longer change the
  expensive decision cheaply.
- Judging the design against taste or trends instead of its actual requirements and
  constraints.
- Focusing on happy-path correctness and never asking what happens when a dependency fails.
- Blocking without a stated reason or alternative, turning the review into a standoff.
- Applying the same heavy process to a trivial reversible change as to an irreversible one.
- Letting the outcome live only in a meeting — no ADR, so the reasoning evaporates.
- Reviewing with only builders in the room and no one who will run the thing at 3 a.m.

## Production Tips

- Keep a reusable checklist (see [AI review checklist](99-ai-review-checklist.md)) so every
  review covers boundaries, data ownership, and failure modes consistently.
- For recurring designs, review against the team's documented
  [best practices](28-best-practices.md) and known
  [anti-patterns](100-common-antipatterns.md) rather than re-deriving them each time.
- Re-review long-lived systems periodically; constraints change and yesterday's right
  decision can become today's bottleneck.

## AI Review Checklist

- Was a written proposal with alternatives available *before* the review started?
- Is the design judged against explicit requirements and constraints, not taste?
- Are service boundaries and data ownership clear, with no dual-writes or hidden coupling?
- Has each external dependency's failure mode (down, slow, wrong) been examined?
- Is the design operable and observable, and is it cheap to change if it is wrong?
- Does every blocking objection state the trade-off it protects and an alternative?
- Was the outcome, including changed decisions, captured as an ADR?

## Related

- `knowledge/architecture/26-architecture-decision-records.md`
- `knowledge/architecture/28-best-practices.md`
- `knowledge/architecture/99-ai-review-checklist.md`
- `knowledge/architecture/100-common-antipatterns.md`
- `knowledge/architecture/25-documentation.md`
