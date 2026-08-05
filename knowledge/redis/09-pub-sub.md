---
id: redis/09-pub-sub
topic: redis
slug: pub-sub
title: "Pub Sub"
type: doc
order: 9
status: ready
tags: [redis, pub-sub, PUBLISH, SUBSCRIBE]
related: [redis/08-streams, redis/16-message-queues, redis/19-clustering, redis/23-performance, redis/100-common-antipatterns]
when_to_use: "Read before using PUBLISH/SUBSCRIBE for notifications, and to decide whether you actually need a stream instead."
---
# Pub Sub

## Purpose

This document defines how to use Redis **publish/subscribe** (`PUBLISH`, `SUBSCRIBE`,
`PSUBSCRIBE`): a fire-and-forget messaging mechanism where publishers send to channels and
every currently-connected subscriber receives a copy. It is written so an agent chooses
pub/sub only for **ephemeral, best-effort fan-out** — and reaches for a
[stream](08-streams.md) whenever delivery must be guaranteed.

Pub/sub is a broadcast, not a queue. There is no storage, no acknowledgement, no replay. A
message exists only in the instant it is delivered to whoever happens to be listening. Use
it for live notifications, cache-invalidation signals, and real-time UI updates where a
missed message is harmless.

## Why It Matters

Pub/sub is the most misused Redis feature. Its API looks like a message queue, so teams
build order processing, job dispatch, and event sourcing on it — then lose messages every
time a subscriber restarts, deploys, or briefly disconnects. There is no buffer: if no one
is subscribed at the moment of `PUBLISH`, the message is gone with no error. This is by
design and cannot be tuned away. Understanding the guarantee (there is none) is the whole
point: use pub/sub where loss is acceptable, and never where it is not. The blast radius of
confusing it with a durable queue is silent, unrecoverable data loss.

## Core Principles

- **At-most-once, best-effort.** Delivered only to subscribers connected at publish time.
  No persistence, no replay, no ack. A slow or absent subscriber simply misses messages.
- **A subscribed connection is dedicated.** In classic (RESP2) pub/sub, a connection in
  `SUBSCRIBE` mode can only run subscribe/unsubscribe commands. Use a separate connection
  for normal commands.
- **Pattern subscriptions cost more.** `PSUBSCRIBE news.*` matches every published channel
  against every pattern — powerful but `O(patterns)` per publish. Prefer explicit channels.
- **Plain pub/sub does not fan out across a cluster.** In Redis Cluster, use
  **`SPUBLISH`/`SSUBSCRIBE`** (sharded pub/sub) or messages only reach the shard that
  received them (older versions broadcast to all nodes, wasting bandwidth).
- **Publisher throughput is bounded by the slowest subscriber.** A slow consumer grows the
  server-side output buffer; hitting `client-output-buffer-limit` disconnects it.

## Best Practices

- Use pub/sub only for signals where loss is acceptable: live dashboards, presence, cache
  invalidation, "something changed, go re-fetch" pings.
- If you need durability, delivery tracking, or replay, use a [stream](08-streams.md) with
  consumer groups instead — do not try to bolt reliability onto pub/sub.
- Keep one connection for subscribing and a separate one for publishing/other commands;
  most client libraries enforce this, but be explicit in pooled setups.
- Prefer many specific channels over broad `PSUBSCRIBE` patterns to keep per-publish cost low.
- In Redis Cluster, use `SPUBLISH`/`SSUBSCRIBE` so messages are delivered efficiently within
  the correct shard.
- Treat every message as a hint, not a source of truth: on receipt, re-read authoritative
  state rather than trusting the payload to have arrived exactly once.
- Handle reconnects: on a dropped subscriber connection, re-subscribe and re-sync state,
  because anything published during the gap is lost.

## Examples

**Good Example** — pub/sub for a loss-tolerant invalidation signal

```bash
# Publisher: "user 42 changed, drop your cached copy." If a node misses this,
# it just serves a slightly stale cache until the next TTL — acceptable loss.
PUBLISH cache.invalidate "user:42"

# Subscriber (on its OWN dedicated connection): react by re-reading source of truth.
SUBSCRIBE cache.invalidate
# on message -> evict local cache for user:42, then lazily reload from DB on next read
```

**Bad Example** — pub/sub as a job queue

```bash
# Publisher dispatches a job. If the worker is deploying/restarting right now,
# NO subscriber is connected — the job is silently dropped, no error, no retry.
PUBLISH jobs '{"task":"send_email","to":"ada@x.io"}'

# Worker: any downtime = permanent message loss. There is no backlog to catch up on.
SUBSCRIBE jobs
# a restart between these two lines loses every job published in the gap
```

## Common Mistakes

- Using pub/sub as a durable queue or event log — messages vanish for any offline subscriber.
- Assuming messages are buffered for reconnecting clients. They are not.
- Running normal commands on a connection that is in subscribe mode (RESP2), causing errors.
- Relying on plain `PUBLISH` in Redis Cluster and wondering why some nodes never receive it —
  use sharded `SPUBLISH`.
- Overusing `PSUBSCRIBE` patterns and paying per-publish matching cost at scale.
- Trusting the payload as exactly-once truth instead of re-reading authoritative state.
- No reconnect/re-subscribe logic, so a blip permanently desyncs the subscriber.

## Production Tips

- Monitor `client-output-buffer-limit` for pubsub clients; a slow subscriber that overflows
  its buffer is force-disconnected and loses its subscription.
- Track publish rate and subscriber count; a channel with zero subscribers means every
  message is being discarded — often a sign of a misconfigured consumer.
- For real-time features that must tolerate reconnects, pair a stream (for catch-up on
  connect) with pub/sub (for low-latency live updates), rather than pub/sub alone.

## AI Review Checklist

- Is pub/sub used only for loss-tolerant, ephemeral signals — never as a durable queue?
- If durability, replay, or acks are required, is a [stream](08-streams.md) used instead?
- Is subscribing done on a dedicated connection, separate from publishing/other commands?
- In a cluster, is sharded `SPUBLISH`/`SSUBSCRIBE` used where cross-node delivery matters?
- Do subscribers re-subscribe and re-sync state after a reconnect?
- Are messages treated as hints that trigger a re-read, not as exactly-once truth?

## Related

- `knowledge/redis/08-streams.md`
- `knowledge/redis/16-message-queues.md`
- `knowledge/redis/19-clustering.md`
- `knowledge/redis/23-performance.md`
- `knowledge/redis/100-common-antipatterns.md`
