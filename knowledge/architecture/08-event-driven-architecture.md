---
id: architecture/08-event-driven-architecture
topic: architecture
slug: event-driven-architecture
title: "Event Driven Architecture"
type: doc
order: 8
status: ready
tags: [architecture, event-driven-architecture]
related: [architecture/07-cqrs, architecture/09-microservices, architecture/20-message-brokers, architecture/17-fault-tolerance, architecture/06-domain-driven-design]
when_to_use: "Read before designing asynchronous communication between services or components using events, queues, or a message broker."
---
# Event Driven Architecture

## Purpose

This document defines how components communicate by producing and consuming *events* —
immutable records of facts that already happened — instead of calling each other
directly. It covers event design, delivery guarantees, ordering, idempotency, and the
failure modes that async introduces.

Event-driven architecture (EDA) decouples the producer of a fact from whoever cares
about it. It underpins [microservices](09-microservices.md) integration, powers
[CQRS](07-cqrs.md) read models, and rides on [message brokers](20-message-brokers.md).
It is powerful and dangerous in equal measure: async correctness is where most
distributed-systems bugs live.

## Why It Matters

Direct synchronous calls couple services in time — if one is down or slow, the caller
is too, and failures cascade. Events break that coupling: the producer emits a fact and
moves on; consumers process at their own pace, retry on failure, and can be added
without touching the producer. The price is that you trade a simple call stack for a
distributed system with no global clock: messages arrive late, out of order, or twice,
and "did it work?" no longer has an immediate answer. Every consumer must be written to
survive that. Ignore these guarantees and the system will corrupt data silently under
load.

## Core Principles

- **Events are immutable facts, past tense.** `OrderPlaced`, not `PlaceOrder`. An event
  states what happened; it is never a disguised command telling one consumer what to do.
- **Assume at-least-once delivery.** Brokers redeliver on failure or timeout, so the
  same event *will* arrive twice. Exactly-once is a marketing claim, not a runtime
  guarantee — engineer for duplicates.
- **Consumers must be idempotent.** Processing an event twice must produce the same
  result as processing it once. This is the single most important rule in EDA.
- **Do not assume global ordering.** Order is only guaranteed within a partition/key at
  best. Design so that out-of-order arrival is tolerable, or key by aggregate id.
- **The event is the contract.** Its schema is a published API. Adding consumers must
  not require changing producers, and schema changes must stay backward compatible.

## Best Practices

- Give every event a unique id and process it through a dedup/inbox table, so a
  redelivered event is recognized and skipped — this is how you make at-least-once safe.
- Use the **transactional outbox** pattern: within the same DB transaction that changes
  state, write the event to an outbox table; a separate relay publishes it. This closes
  the gap where a crash after commit-before-publish (or vice versa) loses or duplicates
  events.
- Version event schemas and evolve them additively (new optional fields only). Never
  remove or repurpose a field consumers may read, because you cannot redeploy every
  consumer atomically.
- Configure a **dead-letter queue** for messages that fail repeatedly, so one poison
  message does not block the whole partition. Alert on DLQ growth.
- Key events by their aggregate id when ordering matters, so all events for one entity
  land on the same partition and stay ordered.
- Keep events lean: include the ids and the changed facts, not entire object graphs.
  Bloated events couple consumers to the producer's internal model.

## Examples

**Good Example** — outbox on write, idempotent consumer on read

```ts
// Producer: state change and event are written in ONE transaction (outbox pattern),
// so they cannot diverge if the process crashes mid-way.
await db.transaction(async (tx) => {
  await tx.orders.insert(order);
  await tx.outbox.insert({
    id: uuid(),                       // stable event id, used downstream for dedup
    type: "OrderPlaced",
    payload: { orderId: order.id, total: order.total },
  });
});
// A separate relay polls `outbox` and publishes to the broker, then marks rows sent.

// Consumer: idempotent via an inbox table keyed by event id.
async function onOrderPlaced(e: Event) {
  await db.transaction(async (tx) => {
    const seen = await tx.inbox.exists(e.id);
    if (seen) return;                 // duplicate delivery → no-op, safe to retry
    await tx.inbox.insert({ id: e.id });
    await tx.readModel.applyOrderPlaced(e.payload);
  });
}
```

**Bad Example** — dual write, non-idempotent side effect

```ts
async function placeOrder(order: Order) {
  await db.orders.insert(order);      // commit 1
  await broker.publish("OrderPlaced", order); // commit 2 — if this throws, event is lost;
                                              // if the DB insert is retried, event is duplicated
}

async function onOrderPlaced(e: Event) {
  // Charges the card every time the event is delivered. At-least-once → double charge.
  await payments.charge(e.payload.orderId, e.payload.total);
}
```

## Common Mistakes

- Dual writes: committing to the database and publishing to the broker as two separate
  operations, so a crash between them loses or duplicates the event.
- Non-idempotent consumers that repeat side effects (charge, email, decrement) on
  redelivery.
- Treating an event as a command aimed at one specific consumer, recoupling producer and
  consumer.
- Assuming global ordering and breaking when events arrive out of sequence.
- Breaking-change schema edits (removing/renaming fields) that silently break consumers.
- No dead-letter handling, so one unprocessable message stalls an entire partition.

## Production Tips

- Monitor consumer lag and DLQ depth; both are leading indicators of an incident.
- Include a `correlationId`/`traceId` in every event and propagate it, so a business
  transaction can be traced across async hops (see [observability](18-observability.md)).
- Make retries use exponential backoff with a cap, and set a max attempts before
  dead-lettering, so a struggling downstream is not hammered.

## AI Review Checklist

- Are events immutable, past-tense facts rather than commands?
- Is every consumer idempotent against at-least-once redelivery?
- Is the outbox (or equivalent) used so state change and event publish are atomic?
- Do events carry a unique id used for deduplication?
- Are schema changes additive and backward compatible?
- Is there a dead-letter queue and retry-with-backoff for failing messages?
- Does the design avoid relying on global event ordering?

## Related

- `knowledge/architecture/07-cqrs.md`
- `knowledge/architecture/09-microservices.md`
- `knowledge/architecture/20-message-brokers.md`
- `knowledge/architecture/17-fault-tolerance.md`
- `knowledge/architecture/06-domain-driven-design.md`
