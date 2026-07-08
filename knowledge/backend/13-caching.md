---
id: backend/13-caching
topic: backend
slug: caching
title: "Caching"
type: doc
order: 13
status: ready
tags: [backend, caching]
related: [backend/19-performance, backend/20-scalability, backend/18-database-design, backend/14-events, backend/17-transactions]
when_to_use: "Read before adding a cache in front of a database, API, or expensive computation."
---
# Caching

## Purpose

This document defines how to add caching to a backend safely. It covers what may be
cached, where the cache lives (in-process, distributed, HTTP), how entries expire and
get invalidated, and how to avoid the failure modes that make a cache worse than no
cache. The goal is that an agent can introduce a cache that improves latency and load
*without* serving stale or wrong data.

Caching is a correctness problem disguised as a performance optimization. The read
speedup is easy; keeping cached data consistent with the source of truth is the hard part.

## Why It Matters

A cache trades freshness for speed and cost. Done well, it removes load from your
database and cuts tail latency. Done badly, it becomes the top source of "works on my
machine but wrong in production" bugs: a user updates their email, sees the old one, and
files a support ticket you cannot reproduce because your cache is warm and theirs is
stale. Worse, an unbounded or poorly-keyed cache can leak one user's data to another, or
fall over under a thundering herd. Because a cache silently sits between correctness and
performance, it must be designed, not sprinkled in.

## Core Principles

- **The database is the source of truth; the cache is a disposable copy.** The system
  must be correct if the cache is empty, cold, or entirely down. Never store data that
  exists *only* in the cache.
- **Every entry must have a bounded lifetime.** A TTL is the safety net that guarantees
  staleness self-heals even when explicit invalidation is missed. No TTL, no cache.
- **Invalidation is the hard part — design it first.** Decide, before writing the read
  path, exactly which writes invalidate which keys. Stale data is a caching bug, not a
  caching feature.
- **Key on everything the value depends on.** Include tenant/user id, version, and locale
  in the key. A key that is too broad serves one user's data to another.
- **Cache the expensive and the stable.** Caching cheap or rapidly-changing data adds
  complexity and staleness risk for little gain.

## Best Practices

- Prefer **cache-aside (lazy loading)**: on read, check cache; on miss, load from the
  source, populate the cache, return. It is simple and the cache only holds data that is
  actually requested.
- Set a **TTL on every key**, sized to how stale the data may acceptably be. Add small
  random **jitter** to TTLs so many keys do not expire at the same instant (herd).
- On write, **invalidate (delete) the key rather than updating it in place**. Delete-then-
  reload avoids a race where two writers leave the cache holding an older value.
- Protect against **stampedes**: use a per-key lock / single-flight so one request
  recomputes a hot key while others wait, instead of all hitting the database at once.
- **Cache negative results** (not-found) briefly to blunt lookups for keys that do not
  exist, but keep that TTL short so newly-created rows appear quickly.
- Choose the tier deliberately: **in-process** cache for tiny, hot, host-local data;
  **distributed** cache (Redis/Memcached) when multiple instances must share state and
  invalidation. In-process caches on N hosts mean N independent staleness windows.
- For HTTP, use `Cache-Control`, `ETag`, and conditional requests instead of re-inventing
  caching in application code.
- **Never cache per-user data under a shared key**, and never cache secrets or auth
  decisions unless the key fully captures the principal.

## Examples

**Good Example** — cache-aside with TTL, jitter, single-flight, and invalidation

```ts
async function getUser(id: string): Promise<User> {
  const key = `user:v2:${id}`;             // versioned key: schema change -> new namespace
  const hit = await redis.get(key);
  if (hit) return JSON.parse(hit);

  // Single-flight: one caller loads, others wait, preventing a stampede on a hot key.
  return singleFlight(key, async () => {
    const user = await db.users.findById(id);         // source of truth
    if (!user) throw new NotFoundError(id);
    const ttl = 300 + Math.floor(Math.random() * 60); // 5min + jitter to avoid herd
    await redis.set(key, JSON.stringify(user), "EX", ttl);
    return user;
  });
}

async function updateEmail(id: string, email: string) {
  await db.users.update(id, { email });
  await redis.del(`user:v2:${id}`);        // invalidate on write; next read repopulates
}
```

**Bad Example** — no TTL, stale-forever, and a cross-user key leak

```ts
const cache = new Map<string, User>();     // in-process, unbounded, never expires

async function getCurrentUser(req: Request): Promise<User> {
  // Key omits the user id: every request shares one entry -> data leaks across users.
  if (cache.has("currentUser")) return cache.get("currentUser")!;
  const user = await db.users.findById(req.userId);
  cache.set("currentUser", user);          // no TTL: grows forever, never invalidated
  return user;
}

async function updateEmail(id: string, email: string) {
  await db.users.update(id, { email });
  // No invalidation: cache serves the old email indefinitely.
}
```

## Common Mistakes

- Caching without a TTL, so a missed invalidation means data is stale forever.
- Keys that omit tenant/user/version, leaking or mixing data across principals.
- Updating a cached value in place instead of deleting it, creating write races.
- Treating the cache as durable storage — losing data when it evicts or restarts.
- No stampede protection, so a cold hot-key floods the database on expiry.
- In-process caches on a multi-instance service, giving each host a different view.
- Caching authorization decisions under keys that don't include the current user.

## Production Tips

- Track **hit rate, miss rate, and eviction rate**. A low hit rate means the cache costs
  more than it saves; high evictions mean it is undersized.
- Configure a **max-memory eviction policy** (e.g. `allkeys-lru`) so the cache never
  fills and starts refusing writes.
- Add a **kill switch** to bypass the cache entirely; if it serves bad data you need to
  disable it without a deploy.
- Version keys (`user:v2:`) so a schema or serialization change invalidates the whole
  namespace at once instead of leaving poisoned entries.

## AI Review Checklist

- Does every cache entry have a TTL, and is the system correct with a cold/empty cache?
- Do keys include tenant/user/version so data cannot leak or collide across principals?
- Is there an explicit invalidation on the write path for each cached read?
- Does invalidation delete the key rather than mutating it in place?
- Is there stampede protection (single-flight or lock) on hot keys?
- Is a distributed cache used when multiple instances must share invalidation?
- Is nothing stored *only* in the cache with no source of truth behind it?

## Related

- `knowledge/backend/19-performance.md`
- `knowledge/backend/20-scalability.md`
- `knowledge/backend/18-database-design.md`
- `knowledge/backend/14-events.md`
- `knowledge/backend/17-transactions.md`
