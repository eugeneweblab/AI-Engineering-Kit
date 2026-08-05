---
id: architecture/28-best-practices
topic: architecture
slug: best-practices
title: "Architecture Best Practices"
type: doc
order: 28
status: ready
tags: [architecture, best-practices]
related: [architecture/30-engineering-principles, architecture/100-common-antipatterns, architecture/27-architecture-review, architecture/00-overview, architecture/26-architecture-decision-records]
when_to_use: "Read before making a design decision when you want the cross-cutting rules that apply regardless of the specific pattern or stack."
---
# Architecture Best Practices

## Purpose

This document collects the cross-cutting practices that hold across architectural styles —
monolith or microservices, sync or async, cloud or on-prem. It is the distilled "default
to this unless you have a specific reason not to" list. It is written so an agent can make
sound structural decisions without re-deriving first principles each time, and recognize
when a design violates a well-established rule.

These practices complement the deeper [engineering principles](30-engineering-principles.md)
and the catalogue of [anti-patterns](100-common-antipatterns.md) to avoid. Where those
explain *why*, this document gives the actionable *do this*.

## Why It Matters

Most architectural failures are not exotic; they are the same handful of mistakes repeated:
coupling that should have been a boundary, a decision made for a scale that never arrives,
a shared database that quietly welds two services together. A short list of well-reasoned
defaults prevents the majority of these, freeing judgment for the genuinely novel problems.
The practices below are not arbitrary conventions — each pays for itself by making the
system cheaper to change, and *changeability is the property that determines whether an
architecture survives contact with reality*.

## Core Principles

- **Optimize for change, not for prediction.** You will be wrong about the future. Build so
  that being wrong is cheap: clear boundaries, loose coupling, reversible decisions.
- **Coupling is the enemy; cohesion is the goal.** Put things that change together in one
  place; separate things that change for different reasons. Every dependency is a liability.
- **Match complexity to the problem.** The right architecture is the *simplest* one that
  meets the real requirements. Complexity you add for imagined future needs is pure cost.
- **Make the implicit explicit.** Boundaries, contracts, ownership, and failure behavior
  should be stated, not assumed. Hidden assumptions are where systems break.
- **Design for failure as the normal case.** In any distributed system, dependencies will
  be slow or down. A design that only works when everything is up is already broken.

## Best Practices

- Define boundaries around business capabilities, and let each own its data. One writer per
  dataset; others read via an explicit contract, never the raw database.
- Depend on abstractions, not concretions. Point dependencies inward toward stable domain
  logic so volatile details (frameworks, vendors) can change without rippling.
- Keep contracts explicit and versioned. A boundary you can call is a promise; make it
  backward-compatible and evolve it deliberately (see [API-first](11-api-first.md)).
- Prefer the simplest architecture that works: a well-structured modular monolith over
  premature microservices. Split only when a concrete force (independent scaling, team
  autonomy, isolation) demands it.
- Make every non-trivial decision reversible where you can, and record the irreversible
  ones as [ADRs](26-architecture-decision-records.md).
- Build in observability from the start — structured logs, metrics, traces, and health
  checks. A system you cannot see into cannot be operated or reviewed.
- Handle failure explicitly at every boundary: timeouts, retries with backoff, circuit
  breakers, and idempotency. Never call a remote dependency without a timeout.
- Keep configuration and secrets out of code and out of artifacts; inject per environment.

## Examples

**Good Example** — explicit boundary, owned data, inward dependency, timeout

```ts
// Inventory owns its data. Other services call this contract; none touch the DB.
interface InventoryPort {
  reserve(sku: string, qty: number): Promise<ReservationResult>;
}

class Checkout {
  // Depends on the abstraction (port), not a concrete client or Inventory's DB.
  constructor(private readonly inventory: InventoryPort) {}

  async place(order: Order) {
    // Remote call always bounded: never let a slow dependency hang the request.
    const res = await withTimeout(this.inventory.reserve(order.sku, order.qty), 500);
    if (!res.ok) return this.reject(order, res.reason); // explicit failure handling
    // ...
  }
}
```

**Bad Example** — shared DB, hidden coupling, unbounded call

```ts
class Checkout {
  async place(order: Order) {
    // Reaches directly into Inventory's tables: two services, one schema, welded
    // together. Inventory can never change its schema without breaking Checkout.
    await db.query("UPDATE inventory SET qty = qty - $1 WHERE sku = $2",
                   [order.qty, order.sku]);

    // Synchronous call with no timeout: if Payments is slow, every checkout hangs
    // and the thread pool exhausts — one slow dependency takes down the service.
    await paymentsHttpClient.charge(order.total);
  }
}
```

## Common Mistakes

- Splitting into microservices before there is a concrete force requiring it — buying
  distributed-systems cost with no benefit.
- Sharing one database across services, which couples them through the schema and defeats
  the boundary you drew.
- Calling remote dependencies with no timeout, retry policy, or circuit breaker, so one
  slow service cascades into an outage.
- Building for a scale or flexibility you do not have yet (speculative generality), adding
  complexity that only ever costs.
- Leaving boundaries, ownership, and contracts implicit, so coupling grows silently.
- Adding observability after an incident instead of designing it in — you cannot debug what
  you cannot see.
- Making irreversible decisions casually and recording none of them.

## Production Tips

- When two components always change together, that is a signal they belong in one boundary;
  when one boundary changes for many unrelated reasons, it is a signal to split it.
- Review new designs against this list and the [anti-patterns](100-common-antipatterns.md)
  during [architecture review](27-architecture-review.md), so the defaults are enforced,
  not just documented.
- Revisit "temporary" simplifications on a schedule; the ones still standing and still fine
  were correct, and the rest are now known debt.

## AI Review Checklist

- Is each dataset owned by exactly one service, accessed by others via a contract?
- Do dependencies point inward toward stable domain logic, via abstractions?
- Is this the simplest architecture that meets the *actual* requirements?
- Does every remote call have a timeout, and a retry/circuit-breaker where appropriate?
- Are boundaries, contracts, and data ownership explicit rather than assumed?
- Is observability (logs, metrics, traces, health checks) built in, not bolted on?
- Are irreversible decisions recorded as ADRs?

## Related

- `knowledge/architecture/30-engineering-principles.md`
- `knowledge/architecture/100-common-antipatterns.md`
- `knowledge/architecture/27-architecture-review.md`
- `knowledge/architecture/26-architecture-decision-records.md`
- `knowledge/architecture/00-overview.md`
