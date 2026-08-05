---
id: architecture/20-message-brokers
topic: architecture
slug: message-brokers
title: "Architecture Message Brokers"
type: doc
order: 20
status: ready
tags: [architecture, message-brokers, handle, nack, contains]
related: [architecture/08-event-driven-architecture, architecture/12-integration-patterns, architecture/09-microservices, architecture/21-distributed-systems, architecture/17-fault-tolerance]
when_to_use: "Read before adding a queue or event stream, or when designing how services communicate asynchronously."
---
# Architecture Message Brokers

## Purpose

This document defines how to move work and events between services through a broker — queues,
topics, and streams — reliably and without losing or duplicating messages. It is written so
an agent can build a producer or consumer that survives crashes, retries, and redeploys.

A broker decouples producers from consumers in time and load: the producer hands off a message
and moves on; the consumer processes at its own pace. That decoupling is the value, but it also
means delivery is asynchronous and imperfect. Reasoning about *what happens when a message is
delivered twice, out of order, or not at all* is the core of using a broker correctly.

## Why It Matters

The moment a message leaves the producer's process, the strong guarantees of a local function
call are gone. Networks partition, consumers crash mid-handler, and brokers redeliver. A design
that assumes exactly-once, in-order, never-lost delivery will corrupt data the first time
reality disagrees. Most brokers offer *at-least-once* delivery, which means duplicates are not
an edge case — they are the contract. Systems that ignore this double-charge cards and
double-ship orders. Systems that embrace it (idempotent consumers, explicit acks) are boring
and correct. The difference is entirely in how the consumer is written.

## Core Principles

- **Assume at-least-once delivery.** Duplicates and redelivery are normal. Every consumer must
  be idempotent — processing the same message twice produces the same result as once.
- **Acknowledge only after work is durable.** Ack after the side effect is committed, not on
  receipt. Ack-then-crash loses the message; crash-before-ack redelivers it (which idempotency
  handles).
- **Order is per-partition, not global.** Global ordering does not scale. If you need ordering,
  key related messages to the same partition and accept that unrelated messages interleave.
- **A dead message must not block the queue.** A poison message that always fails will halt a
  queue forever unless it can be retried with backoff and finally parked in a dead-letter queue.
- **The broker is infrastructure, not your database.** Use it to move messages, not as the
  long-term store of record. Persist state you need to keep in a real datastore.

## Best Practices

- Give every message a stable, unique `message_id` (or business key) and dedupe on it in the
  consumer. This is what makes at-least-once safe.
- Make handlers idempotent: upsert instead of insert, use conditional writes, or record
  processed IDs. Never let a redelivery apply an effect twice.
- Use manual acknowledgement. Enable auto-ack only for telemetry you can afford to lose.
- Configure retries with exponential backoff and a **dead-letter queue** with a max-delivery
  count, so poison messages are quarantined for inspection instead of looping forever.
- Choose the model deliberately: a **queue** (competing consumers, each message processed once
  across the group) for work distribution; a **topic/stream** (fan-out, each subscriber gets a
  copy, replayable log) for events. Kafka-style logs let you replay; classic queues do not.
- Keep messages small and self-describing; put large payloads in object storage and send a
  reference (claim-check pattern). Brokers degrade under multi-megabyte messages.
- Version message schemas and evolve them additively. A consumer must tolerate unknown fields
  so producers and consumers can deploy independently.
- Bound consumer concurrency and prefetch so one slow downstream cannot be overwhelmed.

## Examples

**Good Example** — idempotent consumer, ack after commit, DLQ on repeated failure

```python
async def handle(msg: Message) -> None:
    # Dedupe on a stable id: a redelivered message is a no-op, so at-least-once
    # delivery cannot apply the side effect twice.
    if await processed.contains(msg.id):
        await msg.ack()                     # already done; drop the duplicate
        return
    try:
        await charge_payment(msg.order_id, msg.amount)   # the real side effect
        await processed.add(msg.id)          # record it in the same commit boundary
        await msg.ack()                      # ack only after work is durable
    except TransientError:
        await msg.nack(requeue=True)         # backoff + retry; DLQ after max attempts
```

**Bad Example** — ack on receipt, non-idempotent, no DLQ

```python
async def handle(msg: Message) -> None:
    await msg.ack()                          # acked before work -> crash here loses it
    await charge_payment(msg.order_id, msg.amount)  # redelivery double-charges the card
    # no dedupe, no retry policy: a message that always throws either vanishes
    # (acked early) or loops forever, blocking the queue.
```

## Common Mistakes

- Assuming exactly-once delivery and writing non-idempotent consumers, causing double effects.
- Acknowledging on receipt instead of after the work is committed, losing messages on crash.
- No dead-letter queue, so one poison message blocks the queue or is silently dropped.
- Expecting global ordering across partitions; only per-partition/per-key order is guaranteed.
- Putting large payloads directly in messages, degrading broker throughput.
- Using the broker as a database — relying on retained messages as the source of truth.
- Breaking schema changes that force producer and consumer to deploy in lockstep.

## Production Tips

- Alert on consumer **lag** (unprocessed backlog) and DLQ depth; both are leading indicators of
  an incident before users notice.
- Make DLQs actionable: have a documented replay procedure once the root cause is fixed.
- Load-test the redelivery path, not just the happy path — most bugs live in retries.
- For ordered streams, size partitions for peak parallelism up front; repartitioning live is
  disruptive.

## AI Review Checklist

- Is every consumer idempotent (dedupe by `message_id` or conditional write)?
- Is acknowledgement done only after the side effect is durably committed?
- Is there a retry-with-backoff policy and a dead-letter queue with a max-delivery count?
- Does the design rely only on per-partition ordering, never global ordering?
- Are large payloads sent by reference (claim-check) rather than inline?
- Are message schemas versioned and evolved additively?
- Are consumer lag and DLQ depth monitored and alerted on?

## Related

- `knowledge/architecture/08-event-driven-architecture.md`
- `knowledge/architecture/12-integration-patterns.md`
- `knowledge/architecture/09-microservices.md`
- `knowledge/architecture/21-distributed-systems.md`
- `knowledge/architecture/17-fault-tolerance.md`
