---
id: sql/08-window-functions
topic: sql
slug: window-functions
title: "Window Functions"
type: doc
order: 8
status: ready
tags: [sql, window-functions, SUM, RANGE, HAVING, LIMIT]
related: [sql/09-aggregate-functions, sql/04-grouping, sql/07-common-table-expressions, sql/17-query-optimization, sql/15-indexes]
when_to_use: "Read before computing running totals, rankings, per-group top-N, or row-to-row comparisons without collapsing rows."
---
# Window Functions

## Purpose

This document defines how to use window functions — `OVER (...)` computations such as
`ROW_NUMBER`, `RANK`, `SUM`, `LAG`, and `LEAD` that produce a value *per row* while seeing
a "window" of related rows. It is written so an agent can compute rankings, running
totals, and row-to-row deltas without collapsing rows the way [`GROUP BY`](04-grouping.md)
does.

A window function answers questions that need both the detail row *and* an aggregate over
its neighbors: "rank each sale within its region", "running balance per account",
"each row's value minus the previous row's". If you need one row per group, use an
[aggregate](09-aggregate-functions.md); if you need every row *plus* a group-level number,
use a window function.

## Why It Matters

Window functions replace slow, error-prone self-joins and correlated subqueries with a
single pass the engine can optimize. The classic "top N per group" and "running total"
problems, written with subqueries, are O(n²); written as window functions they are one
sort and one scan. But the mechanics are subtle: `RANK` vs `DENSE_RANK` vs `ROW_NUMBER`
differ on ties, and the default frame (`RANGE` vs `ROWS`) changes a running total's result
silently. A wrong frame produces plausible-looking numbers that are quietly incorrect.

## Core Principles

- **Windows do not collapse rows.** `OVER()` keeps every input row and attaches a computed
  value. This is the defining difference from `GROUP BY`.
- **`PARTITION BY` resets the computation per group; `ORDER BY` inside `OVER` defines the
  running order.** Omitting `ORDER BY` for a ranking or running total is a bug.
- **Choose the ranking function by tie behavior.** `ROW_NUMBER` = unique 1..n (arbitrary on
  ties), `RANK` = gaps after ties (1,1,3), `DENSE_RANK` = no gaps (1,1,2).
- **The frame clause changes the answer.** With `ORDER BY` present, the default frame is
  `RANGE ... CURRENT ROW`, which lumps peer rows together; for a true row-by-row running
  total use `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.
- **Window functions run after `WHERE`/`GROUP BY`/`HAVING` but before `ORDER BY`/`LIMIT`.**
  You cannot filter on a window result in `WHERE`; wrap it in a
  [CTE](07-common-table-expressions.md) or subquery first.

## Best Practices

- Always specify `ORDER BY` inside `OVER` for `ROW_NUMBER`, `RANK`, `LAG`, `LEAD`, and any
  running aggregate — the result is undefined without it.
- For running totals and moving averages, write the frame explicitly with `ROWS` so the
  result does not depend on the engine's default and does not merge tied rows.
- To filter or top-N on a window result, compute it in a CTE and filter in the outer query
  (`WHERE rn <= 3`) — window functions are not allowed in `WHERE`.
- Give `LAG`/`LEAD` a default (`LAG(x, 1, 0)`) so the first/last row is not an unexpected
  `NULL`.
- Reuse one window with a named `WINDOW` clause when several columns share the same
  `PARTITION BY`/`ORDER BY`, avoiding copy-paste drift.
- Ensure the `PARTITION BY`/`ORDER BY` columns are indexed to let the planner avoid an
  extra sort.

## Examples

**Good Example** — top-3 per group with explicit ordering and a CTE to filter

```sql
-- Highest-paid 3 employees per department. ROW_NUMBER gives a unique rank so
-- ties do not return a 4th row; ORDER BY makes "highest" well-defined.
WITH ranked AS (
    SELECT
        id, department_id, salary,
        ROW_NUMBER() OVER (
            PARTITION BY department_id      -- restart numbering per department
            ORDER BY salary DESC            -- required: defines "highest"
        ) AS rn
    FROM employees
)
SELECT id, department_id, salary
FROM ranked
WHERE rn <= 3;                              -- filter the window result in the outer query
```

**Bad Example** — running total with the wrong (default) frame and no explicit rows

```sql
-- Intent: a per-row running total. But with ORDER BY and no frame clause the
-- default is RANGE, which sums ALL rows sharing the same order_date into one
-- value — every same-day row shows the same lumped total, not a row-by-row sum.
SELECT
    id, order_date, amount,
    SUM(amount) OVER (ORDER BY order_date) AS running_total  -- silently RANGE
FROM orders;
```

## Common Mistakes

- Omitting `ORDER BY` inside `OVER` for a ranking or running total, yielding undefined
  results that differ between runs.
- Relying on the default `RANGE` frame for a running total, merging tied rows instead of
  accumulating row by row.
- Using `ROW_NUMBER` where ties should share a rank (needs `RANK`/`DENSE_RANK`), or vice
  versa.
- Referencing a window column in `WHERE`, which is evaluated before window functions —
  causes a syntax error or forces a subquery.
- Forgetting `LAG`/`LEAD` returns `NULL` at the boundary and not supplying a default.
- Re-implementing top-N-per-group with correlated subqueries when a window does it in one
  pass.

## Production Tips

- `EXPLAIN ANALYZE` a windowed query and look for a `WindowAgg` preceded by a `Sort`; an
  index on the partition/order columns can eliminate that sort on large tables.
- Windowing a huge unpartitioned set materializes and sorts everything — partition, or
  pre-filter with a `WHERE`, before applying the window.
- Prefer window functions over `DISTINCT ON` (PostgreSQL) when you also need the rank
  value, not just the winning row.

## AI Review Checklist

- Does every ranking / running function have an explicit `ORDER BY` inside `OVER`?
- Is the frame written with `ROWS` when a true row-by-row running total is intended?
- Is the ranking function (`ROW_NUMBER`/`RANK`/`DENSE_RANK`) correct for the tie semantics?
- Is any window result filtered in `WHERE` (illegal) instead of a wrapping CTE/subquery?
- Do `LAG`/`LEAD` handle the boundary `NULL` with a default where needed?
- Are the `PARTITION BY`/`ORDER BY` columns indexed to avoid an extra sort at scale?

## Related

- `knowledge/sql/09-aggregate-functions.md`
- `knowledge/sql/04-grouping.md`
- `knowledge/sql/07-common-table-expressions.md`
- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/15-indexes.md`
