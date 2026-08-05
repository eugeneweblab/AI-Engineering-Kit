---
id: performance/28-real-world-patterns
topic: performance
slug: real-world-patterns
title: "Real World Performance Patterns"
type: doc
order: 28
status: ready
tags: [performance, real-world-patterns, OFFSET, get_product, fetch_one, append]
related: [performance/08-caching, performance/14-api-performance, performance/09-lazy-loading, performance/21-scalability, performance/27-best-practices]
when_to_use: "Read when designing a feature that must stay fast under real load and you need a proven pattern for it."
---
# Real World Performance Patterns

## Purpose

This document catalogs battle-tested patterns for keeping systems fast under real
production load, and — just as important — when *not* to use them. It is written so an
agent can reach for the right pattern for a concrete situation (hot reads, expensive
writes, bursty traffic, large lists) instead of improvising.

Each pattern is a named trade-off. The skill is matching the pattern to the workload's
actual shape, not applying all of them everywhere.

## Why It Matters

Performance patterns encode hard-won solutions to recurring load problems: a cache for
read-heavy data, a queue for spiky writes, pagination for large sets. Applied to the right
workload they deliver order-of-magnitude wins. Applied to the wrong one they add
complexity and new failure modes — a cache in front of write-heavy data just adds
invalidation bugs; a queue on a synchronous flow just adds latency. Knowing the pattern
*and* its preconditions is what separates a real improvement from cargo-culting.

## Core Principles

- **Match the pattern to the read/write ratio.** Caching and read replicas pay off on
  read-heavy data; queues and batching pay off on write-heavy or bursty flows.
- **Every pattern is a trade-off.** Caching trades freshness for speed; async trades
  immediacy for throughput; denormalization trades write cost for read speed. State the
  cost before adopting it.
- **Absorb bursts, do not drop them.** Queues, buffers, and backpressure convert traffic
  spikes into steady work instead of overload. See [scalability](21-scalability.md).
- **Fail fast and degrade gracefully.** Timeouts, circuit breakers, and fallbacks keep one
  slow dependency from cascading into a full outage.
- **Bound resource usage under load.** Connection pools, concurrency limits, and rate
  limits protect the system when demand exceeds capacity.

## Best Practices

- **Cache-aside for hot reads:** read cache, on miss load from source and populate, with a
  TTL. Use for read-heavy, tolerably-stale data. See [caching](08-caching.md).
- **Async offload for expensive writes:** enqueue slow or deferrable work (emails, media
  processing, exports) and return immediately; a worker pool drains the queue.
- **Batching / debouncing for chatty operations:** coalesce many small writes or calls into
  one (bulk insert, batched API call) to amortize per-operation overhead.
- **Keyset (cursor) pagination for large lists:** page by `WHERE id > last_seen LIMIT n`,
  not `OFFSET`, which scans and skips rows and degrades linearly on deep pages.
- **Read replicas / CQRS for read-heavy load:** serve reads from replicas or a
  read-optimized projection so they do not contend with writes.
- **Circuit breaker + timeout + fallback** on every remote dependency so a slow service is
  shed quickly instead of exhausting threads and cascading.
- **Precompute and denormalize** expensive aggregates when reads vastly outnumber writes;
  update them on write instead of computing per read.
- **Backpressure and bounded queues:** reject or shed load at the edge rather than letting
  an unbounded queue grow until the process runs out of memory.

## Examples

**Good Example** — cache-aside with TTL for read-heavy data

```python
async def get_product(pid):
    cached = await cache.get(f"product:{pid}")
    if cached is not None:
        return cached                              # hot path: no DB hit
    product = await db.fetch_one("SELECT * FROM products WHERE id=$1", pid)
    # TTL bounds staleness; the write path also deletes this key on update.
    await cache.set(f"product:{pid}", product, ttl=300)
    return product
    # Right pattern: products are read far more than written and can be
    # seconds-stale. The cost (bounded staleness) is stated and acceptable.
```

**Bad Example** — caching write-heavy data, unbounded queue

```python
async def record_event(event):
    # Anti-pattern 1: caching a write-heavy counter -> constant invalidation,
    # stale reads, and no actual read benefit.
    count = await cache.get("event_count") or 0
    await cache.set("event_count", count + 1)      # lost updates under concurrency

    # Anti-pattern 2: an unbounded in-memory queue as a "buffer".
    PENDING.append(event)                          # grows without limit under a burst
    # A traffic spike fills PENDING until the process OOMs. A bounded queue
    # with backpressure (reject/shed on full) was the right pattern here.
```

## Common Mistakes

- Caching write-heavy or must-be-fresh data, buying invalidation bugs for no read win.
- Using `OFFSET` pagination on deep pages, which scans and skips ever more rows.
- Adding async/queues to a flow that must be synchronous, adding latency and complexity.
- Unbounded queues or buffers that turn a traffic burst into an out-of-memory crash.
- Calling a remote dependency with no timeout, so one slow service exhausts the pool.
- Denormalizing on write-heavy data, where the write amplification outweighs read savings.
- Applying every pattern by default instead of matching one to the workload's shape.

## Production Tips

- Instrument each pattern's key metric: cache hit rate, queue depth/age, breaker state,
  replica lag. A pattern you cannot observe is a pattern you cannot trust.
- Load-test the pattern under the burst it is meant to absorb, not just steady state — many
  patterns only reveal their failure mode near saturation. See [scalability](21-scalability.md).

## AI Review Checklist

- Does the pattern match the workload's read/write ratio and freshness needs?
- Is the trade-off (staleness, latency, write cost) stated and acceptable here?
- Are queues and buffers bounded, with backpressure or shedding when full?
- Does pagination use a cursor/keyset rather than a large `OFFSET`?
- Does every remote call have a timeout, and hot dependencies a circuit breaker?
- Is the pattern's health metric (hit rate, queue depth, replica lag) monitored?

## Related

- `knowledge/performance/08-caching.md`
- `knowledge/performance/14-api-performance.md`
- `knowledge/performance/09-lazy-loading.md`
- `knowledge/performance/21-scalability.md`
- `knowledge/performance/27-best-practices.md`
