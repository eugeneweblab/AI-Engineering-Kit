---
id: performance/08-caching
topic: performance
slug: caching
title: "Performance Caching"
type: doc
order: 8
status: ready
tags: [performance, caching]
related: [performance/07-loading, performance/05-network, performance/14-api-performance, performance/13-database-performance, performance/11-images]
when_to_use: "Read before adding, configuring, or reviewing any cache — HTTP headers, CDN, application, or database layer."
---
# Performance Caching

## Purpose

This document defines how to serve a result without recomputing or refetching it:
HTTP caching, CDNs, application caches, and invalidation. It is written so an agent can
add a cache that makes the system faster *and* still correct.

Caching trades freshness and memory for speed. Done right, it removes work entirely.
Done wrong, it serves stale or leaked data — a correctness bug, not a performance one.
Every cache decision is really two decisions: *what to store* and *when to stop trusting it*.

## Why It Matters

The cheapest request is the one that never reaches your server; the next cheapest never
reaches your database. Caching is the highest-leverage performance tool because it cuts
whole layers of work — network round trips, query execution, template rendering — at a
stroke. But it is also the most dangerous: a cache that keys or invalidates incorrectly
can serve one user's private data to another, or pin a bug in place long after the fix
shipped. "There are only two hard things in computer science" is about this. Treat cache
correctness with the same rigor as the data it caches.

## Core Principles

- **Cache is an optimization, never a source of truth.** The system must be correct
  with the cache emptied at any moment. If it isn't, that's a bug, not a cache.
- **Every entry needs an expiry or an invalidation trigger.** Data with no way to become
  stale-free will eventually be wrong. Decide the staleness bound explicitly.
- **Key on everything that changes the result.** A cache key must include user/tenant,
  locale, permissions, and query params — anything that alters the output. Missing a
  key dimension leaks or mixes data.
- **Never cache per-user data on a shared cache.** Private responses must be marked
  `private`/`no-store` so a CDN or proxy can't serve them to someone else.
- **Prefer immutability over invalidation.** Content-hashed URLs (`app.a1b2c3.js`) can
  cache forever because a change produces a new URL. This sidesteps invalidation entirely.

## Best Practices

- Fingerprint static assets and serve them with `Cache-Control: public, max-age=31536000,
  immutable`. The hash in the filename makes long-lived caching safe.
- Serve HTML and API responses with short or revalidated caching: `no-cache` (revalidate
  every time via ETag) or `max-age` plus `stale-while-revalidate` for a fast-but-fresh
  balance.
- Return and honor `ETag`/`Last-Modified` so conditional requests get a cheap `304 Not
  Modified` instead of re-sending the body.
- Mark user-specific responses `Cache-Control: private, no-store` and add `Vary` on
  headers that change the response (`Accept-Encoding`, `Authorization`).
- For application caches (Redis/Memcached), set a TTL on every key and pick an eviction
  policy (`allkeys-lru`) so the cache can't grow unbounded.
- Guard against cache stampede: use a lock or `stale-while-revalidate` so one miss
  doesn't trigger thousands of simultaneous recomputations.
- Invalidate on write: when the underlying data changes, delete or update the key in the
  same transaction path so readers never see stale data past the write.
- Layer caches deliberately (browser → CDN → app → DB) and know the TTL at each layer;
  the effective staleness is the sum.

## Examples

**Good Example** — correct keys, bounded staleness, safe invalidation

```js
// Key includes tenant + locale so results never leak across boundaries.
const key = `product:${tenantId}:${locale}:${productId}`;

async function getProduct(tenantId, locale, productId) {
  const hit = await redis.get(key);
  if (hit) return JSON.parse(hit);

  const product = await db.products.find(productId);
  // TTL bounds staleness even if an invalidation is ever missed.
  await redis.set(key, JSON.stringify(product), "EX", 300);
  return product;
}

// On write, invalidate in the same path so no reader sees stale data afterward.
async function updateProduct(tenantId, locale, product) {
  await db.products.update(product);
  await redis.del(`product:${tenantId}:${locale}:${product.id}`);
}
```

**Bad Example** — leaky key, unbounded, never invalidated

```js
// Key omits tenant/locale → one tenant's data served to another.
async function getProduct(productId) {
  const hit = await redis.get(`product:${productId}`);
  if (hit) return JSON.parse(hit);

  const product = await db.products.find(productId);
  await redis.set(`product:${productId}`, JSON.stringify(product)); // no TTL: stale forever
  return product;
}
// No invalidation on update → the cache pins old data until eviction, if ever.
```

## Common Mistakes

- Caching per-user or authenticated responses on a shared CDN/proxy (data leak).
- Cache keys that omit a dimension that changes the result (tenant, locale, permission).
- Setting no TTL and no invalidation, so entries go stale silently and forever.
- Long-lived caching of an un-fingerprinted asset, so users get old JS/CSS after a deploy.
- Ignoring `ETag`/conditional requests and re-sending unchanged bodies.
- No stampede protection, so a popular key expiring hammers the origin/database.
- Treating the cache as authoritative — code that breaks when the cache is cold.

## Production Tips

- Track hit rate and eviction rate per cache; a low hit rate means the key is too
  specific or the TTL too short, and eviction spikes mean the cache is undersized.
- Make caches safe to flush: you should be able to clear any cache in production and
  see only a temporary latency bump, never wrong data.
- Version cache keys (`v2:product:...`) so a schema change invalidates old entries
  atomically without a manual purge.

## AI Review Checklist

- Is the system still correct if this cache is emptied at any moment?
- Does every cache key include all dimensions that change the result?
- Does every entry have a TTL or an explicit invalidation trigger?
- Are user-specific responses marked `private`/`no-store` and never on a shared cache?
- Are static assets content-hashed and served `immutable`, HTML/API revalidated?
- Is there stampede protection on hot keys, and a bounded eviction policy?
- Does a write invalidate or update the corresponding cache entry?

## Related

- `knowledge/performance/07-loading.md`
- `knowledge/performance/05-network.md`
- `knowledge/performance/14-api-performance.md`
- `knowledge/performance/13-database-performance.md`
- `knowledge/performance/11-images.md`
