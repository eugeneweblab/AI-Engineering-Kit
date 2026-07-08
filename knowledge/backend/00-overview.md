---
id: backend/00-overview
topic: backend
slug: overview
title: "Overview"
type: doc
order: 0
status: ready
tags: [backend, overview]
related: [backend/01-backend-architecture, backend/02-layered-architecture, backend/03-clean-architecture, backend/04-hexagonal-architecture, backend/05-ddd]
when_to_use: "Read first when starting or reviewing any backend service, to find the right doc for the task at hand."
---
# Overview

## Purpose

This topic teaches an agent to design, build, and review server-side systems: how to
structure code, model a domain, expose an API, persist data, handle failure, and run
in production. It is the map for the `backend/` knowledge base — it tells you which
document answers which question, and in what order the ideas build.

Read this page to orient, then jump to the specific doc for your task. Do not treat
these docs as a linear book to read cover to cover; treat them as a reference you
consult when you hit the corresponding decision.

## Why It Matters

Backend code holds the data and enforces the rules. A frontend bug annoys one user; a
backend bug corrupts shared state, leaks other people's data, or takes the whole
service down. The cost of a wrong decision compounds: an architecture choice made in
week one shapes every feature for years, and unwinding it later is expensive. Getting
the structure right up front is cheaper than any refactor.

## Core Principles

- **Separate policy from mechanism.** Business rules (what the system decides) belong
  apart from delivery and infrastructure (HTTP, SQL, queues). This is the through-line
  of the architecture docs, from [layered](02-layered-architecture.md) to
  [clean](03-clean-architecture.md) to [hexagonal](04-hexagonal-architecture.md).
- **Depend on abstractions at boundaries.** Code you own should not depend on a
  specific database, broker, or framework. Hide each behind an interface you control.
- **Make the domain the center.** Models, invariants, and language come first; storage
  and transport are details that serve them. See [DDD](05-ddd.md).
- **Design for failure.** Networks drop, disks fill, dependencies time out. Correct
  backends assume this and stay consistent anyway.
- **Optimize for change, then for speed.** Most cost is in maintenance. Prefer the
  structure a future engineer can safely modify over a clever one they cannot.

## How These Docs Fit Together

- **[01 Backend Architecture](01-backend-architecture.md)** — the umbrella. How to
  choose a structure, what all good backends share, and how to reason about trade-offs.
  Start here when designing a new service.
- **[02 Layered Architecture](02-layered-architecture.md)** — the baseline pattern:
  controller → service → repository. The default for most CRUD-heavy services.
- **[03 Clean Architecture](03-clean-architecture.md)** — inverts dependencies so the
  domain depends on nothing. Use when business rules are complex and long-lived.
- **[04 Hexagonal Architecture](04-hexagonal-architecture.md)** — ports and adapters;
  the same dependency-inversion idea framed around swappable I/O. Use when the same
  logic must be driven by many transports or back by many providers.
- **[05 DDD](05-ddd.md)** — how to model the domain itself: entities, value objects,
  aggregates, bounded contexts. Orthogonal to the above; it fills the center.

Beyond these foundations, the topic continues into concrete concerns:
[API design](06-api-design.md), [business logic](07-business-logic.md),
[validation](09-validation.md), [error handling](12-error-handling.md),
[transactions](17-transactions.md), [observability](22-observability.md), and
[testing](23-testing.md), closing with the
[production checklist](98-production-checklist.md) and
[AI review checklist](99-ai-review-checklist.md).

## Best Practices

- Pick the *simplest* architecture that fits the problem. A layered monolith beats a
  misapplied hexagonal one; complexity you do not need is pure cost.
- Keep the domain free of framework and I/O imports. If your entity imports the ORM or
  the HTTP library, the boundary has already leaked.
- Make the same decision the same way everywhere. Consistency lets an agent (or a
  human) predict where code lives and how it behaves.
- Write down non-obvious architecture choices as short decision records; the reasoning
  is worth more later than the outcome.

## Common Mistakes

- Reaching for microservices or CQRS before the domain is understood — buying
  operational cost with no matching benefit.
- Letting HTTP or SQL concepts (request objects, ORM entities) reach into business
  logic, coupling rules to a framework you will one day replace.
- Treating "architecture" as folder names only, while dependencies still point every
  direction. The rule is the direction of dependencies, not the directory tree.
- Reading these docs top to bottom instead of consulting the one you need.

## AI Review Checklist

- Is the chosen architecture justified by the problem, not by fashion?
- Do dependencies point inward, toward the domain, at every boundary?
- Is business logic free of framework, HTTP, and database imports?
- Did the change land in the layer the pattern dictates?
- Is the simplest structure that works being used, not the most sophisticated?

## Related

- `knowledge/backend/01-backend-architecture.md`
- `knowledge/backend/02-layered-architecture.md`
- `knowledge/backend/03-clean-architecture.md`
- `knowledge/backend/04-hexagonal-architecture.md`
- `knowledge/backend/05-ddd.md`
