---
id: performance/27-best-practices
topic: performance
slug: best-practices
title: "Performance Best Practices"
type: doc
order: 27
status: ready
tags: [performance, best-practices, fetch_one, list, append, LIMIT]
related: [performance/24-optimization-workflow, performance/08-caching, performance/13-database-performance, performance/23-performance-budget, performance/100-common-antipatterns]
when_to_use: "Read before writing performance-sensitive code to apply the defaults that prevent most slowdowns."
---
# Performance Best Practices

## Purpose

This document collects the durable, technology-agnostic rules that prevent most
performance problems before they start. It is written so an agent writes code that is fast
by default — good algorithmic choices, bounded work, minimized I/O — without prematurely
optimizing or sacrificing clarity.

These are defaults, not micro-tricks. Follow them and most systems stay well inside budget
without a dedicated optimization pass.

## Why It Matters

The largest performance wins are decisions made while writing the code, not tuning added
later: the data structure, the query shape, whether work is batched or per-item, what runs
on the request path. A poor choice here (an O(n^2) loop, an N+1 query, a synchronous call
inside a hot loop) is cheap to avoid now and expensive to retrofit under load. Applying
good defaults is also cheaper than optimizing: it needs no profiler and adds no complexity,
because correct-by-construction code is usually the simple code too.

## Core Principles

- **Complexity dominates at scale.** Pick the right algorithm and data structure first; a
  better Big-O beats any constant-factor tweak once inputs grow.
- **The fastest work is work you skip.** Do less: cache, memoize, paginate, filter at the
  source, and short-circuit early. Every avoided operation is free.
- **I/O is the usual bottleneck, not CPU.** Batch queries, reuse connections, and
  parallelize independent I/O. A network round trip dwarfs most computation.
- **Bound everything.** Every loop, query, buffer, and payload needs a limit. Unbounded
  work is a latency and memory incident waiting for a large input.
- **Measure before micro-optimizing.** Apply these defaults freely, but do not hand-tune a
  specific line without a profile — see [optimization workflow](24-optimization-workflow.md).

## Best Practices

- Choose data structures by access pattern: a set/map for membership and lookup (O(1)),
  not a linear scan of a list (O(n)) inside a loop.
- Eliminate **N+1** access: fetch related data in one batched query or call, not one per
  item. See [database performance](13-database-performance.md).
- **Paginate and stream** unbounded result sets; never load a whole table or an unbounded
  list into memory.
- Move non-essential work **off the request path** — enqueue it, defer it, or run it in a
  background job. Users wait only for what they need now.
- **Parallelize independent I/O** (fan-out with a bounded concurrency limit) instead of
  awaiting calls serially.
- **Cache deliberately** with an explicit key, TTL, and invalidation plan; an unmanaged
  cache trades a speed bug for a correctness bug. See [caching](08-caching.md).
- Push filtering, sorting, and aggregation **down to the data store**, which is indexed
  for it, rather than pulling rows and doing it in application code.
- Reuse expensive resources (connection pools, compiled regexes, HTTP clients) instead of
  recreating them per request.
- Keep the **payload small**: select only needed columns/fields, compress responses, and
  avoid over-fetching.

## Examples

**Good Example** — O(1) lookups, batched I/O, bounded parallelism

```python
async def enrich(order_ids):
    # One batched query instead of N (kills the N+1) ...
    orders = await db.fetch("SELECT * FROM orders WHERE id = ANY($1)", order_ids)
    user_ids = {o.user_id for o in orders}            # set: dedupe + O(1) membership
    users = await db.fetch("SELECT * FROM users WHERE id = ANY($1)", list(user_ids))
    by_id = {u.id: u for u in users}                  # map for O(1) join in code

    # ... and independent enrichment fanned out with a concurrency cap.
    sem = asyncio.Semaphore(10)                        # bound: never unleash N calls
    async def score(o):
        async with sem: return await risk_service.score(o)
    scores = await asyncio.gather(*(score(o) for o in orders))
    # strict=True: a length mismatch is a bug, not something to silently truncate.
    return [(o, by_id[o.user_id], s) for o, s in zip(orders, scores, strict=True)]
```

**Bad Example** — N+1, O(n) scans, serial I/O, unbounded

```python
async def enrich(order_ids):
    results = []
    orders = await db.fetch("SELECT * FROM orders")     # loads the whole table
    for oid in order_ids:
        order = next(o for o in orders if o.id == oid)  # O(n) scan inside the loop -> O(n^2)
        user = await db.fetch_one(                      # N+1: one query per order
            "SELECT * FROM users WHERE id = $1", order.user_id
        )
        score = await risk_service.score(order)         # serial, awaited one at a time
        results.append((order, user, score))
    return results
```

## Common Mistakes

- Reaching for micro-optimizations while an O(n^2) loop or N+1 query dominates.
- Loading unbounded result sets into memory instead of paginating or streaming.
- Doing filtering/sorting in application code that the database could do while indexed.
- Awaiting independent I/O serially instead of fanning out with a concurrency bound.
- Recreating connections, clients, or compiled regexes on every call.
- Adding a cache with no TTL or invalidation, turning staleness into a correctness bug.
- Doing deferrable work (emails, thumbnails, analytics) synchronously on the request path.

## Production Tips

- Set explicit limits (query `LIMIT`, page size, request timeout, max payload) as defaults
  so a large input degrades gracefully instead of taking the service down.
- Add a lightweight budget check in CI for hot endpoints so a regression is caught in
  review, not production. See [performance budget](23-performance-budget.md).

## AI Review Checklist

- Are algorithm and data structure chosen for the access pattern (no O(n) scan in a loop)?
- Is related data fetched in a batch, not one query per item (no N+1)?
- Are all result sets, loops, buffers, and payloads bounded?
- Is deferrable work moved off the request path?
- Is independent I/O parallelized with a concurrency limit?
- Are filtering/sorting pushed down to the data store?
- Does every cache have an explicit key, TTL, and invalidation plan?

## Related

- `knowledge/performance/24-optimization-workflow.md`
- `knowledge/performance/08-caching.md`
- `knowledge/performance/13-database-performance.md`
- `knowledge/performance/23-performance-budget.md`
- `knowledge/performance/100-common-antipatterns.md`
