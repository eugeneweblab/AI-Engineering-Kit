---
id: redis/16-message-queues
topic: redis
slug: message-queues
title: "Message Queues"
type: doc
order: 16
status: ready
tags: [redis, message-queues]
related: [redis/08-streams, redis/09-pub-sub, redis/04-lists, redis/17-distributed-locks, redis/20-persistence]
when_to_use: "Read before building a job queue, worker pool, or event pipeline on Redis."
---
# Message Queues

## Purpose

This document defines how to build a reliable message/job queue on Redis: which
primitive to use (Streams vs Lists vs Pub/Sub), how to guarantee a message is not
lost when a worker crashes, and how to avoid duplicate or stuck work. It is
written so an agent can build a queue that survives worker failure without losing
or double-processing jobs.

Redis can be a queue, but "reliable queue" and "fire-and-forget notification" are
different problems with different primitives. Choosing wrong is the root of most
Redis queue bugs.

## Why It Matters

A queue's whole job is to not lose work. The moment a worker pops a job and then
crashes before finishing, a naive queue has silently dropped that job — an order
never ships, an email never sends, and nothing errors. These losses are invisible
until a customer complains.

The mirror-image failure is duplication: a redelivery mechanism that re-runs a
job whose side effects already happened, charging a card twice. A correct queue
picks a delivery guarantee (at-least-once is the practical default), makes
consumers **idempotent**, and uses a primitive that can recover in-flight work
after a crash.

## Core Principles

- **Pub/Sub is not a queue.** `PUBLISH`/`SUBSCRIBE` is fire-and-forget: messages
  sent while no subscriber is connected are gone forever, with no ack and no
  replay. Use it for live notifications, never for work that must complete.
- **Reliable delivery requires an acknowledgement.** A message must stay
  recoverable until a consumer explicitly confirms success. A pop that removes the
  message before processing loses it on any crash.
- **Prefer Redis Streams for real queues.** Streams give consumer groups,
  per-message ack (`XACK`), a pending-entries list for crash recovery, and
  `XCLAIM` to reassign stuck messages. This is the modern, correct primitive.
- **At-least-once means consumers must be idempotent.** Redelivery after a crash
  is a feature; design every handler so processing the same message twice is
  harmless.
- **A message is durable only if Redis is.** Queue reliability is bounded by your
  persistence and replication config; an unpersisted primary that dies loses the
  queue.

## Best Practices

- Use **Streams + consumer groups**: producers `XADD`, workers `XREADGROUP`,
  confirm with `XACK`, and periodically scan the pending list (`XPENDING`) to
  `XCLAIM` messages abandoned by dead workers.
- Set an **idle threshold** for `XCLAIM`/`XAUTOCLAIM` so a crashed worker's
  in-flight messages are reassigned, not stranded.
- Make handlers **idempotent** via a dedupe key (store the message id in a `SET`
  with TTL, or use an idempotent DB upsert) so redelivery is safe.
- Add a **dead-letter** path: after N delivery attempts (track via the pending
  entry's delivery count), move the message to a separate stream for inspection
  instead of retrying forever.
- Cap stream growth with `XADD ... MAXLEN ~ N` (approximate trimming) or
  `XTRIM`, or by trimming acked ranges, so the stream doesn't grow unbounded.
- If you must use **Lists**, use the reliable-queue pattern: `LMOVE`
  (`BLMOVE` for blocking) from a `pending` list into a per-worker `processing`
  list, then `LREM` on success — so a crash leaves the job in `processing` for
  recovery, never lost. Never use bare `LPOP`/`RPOP` for work you can't lose.
- For scheduled/delayed jobs, use a **sorted set** keyed by run-at timestamp;
  a dispatcher `ZRANGEBYSCORE`s due jobs and moves them onto the stream.

## Examples

**Good Example** — Streams consumer group with ack and crash recovery

```bash
# Producer: append a job (auto-trim to ~10k entries).
XADD jobs MAXLEN '~' 10000 '*' type email to user@example.com

# One-time: create the consumer group starting at the beginning.
XGROUP CREATE jobs workers 0 MKSTREAM

# Worker: read new messages for this consumer, then ACK only after success.
XREADGROUP GROUP workers worker-1 COUNT 10 BLOCK 5000 STREAMS jobs '>'
#   ... process message ...
XACK jobs workers 1700000000000-0        # confirm: removes it from pending

# Recovery: reclaim messages idle > 60s from a crashed worker.
XAUTOCLAIM jobs workers worker-1 60000 0
```

**Bad Example** — Pub/Sub as a job queue (loses everything)

```bash
# Producer fires and forgets. If no worker is connected right now, or a worker
# crashes mid-job, the message is gone: no ack, no retry, no replay.
PUBLISH jobs '{"type":"email","to":"user@example.com"}'

# "Worker": receives only messages delivered while connected; a crash after
# receipt but before completion silently drops the job forever.
SUBSCRIBE jobs
```

## Common Mistakes

- Using Pub/Sub for work that must complete — the single most common Redis queue
  mistake; messages vanish on any disconnect.
- Using `LPOP`/`RPOP` (remove-then-process), so a worker crash between pop and
  completion loses the job. Use `BLMOVE` into a processing list instead.
- Never acking Stream messages, so the pending list grows forever and memory
  leaks — or acking *before* processing, which reintroduces the loss-on-crash bug.
- Assuming at-least-once but writing non-idempotent handlers, causing double
  charges/emails on redelivery.
- No dead-letter path, so a permanently-failing message is retried infinitely.
- Letting the stream grow unbounded with no `MAXLEN`/`XTRIM`, exhausting memory.
- Relying on Redis for durability without enabling persistence/replication.

## Production Tips

- Monitor consumer-group **lag** (`XINFO GROUPS`, pending count) and alert when
  it grows — the earliest sign workers are down or too slow.
- Right-size worker `COUNT` and `BLOCK` timeouts; blocking reads avoid busy-poll
  CPU while still reacting quickly.
- For high throughput or strict ordering/durability guarantees beyond Redis's
  reach, evaluate a dedicated broker (Kafka, RabbitMQ, SQS); Redis Streams is
  excellent for many workloads but is not a full replacement for all of them.

## AI Review Checklist

- Is the workload using Streams (or the reliable List pattern), not Pub/Sub, for
  work that must not be lost?
- Is every message acknowledged (`XACK`/`LREM`) only *after* successful
  processing?
- Is there crash recovery (`XCLAIM`/`XAUTOCLAIM` or a processing list) for
  messages orphaned by dead workers?
- Are consumers idempotent, given at-least-once redelivery?
- Is there a dead-letter path with a bounded retry count?
- Is stream/queue growth bounded (`MAXLEN`/`XTRIM`)?
- Is Redis persistence/replication configured to match the durability the queue
  promises?

## Related

- `knowledge/redis/08-streams.md`
- `knowledge/redis/09-pub-sub.md`
- `knowledge/redis/04-lists.md`
- `knowledge/redis/17-distributed-locks.md`
- `knowledge/redis/20-persistence.md`
