---
id: architecture/19-caching-strategies
topic: architecture
slug: caching-strategies
title: "Caching Strategies"
type: doc
order: 19
status: ready
tags: [architecture, caching-strategies, get_product, save, random]
related: [architecture/14-performance, architecture/13-scalability, architecture/21-distributed-systems, architecture/09-microservices, architecture/18-observability]
when_to_use: "Read before adding a cache layer, or when reads are slow, the database is hot, or stale data is causing bugs."
---
# Caching Strategies

## Purpose

This document defines how to cache data safely: what to cache, where, how to invalidate it,
and how to avoid the failure modes that make caches worse than no cache at all. It is written
so an agent can add a cache that improves latency without silently serving wrong data.

A cache trades freshness and correctness for speed and cost. Every cache decision is really a
decision about *how stale is acceptable* for a given piece of data. If you cannot answer that
question for the data in front of you, you are not ready to cache it.

## Why It Matters

Caching is one of the highest-leverage performance tools and one of the most common sources
of subtle, intermittent bugs. A correct cache can cut read latency and database load by an
order of magnitude. A broken one serves a deleted user's data, shows the wrong price, or
takes the whole system down when it restarts empty and every request stampedes the database
at once. The two hard problems — invalidation and cold-start behavior — are exactly the parts
that are invisible in a demo and catastrophic in production. Treat a cache as a correctness
surface, not just an optimization.

## Core Principles

- **Cache is an optimization, not a source of truth.** The system must stay correct if the
  cache is empty, cold, or wiped. Never store the only copy of data in a cache.
- **Every entry needs a TTL and an invalidation story.** Decide up front how an entry becomes
  wrong and how it gets removed. "Cache forever" is a bug waiting for a deploy.
- **Prefer bounded staleness you chose over surprise staleness you didn't.** A deliberate
  60-second TTL is safe; an entry that lingers because nothing invalidates it is a landmine.
- **Protect the origin from the cache's failure modes.** Design against stampedes, hot keys,
  and the thundering herd on restart — these hit precisely when load is highest.
- **Cache the expensive and the reused.** Caching a cheap or rarely-read value adds
  invalidation risk for no gain.

## Best Practices

- Pick a pattern deliberately: **cache-aside** (app reads cache, loads on miss, most common),
  **read-through/write-through** (cache library owns the load/store), or **write-behind**
  (async flush, fast writes, risk of loss). Match it to your consistency needs.
- Set a TTL on **every** key. Add small random jitter to TTLs so a batch of keys does not all
  expire in the same second and stampede the origin.
- Prevent cache stampede with a per-key lock or `singleflight`: on a miss, one caller recomputes
  while others wait, instead of thousands hitting the database simultaneously.
- Invalidate on write. On update or delete, evict (or update) the key in the same transaction
  boundary as the data change, so a stale read cannot outlive the write.
- Namespace and version cache keys (`user:v2:{id}`). A schema change bumps the version and
  retires every old entry without a manual flush.
- Cache negative results (a "not found") briefly to stop repeated lookups for missing keys
  from hammering the database — but keep that TTL short so creates appear quickly.
- Track hit ratio, evictions, and latency. A cache you cannot measure is a cache you cannot
  trust; a falling hit ratio is an early warning.

## Examples

**Good Example** — cache-aside with stampede protection and write invalidation

```python
async def get_product(pid: str) -> Product:
    if hit := await cache.get(f"product:v1:{pid}"):
        return hit
    # singleflight: only one coroutine loads a given key on a miss; the rest
    # await the same result, so a cold key cannot stampede the database.
    async with singleflight(f"product:v1:{pid}"):
        if hit := await cache.get(f"product:v1:{pid}"):   # re-check after lock
            return hit
        product = await db.load_product(pid)
        # TTL + jitter: entries don't all expire in the same second.
        await cache.set(f"product:v1:{pid}", product, ttl=300 + random(0, 30))
        return product

async def update_product(p: Product) -> None:
    await db.save(p)
    await cache.delete(f"product:v1:{p.id}")   # invalidate in step with the write
```

**Bad Example** — no TTL, no invalidation, no stampede guard

```python
async def get_product(pid: str) -> Product:
    if hit := await cache.get(pid):
        return hit
    product = await db.load_product(pid)
    await cache.set(pid, product)   # no TTL -> entry never expires, goes stale forever
    return product                  # every cold miss hits the DB directly -> stampede

async def update_product(p: Product) -> None:
    await db.save(p)                # cache still holds the OLD product -> stale reads
```

## Common Mistakes

- Setting no TTL, so entries go permanently stale after the underlying data changes.
- Forgetting to invalidate on write, serving deleted or edited data indefinitely.
- No stampede protection, so a cold or expired hot key floods the origin at once.
- Caching per-user private data under a shared key, leaking one user's data to another.
- Treating the cache as the source of truth, so a flush loses data.
- Unbounded key cardinality with no eviction policy, driving the cache out of memory.
- Caching before measuring, adding complexity to a read that was never the bottleneck.

## Production Tips

- On planned cache-cluster restarts, pre-warm hot keys or ramp traffic; an empty cache under
  full load is a self-inflicted outage (the thundering herd).
- Choose an eviction policy that matches access shape (LRU for recency, LFU for skew) and
  alert when eviction rate spikes — it means the cache is undersized.
- For multi-region systems, prefer per-region caches with short TTLs over one global cache;
  cross-region invalidation is slow and races the read.

## AI Review Checklist

- Does every cache key have an explicit TTL, with jitter to avoid synchronized expiry?
- Is there an invalidation path on every write/delete of the underlying data?
- Is the origin protected from stampedes (singleflight or per-key lock) on a miss?
- Does the system remain correct if the cache is empty or wiped?
- Are private/per-user values keyed so they cannot leak across users?
- Are keys namespaced and versioned so a schema change retires old entries?
- Are hit ratio, evictions, and latency measured?

## Related

- `knowledge/architecture/14-performance.md`
- `knowledge/architecture/13-scalability.md`
- `knowledge/architecture/21-distributed-systems.md`
- `knowledge/architecture/09-microservices.md`
- `knowledge/architecture/18-observability.md`
