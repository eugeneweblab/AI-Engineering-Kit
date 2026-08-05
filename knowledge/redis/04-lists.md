---
id: redis/04-lists
topic: redis
slug: lists
title: "Redis Lists"
type: doc
order: 4
status: ready
tags: [redis, lists, RPOP, BLMOVE, LPOP, LREM, LRANGE, processing]
related: [redis/02-data-types, redis/05-sets, redis/08-streams, redis/16-message-queues]
when_to_use: "Read before using Redis lists for queues, stacks, or recent-item feeds, or when choosing between a list and a stream."
---
# Redis Lists

## Purpose

This document covers the Redis list: an ordered sequence of strings, implemented as a
linked list, supporting fast pushes and pops at both ends. Lists back simple queues
(FIFO), stacks (LIFO), and bounded "most recent N" feeds. It also explains the blocking
pop commands that make lists usable as work queues, and when to reach for a
[stream](08-streams.md) instead.

## Why It Matters

Lists are the go-to for queues, and the go-to source of two production bugs. First,
end operations (`LPUSH`/`RPUSH`/`LPOP`/`RPOP`) are `O(1)`, but *indexed* and *range*
operations (`LINDEX`, `LRANGE`, `LINSERT`, `LREM`) are `O(N)` — treating a list like an
array and scanning it blocks the single thread. Second, naive consumers busy-poll with
`RPOP` in a loop, burning CPU and round trips; the fix, `BRPOP`, blocks server-side until
work arrives. Knowing which end to use and which pop to call is the whole game.

## Core Principles

- **Push and pop at the ends; that is what lists are `O(1)` at.** Use `LPUSH`+`RPOP` for
  FIFO or `LPUSH`+`LPOP` for LIFO. Avoid random access.
- **Block instead of poll.** For a work queue, consume with `BRPOP`/`BLMOVE` so the
  server wakes the client when an item arrives — no busy loop.
- **Keep lists bounded.** Use `LTRIM` after `LPUSH` to cap "recent N" feeds; an unbounded
  producer with a slow consumer grows the list until Redis runs out of memory.
- **Use `LMOVE`/`BLMOVE` for reliable queues.** Atomically move an item to a
  processing list so a crashed worker doesn't lose the job.
- **Lists have no dedup and no ack.** If you need uniqueness use a [set](05-sets.md);
  if you need consumer groups and acknowledgements use a [stream](08-streams.md).

## Best Practices

- Model a queue as producer `LPUSH` + consumer `BRPOP`; pick one direction and keep it
  consistent so ordering is predictable.
- Cap recent-item feeds atomically: `LPUSH feed item` then `LTRIM feed 0 99` to keep the
  newest 100. The cost is dropping old items; the benefit is bounded memory.
- For at-least-once processing, use `BLMOVE queue processing LEFT RIGHT` so the job sits in
  a processing list until the worker `LREM`s it on success; a crashed worker's job can be
  recovered from `processing`.
- Set a timeout on blocking pops (`BRPOP key 5`) so consumers can shut down cleanly and
  don't hang forever.
- Prefer a [stream](08-streams.md) when you need multiple consumer groups, replay, or
  explicit acks — lists give none of these.

## Examples

**Good Example** — reliable FIFO queue with blocking consumer and cap

```redis
# Producer: enqueue at the left, and bound a parallel "recent" view to 1000 items.
LPUSH jobs "job-1001"
LPUSH recent:jobs "job-1001"
LTRIM recent:jobs 0 999        # O(1)-ish trim keeps memory bounded

# Consumer: block up to 5s, and atomically move the job to a processing list
# so it survives a worker crash (at-least-once delivery).
BLMOVE jobs processing RIGHT LEFT 5
# ... do the work ...
LREM processing 1 "job-1001"   # ack: remove exactly one matching entry on success
```

**Bad Example** — busy-poll, unbounded growth, O(N) scans

```redis
# Busy-poll: hammers Redis with round trips and burns CPU when the queue is empty.
RPOP jobs                      # returns nil, so the app loops and calls again immediately

# Unbounded: fast producer, slow consumer → list grows until OOM.
LPUSH feed "event"             # no LTRIM anywhere

# Treating a list like an array: O(N) scan blocks every other client.
LRANGE jobs 0 -1               # pulls the entire list to the client to "find" an item
LREM jobs 0 "job-1001"         # O(N) search-and-remove across the whole list
```

## Common Mistakes

- Busy-polling with `RPOP` in a loop instead of blocking with `BRPOP`.
- Never trimming, so a producer/consumer speed mismatch fills memory.
- Using `RPOP`/`LPOP` alone for a work queue, so a crash between pop and processing loses
  the job (use `BLMOVE` into a processing list).
- Random access via `LINDEX`/`LRANGE`/`LINSERT` on large lists — `O(N)` and blocking.
- Using a list where uniqueness matters (duplicates pile up) — use a set.
- Building consumer groups and acks by hand on a list instead of using a stream.

## Production Tips

- Alert on queue depth (`LLEN`); a steadily growing list means the consumer can't keep up.
- Run a reaper that re-queues stale entries left in the `processing` list by crashed
  workers (compare against a per-job timestamp).
- Size blocking-pop timeouts to balance shutdown responsiveness against reconnection churn.

## AI Review Checklist

- Are pushes/pops confined to the list ends (`O(1)`), with no `O(N)` indexed/range ops on
  large lists?
- Do consumers block with `BRPOP`/`BLMOVE` instead of busy-polling `RPOP`?
- Is every unbounded list capped with `LTRIM` or otherwise drained?
- Does the queue survive worker crashes (processing list + ack), if delivery must be
  reliable?
- Is a stream used instead where consumer groups, acks, or replay are required?

## Related

- `knowledge/redis/02-data-types.md`
- `knowledge/redis/05-sets.md`
- `knowledge/redis/08-streams.md`
- `knowledge/redis/16-message-queues.md`
