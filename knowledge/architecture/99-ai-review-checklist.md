---
id: architecture/99-ai-review-checklist
topic: architecture
slug: ai-review-checklist
title: "Architecture AI Review Checklist"
type: doc
order: 99
status: ready
tags: [architecture, ai-review-checklist]
related: [architecture/27-architecture-review, architecture/28-best-practices, architecture/30-engineering-principles, architecture/100-common-antipatterns, architecture/98-production-checklist]
when_to_use: "Read before reviewing or generating any change that adds, moves, or removes an architectural boundary."
---
# Architecture AI Review Checklist

## Purpose

This is the checklist an AI agent runs when reviewing (or self-reviewing) an architectural
change: a new module, service, dependency, boundary, or pattern. Every item is a
verifiable yes/no about the *design*. It is the design counterpart to the
[production checklist](98-production-checklist.md), which covers operational readiness. Use
this during code review and before opening a pull request that touches structure.

## Why It Matters

Architectural mistakes are the expensive kind: they are hard to reverse, they spread
before anyone notices, and tests do not catch them because the code "works". A wrong
boundary or a leaked dependency passes CI green and only reveals its cost months later as
friction on every change. A concrete review checklist catches these at the one moment they
are cheap to fix — before merge — and gives the agent a reason to reject, not just a vibe.

## Boundaries & Coupling

**Rules:** [Clean Architecture](03-clean-architecture.md) · [Modular Monolith](10-modular-monolith.md)

- [ ] Does every new module/service boundary follow a **change or ownership** axis, not a
  technical layer, so things that change together live together?
- [ ] Do dependencies point **inward** (toward stable domain logic), with no domain code
  importing framework, DB, or vendor SDK types (see
  [clean architecture](03-clean-architecture.md))?
- [ ] Is coupling minimized — does each component know the *least* it can about others
  (interfaces over concretions, no reaching into another module's internals)?
- [ ] Is there **one owner** for each piece of data? No two services write the same table.

## Simplicity & Abstraction

**Rules:** [Best Practices](28-best-practices.md) · [Engineering Principles](30-engineering-principles.md)

- [ ] Does every new abstraction (interface, layer, generic, service) have **at least two
  real callers** or a concrete imminent need (see
  [engineering principles](30-engineering-principles.md))?
- [ ] Is this the **simplest** design that meets the current requirement, with no
  speculative flexibility?
- [ ] Is any duplication either accepted deliberately or extracted only after the third
  occurrence — not abstracted prematurely?
- [ ] Are there fewer, not more, ways to do the same thing after this change?

## Correctness of the Design

**Rules:** [System Design](02-system-design.md) · [Review](27-architecture-review.md)

- [ ] Are consistency and transaction boundaries explicit, and does no operation assume
  distributed ACID it does not have?
- [ ] For any async/event flow, is delivery semantics stated (at-least-once vs.
  exactly-once) and are **consumers idempotent** (see
  [event-driven](08-event-driven-architecture.md))?
- [ ] Are failure modes designed for — timeouts, retries, and fallbacks on every external
  call (see [fault tolerance](17-fault-tolerance.md))?
- [ ] Are illegal states made unrepresentable in the type or schema where practical?

## Change Cost & Reversibility

**Rules:** [Decision Records](26-architecture-decision-records.md) · [Real World Patterns](29-real-world-patterns.md)

- [ ] Is any **one-way-door** decision (public API, data model, service split) recorded in
  an [ADR](26-architecture-decision-records.md) with alternatives and reasoning?
- [ ] Can this change be **rolled back** independently, without a coordinated multi-service
  deploy?
- [ ] Does a public API or event schema change preserve **backward compatibility**, or
  version explicitly?

## Consistency With the System

**Rules:** [Software Architecture](01-software-architecture.md) · [Integration Patterns](12-integration-patterns.md)

- [ ] Does the change follow the existing patterns and conventions of the codebase, or
  justify a deliberate departure?
- [ ] Does it use boring, proven technology for the core, reserving novelty for the one
  thing that is genuinely new?
- [ ] Is cross-cutting concern handling (auth, logging, error handling) consistent with the
  rest of the system rather than reinvented locally?

## How to Use This Checklist

Treat any "no" as a finding, not a formality. For each "no", either change the design or
write down why the exception is acceptable — an unexplained "no" blocks the merge. Rank
findings by reversibility: a wrong data model or service boundary outranks a naming nit,
because it costs far more to undo later.

## Related

- `knowledge/architecture/27-architecture-review.md`
- `knowledge/architecture/28-best-practices.md`
- `knowledge/architecture/30-engineering-principles.md`
- `knowledge/architecture/100-common-antipatterns.md`
- `knowledge/architecture/98-production-checklist.md`
