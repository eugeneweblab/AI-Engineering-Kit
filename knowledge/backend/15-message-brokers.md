---
id: backend/15-message-brokers
topic: backend
slug: message-brokers
title: "Backend Message Brokers"
type: doc
order: 15
status: ready
tags: [backend, message-brokers]
related: [backend/14-events, backend/16-background-jobs, backend/17-transactions, backend/20-scalability, backend/12-error-handling]
when_to_use: "Read before publishing to or consuming from a broker (Kafka, RabbitMQ, SQS, NATS) or choosing one."
---
# Backend Message Brokers

## Purpose

This document defines how to use a message broker — Kafka, RabbitMQ, SQS, NATS, or
similar — correctly. It covers delivery semantics, acknowledgements, consumer groups and
partitioning, ordering, retries, dead-letter queues, and how to pick a broker for a
workload. The goal is that an agent can wire up a producer or consumer that does not lose,
duplicate, or reorder messages in ways the business cannot tolerate.

The broker is the *transport*; [events](14-events.md) covers the message design and the
outbox that feeds the broker. This doc is about operating the pipe itself.

## Why It Matters

A broker is the backbone of asynchronous and distributed systems: it absorbs traffic
spikes, decouples services, and lets slow work happen off the request path. But every
broker forces explicit choices about *delivery guarantees*, and those choices are where
teams get burned. "At-least-once" (the common default) means duplicates are normal;
"ordering" usually holds only within a partition; an un-acked message will be redelivered
after a crash. If you treat the broker as a magic reliable queue and ignore these
semantics, you ship duplicate charges, out-of-order state, and silently dropped messages.

## Core Principles

- **Know your delivery guarantee and design for it.** Most brokers give **at-least-once**
  by default: assume every message can arrive more than once and build idempotent
  consumers. True exactly-once is rare, narrow, and costly — do not assume it.
- **Acknowledge only after the work is durably done.** Ack before processing and a crash
  loses the message; ack after committing side effects and a crash merely redelivers.
  Prefer redelivery over loss.
- **Ordering is per-partition, not global.** If order matters, route related messages to
  the same partition via a partition key. Across partitions, assume interleaving.
- **A consumer must be able to fail safely.** Bounded retries with backoff, then a
  dead-letter queue (DLQ) so one bad message never blocks the whole partition.
- **The broker is not a database.** It is a transport with retention, not a query store.
  Do not use it as your source of truth or search index.

## Best Practices

- Make consumers **idempotent** (dedup by message id / business key). This is mandatory
  under at-least-once, not optional.
- **Manual ack after commit**: disable auto-ack; acknowledge (or commit offset) only once
  the message's side effects are persisted. This turns "loss" into "redelivery".
- Set a **partition/routing key** on the producer for any messages that must stay ordered
  relative to each other (e.g. all events for one account).
- Configure **bounded retries with exponential backoff and jitter**, then route failures
  to a **DLQ**. Never retry forever in-line — it blocks the partition and hides bugs.
- Right-size **consumer concurrency and prefetch**: too high starves ordering and memory;
  too low wastes throughput. Scale consumers up to (but not beyond) the partition count.
- Keep messages **small and self-describing** (typed schema + version). Put large payloads
  in object storage and pass a reference (claim-check pattern).
- Feed the broker from a **transactional outbox** ([events](14-events.md)) so publishing
  is atomic with the state change, rather than publishing inside business logic.
- Pick the broker for the job: **Kafka** for high-throughput ordered logs and replay;
  **RabbitMQ** for flexible routing and per-message ack; **SQS** for managed simplicity;
  **NATS** for low-latency lightweight messaging.

## Examples

**Good Example** — manual ack after commit, idempotent, DLQ on repeated failure

```ts
consumer.subscribe("orders", { autoAck: false, prefetch: 20 });

consumer.on("message", async (msg) => {
  try {
    await db.transaction(async (tx) => {
      const fresh = await tx.processed.insertIfAbsent(msg.id); // dedup: at-least-once safe
      if (!fresh) return;                                      // duplicate -> no-op
      await fulfil(tx, msg.body);
    });
    await msg.ack();          // ack ONLY after side effects are committed
  } catch (err) {
    if (msg.deliveryCount >= 5) {
      await msg.deadLetter(err); // stop blocking the partition; alert on the DLQ
    } else {
      await msg.nack({ requeue: true, backoffMs: expBackoff(msg.deliveryCount) });
    }
  }
});
```

**Bad Example** — auto-ack before work, no dedup, infinite in-line retry

```ts
consumer.subscribe("orders", { autoAck: true }); // acked on receipt, before processing

consumer.on("message", async (msg) => {
  // If fulfil() throws or the process crashes here, the message is already acked -> LOST.
  await fulfil(msg.body);      // not idempotent: redelivery would double-fulfil
  // On error, some code just retries in a loop forever, blocking the partition
  // and never surfacing the bug. No DLQ, no backoff.
});
```

## Common Mistakes

- Auto-acking on receipt, losing messages whenever processing fails or the process dies.
- Non-idempotent consumers under at-least-once delivery, causing duplicate side effects.
- Assuming global ordering when the broker only guarantees it within a partition.
- Retrying a failing message forever in-line, blocking the partition and hiding the bug.
- No DLQ, so one poison message halts an entire consumer group.
- Publishing inside business logic instead of via an outbox, re-creating the dual-write gap.
- Using the broker as durable storage or as a query surface.
- More consumers than partitions (Kafka), leaving consumers idle.

## Production Tips

- Alarm on **consumer lag** (unprocessed backlog) and on **DLQ depth** — both signal a
  stuck or failing pipeline before users notice.
- Make the **DLQ replayable**: a tool to fix the cause and re-inject messages is worth
  more than any dashboard.
- Set **message TTLs / retention** deliberately; a silent expiry is indistinguishable
  from loss.
- Load-test consumer **throughput vs. partition count** before launch; you cannot scale
  past the partition count without repartitioning.

## AI Review Checklist

- Is the delivery guarantee known, and are consumers idempotent for at-least-once?
- Are messages acked/committed only *after* side effects are durably persisted?
- Is a partition/routing key set wherever message ordering matters?
- Are retries bounded with backoff, with a DLQ for repeated failures?
- Is consumer concurrency bounded and no greater than the partition count?
- Is the broker fed from an outbox rather than a dual write in business logic?
- Are consumer lag and DLQ depth monitored and alerted on?

## Related

- `knowledge/backend/14-events.md`
- `knowledge/backend/16-background-jobs.md`
- `knowledge/backend/17-transactions.md`
- `knowledge/backend/20-scalability.md`
- `knowledge/backend/12-error-handling.md`
