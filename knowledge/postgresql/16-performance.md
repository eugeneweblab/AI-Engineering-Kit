---
id: postgresql/16-performance
topic: postgresql
slug: performance
title: "PostgreSQL Performance"
type: doc
order: 16
status: ready
tags: [postgresql, performance, pg_stat_statements, OFFSET, EXPLAIN, auto_explain, pg_stat_activity, CONCURRENTLY, high, index, load]
related: [postgresql/04-indexes, postgresql/05-query-planner, postgresql/17-monitoring, postgresql/20-vacuum, postgresql/27-tuning]
when_to_use: "Read before optimizing a slow query, adding an index, or diagnosing high database load in PostgreSQL."
---
# PostgreSQL Performance

## Purpose

This document defines how to make PostgreSQL queries and workloads fast: reading plans,
indexing correctly, avoiding N+1 and full scans, controlling connections, and knowing
when the bottleneck is the query versus the configuration. It is written so an agent can
diagnose and fix a performance problem from evidence, not guesswork.

Performance work overlaps with [indexes](04-indexes.md), the [query planner](05-query-planner.md),
[monitoring](17-monitoring.md), and [vacuum](20-vacuum.md). This doc is the method that
ties them together: measure, find the real bottleneck, fix that, re-measure.

## Why It Matters

Database performance decides whether the whole application feels fast or falls over under
load, and it is where most scaling incidents actually originate. The trap is that
performance is deeply counter-intuitive: developers add indexes that are never used, tune
config that was never the bottleneck, and "optimize" queries by guessing. Every wrong fix
costs time and often adds write overhead or bloat while the real problem persists. Because
PostgreSQL exposes exactly what it is doing — `EXPLAIN (ANALYZE, BUFFERS)`,
`pg_stat_statements`, wait events — the discipline is to *measure first* and change one
thing at a time, so improvements are proven, not hoped for.

## Core Principles

- **Measure before you change anything.** Use `EXPLAIN (ANALYZE, BUFFERS)` for a single
  query and `pg_stat_statements` for the workload. Optimizing without a measured
  bottleneck is guessing.
- **Optimize the workload, not the worst single query.** The query worth fixing is the one
  with the highest *total* time (frequency × per-call cost), which `pg_stat_statements`
  ranks — not the scariest one-off.
- **Most slow queries are missing or wrong indexes.** A sequential scan on a large table
  in a hot path is the first thing to check. But an index has a write cost, so index for
  real access patterns, not speculatively.
- **Row counts drive plan choice; keep statistics fresh.** The planner picks plans from
  `ANALYZE` estimates. Stale stats cause bad plans. A huge gap between estimated and actual
  rows in `EXPLAIN ANALYZE` points straight at the problem.
- **Connections are a scarce, expensive resource.** Each connection is a backend process.
  Thousands of direct connections crush the server; use a pooler and cap concurrency.

## Best Practices

- Read plans with `EXPLAIN (ANALYZE, BUFFERS)` and compare **estimated vs actual rows**;
  a large mismatch means stale stats, a bad correlation assumption, or a missing extended
  statistic.
- Index for the access pattern: **composite index column order = equality columns first,
  then range/sort column**; add a covering `INCLUDE` clause to enable index-only scans.
- Use **partial indexes** (`WHERE status = 'active'`) for skewed predicates — smaller,
  cheaper to maintain, and often faster than a full index.
- Put a **connection pooler** (PgBouncer, or the app framework's pool) in front of the
  database; size the pool to roughly `cores × 2–4`, not to the number of app instances.
- Fetch related data with a **join or a single batched query**, never a query per row
  (N+1). N+1 is the most common application-level performance bug.
- Select only the columns you need; `SELECT *` defeats index-only scans and ships dead
  bytes over the wire.
- Keep autovacuum healthy — table bloat and stale stats degrade every plan (see
  [vacuum](20-vacuum.md)); a "sudden" slowdown with no query change is often bloat.
- Use `LIMIT` with keyset (seek) pagination for large result sets; `OFFSET 100000` scans
  and discards 100k rows every page.

## Examples

**Good Example** — index built from a measured plan, verified

```sql
-- 1. Measure: the plan shows a Seq Scan and estimated 12 vs actual 480,000 rows.
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, total FROM orders WHERE customer_id = 42 AND status = 'open';

-- 2. Index the real predicate: equality columns, ordered, covering the selected columns.
CREATE INDEX CONCURRENTLY idx_orders_customer_status
  ON orders (customer_id, status) INCLUDE (id, total);  -- CONCURRENTLY: no write lock in prod

-- 3. Re-measure: plan is now an Index Only Scan, actual rows ~= estimated. Improvement proven.
```

**Bad Example** — guessing, and a query pattern that cannot scale

```sql
-- Added "just in case", never validated against a plan; adds write cost for nothing.
CREATE INDEX ON orders (created_at);
CREATE INDEX ON orders (updated_at);
CREATE INDEX ON orders (status);   -- low-selectivity single column: planner ignores it

```

The application then does N+1 instead of one query:

```ts
for (const c of customers) {                       // 10k customers
  await db.query('SELECT * FROM orders WHERE customer_id = $1', [c.id]); // 10k round trips
}
```

The fix is one set-based query plus the composite index:

```sql
SELECT * FROM orders WHERE customer_id = ANY($1);
```

## Common Mistakes

- Tuning configuration or adding indexes before measuring where time actually goes.
- Fixing the scariest single query instead of the highest *total*-time query.
- Adding speculative indexes that are never used, paying write overhead for no read gain.
- N+1 query patterns from ORMs — one query per row instead of a join or batch.
- `SELECT *` in hot paths, defeating index-only scans and moving dead bytes.
- `OFFSET`-based pagination on large tables, re-scanning discarded rows every page.
- Thousands of direct connections with no pooler, so the server thrashes on process
  scheduling and memory.
- Ignoring stale statistics and bloat, then blaming the query for a planner that has bad
  estimates.

## Production Tips

- Enable `pg_stat_statements` and review the top queries by total time weekly; regressions
  show up there before users complain.
- Set `log_min_duration_statement` (e.g. 500ms) to capture slow queries with their
  parameters for offline `EXPLAIN`.
- Use `auto_explain` in staging to capture plans of slow queries automatically without
  reproducing them by hand.
- Watch `pg_stat_activity` **wait events**: `LWLock`/`Lock` waits mean contention,
  `IO` waits mean the working set does not fit in cache — different fixes entirely.

## AI Review Checklist

- Was the change driven by a measured plan (`EXPLAIN ANALYZE`) or `pg_stat_statements`,
  not a guess?
- Do estimated and actual row counts roughly agree (stats are fresh)?
- Are new indexes justified by a real access pattern, and built `CONCURRENTLY` in prod?
- Is composite-index column order equality-then-range, with `INCLUDE` where index-only
  scans help?
- Are there any N+1 patterns that should be a single joined/batched query?
- Is there a connection pooler with a sane pool size?
- Is large-result pagination keyset-based rather than large `OFFSET`?

## Related

- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/05-query-planner.md`
- `knowledge/postgresql/17-monitoring.md`
- `knowledge/postgresql/20-vacuum.md`
- `knowledge/postgresql/27-tuning.md`
