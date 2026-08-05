---
id: architecture/07-cqrs
topic: architecture
slug: cqrs
title: "CQRS"
type: doc
order: 7
status: ready
tags: [architecture, cqrs, OrderPlaced, OrderId, PlaceOrder, save, onOrderPlaced, cancelOrder]
related: [architecture/06-domain-driven-design, architecture/08-event-driven-architecture, architecture/14-performance, architecture/13-scalability, architecture/03-clean-architecture]
when_to_use: "Read before splitting read and write models, or when reads and writes have very different scaling or shape requirements."
---
# CQRS

## Purpose

This document defines Command Query Responsibility Segregation (CQRS): separating the
model that *changes* state (commands) from the model that *reads* state (queries). Each
side gets its own model, and often its own data store, optimized for its job.

CQRS is a pattern applied within a [bounded context](06-domain-driven-design.md), not a
system-wide architecture. It is frequently confused with event sourcing — they are
independent. This doc covers when the split earns its cost, and the correctness traps
(chiefly eventual consistency) it introduces.

## Why It Matters

Reads and writes have opposite needs. Writes must protect invariants — they want a
normalized, behavior-rich model and strong consistency. Reads want denormalized,
query-shaped data served fast to many callers. Forcing both through one model means
every read drags the write model's complexity, and every write is constrained by read
shapes. Splitting them lets each scale and evolve on its own axis. The cost is real:
two models to keep in sync, and (when stores differ) eventual consistency that the UI
and clients must tolerate. Apply CQRS only where that asymmetry actually hurts.

## Core Principles

- **Commands change state and return nothing** (or just an id/ack). A command is an
  imperative request — `PlaceOrder` — that can be rejected. Never return query data
  from a command; that recouples the two sides.
- **Queries return data and change nothing.** A query has no side effects, so it is
  safe to cache, retry, and route to replicas.
- **Separate models, not necessarily separate databases.** The lightest CQRS is two
  models over one schema. Only split stores when read scale or shape demands it.
- **The read model is derived and disposable.** It is a projection you can rebuild from
  the write side. Treat it as a cache, never as the source of truth.
- **Eventual consistency is a design input, not an accident.** If stores are separate,
  a read may lag a write. Decide explicitly how the client handles that lag.

## Best Practices

- Start with a shared database and two models; introduce a separate read store only
  when a measured read bottleneck justifies the sync machinery, because separate stores
  add lag and operational load.
- Keep the write model built around [aggregates](06-domain-driven-design.md) that
  enforce invariants. CQRS does not remove the need for a real domain model on the
  write side.
- Update read models by subscribing to [domain events](08-event-driven-architecture.md)
  emitted after a successful command. This decouples projection-building from command
  handling.
- Make projections **idempotent** — the same event applied twice must not double-count —
  because at-least-once delivery will redeliver.
- Surface staleness to clients: return the version/timestamp a read reflects, or use
  read-your-writes routing for the just-written user, so the UI does not show stale data
  as if it were current.
- Keep the ability to rebuild any read model from scratch (replay events or reproject
  from the write store); it is your recovery path when a projection is corrupted.

## Examples

**Good Example** — command mutates, query reads a projection, each side isolated

```ts
// Command side: validates, mutates one aggregate, emits an event. Returns only an id.
async function handlePlaceOrder(cmd: PlaceOrder): Promise<OrderId> {
  const order = Order.create(cmd.customerId, cmd.items); // aggregate enforces invariants
  await writeStore.save(order);
  await events.publish(new OrderPlaced(order.id, order.total)); // read side rebuilds later
  return order.id;                                         // no query data leaks out
}

// Read side: a denormalized projection updated from the event. Fast, no domain logic.
async function onOrderPlaced(e: OrderPlaced) {
  await readStore.upsert("order_summaries", e.orderId, {   // idempotent by primary key
    orderId: e.orderId, total: e.total, status: "Placed",
  });
}

// Query: pure read, safe to cache and route to a replica.
function getOrderSummary(id: OrderId) {
  return readStore.findById("order_summaries", id);
}
```

**Bad Example** — command returns query data, read model treated as source of truth

```ts
async function placeOrder(cmd: PlaceOrder): Promise<OrderSummaryDto> {
  const order = Order.create(cmd.customerId, cmd.items);
  await writeStore.save(order);
  // Command returns a fully hydrated read DTO → the two responsibilities are fused,
  // so the read shape now constrains every write path.
  return buildSummaryDto(order);
}

async function cancelOrder(id: OrderId) {
  // Mutating the READ store directly. It is derived data; this write is lost on the
  // next reprojection, and the write model never learns the order was cancelled.
  await readStore.update("order_summaries", id, { status: "Cancelled" });
}
```

## Common Mistakes

- Applying CQRS everywhere, including simple CRUD, so every feature pays for two models
  it does not need.
- Assuming CQRS requires event sourcing or separate databases — it requires neither.
- Non-idempotent projections that double-apply a redelivered event.
- Writing to the read model as if it were authoritative, then losing those writes on
  reprojection.
- Ignoring the consistency lag in the UI, so a user places an order and does not see it.
- Letting the read and write schemas drift with no way to rebuild the projection.

## Production Tips

- Monitor projection lag (event timestamp vs. applied timestamp) and alert when it grows;
  rising lag is your early warning that the read side is falling behind.
- Store a checkpoint (last processed event position) per projection so it can resume
  after a restart without reprocessing everything.
- Keep a documented, tested reprojection job; rehearse rebuilding a read model in staging.

## AI Review Checklist

- Do commands change state and return only an id/ack, never query DTOs?
- Are queries free of side effects and safe to cache?
- Is the read model derived from the write side and never the source of truth?
- Are projections idempotent under redelivery?
- Is eventual consistency handled explicitly in the client or UI?
- Can every read model be rebuilt from the write store or event log?
- Is CQRS actually justified here, or would a single model be simpler?

## Related

- `knowledge/architecture/06-domain-driven-design.md`
- `knowledge/architecture/08-event-driven-architecture.md`
- `knowledge/architecture/13-scalability.md`
- `knowledge/architecture/14-performance.md`
- `knowledge/architecture/03-clean-architecture.md`
