---
id: databases/08-query-optimization
topic: databases
slug: query-optimization
title: "Query Optimization"
type: doc
order: 8
status: ready
tags: [databases, query-optimization]
related: [databases/07-indexing, databases/20-performance, databases/06-schema-design, databases/21-monitoring, databases/10-concurrency]
when_to_use: "Read before optimizing a slow query, reviewing an N+1 pattern, or reading a query plan."
---
# Query Optimization

## Purpose

This document defines how to make queries fast: how to read a query plan, avoid the
common pathologies (N+1, `SELECT *`, unbounded results), and change SQL or indexes
so the engine picks an efficient plan. It is written so an agent can diagnose a slow
query from evidence rather than guesswork.

Query optimization depends on [indexing](07-indexing.md) — the plan can only be as
good as the access paths available — and feeds [performance](20-performance.md) and
[monitoring](21-monitoring.md) at the system level.

## Why It Matters

A single bad query can take down a healthy database. A missing index or an N+1 loop
that is invisible in development becomes a full-table scan run thousands of times per
second in production, saturating CPU and I/O for every other query too. The failure
is non-linear: everything is fine until the table crosses a size threshold, then the
whole system falls over at once.

Optimization also has to be *measured*, not intuited. Query planners are cost-based
and adapt to data distribution; the "obviously faster" rewrite is often identical or
worse. The discipline is: reproduce, read the plan, change one thing, re-measure.

## Core Principles

- **The query plan is the source of truth.** Never optimize by intuition. Run
  `EXPLAIN (ANALYZE, BUFFERS)` and read what the engine actually does.
- **Filter and paginate at the database.** Fetch only the rows and columns you need.
  Moving work into application memory is almost always slower and unbounded.
- **One query, not N.** Fetching related rows in a loop (N+1) multiplies round-trips.
  Use a join, a batched `IN (...)`, or the ORM's eager-load.
- **Sargable predicates win.** Keep indexed columns bare on one side of the
  comparison. Wrapping a column in a function (`lower(email)`, `date(created_at)`)
  defeats its index.
- **Measure at production scale.** A plan on 1k rows tells you nothing about 10M.
  Test against representative data volume and distribution.

## Best Practices

- Start every investigation with `EXPLAIN ANALYZE`. Look for `Seq Scan` on large
  tables, `Nested Loop` over many rows, high `rows` estimates far from actual, and
  spills to disk (`Sort Method: external`).
- Select explicit columns, never `SELECT *`. Extra columns bloat network transfer and
  prevent index-only scans.
- Always bound result sets with `LIMIT` and keyset (cursor) pagination. `OFFSET`
  pagination re-scans and skips rows, degrading linearly as the offset grows.
- Eliminate N+1 by eager-loading associations or batching IDs into one `IN` query.
- Rewrite non-sargable predicates: store a normalized column or use an expression
  index instead of `WHERE lower(email) = ?`.
- Prefer `EXISTS`/`JOIN` over `IN (subquery)` when the subquery is large; prefer
  `EXISTS` over `COUNT(*) > 0` when you only need existence.
- Keep table statistics fresh (`ANALYZE`/auto-vacuum). Stale stats give the planner
  wrong row estimates and bad plans.
- Use parameterized queries — they let the engine reuse plans and prevent injection.

## Examples

**Good Example** — one bounded, sargable, index-friendly query

```sql
-- Fetch a customer's recent paid orders, one round-trip, keyset paginated.
SELECT id, total_cents, created_at
FROM orders
WHERE customer_id = $1
  AND status = 'paid'
  AND created_at < $2          -- keyset cursor: no OFFSET re-scan
ORDER BY created_at DESC
LIMIT 20;
-- Uses idx_orders (customer_id, status, created_at DESC): Index Scan, no Sort.
```

**Bad Example** — N+1, unbounded, non-sargable, over-fetching

```python
# One query to list customers...
customers = db.query("SELECT * FROM customers")          # SELECT *, unbounded
for c in customers:
    # ...then one query PER customer: the N+1 explosion.
    orders = db.query(
        "SELECT * FROM orders "
        "WHERE YEAR(created_at) = 2026 "                 # function on column: no index used
        "AND customer_id = %s", c.id)
    c.total = sum(o.total_cents for o in orders)         # aggregation the DB should do
# 1 + N queries, full scans each, summing in Python instead of SUM() in SQL.
```

## Common Mistakes

- Optimizing without reading the plan — changing SQL blindly and hoping.
- N+1 queries hidden behind an ORM's lazy loading.
- `SELECT *` pulling columns (and blobs) the caller never uses.
- Unbounded queries with no `LIMIT`, or `OFFSET` pagination on deep pages.
- Non-sargable predicates: functions, leading wildcards (`LIKE '%x'`), or type casts
  on indexed columns.
- Doing filtering, joining, or aggregation in application code instead of SQL.
- Stale statistics producing wildly wrong row estimates and bad join orders.

## Production Tips

- Enable slow-query logging (`log_min_duration_statement`) and review the top
  queries by total time, not just per-call time — a fast query run a million times
  can outweigh one slow one.
- Watch for plan regressions after data growth or a stats change; a query that was
  an index scan can silently flip to a seq scan.
- Long-running read queries can hold snapshots and interact with
  [concurrency](10-concurrency.md); keep transactions short.

## AI Review Checklist

- Was the query diagnosed with `EXPLAIN ANALYZE`, not intuition?
- Does it select explicit columns and bound results with `LIMIT`?
- Is pagination keyset-based, not deep `OFFSET`?
- Are there any N+1 loops that should be a single join or batched query?
- Are all predicates sargable (no functions/casts on indexed columns)?
- Is filtering and aggregation pushed into SQL rather than application memory?
- Was it measured at representative data volume?

## Related

- `knowledge/databases/07-indexing.md`
- `knowledge/databases/20-performance.md`
- `knowledge/databases/06-schema-design.md`
- `knowledge/databases/21-monitoring.md`
- `knowledge/databases/10-concurrency.md`
