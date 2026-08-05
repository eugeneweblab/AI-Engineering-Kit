---
id: redis/13-caching
topic: redis
slug: caching
title: "Redis Caching"
type: doc
order: 13
status: ready
tags: [redis, caching]
related: [redis/12-expiration, redis/17-distributed-locks, redis/03-strings, redis/23-performance, redis/100-common-antipatterns]
when_to_use: "Read before putting Redis in front of a database or API to cache reads."
---
# Redis Caching

## Purpose

This document defines how to use Redis as a cache in front of a slower system of
record (SQL, an API, a computed result). It covers the read/write patterns,
invalidation, and the failure modes — stampede, staleness, and inconsistency —
that separate a correct cache from a data-corruption bug.

A cache is an optimization, never the source of truth. Every rule here follows
from that: the database owns the data; Redis holds a disposable, expiring copy.

## Why It Matters

Caching is the most common Redis use case and the easiest to get subtly wrong.
The bugs are not crashes — they are *wrong answers served fast*: a user sees a
deleted record, a price that changed an hour ago, or a balance that never
updates. Because the app still responds quickly, these defects hide until a
customer notices.

The other failure mode is operational: a popular key expires, thousands of
requests miss simultaneously, and they all hammer the database at once — a
stampede that can take the origin down. Correct caching means planning for both
staleness and stampede up front, not after the incident.

## Core Principles

- **The database is the source of truth; the cache is disposable.** The system
  must be correct (just slower) if Redis is wiped. Never store data that exists
  only in the cache.
- **Always set a TTL.** Even with active invalidation, a TTL is the backstop that
  bounds how long a bug can serve stale data. A cache entry with no expiry is a
  memory leak waiting to happen.
- **Prefer invalidation over update.** On a write, *delete* the cache key rather
  than trying to write the new value into it. Deleting is idempotent and races
  safely; updating the cache can race with concurrent reads and persist a stale
  value.
- **Cache misses must be safe and cheap.** A miss should transparently fall back
  to the origin and repopulate. Design for the miss, not just the hit.
- **Protect the origin from stampede.** When a hot key misses, prevent a thundering
  herd from all recomputing it at once.

## Best Practices

- Use **cache-aside** (lazy loading) as the default: read cache → on miss, read
  DB → write cache with TTL → return. It keeps the cache populated only with data
  that is actually requested.
- On any write to the DB, **delete** the corresponding cache key(s) inside or
  immediately after the transaction. Do not update-in-place.
- Add **TTL jitter** so related keys don't expire together (see
  [expiration](12-expiration.md)).
- Prevent stampede with a **per-key lock** (a short-lived `SET NX` mutex): the
  first misser recomputes, others briefly wait or serve stale. See
  [distributed locks](17-distributed-locks.md).
- Cache **negative results** (e.g. "not found") with a short TTL to stop repeated
  lookups for missing keys from hitting the DB — but keep that TTL short so
  newly-created records appear quickly.
- Namespace and version keys (`user:v2:42`) so a schema change can invalidate an
  entire class of entries by bumping the version.
- Choose `maxmemory-policy allkeys-lru` (or `allkeys-lfu`) so Redis evicts cold
  cache entries under pressure instead of returning OOM errors.

## Examples

**Good Example** — cache-aside with TTL, stampede lock, delete-on-write

```ts
async function getUser(id: string) {
  const key = `user:${id}`;
  const hit = await redis.get(key);
  if (hit) return JSON.parse(hit);              // fast path

  // Stampede guard: only the lock winner queries the DB.
  const lockKey = `lock:${key}`;
  const gotLock = await redis.set(lockKey, "1", "NX", "EX", 5);
  if (!gotLock) {
    await sleep(50);                            // let the winner fill the cache
    return getUser(id);                         // retry read
  }
  try {
    const user = await db.users.findById(id);
    // TTL is mandatory; jitter avoids synchronized expiry.
    await redis.set(key, JSON.stringify(user), "EX", 300 + rand(0, 60));
    return user;
  } finally {
    await redis.del(lockKey);
  }
}

async function updateUser(id: string, patch: Patch) {
  await db.users.update(id, patch);
  await redis.del(`user:${id}`);                // invalidate, don't rewrite
}
```

**Bad Example** — no TTL, write-through that races, cache as truth

```ts
async function getUser(id: string) {
  const key = `user:${id}`;
  const hit = await redis.get(key);
  if (hit) return JSON.parse(hit);
  const user = await db.users.findById(id);
  await redis.set(key, JSON.stringify(user));   // BUG: no TTL -> stale forever + leak
  return user;
}

async function updateUser(id: string, patch: Patch) {
  await db.users.update(id, patch);
  // BUG: writing the new value can lose a race with a concurrent getUser miss
  // that reads the OLD row and writes it back AFTER this line.
  await redis.set(`user:${id}`, JSON.stringify(patch));
}
```

## Common Mistakes

- Omitting the TTL, so a stale or orphaned entry lives until manual eviction.
- Updating the cache value on write instead of deleting it, creating a
  read-vs-write race that persists stale data.
- No stampede protection, so one hot-key miss floods the database.
- Treating the cache as authoritative — storing data that isn't also in the DB,
  so a flush loses it.
- Caching without a versioned namespace, making a schema change impossible to
  invalidate cleanly.
- Never caching negatives, so lookups for nonexistent keys hit the DB every time
  (a cheap denial-of-service vector).

## Production Tips

- Track `keyspace_hits` / `keyspace_misses` from `INFO stats` to compute hit
  ratio; a falling ratio signals a TTL, key-design, or invalidation problem.
- Alert on origin QPS spikes that correlate with cache-key expiry — the signature
  of a stampede.
- For read-heavy, tolerant-of-slight-staleness workloads, consider Redis
  client-side caching (RESP3 tracking) to cut round trips, but only where a few
  seconds of staleness is acceptable.

## AI Review Checklist

- Does every cache write set a TTL, with jitter on bulk fills?
- Do writes to the DB **delete** the cache key rather than overwrite it?
- Is there stampede protection (lock or equivalent) on hot keys?
- Is the system still correct if Redis is flushed — i.e., is the DB the source of
  truth?
- Are negative/not-found results cached with a short TTL?
- Is `maxmemory-policy` an LRU/LFU eviction policy, not `noeviction`, for a
  pure cache instance?

## Related

- `knowledge/redis/12-expiration.md`
- `knowledge/redis/17-distributed-locks.md`
- `knowledge/redis/03-strings.md`
- `knowledge/redis/23-performance.md`
- `knowledge/redis/100-common-antipatterns.md`
