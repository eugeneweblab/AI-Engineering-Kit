---
id: sql/17-query-optimization
topic: sql
slug: query-optimization
title: "SQL Query Optimization"
type: doc
order: 17
status: ready
tags: [sql, query-optimization, EXISTS, trip, OFFSET, DISTINCT, pg_stat_statements]
related: [sql/16-query-planning, sql/15-indexes, sql/05-joins, sql/23-performance, sql/100-common-antipatterns]
when_to_use: "Read before rewriting a slow query, tuning a hot read path, or reviewing SQL for performance."
---
# SQL Query Optimization

## Purpose

This document defines how to make a query faster once the plan (see
[query planning](16-query-planning.md)) has shown you where the time goes: reducing rows
early, using indexes effectively, fixing N+1 access, and choosing set-based over row-by-row
work. It is written so an agent optimizes with evidence and preserves correctness.

Optimization is not "make the SQL clever." It is "do less work": scan fewer rows, fetch
fewer columns, run fewer round trips, and let indexes do the filtering. Every change is
justified by a plan and validated by measuring the plan again.

## Why It Matters

Slow queries do not fail — they degrade, and they degrade worst under the load you most
need to survive. A query that fans out an N+1 pattern issues one call per row and turns a
page render into thousands of round trips; a query that selects unneeded columns or filters
late moves gigabytes to discard most of it. These are the top causes of database CPU and
latency incidents, and every one is fixable in the query. The bar: never optimize by
guessing, and never trade correctness for speed.

## Core Principles

- **Filter early, project narrowly.** Push `WHERE` predicates down so the smallest possible
  set of rows and columns flows through the plan. `SELECT *` on a wide table is wasted I/O.
- **Let the index do the filtering — keep predicates sargable.** No functions/casts on
  indexed columns, no leading wildcard; otherwise the planner falls back to a full scan.
- **Set-based beats row-by-row.** One statement that processes a set is faster and atomic;
  a loop of per-row queries (N+1) is the most common performance bug in application code.
- **Paginate by keyset, not large `OFFSET`.** `OFFSET 100000` still scans and discards
  100,000 rows every page; a keyset (`WHERE id > $last`) seeks directly.
- **Optimize the plan, then re-measure.** A change is only an improvement if
  `EXPLAIN ANALYZE` says so; intuition is unreliable and sometimes backwards.

## Best Practices

- Replace N+1 access with a single join or an `IN (...)`/`ANY($1)` batch; fetch the parent
  and all children in one query, not one query per parent.
- Select only the columns you use; narrower rows mean less I/O and enable index-only scans.
- Use `EXISTS` instead of `IN (subquery)` for existence checks — it can short-circuit and
  avoids materializing the full subquery result.
- Prefer keyset pagination for deep lists; reserve `LIMIT/OFFSET` for shallow paging only.
- Avoid `SELECT DISTINCT`/`GROUP BY` used to paper over a fan-out join; fix the join
  condition instead, so you are not de-duplicating rows you should not have produced.
- Precompute expensive aggregates with a materialized view or summary table when the read
  pattern is frequent and the data tolerates slight staleness.
- Batch writes and reads to amortize round-trip latency, but keep transactions short.

## Examples

**Good Example** — one set-based query and keyset pagination

```sql
-- Fetch orders AND their line items in one round trip (no N+1):
SELECT o.id, o.total_cents, li.sku, li.qty
  FROM orders o
  JOIN line_items li ON li.order_id = o.id
 WHERE o.customer_id = $1
   AND o.id > $2              -- keyset: seek past the last page, no OFFSET scan
 ORDER BY o.id
 LIMIT 50;                    -- bounded, index-friendly page
```

**Bad Example** — N+1 plus deep OFFSET

```sql
-- Application loop: 1 query for orders, then 1 per order for its items = N+1.
SELECT id FROM orders WHERE customer_id = $1 ORDER BY id OFFSET 100000 LIMIT 50;
--   ^ OFFSET 100000 scans and throws away 100k rows on every page fetch.
-- for each order_id:
SELECT * FROM line_items WHERE order_id = $each;  -- one round trip per row
```

## Common Mistakes

- N+1 queries: looping in application code instead of one join or batched `IN`.
- `SELECT *` on wide tables, moving and caching columns nobody reads.
- Non-sargable predicates that silently disable index use.
- Deep `LIMIT/OFFSET` pagination that scans everything before the offset.
- `DISTINCT`/`GROUP BY` masking a fan-out join bug rather than fixing the join.
- `IN (large subquery)` where `EXISTS` or a join would short-circuit.
- "Optimizing" without re-running `EXPLAIN ANALYZE`, so a change that looks faster is
  actually slower on real data.

## Production Tips

- Rank queries by *total* time (`pg_stat_statements`), then fix the highest-impact one;
  a cheap query run a million times outweighs one slow report.
- Add a covering index for a proven hot read path so it becomes an index-only scan; verify
  the plan shows "Index Only Scan" afterward.
- For dashboards and counts over huge tables, prefer a maintained summary/materialized view
  to recomputing an aggregate on every request.

## AI Review Checklist

- Is N+1 access replaced by a single join or a batched `IN`/`ANY` query?
- Does the query select only needed columns instead of `SELECT *`?
- Are all `WHERE` predicates sargable so indexes are usable?
- Is deep pagination done by keyset rather than large `OFFSET`?
- Is `EXISTS` used over `IN (subquery)` for existence checks where it helps?
- Was the improvement confirmed by re-running `EXPLAIN ANALYZE`?
- Does the rewrite preserve the original result set exactly (no accidental dedupe/loss)?

## Related

- `knowledge/sql/16-query-planning.md`
- `knowledge/sql/15-indexes.md`
- `knowledge/sql/05-joins.md`
- `knowledge/sql/23-performance.md`
- `knowledge/sql/100-common-antipatterns.md`
