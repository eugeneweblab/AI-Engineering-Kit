---
id: performance/100-common-antipatterns
topic: performance
slug: common-antipatterns
title: "Performance Common Antipatterns"
type: antipatterns
order: 100
status: ready
tags: [performance, common-antipatterns, EXPLAIN, indexOf, LIMIT]
related: [performance/01-performance-fundamentals, performance/13-database-performance, performance/08-caching, performance/30-engineering-principles, performance/99-ai-review-checklist]
when_to_use: "Read before optimizing a loop, a query, or a cache, to check you are not walking into a known trap."
---
# Performance Common Antipatterns

## Purpose

This document catalogs the recurring performance mistakes an agent is most likely to make or
approve, and for each states *why it is wrong* and *the fix*. These are the patterns that
look reasonable in the moment and cost dearly at scale. Recognizing the shape of a trap is
faster than re-deriving why it hurts, so use this as a lookup during optimization and
[review](99-ai-review-checklist.md).

## Why It Matters

Performance antipatterns hide behind green tests. Each one is correct and fast on fixture
data, so nothing stops it until production scale makes it bite — and by then it is spread
across the codebase by copy-paste. Naming the antipattern is what lets a reviewer reject it
early, while it is still one instance and cheap to undo.

## Measurement Antipatterns

### Optimizing Without Measuring

- **What it is:** Rewriting code believed to be slow, with no profile identifying it as the
  bottleneck.
- **Why it is wrong:** Intuition about hot spots is wrong more often than right. You spend
  effort and add complexity to code that may be under 1% of runtime, while the real cost sits
  untouched (Amdahl's law).
- **The fix:** Profile first ([profiling](16-profiling.md)); optimize the dominant cost;
  prove the win with a before/after number.

### Premature Optimization

- **What it is:** Adding caches, pooling, or hand-tuned concurrency before any measurement
  shows a need.
- **Why it is wrong:** It buys speed you cannot prove with complexity you must maintain and
  debug forever. It often makes the code slower to change and no faster to run.
- **The fix:** Write the simple version, measure it against the [budget](23-performance-budget.md),
  and add complexity only when it misses.

## Data Access Antipatterns

### N+1 Queries

- **What it is:** Loading a list, then issuing one query per item to fetch related data.
- **Why it is wrong:** 100 items become 101 round-trips. Each round-trip is latency the loop
  cannot hide; the pattern is invisible at 10 rows and fatal at 10,000.
- **The fix:** Batch with a single `WHERE id = ANY(...)`, a join, or a data-loader that
  coalesces the fetches (see [database performance](13-database-performance.md)).

### Unbounded Result Sets

- **What it is:** `SELECT *` with no `LIMIT`, or an endpoint that returns every row.
- **Why it is wrong:** Response size and memory grow with the table. It works in test, then
  one large tenant OOMs the process or times out.
- **The fix:** Paginate or cap every list query; select only the columns you use; index the
  filter and sort.

### Missing Index / Full Scan

- **What it is:** Filtering or sorting on an unindexed column on a large table.
- **Why it is wrong:** The database scans every row; latency grows linearly with table size
  while `EXPLAIN` quietly shows a sequential scan.
- **The fix:** Add an index matching the query's filter and sort order; verify with `EXPLAIN`
  (see [query optimization](15-query-optimization.md)).

## Memory & Loop Antipatterns

### Loading Everything Into Memory

- **What it is:** Reading an entire file, table, or API response into a list to process it.
- **Why it is wrong:** Memory scales with input size, so the job that ran on the sample
  dataset OOMs on the real one.
- **The fix:** Stream or paginate — process in chunks with bounded memory.

### Accidental Quadratic Work

- **What it is:** A nested loop or a `list.contains`/`indexOf` inside a loop, turning an O(n)
  task into O(n²).
- **Why it is wrong:** It is imperceptible at n=100 and catastrophic at n=100,000. It is the
  single most common silent scaling bug.
- **The fix:** Use a hash set/map for membership and lookups; hoist invariant work out of the
  loop.

### Repeated Work in a Loop

- **What it is:** Recomputing the same value, recompiling a regex, or re-fetching config on
  every iteration or request.
- **Why it is wrong:** You pay a fixed cost N times for a result that never changes.
- **The fix:** Compute once outside the loop and reuse; memoize pure functions of stable
  inputs.

## Caching & Concurrency Antipatterns

### Cache Without Invalidation

- **What it is:** Caching a value with no TTL and no invalidation on the underlying change.
- **Why it is wrong:** It converts a speed problem into a correctness problem — the system is
  fast and wrong, serving stale data indefinitely.
- **The fix:** Give every cache a TTL or an explicit invalidation tied to the source of
  truth; include every input the result depends on in the key (see [caching](08-caching.md)).

### Cache Stampede

- **What it is:** A hot key expires and thousands of concurrent requests all recompute it at
  once.
- **Why it is wrong:** The cache miss stampedes the backend, causing exactly the overload the
  cache was meant to prevent.
- **The fix:** Single-flight (one recompute, others wait), add jitter to TTLs, or refresh
  ahead of expiry.

### Blocking the Request Path

- **What it is:** Doing slow synchronous I/O — an email send, a report build, a third-party
  call without a timeout — inside the request.
- **Why it is wrong:** One slow dependency stalls the thread/connection; under load the pool
  exhausts and the whole service hangs, not just that feature.
- **The fix:** Add timeouts to every outbound call; move non-critical work to a background
  job or queue; isolate dependencies behind a circuit breaker.

## Example — the N+1 trap and its fix

```python
# Bad: one query per order -> 1 + N round-trips. Fine on 5 orders in a test,
# 30 seconds of latency on a customer with 5,000 orders.
orders = db.query("SELECT id FROM orders WHERE user_id = %s", (uid,))
for o in orders:
    o.items = db.query("SELECT * FROM items WHERE order_id = %s", (o.id,))  # N+1

# Good: two queries total, grouped in memory. Latency independent of order count.
orders = db.query("SELECT id FROM orders WHERE user_id = %s", (uid,))
ids = [o.id for o in orders]
items = db.query("SELECT * FROM items WHERE order_id = ANY(%s)", (ids,))  # one batched call
by_order = group_by(items, key=lambda i: i.order_id)
for o in orders:
    o.items = by_order.get(o.id, [])
```

## Common Mistakes

- Calling a change "optimized" with no profile and no before/after number.
- Shipping an N+1 or an unindexed query because it was fast on fixture data.
- Adding a cache with no invalidation, trading a speed bug for a staleness bug.
- Parallelizing a path that is wait-bound, adding races without removing the wait.
- Testing at toy data sizes, so quadratic and unbounded patterns never surface.

## AI Review Checklist

- Does any list operation issue a query per item? (N+1 — reject.)
- Can any query or response return unbounded rows or bytes? (Unbounded set.)
- Is there a nested loop or in-loop lookup that is secretly O(n²)?
- Does any cache lack a TTL or invalidation, or an incomplete key? (Stale-data risk.)
- Does any outbound call on the request path lack a timeout?
- Is the change justified by a measurement, or is it premature optimization?

## Related

- `knowledge/performance/01-performance-fundamentals.md`
- `knowledge/performance/13-database-performance.md`
- `knowledge/performance/08-caching.md`
- `knowledge/performance/30-engineering-principles.md`
- `knowledge/performance/99-ai-review-checklist.md`
