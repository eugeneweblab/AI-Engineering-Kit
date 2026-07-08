---
id: backend/14-events
topic: backend
slug: events
title: "Events"
type: doc
order: 14
status: ready
tags: [backend, events]
related: [backend/15-message-brokers, backend/16-background-jobs, backend/17-transactions, backend/05-ddd, backend/12-error-handling]
when_to_use: "Read before designing domain events, an outbox, or any produce/consume flow that reacts to state changes."
---
# Events

## Purpose

This document defines how backend systems should design and use *events* — immutable
records that something happened ("OrderPlaced", "PaymentCaptured"). It covers event
schema and naming, the difference between domain and integration events, ordering and
delivery guarantees, idempotent consumers, and the transactional outbox pattern. The
goal is that an agent can add an event-producing or event-consuming path that stays
consistent even when processes crash mid-flight.

Events are about *decoupling producers from consumers*. This doc is about designing the
events themselves; [message brokers](15-message-brokers.md) covers the transport that
carries them.

## Why It Matters

Events let one part of a system react to another without a direct call, which is what
makes systems extensible and resilient. But events introduce a hard problem: the state
change and the event announcing it live in two places (a database and a broker), and any
crash between them causes either a lost event (consumers never react) or a phantom event
(consumers react to something that never committed). Every serious event bug traces back
to this dual-write gap or to a consumer that isn't idempotent. Get those two right and
events are safe; ignore them and you get silent, intermittent data divergence.

## Core Principles

- **An event is an immutable fact in the past tense.** Name it for what *happened*
  (`OrderShipped`), not for what should happen next (`SendShipmentEmail`). Commands tell;
  events inform. Confusing the two couples the producer to the consumer's job.
- **Events carry data, not just ids — but only what happened.** Include enough context
  for consumers to act without calling back, but do not smuggle a consumer's needs into
  the producer's event.
- **Producing an event and committing the state change must be atomic.** Use the
  transactional **outbox**: write the event to the same database transaction as the state
  change, then a relay publishes it. Never publish to a broker inside a business
  transaction.
- **Assume at-least-once delivery; make consumers idempotent.** The same event will be
  delivered more than once. Processing it twice must equal processing it once.
- **Assume no global ordering.** Do not require that event B is seen after event A unless
  you explicitly partition by key. Design consumers to tolerate reordering.

## Best Practices

- Give every event a **stable, versioned schema**: a `type`, a unique `id`, an
  `occurredAt`, an aggregate/partition key, and a typed `payload`. Version the schema and
  only make **backward-compatible** changes (add optional fields; never repurpose one).
- **Separate domain events from integration events.** Domain events are internal and rich;
  integration events are the public, minimized contract you publish to other services.
  Publishing raw domain events leaks your internal model.
- Use the **outbox** to bridge the transaction and the broker. A separate relay/poller (or
  change-data-capture) reads unpublished rows and pushes them, marking them sent.
- Make consumers **idempotent** by tracking processed event ids (a dedup table or unique
  constraint), so a redelivery is a no-op.
- Partition by the **aggregate key** (e.g. order id) when you need per-entity ordering;
  accept that events for different keys may interleave.
- Keep events **self-contained and small**; if a consumer needs more, it can look up the
  id. Do not embed large blobs.
- Handle **poison events**: after N failed attempts, route to a dead-letter destination
  and alert, rather than blocking the stream forever.

## Examples

**Good Example** — transactional outbox + idempotent consumer

```ts
// Producer: state change and event are written in ONE transaction. No broker call here.
await db.transaction(async (tx) => {
  await tx.orders.insert(order);
  await tx.outbox.insert({
    id: uuid(),
    type: "OrderPlaced.v1",
    aggregateId: order.id,          // partition key -> per-order ordering
    occurredAt: new Date(),
    payload: { orderId: order.id, total: order.total, customerId: order.customerId },
  });
}); // if the tx rolls back, no order AND no event — they can never disagree

// A separate relay polls the outbox and publishes, then marks rows as sent (at-least-once).

// Consumer: idempotent via a processed-events table.
async function onOrderPlaced(evt: Event) {
  await db.transaction(async (tx) => {
    const fresh = await tx.processed.insertIfAbsent(evt.id); // unique constraint on id
    if (!fresh) return;             // already handled -> redelivery is a no-op
    await tx.invoices.create(evt.payload.orderId);
  });
}
```

**Bad Example** — dual write + non-idempotent consumer

```ts
// Producer: two separate systems, no atomicity.
await db.orders.insert(order);      // commits
await broker.publish("OrderPlaced", order); // if THIS throws, order exists but no event
// If the process crashes between the lines, the event is lost forever.

// Consumer: no dedup. At-least-once delivery means this can bill the customer twice.
async function onOrderPlaced(evt: Event) {
  await invoices.create(evt.payload.orderId); // redelivery -> duplicate invoice
}
```

## Common Mistakes

- Dual-writing to the database and the broker without an outbox, losing or inventing events.
- Publishing an event *before* the transaction commits, so consumers react to rolled-back state.
- Non-idempotent consumers that duplicate side effects on redelivery.
- Naming events as commands (`CreateInvoice`), coupling producer to consumer behavior.
- Assuming global ordering, then breaking when events for one key arrive out of order.
- Making a breaking change to an event schema, silently breaking every consumer.
- No dead-letter path, so one poison event stalls the entire stream.

## Production Tips

- Monitor **outbox lag** (unpublished rows age) and **consumer lag**; both are early
  warnings of a stuck pipeline.
- Keep a **schema registry** or shared package for event types so producers and consumers
  cannot drift.
- Retain events (or the outbox) long enough to **replay** into a new or recovered consumer.
- Emit metrics on **dead-lettered events** and alert — a poison event is a code bug, not
  noise.

## AI Review Checklist

- Is the event written in the same transaction as the state change (outbox), not dual-written?
- Are events named as past-tense facts, not as commands?
- Is every consumer idempotent (dedup by event id) against at-least-once delivery?
- Does each event have a stable, versioned schema with only backward-compatible changes?
- Are domain events kept internal and only integration events published externally?
- Is ordering only assumed within a partition key, never globally?
- Is there a dead-letter path and alert for poison events?

## Related

- `knowledge/backend/15-message-brokers.md`
- `knowledge/backend/16-background-jobs.md`
- `knowledge/backend/17-transactions.md`
- `knowledge/backend/05-ddd.md`
- `knowledge/backend/12-error-handling.md`
