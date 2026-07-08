---
id: mysql/14-performance
topic: mysql
slug: performance
title: "Performance"
type: doc
order: 14
status: ready
tags: [mysql, performance]
related: [mysql/04-indexes, mysql/05-query-optimization, mysql/02-configuration, mysql/15-monitoring]
when_to_use: "Read before tuning a slow MySQL workload, sizing server memory, or reviewing schema and query changes for scale."
---
# Performance

## Purpose

This document defines how to make MySQL fast and keep it fast under load: indexing
for access patterns, sizing the InnoDB buffer pool, managing connections, and
avoiding the query shapes that do not scale. It is written so an agent can tune a
workload with measurement rather than folklore.

Index mechanics and query rewriting have dedicated documents —
[indexes](04-indexes.md) and [query optimization](05-query-optimization.md). This
file is the system-level view: how memory, connections, and schema choices combine
to determine throughput and latency.

## Why It Matters

Database performance is where most application slowness ultimately lives, and it
degrades non-linearly. A query that scans 10k rows is fine in staging and melts
the server at 10M rows in production — the plan was wrong all along, it just
didn't hurt yet. MySQL performance work is high-leverage but easy to get wrong by
guessing: teams add indexes that are never used, or raise connection limits and
make contention worse. The discipline is to measure first, change one thing, and
verify with the same measurement.

## Core Principles

- **Index for the query, not the table.** The right index turns a table scan into
  a lookup; the wrong one just costs write throughput and disk. Design indexes from
  actual `WHERE`/`JOIN`/`ORDER BY` clauses.
- **Memory is the biggest lever.** For InnoDB, the buffer pool caching hot data and
  indexes in RAM is the single largest factor in read latency. Undersize it and
  every query hits disk.
- **Fewer round trips beat faster ones.** N+1 queries, per-row loops, and chatty ORMs
  dominate latency. Batch and set-based operations win.
- **Bound every result set.** Always constrain rows with `WHERE` and `LIMIT`;
  unbounded `SELECT *` and offset pagination degrade as data grows.
- **Measure, then change.** Use `EXPLAIN ANALYZE` and the performance schema to find
  the real bottleneck. Never tune a config you have not proven is the limit.

## Best Practices

- Size `innodb_buffer_pool_size` to hold the working set — commonly 60-75% of RAM on
  a dedicated server. This is the first knob to check on a slow read workload.
- Add covering and composite indexes matching your predicates; order composite index
  columns by equality-first, then range, then sort (`WHERE a=? AND b>? ORDER BY c`).
- Verify plans with `EXPLAIN ANALYZE`: watch for `type: ALL` (full scan), large
  `rows` estimates, `Using filesort`, and `Using temporary`.
- Use keyset (seek) pagination — `WHERE id > :last ORDER BY id LIMIT n` — instead of
  `LIMIT n OFFSET m`, which re-scans skipped rows and slows down as offset grows.
- Select only needed columns; `SELECT *` defeats covering indexes and moves dead weight.
- Use a connection pool sized to a few times the CPU count, not thousands of raw
  connections. Excess connections cause context-switching and lock contention, not speed.
- Keep transactions short; long-running or idle-in-transaction sessions hold locks
  and undo, bloating history and stalling others. See [transactions](06-transactions.md).
- Batch writes (`INSERT ... VALUES (...),(...)`, multi-row `UPDATE`) and prefer
  set-based SQL over row-by-row application loops.

## Examples

**Good Example** — composite index + keyset pagination, proven by EXPLAIN

```sql
-- Index matches the access pattern: filter by status, order by id.
CREATE INDEX idx_orders_status_id ON orders (status, id);

-- Keyset pagination: each page is an index range, O(page size) regardless of depth.
SELECT id, customer_id, total
FROM orders
WHERE status = 'shipped' AND id > 100000   -- 100000 = last id from previous page
ORDER BY id
LIMIT 50;

-- Confirm the plan uses the index and not a scan or filesort.
EXPLAIN ANALYZE SELECT id, customer_id, total
FROM orders WHERE status = 'shipped' AND id > 100000 ORDER BY id LIMIT 50;
```

**Bad Example** — unindexed filter, offset pagination, select-star

```sql
-- No index on status: full table scan. OFFSET 100000 reads and throws away
-- 100000 rows every page, getting slower the deeper you go. SELECT * hauls
-- every column over the wire even though three are used.
SELECT *
FROM orders
WHERE status = 'shipped'
ORDER BY id
LIMIT 50 OFFSET 100000;
```

## Common Mistakes

- Raising `max_connections` to mask a pool/contention problem, worsening it.
- Adding indexes speculatively; unused indexes slow every write and waste buffer pool.
- `LIMIT ... OFFSET` deep pagination that re-scans skipped rows.
- `SELECT *` that prevents index-only (covering) scans.
- N+1 query loops in the application instead of a single set-based query or `JOIN`.
- Wrapping an indexed column in a function (`WHERE DATE(created_at)=...`), which
  disables the index — filter on a range against the raw column instead.
- Leaving the buffer pool at the tiny default (128M) on a server with plenty of RAM.

## Production Tips

- Enable the slow query log (`long_query_time` low, e.g. 0.5s) and mine it with
  `pt-query-digest` or the `performance_schema` statement summaries to find the top
  offenders by total time, not just per-call time. See [monitoring](15-monitoring.md).
- Re-check `EXPLAIN` plans after data growth; a plan that was fine at 10k rows can
  flip to a scan at 10M as statistics change.
- Load-test at production data volume, not an empty schema — most plan regressions
  only appear at scale.

## AI Review Checklist

- Does every hot query have a supporting index verified by `EXPLAIN ANALYZE`?
- Is the InnoDB buffer pool sized to the working set rather than left at default?
- Does pagination use keyset/seek rather than deep `OFFSET`?
- Do queries select only needed columns, not `SELECT *`?
- Are there N+1 loops that should be a single set-based query or join?
- Are indexed columns used raw in predicates (no wrapping functions)?
- Are connections pooled and bounded rather than raised to mask contention?

## Related

- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/02-configuration.md`
- `knowledge/mysql/15-monitoring.md`
