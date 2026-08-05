---
id: architecture/100-common-antipatterns
topic: architecture
slug: common-antipatterns
title: "Architecture Common Antipatterns"
type: antipatterns
order: 100
status: ready
tags: [architecture, common-antipatterns, schema, OrderPlaced]
related: [architecture/09-microservices, architecture/03-clean-architecture, architecture/30-engineering-principles, architecture/08-event-driven-architecture, architecture/99-ai-review-checklist]
when_to_use: "Read before adding a service, layer, or shared component, to check you are not walking into a known trap."
---
# Architecture Common Antipatterns

## Purpose

This document catalogs the recurring architectural mistakes an agent is most likely to
make or approve, and for each one states *why it is wrong* and *the fix*. These are the
patterns that look reasonable in the moment and cost dearly later. Recognizing the shape of
a trap is faster than re-deriving why it hurts, so use this as a lookup during design and
[review](99-ai-review-checklist.md).

## Why It Matters

Antipatterns spread by imitation. One team splits a service the wrong way and every
neighboring team copies it; one shared "utils" module becomes the dumping ground for the
whole codebase. Because each instance passes tests and "works", nothing stops the spread
until change velocity has collapsed. Naming the antipattern is what lets a reviewer reject
it early, while it is still one instance and cheap to undo.

## Structural Antipatterns

### Distributed Monolith

- **What it is:** Services split physically but still deployed together, sharing a
  database or calling each other synchronously for every operation.
- **Why it is wrong:** You pay the full cost of distribution (network failures, latency,
  operational overhead) and get none of the benefit (independent deploy, independent
  scaling, isolation). It is the worst of both worlds.
- **The fix:** Either recombine into a [modular monolith](10-modular-monolith.md) with
  clear internal boundaries, or make the split real — separate data ownership, async where
  possible, and independent deployability (see [microservices](09-microservices.md)).

### Big Ball of Mud

- **What it is:** No discernible boundaries; every module imports every other; logic,
  persistence, and presentation are tangled.
- **Why it is wrong:** Every change risks breaking something unrelated because nothing is
  isolated. Onboarding and reasoning cost grow without bound.
- **The fix:** Introduce boundaries along business capabilities, enforce dependency
  direction, and depend on interfaces (see [clean architecture](03-clean-architecture.md)).

### Premature Microservices

- **What it is:** Splitting a green-field system into many services before the domain
  boundaries are understood.
- **Why it is wrong:** You commit to expensive, hard-to-move boundaries at the moment you
  know least about where they belong, then pay distributed-system tax to iterate on them.
- **The fix:** Start with a modular monolith. Extract a service only when a real driver
  (independent scaling, isolation, team ownership) appears (see
  [engineering principles](30-engineering-principles.md)).

## Coupling Antipatterns

### Shared Database

- **What it is:** Multiple services reading and writing the same tables directly.
- **Why it is wrong:** The schema becomes a public API no one owns; any service's write can
  break another; you cannot evolve the model or deploy independently.
- **The fix:** One writer per dataset. Other services get data through an API or via
  events, never by reaching into the tables.

### God Object / God Service

- **What it is:** A single class or service that accumulates responsibilities until it
  touches everything.
- **Why it is wrong:** Low cohesion and high coupling in one place — it becomes a
  bottleneck for changes, merges, and deploys, and no one dares refactor it.
- **The fix:** Split by responsibility along cohesive lines; each unit should have one
  reason to change.

### Chatty Coupling

- **What it is:** A workflow that requires many fine-grained synchronous calls between
  services to complete one operation.
- **Why it is wrong:** Latency and failure probability multiply with each hop; one slow
  dependency stalls the whole chain.
- **The fix:** Coarsen the API to fewer, higher-level calls, move the boundary so the data
  lives with the logic, or make steps asynchronous.

## Process & Reasoning Antipatterns

### Golden Hammer / Cargo Cult

- **What it is:** Applying a favored pattern (CQRS, event sourcing, Kubernetes, a mesh)
  everywhere, regardless of the problem.
- **Why it is wrong:** Complexity is added without the problem that justifies it; the team
  maintains machinery it does not need.
- **The fix:** Start from the problem. Adopt a pattern only when the specific pain it
  solves is present and measured.

### Resume-Driven / Accidental Complexity

- **What it is:** Choosing technology for novelty or interest rather than fit; layers and
  indirection added "to be safe".
- **Why it is wrong:** Every unjustified moving part is a lifelong maintenance and
  reliability cost paid by the whole team.
- **The fix:** Prefer boring, proven technology for the core; spend the innovation budget
  on the one genuinely novel thing.

## Example — the shared-database trap and its fix

```text
// Bad: Orders and Billing both write the orders table directly.
//   Billing changes a column type -> Orders breaks at runtime, no compiler warning.
//   Neither team can deploy a schema change without coordinating with the other.
[Orders svc] --writes--> (orders table) <--writes-- [Billing svc]

// Good: Orders owns its data. Billing consumes an event and keeps its own view.
//   The contract is the event schema (versioned), not the table. Each deploys freely.
[Orders svc] --(OrderPlaced event)--> [Billing svc] --> (billing's own store)
```

## Common Mistakes

- Calling a system "microservices" when the services share a database — that is a
  distributed monolith, not microservices.
- Extracting a service to "future-proof" before any driver for the split exists.
- Letting a "common" or "utils" module become an unowned dependency magnet.
- Adding a message broker or event bus without defining delivery semantics or making
  consumers idempotent (see [event-driven](08-event-driven-architecture.md)).
- Justifying a pattern by its popularity instead of by the problem it solves.

## AI Review Checklist

- Do any two services write the same table? (Shared database — reject.)
- Are services split before their domain boundaries are understood? (Premature split.)
- Does one operation require many synchronous cross-service hops? (Chatty coupling.)
- Is a pattern or technology present without a stated problem it solves? (Golden hammer.)
- Does any single class or service accumulate unrelated responsibilities? (God object.)
- Are async consumers idempotent and delivery semantics defined?

## Related

- `knowledge/architecture/09-microservices.md`
- `knowledge/architecture/03-clean-architecture.md`
- `knowledge/architecture/30-engineering-principles.md`
- `knowledge/architecture/08-event-driven-architecture.md`
- `knowledge/architecture/99-ai-review-checklist.md`
