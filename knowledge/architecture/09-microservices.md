---
id: architecture/09-microservices
topic: architecture
slug: microservices
title: "Microservices"
type: doc
order: 9
status: ready
tags: [architecture, microservices]
related: [architecture/10-modular-monolith, architecture/08-event-driven-architecture, architecture/06-domain-driven-design, architecture/21-distributed-systems, architecture/12-integration-patterns]
when_to_use: "Read before splitting a system into independently deployable services, or when deciding whether you need microservices at all."
---
# Microservices

## Purpose

This document defines when and how to build a system as independently deployable
services, each owning its own data and communicating over the network. It is equally
about *when not to* — microservices trade in-process simplicity for distributed-systems
complexity, and that trade is only worth it for specific reasons.

A microservice is a bounded context (see [DDD](06-domain-driven-design.md)) deployed on
its own, with its own database and lifecycle. This doc covers service boundaries, data
ownership, communication, and the failure modes the network forces on you. The default
alternative is a [modular monolith](10-modular-monolith.md); read that first.

## Why It Matters

Microservices exist to let independent teams deploy independently and scale hot parts of
the system separately. That is their real payoff: organizational and scaling autonomy.
But every in-process method call that becomes a network call gains latency, partial
failure, serialization, and versioning problems — and a local transaction becomes a
distributed one you can no longer roll back. Teams routinely adopt microservices for the
resume rather than the requirement, and inherit all the cost with none of the benefit.
Choose them because you have a scaling or team-autonomy problem a monolith cannot solve —
not by default.

## Core Principles

- **A service owns its data.** No other service may touch its database. Sharing a schema
  recreates a distributed monolith with all the coupling and none of the isolation.
- **Boundaries follow business capabilities, not layers.** Split by domain (Orders,
  Billing, Shipping), never into "the database service" and "the UI service".
- **The network is unreliable.** Every remote call can be slow, fail, or time out. Design
  for partial failure with timeouts, retries, and circuit breakers by default.
- **Prefer asynchronous integration.** Synchronous call chains couple services in time
  and cascade failures; [events](08-event-driven-architecture.md) let services proceed
  independently.
- **No distributed transactions.** You cannot two-phase-commit across services in
  practice. Use sagas with compensating actions and accept eventual consistency.
- **Independently deployable is the whole point.** If two services must ship together,
  they are one service that has been split for no reason.

## Best Practices

- Start with a [modular monolith](10-modular-monolith.md) and extract a service only when
  a clear boundary and a concrete driver (scaling, team ownership) appear, because
  boundaries are cheap to move in-process and expensive to move across the network.
- Give each remote call a **timeout** and wrap unstable dependencies in a **circuit
  breaker**, so a slow downstream cannot exhaust the caller's threads and take it down too.
- Communicate across services via published contracts (async events or a versioned API),
  never by reading another service's tables.
- Implement cross-service workflows as **sagas**: a sequence of local transactions, each
  with a compensating action to undo prior steps on failure, since you cannot roll back
  atomically.
- Make every remote-triggered operation idempotent and retry-safe; at-least-once
  delivery and client retries guarantee duplicates.
- Propagate a `traceId` through every hop and centralize logs/metrics/traces — you cannot
  debug a distributed system by reading one service's logs.
- Version APIs and evolve them backward-compatibly; you can never redeploy all callers at
  once.

## Examples

**Good Example** — resilient call, own data, async fact

```ts
// Caller protects itself: bounded timeout + circuit breaker, so a sick Inventory
// service degrades this service gracefully instead of hanging every request.
const reserve = breaker.wrap(() =>
  httpClient.post("/inventory/reserve", body, { timeoutMs: 500 })
);

async function placeOrder(cmd: PlaceOrder) {
  const order = await orderRepo.save(Order.create(cmd)); // Orders owns Orders data only
  try {
    await reserve();
  } catch {
    // No distributed transaction: compensate explicitly (saga step).
    await orderRepo.markFailed(order.id);
    throw new ServiceError("Inventory unavailable, order not placed");
  }
  await events.publish(new OrderPlaced(order.id)); // Billing/Shipping react on their own
}
```

**Bad Example** — shared database, unbounded synchronous chain

```ts
async function placeOrder(cmd: PlaceOrder) {
  // Reaching directly into another service's tables → distributed monolith.
  await sharedDb.query("UPDATE inventory.items SET count = count - 1 WHERE ...");

  // Synchronous chain with no timeout: Orders waits on Billing waits on Tax...
  // one slow hop stalls the whole request and cascades under load.
  const invoice = await billingClient.createInvoice(cmd); // could hang forever
  const label = await shippingClient.createLabel(invoice);
  return { invoice, label };
}
```

## Common Mistakes

- **Distributed monolith**: services share a database or must be deployed together, so
  you pay network costs for zero independence.
- Splitting by technical layer instead of business capability.
- Synchronous request chains with no timeouts or circuit breakers, so failures cascade.
- Expecting distributed transactions to roll back like a local one.
- Non-idempotent handlers that break under retries and redelivery.
- No centralized tracing/logging, making incidents nearly impossible to diagnose.
- Going microservices-first on a small system that a modular monolith would serve better.

## Production Tips

- Enforce timeouts, retries with backoff, and circuit breakers at the platform level
  (mesh or shared client), not ad hoc per team.
- Track per-service SLOs and error budgets; a service's blast radius is only contained if
  its dependencies degrade gracefully.
- Automate deployment per service (CI/CD, health checks, rollback) — independent deploy is
  the benefit you are paying for, so make it routine and safe.

## AI Review Checklist

- Does each service own its data, with no cross-service database access?
- Are boundaries aligned to business capabilities, not technical layers?
- Do all remote calls have timeouts, and unstable ones circuit breakers?
- Are cross-service workflows sagas with compensating actions, not distributed transactions?
- Are remote-triggered handlers idempotent and retry-safe?
- Is a trace/correlation id propagated across every hop?
- Is a microservice actually warranted, or would a modular monolith suffice?

## Related

- `knowledge/architecture/10-modular-monolith.md`
- `knowledge/architecture/08-event-driven-architecture.md`
- `knowledge/architecture/06-domain-driven-design.md`
- `knowledge/architecture/21-distributed-systems.md`
- `knowledge/architecture/12-integration-patterns.md`
