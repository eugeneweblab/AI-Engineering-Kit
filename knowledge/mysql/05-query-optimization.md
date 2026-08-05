---
id: mysql/05-query-optimization
topic: mysql
slug: query-optimization
title: "Query Optimization"
type: doc
order: 5
status: ready
tags: [mysql, query-optimization]
related: [mysql/04-indexes, mysql/03-data-types, mysql/14-performance, mysql/15-monitoring, mysql/06-transactions]
when_to_use: "Read before writing a query on a large table or when diagnosing a slow query."
---
# Query Optimization

## Purpose

This document defines how to make MySQL queries fast: how to read `EXPLAIN`, how to write
SQL that the optimizer can use an index for, and which common patterns quietly force full
scans. The goal is that an agent can look at a query, predict how MySQL will run it, and
fix it before it reaches production.

## Why It Matters

A query that runs fine on a developer's 1,000-row table can bring production down at 10
million rows, because the cost of a full table scan grows with the data while an indexed
lookup stays roughly constant. These regressions never show up in tests — they appear as a
slow endpoint or a locked table under real load. `EXPLAIN` is the tool that makes the cost
visible before it hurts, and a few rewrite patterns eliminate most of the damage. Optimizing
queries is cheaper than scaling hardware to hide a bad one.

## Core Principles

- **`EXPLAIN` is the source of truth.** Before trusting a query on a large table, read its plan.
  Look at `type` (avoid `ALL`), `key` (an index should be chosen), and `rows` (how many MySQL
  expects to examine). Guessing is how full scans ship.
- **Keep columns bare in the `WHERE` clause.** `WHERE created_at >= '2026-01-01'` uses an index;
  `WHERE YEAR(created_at) = 2026` wraps the column in a function and cannot. Rewrite to a range
  against the raw column.
- **Select only what you need.** `SELECT *` prevents covering indexes, pulls large columns you
  won't use, and breaks when the schema changes. Name the columns.
- **Filter and paginate in the database, not the application.** Push `WHERE`, `LIMIT`, and joins
  into SQL; never fetch a whole table and filter in code.

## Best Practices

- Run `EXPLAIN` (or `EXPLAIN ANALYZE` in 8.0+ for real timings) on any query touching a large
  table. Aim for `type` of `ref`, `range`, `eq_ref`, or `const` — never `ALL` on a big table.
- Rewrite non-sargable predicates: replace `WHERE DATE(col) = '…'` with a `>= … AND < …` range,
  and `WHERE col + 0 = 5` with `WHERE col = 5`, so an index can be used.
- Avoid `SELECT *`; list columns so hot queries can be served by a covering index.
- Paginate large result sets by **keyset** (`WHERE id > :last_id ORDER BY id LIMIT 20`) rather
  than large `OFFSET`, which still scans and discards every skipped row.
- Prefer a `JOIN` over a correlated subquery in a `SELECT` list or a per-row `N+1` query pattern;
  fetch related rows in one statement.
- Batch writes and `IN (...)` reads instead of looping single-row statements from the app.
- Keep transactions short so they don't hold locks while doing slow work. See [transactions](06-transactions.md).

## Examples

**Good Example** — sargable, indexed, keyset-paginated

```sql
-- Bare column in a range predicate: the index on created_at is usable.
-- Explicit columns allow a covering index. Keyset pagination avoids scanning
-- and discarding skipped rows the way a large OFFSET would.
SELECT id, user_id, total_cents, created_at
FROM orders
WHERE created_at >= '2026-01-01'
  AND created_at <  '2026-02-01'
  AND id > :last_seen_id           -- keyset cursor, not OFFSET
ORDER BY id
LIMIT 50;
-- EXPLAIN: type=range, key=idx_orders_created, rows in the thousands, not millions.
```

**Bad Example** — function on column, SELECT *, deep OFFSET

```sql
-- YEAR()/MONTH() wrap the column, so no index can be used -> full table scan.
-- SELECT * defeats any covering index and drags large columns along.
-- OFFSET 100000 still reads and throws away 100,000 rows every page.
SELECT *
FROM orders
WHERE YEAR(created_at) = 2026 AND MONTH(created_at) = 1
ORDER BY created_at
LIMIT 50 OFFSET 100000;
-- EXPLAIN: type=ALL, key=NULL, rows in the millions.
```

## Common Mistakes

- Never running `EXPLAIN`, so a full scan (`type=ALL`) ships unnoticed.
- Wrapping a filtered column in a function or arithmetic, making the predicate non-sargable.
- Using `SELECT *`, which blocks covering indexes and couples the query to the schema.
- Deep `OFFSET` pagination that scans and discards everything before the page.
- The N+1 pattern: one query per row in a loop instead of a single join or `IN (...)`.
- Filtering or sorting in application code after fetching far more rows than needed.
- Leading-wildcard `LIKE '%term'` for search instead of a FULLTEXT index.

## Production Tips

- Turn on the slow query log (`long_query_time = 1`) and review the top offenders with
  `pt-query-digest` or the Performance Schema; optimize by real cost, not by guesswork.
- `EXPLAIN ANALYZE` shows actual vs estimated rows — a large gap means stale statistics; run
  `ANALYZE TABLE` to refresh them so the optimizer picks the right plan.
- Watch `Handler_read_rnd_next` (row-by-row scanning) and rows-examined vs rows-sent ratios in
  monitoring to catch queries scanning far more than they return. See [monitoring](15-monitoring.md).

## AI Review Checklist

- Was `EXPLAIN` run, with `type` better than `ALL` and a non-NULL `key` on large tables?
- Are all filtered columns bare (no function or arithmetic wrapping) so indexes apply?
- Does the query name its columns instead of using `SELECT *`?
- Is large-offset pagination replaced with keyset pagination?
- Are related rows fetched with a join or `IN (...)` instead of an N+1 loop?
- Is filtering and sorting done in SQL, not in application code after over-fetching?
- Are table statistics fresh (`ANALYZE TABLE`) if the plan looks wrong?

## Related


- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/03-data-types.md`
- `knowledge/mysql/14-performance.md`
- `knowledge/mysql/15-monitoring.md`
- `knowledge/mysql/06-transactions.md`
