---
id: architecture/29-real-world-patterns
topic: architecture
slug: real-world-patterns
title: "Real World Patterns"
type: doc
order: 29
status: ready
tags: [architecture, real-world-patterns]
related: [architecture/12-integration-patterns, architecture/08-event-driven-architecture, architecture/17-fault-tolerance, architecture/28-best-practices, architecture/100-common-antipatterns]
when_to_use: "Read before designing a flow that spans services, needs reliable messaging, or must stay consistent across a boundary — reach for a proven pattern first."
---
# Real World Patterns

## Purpose

This document catalogs the recurring architectural patterns that solve the problems teams
actually hit in production: reliably crossing a service boundary, keeping two systems
consistent without distributed transactions, absorbing failure, and evolving a system
without downtime. Each entry states the problem it solves and the cost it carries. It is
written so an agent can recognize a known problem and reach for the proven solution instead
of inventing a fragile one.

These are the *applied* patterns that compose the styles covered elsewhere
([event-driven](08-event-driven-architecture.md),
[integration](12-integration-patterns.md), [fault tolerance](17-fault-tolerance.md)). Every
pattern is a trade-off — the skill is matching the pattern to the force that justifies it.

## Why It Matters

The hardest production problems — lost messages, orphaned state, cascading outages, painful
migrations — are already solved. They have names, well-understood trade-offs, and battle
scars. An engineer who reaches for the Outbox pattern avoids a class of data-loss bugs that
a naive dual-write guarantees. An engineer who does not know the pattern reinvents it badly
and rediscovers the failure in production. Knowing the catalogue converts a hard, novel
problem into a solved one — and, just as importantly, tells you the cost you are signing up
for so you can decide whether it is worth paying.

## Core Principles

- **Every pattern is a trade-off, not a free upgrade.** Adopt one because a specific force
  demands it, and accept its cost knowingly. A pattern applied without its problem is just
  added complexity.
- **Prefer eventual consistency to distributed transactions.** Two-phase commit across
  services is fragile and slow; most business flows tolerate a short inconsistency window if
  it is designed for and made visible.
- **Make cross-boundary operations idempotent and retryable.** Networks fail mid-operation;
  the only safe design assumes any message may be delivered zero, one, or many times.
- **Isolate failure so it cannot cascade.** A dependency going down should degrade one
  feature, not topple the system. Bulkheads and circuit breakers are how.
- **Design changes to be backward-compatible.** Evolving a live system means old and new run
  together; patterns like expand/contract and strangler-fig make that safe.

## Best Practices

- **Transactional Outbox** — to publish an event *and* commit a DB change atomically, write
  the event to an `outbox` table in the same transaction, then a relay publishes it. This
  removes the dual-write race where the DB commits but the publish is lost. Cost: eventual
  publish and a relay to operate.
- **Saga** — to coordinate a multi-service transaction without 2PC, model it as a sequence
  of local transactions, each with a compensating action to undo on failure. Cost: you must
  design and test every compensation path.
- **Circuit Breaker** — to stop calling a failing dependency, trip open after a failure
  threshold, fail fast, and probe for recovery. Cost: a half-open state and thresholds to
  tune. Pair with a timeout and a bulkhead to isolate the blast radius.
- **Idempotency Key** — to make retries safe, have the client send a unique key and the
  server deduplicate, returning the original result on replay. Essential for payments and
  any at-least-once delivery.
- **CQRS + read models** — when read and write shapes diverge sharply, separate them and
  project a read model from events. Cost: eventual consistency and a projection to maintain.
  Do *not* apply it by default (see [CQRS](07-cqrs.md)).
- **Strangler Fig** — to replace a legacy system incrementally, route traffic through a
  facade and migrate one capability at a time until the old system is empty. Avoids a risky
  big-bang rewrite.
- **Backend-for-Frontend** — give each client type its own tailored API gateway instead of
  one API straining to serve all clients.

## Examples

**Good Example** — Transactional Outbox: atomic write + publish

```ts
// The DB write and the event are committed in ONE transaction. A separate relay
// publishes rows from `outbox`, so a crash after commit never loses the event.
await db.transaction(async (tx) => {
  await tx.orders.insert(order);
  await tx.outbox.insert({                 // same transaction as the state change
    type: "OrderPlaced",
    payload: order,
    published: false,
  });
});
// Relay (separate process): reads unpublished rows, publishes, marks published.
// Consumers dedupe by event id, because the relay may publish a row twice on retry.
```

**Bad Example** — dual write: guaranteed to lose events

```ts
await db.orders.insert(order);   // 1) commits to the database
await bus.publish("OrderPlaced", order);
// 2) If the process crashes here, the order exists but the event was NEVER sent.
//    Fulfilment never runs. There is no transaction spanning DB and bus, so these
//    two writes cannot be atomic — this WILL silently drop events under load.
```

## Common Mistakes

- Dual-writing to a database and a message bus without an outbox, silently losing events on
  a mid-operation crash.
- Coordinating cross-service work with a distributed transaction (2PC) instead of a saga
  with compensations.
- Making retryable operations non-idempotent, so a delivery retry double-charges or
  duplicates state.
- Adding a circuit breaker but no timeout, so calls still hang before the breaker ever sees
  a failure.
- Applying a heavy pattern (CQRS, event sourcing, sagas) where a simple transaction would
  do — paying the cost with no matching force.
- Rewriting a legacy system big-bang instead of strangling it incrementally.
- Designing a saga's happy path but never testing the compensation paths that failure needs.

## Production Tips

- Instrument every pattern: outbox lag, breaker state transitions, saga compensation counts,
  and dedupe hits are the signals that tell you the pattern is actually working.
- Write the failure-path test first — the whole value of these patterns is behavior under
  failure, and that is exactly the code that never runs in a demo.
- When you adopt a pattern, record *which force* justified it in an
  [ADR](26-architecture-decision-records.md); it stops a future reader from ripping out
  machinery they think is gratuitous.

## AI Review Checklist

- Does any code write to a DB and a message bus separately without an outbox?
- Are cross-service transactions modeled as sagas with tested compensations, not 2PC?
- Are all retryable and at-least-once operations idempotent (idempotency keys, dedupe)?
- Do circuit breakers pair with timeouts and bulkheads to isolate failure?
- Is each applied pattern justified by a real force, not adopted by default?
- Are legacy replacements incremental (strangler fig) rather than big-bang rewrites?
- Are the failure and compensation paths tested and instrumented, not just the happy path?

## Related

- `knowledge/architecture/12-integration-patterns.md`
- `knowledge/architecture/08-event-driven-architecture.md`
- `knowledge/architecture/17-fault-tolerance.md`
- `knowledge/architecture/28-best-practices.md`
- `knowledge/architecture/100-common-antipatterns.md`
