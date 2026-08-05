---
id: sql/06-subqueries
topic: sql
slug: subqueries
title: "Subqueries"
type: doc
order: 6
status: ready
tags: [sql, subqueries]
related: [sql/07-common-table-expressions, sql/05-joins, sql/09-aggregate-functions, sql/17-query-optimization, sql/08-window-functions]
when_to_use: "Read before nesting a query inside a WHERE, FROM, or SELECT clause, or when a join alone cannot express the filter you need."
---
# Subqueries

## Purpose

This document defines how to use a query nested inside another query — in the
`WHERE`, `FROM`, `SELECT`, or `HAVING` clause. It is written so an agent can choose
between a scalar, row, table, or correlated subquery and write one that is both correct
and cheap to execute.

A subquery answers a question the outer query needs *before* it can finish: "which
customer ids placed an order last month?", "what is the average price of this product's
category?". Reach for one when a plain [join](05-joins.md) cannot express the condition,
and prefer a [CTE](07-common-table-expressions.md) when the same subquery is used more
than once or the nesting hurts readability.

## Why It Matters

Subqueries are where correctness and performance quietly diverge. A **correlated**
subquery re-executes once per outer row; on a million-row table that is a million
executions, and the planner cannot always rewrite it. Worse, `NOT IN` against a column
that contains a single `NULL` silently returns **zero rows** — a bug that passes every
test built on non-null data and fails in production. Getting subqueries right means
knowing which shape the SQL contract requires and how the optimizer will run it.

## Core Principles

- **Match the subquery shape to the operator.** A scalar comparison (`=`, `<`) needs a
  subquery returning exactly one row and one column; `IN`/`EXISTS` take a set. Returning
  the wrong shape is a runtime error, not a warning.
- **Prefer `EXISTS` over `IN` for existence checks.** `EXISTS` short-circuits on the
  first match and is `NULL`-safe; `IN` materializes the full list and breaks on `NULL`.
- **Never use `NOT IN` with a nullable subquery column.** One `NULL` makes the entire
  predicate `UNKNOWN`, returning no rows. Use `NOT EXISTS` or add `WHERE col IS NOT NULL`.
- **Understand correlation cost.** A correlated subquery references the outer row and
  runs per row; an uncorrelated one runs once. Know which you wrote.
- **A subquery is not automatically slower than a join** — modern planners rewrite many
  into joins — but you must verify with `EXPLAIN`, not assume.

## Best Practices

- Use `EXISTS (SELECT 1 FROM ...)` for existence; the projected column is ignored, so do
  not compute one.
- Use a scalar subquery in `SELECT` only when it returns one row; guard with `LIMIT 1`
  and an `ORDER BY` if the "one row" is a choice (e.g. latest).
- Prefer a derived table (`FROM (SELECT ...) AS t`) or [CTE](07-common-table-expressions.md)
  over deeply nested inline subqueries — flatter SQL is easier to review and re-plan.
- Push filters *into* the subquery so it returns fewer rows before the outer query runs.
- When a subquery in `FROM` needs to be joined back to the outer query, check whether a
  window function ([window functions](08-window-functions.md)) expresses it in one pass.
- Always run `EXPLAIN` on correlated subqueries over large tables; convert to a join or
  CTE if the plan shows a per-row re-scan.

## Examples

**Good Example** — `NOT EXISTS` for anti-join, null-safe and short-circuiting

```sql
-- Customers who have never placed an order.
-- NOT EXISTS stops at the first matching order and is unaffected by NULL customer_ids.
SELECT c.id, c.email
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1                       -- projected value is irrelevant to EXISTS
    FROM orders AS o
    WHERE o.customer_id = c.id     -- correlation: ties subquery to the outer row
);
```

**Bad Example** — `NOT IN` over a nullable column silently returns nothing

```sql
-- If ANY order has customer_id = NULL, this returns ZERO rows, not "customers
-- without orders". The NULL makes the predicate UNKNOWN for every customer.
SELECT c.id, c.email
FROM customers AS c
WHERE c.id NOT IN (
    SELECT o.customer_id           -- nullable column → the trap
    FROM orders AS o
);
```

## Common Mistakes

- `NOT IN` against a subquery whose column can be `NULL`, silently returning no rows.
- A scalar subquery in `SELECT` or `WHERE` that returns more than one row, erroring at
  runtime under production data volumes.
- Correlated subqueries in `SELECT` that re-scan a large table once per output row.
- Using `IN` with a huge subquery result when `EXISTS` (or a join) would short-circuit.
- Repeating the same subquery in multiple clauses instead of naming it once as a CTE.
- Assuming a subquery is slower than a join without checking `EXPLAIN` — often the
  planner produces the same plan.

## Production Tips

- Add an index on the correlated join column (e.g. `orders.customer_id`) — without it, a
  correlated subquery degrades to a full scan per outer row.
- In `EXPLAIN`/`EXPLAIN ANALYZE`, watch for `SubPlan` re-executed N times; that signals a
  correlated subquery that should be rewritten as a join or CTE.
- Prefer semi-join/anti-join operators (what `EXISTS`/`NOT EXISTS` compile to) — they let
  the planner stop early.

## AI Review Checklist

- Does every scalar subquery provably return at most one row?
- Is any `NOT IN` used against a column that can contain `NULL`? Replace with `NOT EXISTS`.
- Are existence checks written as `EXISTS`/`NOT EXISTS` rather than `IN`/`NOT IN`?
- Is a correlated subquery re-scanning a large table? Is the correlation column indexed?
- Would a [CTE](07-common-table-expressions.md) or [join](05-joins.md) be clearer or faster here?
- Has `EXPLAIN` been run on subqueries over large tables?

## Related


- `knowledge/sql/07-common-table-expressions.md`
- `knowledge/sql/05-joins.md`
- `knowledge/sql/09-aggregate-functions.md`
- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/08-window-functions.md`
