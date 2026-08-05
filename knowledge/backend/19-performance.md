---
id: backend/19-performance
topic: backend
slug: performance
title: "Backend Performance"
type: doc
order: 19
status: ready
tags: [backend, performance]
related: [backend/13-caching, backend/18-database-design, backend/20-scalability, backend/22-observability, backend/16-background-jobs]
when_to_use: "Read before optimizing an endpoint, chasing a latency regression, or when a query or handler is measurably too slow."
---
# Backend Performance

## Purpose

This document defines how to make backend code fast: measuring before changing,
finding the real bottleneck, and applying the fixes that matter (query shape, N+1,
concurrency, caching). It is written so an agent optimizes based on evidence rather than
guessing, and does not trade correctness for speed.

Performance is a feature with a budget, not an afterthought. The goal is not "as fast as
possible" but "fast enough against a stated target" — a p99 latency, a throughput number
— reached by removing the largest cost first.

## Why It Matters

Latency compounds: a service that is slow under light load falls over under real load,
turning a performance problem into an availability outage. Users abandon slow requests,
and slow requests hold connections, threads, and database locks open longer, starving
everyone else. Yet most optimization effort is wasted because it targets code that was
never the bottleneck. The discipline that matters is measuring first — otherwise you pay
the cost of added complexity (harder-to-read code, a cache to invalidate) for no gain.

## Core Principles

- **Measure before you optimize.** Profile the real workload and find where time actually
  goes. Intuition about hot paths is wrong often enough that acting on it is a bug.
- **Optimize the dominant cost.** If the database is 90% of the request, a faster loop
  changes nothing. Fix the biggest slice; ignore the rest.
- **The fastest work is work you don't do.** Removing a query, a serialization, or a
  redundant call beats speeding it up. Do less before doing it faster.
- **Latency is usually I/O, not CPU.** In backend services the bottleneck is almost always
  a database round trip, a network call, or a lock — not arithmetic.
- **Never trade correctness for speed silently.** An optimization that changes behavior
  under concurrency or edge cases is a bug, however fast.

## Best Practices

- Set an explicit target (e.g. "p99 < 200ms at 500 rps") before optimizing, and measure
  against it. Without a target, optimization has no stopping condition.
- Eliminate N+1 queries: fetch related rows in one query (`JOIN` or `WHERE id IN (...)`),
  not one query per parent row. This is the single most common backend slowdown.
- Select only the columns you need; `SELECT *` pulls unused blobs over the wire and defeats
  covering indexes.
- Paginate every unbounded list with keyset (seek) pagination, not `OFFSET`; large offsets
  scan and discard rows.
- Cache read-heavy, expensive, rarely-changing results — but only after measuring, and with
  an explicit invalidation plan (see [caching](13-caching.md)).
- Do slow, non-critical work (email, thumbnails, exports) in a
  [background job](16-background-jobs.md), off the request path.
- Use connection pooling and set query timeouts; a runaway query must fail, not hang forever.
- Batch external calls and set concurrency limits so a burst does not open thousands of
  simultaneous connections.

## Examples

**Good Example** — one query, bounded, only needed columns

```ts
// Fetch all authors for the page in a single round trip, keyed by id.
const posts = await db.query(
  `SELECT id, title, author_id FROM posts
   WHERE published = true
   ORDER BY id DESC
   LIMIT $1`, [pageSize],                       // keyset pagination, bounded result
);
const authorIds = [...new Set(posts.map(p => p.author_id))];
const authors = await db.query(
  `SELECT id, name FROM authors WHERE id = ANY($1)`, [authorIds], // one query, not N
);
```

**Bad Example** — N+1 queries hidden inside a loop

```ts
const posts = await db.query(`SELECT * FROM posts`); // unbounded + SELECT *
for (const post of posts) {
  // One extra query per post: 1 + N round trips. Fine at 10 rows, fatal at 10,000.
  post.author = await db.query(
    `SELECT * FROM authors WHERE id = $1`, [post.author_id],
  );
}
```

## Common Mistakes

- Optimizing before profiling, so effort lands on code that was never the bottleneck.
- N+1 queries introduced by ORM lazy-loading inside a loop or serializer.
- Unbounded queries and `OFFSET` pagination that scan more rows as data grows.
- Caching without an invalidation strategy, trading a speed bug for a correctness bug.
- Micro-optimizing CPU while the request spends 95% of its time waiting on I/O.
- No query timeouts, so one slow query holds a pooled connection and cascades to an outage.
- Measuring average latency only; the p99 is where users actually suffer.

## Production Tips

- Track p50/p95/p99 latency per endpoint and the database time within each request; averages
  hide the tail (see [observability](22-observability.md)).
- Keep a slow-query log and review `EXPLAIN (ANALYZE)` for the worst offenders regularly.
- Load-test against production-like data volume; performance cliffs appear only at scale.
- Add a request-level timeout budget so a slow dependency degrades gracefully instead of
  hanging the whole request.

## AI Review Checklist

- Is there a measurement (profile, timing, `EXPLAIN`) justifying this optimization?
- Are there any N+1 query patterns in loops, serializers, or ORM lazy-loads?
- Are list endpoints paginated with bounded, keyset-based queries?
- Does the change avoid `SELECT *` and fetch only needed columns?
- Does any added cache have a clear invalidation strategy and TTL?
- Are query timeouts and connection pooling configured?
- Is p99 (not just average) latency the metric being optimized against a target?

## Related

- `knowledge/backend/13-caching.md`
- `knowledge/backend/18-database-design.md`
- `knowledge/backend/20-scalability.md`
- `knowledge/backend/22-observability.md`
- `knowledge/backend/16-background-jobs.md`
