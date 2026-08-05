---
id: redis/08-streams
topic: redis
slug: streams
title: "Streams"
type: doc
order: 8
status: ready
tags: [redis, streams]
related: [redis/09-pub-sub, redis/16-message-queues, redis/06-sorted-sets, redis/12-expiration, redis/100-common-antipatterns]
when_to_use: "Read before building an event log, a durable work queue, or any consumer that must not lose messages on restart."
---
# Streams

## Purpose

This document defines how to use the Redis **stream** (`XADD`, consumer groups): an
append-only log of entries, each with an auto-generated ID and a set of field-value pairs.
It is written so an agent can build a durable, replayable message pipeline where consumers
can crash and resume without losing or double-processing work.

A stream is the right tool when you need **persistence, replay, and at-least-once delivery**.
Unlike [pub/sub](09-pub-sub.md), a stream keeps its entries after delivery, so a consumer
that was offline can catch up. Unlike a [list](04-lists.md)-as-queue, consumer groups track
per-consumer progress and let multiple workers share a stream without stepping on each other.

## Why It Matters

Teams reach for pub/sub or a list to build a work queue, then discover the hard way that
pub/sub drops messages for anyone not connected and a list gives no delivery tracking. When
a worker crashes mid-job with a list-based queue, the message is simply gone. Streams exist
precisely to close this gap: an entry stays in the stream until you trim it, a consumer
group remembers exactly which entries each consumer has claimed but not yet acknowledged,
and a crashed worker's pending entries can be reclaimed by another. The cost of getting this
wrong is silent data loss in production — the queue looks healthy while messages vanish.

## Core Principles

- **Entries are immutable and ordered by ID.** IDs are `<ms>-<seq>`, monotonically
  increasing. `XADD stream * field value` lets Redis assign the ID; capture the returned ID.
- **Consumer groups give at-least-once delivery.** `XREADGROUP` hands an entry to one
  consumer in the group and records it as *pending* until that consumer calls `XACK`.
- **Unacknowledged work is recoverable.** The Pending Entries List (PEL) tracks delivered-
  but-not-acked entries. `XPENDING` inspects it; `XCLAIM`/`XAUTOCLAIM` reassign stale ones
  from a dead consumer to a live one.
- **Streams grow forever unless trimmed.** There is no automatic eviction. Use `XADD ...
  MAXLEN` or `MINID`, or periodic `XTRIM`, or the stream will exhaust memory.
- **At-least-once, not exactly-once.** A consumer can process an entry and crash before
  `XACK`. Make processing **idempotent** so redelivery is safe.

## Best Practices

- Create the group with `XGROUP CREATE mystream mygroup $ MKSTREAM`. `$` starts at new
  messages; use `0` to consume all history. `MKSTREAM` creates the stream if absent.
- Read with `XREADGROUP GROUP g c COUNT 10 BLOCK 5000 STREAMS mystream >`. The `>` means
  "new, never-delivered entries." Block instead of busy-polling.
- **Acknowledge only after successful processing:** `XACK mystream g <id>`. Ack-before-work
  turns a crash into lost data; ack-after-work turns it into safe redelivery.
- Recover stuck work with `XAUTOCLAIM mystream g c <min-idle-ms> 0` on a schedule, so entries
  stranded by a dead consumer get reprocessed. Track a delivery count and route poison
  messages (repeatedly failing) to a dead-letter stream.
- Bound the stream at write time: `XADD mystream MAXLEN ~ 100000 * ...`. The `~` (approximate)
  trim is far cheaper than exact and is almost always what you want.
- Make consumers idempotent: key side effects on the entry ID or a business key so a
  redelivered entry is a no-op.
- Use `XINFO STREAM`/`XINFO GROUPS` and `XPENDING` in monitoring to watch lag and PEL size.

## Examples

**Good Example** — consumer group, work-then-ack, bounded stream

```redis
# Bounded append: ~ keeps the stream near 100k entries cheaply. Capture the returned ID.
XADD orders MAXLEN ~ 100000 * type "checkout" order_id "9921"

# One-time group setup: start at new messages, create stream if missing.
XGROUP CREATE orders workers $ MKSTREAM

# Worker loop: block for new entries delivered only to this consumer.
XREADGROUP GROUP workers worker-1 COUNT 10 BLOCK 5000 STREAMS orders >
# ... process the entry (idempotent on order_id) ...
# ACK only AFTER success — a crash before this leaves the entry pending for reclaim.
XACK orders workers 1700000000000-0
```

**Bad Example** — pub/sub as a durable queue, and ack-before-work

```redis
# Pub/sub delivers ONLY to currently-connected subscribers. A worker that is
# restarting or lagging never sees this message — silent, permanent loss.
PUBLISH orders '{"type":"checkout","order_id":"9921"}'

# Even with a stream, acking before processing loses the entry on a crash:
XREADGROUP GROUP workers worker-1 STREAMS orders >
XACK orders workers 1700000000000-0   # acked, now not in PEL...
# ... process here — if the worker dies, the entry is gone and unrecoverable.
```

## Common Mistakes

- Using [pub/sub](09-pub-sub.md) when you need durability — offline subscribers lose messages.
- Calling `XACK` before the work completes, so a crash between ack and completion loses data.
- Never trimming the stream, letting it grow until Redis runs out of memory.
- No `XAUTOCLAIM`/`XCLAIM` recovery, so entries a dead consumer claimed stay pending forever.
- Assuming exactly-once delivery and making side effects non-idempotent.
- Reading with `>` and also expecting to see history — use `0` (or a specific ID) to replay.
- Ignoring the PEL, so poison messages retry forever with no dead-letter path.

## Production Tips

- Alarm on PEL size and consumer idle time (`XPENDING`, `XINFO GROUPS`) — a growing PEL means
  consumers are failing to ack.
- Run a reclaimer that `XAUTOCLAIM`s entries idle longer than a threshold and dead-letters
  those whose delivery count exceeds a limit.
- Prefer `MAXLEN ~` (approximate) trimming; exact trimming scans and can stall under load.
- Deleting acked entries does not remove them from other groups' history — trim by policy,
  and remember a stream is shared state across all its groups.

## AI Review Checklist

- Is a stream (durable, replayable) used where messages must survive consumer downtime?
- Are consumers reading via a consumer group with `XREADGROUP`, not a plain `XREAD` loop?
- Is `XACK` called only after successful processing, never before?
- Is there an `XAUTOCLAIM`/`XCLAIM` path to recover entries from dead consumers?
- Is the stream bounded with `MAXLEN`/`MINID` trimming so it cannot grow unbounded?
- Is processing idempotent, given at-least-once (not exactly-once) delivery?
- Is there a dead-letter path for entries that repeatedly fail?

## Related

- `knowledge/redis/09-pub-sub.md`
- `knowledge/redis/16-message-queues.md`
- `knowledge/redis/06-sorted-sets.md`
- `knowledge/redis/12-expiration.md`
- `knowledge/redis/100-common-antipatterns.md`
