---
id: architecture/00-overview
topic: architecture
slug: overview
title: "Architecture Overview"
type: doc
order: 0
status: ready
tags: [architecture, overview, architecture]
related: [architecture/01-software-architecture, architecture/02-system-design, architecture/03-clean-architecture, architecture/28-best-practices, architecture/100-common-antipatterns]
when_to_use: "Read first, before starting any design task, to find the right doc for the decision in front of you."
---
# Architecture Overview

## Purpose

This is the map for the `architecture` topic. It orients an agent to what lives here,
how the documents relate, and — most importantly — which one to open for the decision
in front of you. Architecture is the set of decisions that are expensive to change later:
module boundaries, data ownership, sync-vs-async, deployment shape. Getting these right
early is far cheaper than refactoring them under load.

Read this page to route yourself. Do not treat it as a concept doc — the depth lives in
the sibling documents it links to.

## Why It Matters

Most production incidents and failed rewrites trace back to an architectural decision that
was made implicitly, by accident, or by copying a pattern that did not fit. An agent that
writes code without an explicit architecture will produce a system that works in the demo
and collapses when a second team, a second data store, or 10x traffic arrives. The cost of
a bad boundary compounds: every feature built on top of it inherits the mistake. Choosing
the right structure up front — and knowing when *not* to add structure — is the highest-
leverage work in the lifecycle.

## Core Principles

- **Match structure to constraints, not fashion.** Microservices, CQRS, and event-driven
  designs solve specific problems at specific scales. Applied early, they add cost with no
  benefit. Start simple; add structure when a real constraint demands it.
- **Boundaries are the product.** The value of an architecture is where you draw the lines
  between parts and who owns what data. Get the boundaries right and the code inside them
  can be mediocre; get them wrong and no amount of clean code saves you.
- **Dependencies point inward, toward stability.** Volatile things (frameworks, databases,
  UIs) should depend on stable things (business rules), never the reverse. This is the
  thread running through clean, hexagonal, and layered architecture.
- **Every decision has a cost.** There is no free abstraction. Record *why* you chose a
  structure and what you traded away, so the next agent can revisit it with context.

## How These Docs Fit Together

- **Foundations** — start here to frame a problem:
  [software-architecture](01-software-architecture.md),
  [system-design](02-system-design.md),
  [engineering-principles](30-engineering-principles.md).
- **Structural patterns** — how to organize a codebase or service internals:
  [clean-architecture](03-clean-architecture.md),
  [hexagonal-architecture](04-hexagonal-architecture.md),
  [layered-architecture](05-layered-architecture.md),
  [domain-driven-design](06-domain-driven-design.md),
  [cqrs](07-cqrs.md).
- **System topology** — how to split and connect services:
  [event-driven-architecture](08-event-driven-architecture.md),
  [microservices](09-microservices.md),
  [modular-monolith](10-modular-monolith.md),
  [api-first](11-api-first.md),
  [integration-patterns](12-integration-patterns.md),
  [message-brokers](20-message-brokers.md),
  [distributed-systems](21-distributed-systems.md).
- **Quality attributes** — the "-ilities" a design must satisfy:
  [scalability](13-scalability.md), [performance](14-performance.md),
  [security](15-security.md), [high-availability](16-high-availability.md),
  [fault-tolerance](17-fault-tolerance.md), [observability](18-observability.md),
  [caching-strategies](19-caching-strategies.md).
- **Operate and deliver** — running the design in production:
  [cloud-architecture](22-cloud-architecture.md), [infrastructure](23-infrastructure.md),
  [deployment](24-deployment.md).
- **Practice and governance** — decide, document, review:
  [documentation](25-documentation.md),
  [architecture-decision-records](26-architecture-decision-records.md),
  [architecture-review](27-architecture-review.md),
  [best-practices](28-best-practices.md),
  [real-world-patterns](29-real-world-patterns.md).
- **Guardrails** — verify before you ship:
  [production-checklist](98-production-checklist.md),
  [ai-review-checklist](99-ai-review-checklist.md),
  [common-antipatterns](100-common-antipatterns.md).

## Best Practices

- Before writing code, name the architecture you are working in. If you cannot name it,
  you are about to invent one by accident — stop and pick one.
- Prefer a [modular monolith](10-modular-monolith.md) as the default. Reach for
  [microservices](09-microservices.md) only when team autonomy or independent scaling is a
  proven need, because the cost is a distributed system.
- Record consequential choices as [ADRs](26-architecture-decision-records.md). A decision
  no one can trace will be silently reversed.
- Design for the *current* constraints plus one realistic step of growth — not for
  hypothetical scale you may never reach.

## Common Mistakes

- Adopting a heavyweight pattern (microservices, event sourcing, CQRS) to a problem that a
  single service and a relational database would solve.
- Copying a big tech company's architecture without their scale, team size, or constraints.
- Treating architecture as a one-time upfront phase instead of a set of revisitable
  decisions with recorded rationale.
- Optimizing internal code cleanliness while leaving module and data boundaries a mess.

## AI Review Checklist

- Can you name the architecture style this code belongs to, and is it consistent with it?
- Is the chosen structure justified by a real constraint, or is it speculative complexity?
- Do dependencies point from volatile toward stable components?
- Are consequential decisions captured in an [ADR](26-architecture-decision-records.md)?
- Did you route to the most specific sibling doc for this decision, not just this overview?

## Related

- `knowledge/architecture/01-software-architecture.md`
- `knowledge/architecture/02-system-design.md`
- `knowledge/architecture/03-clean-architecture.md`
- `knowledge/architecture/28-best-practices.md`
- `knowledge/architecture/100-common-antipatterns.md`
