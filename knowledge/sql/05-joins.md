---
id: sql/05-joins
topic: sql
slug: joins
title: "Joins"
type: doc
order: 5
status: ready
tags: [sql, joins, LEFT, INNER, SUM, EXISTS, COALESCE, EXPLAIN]
related: [sql/01-select, sql/02-filtering, sql/04-grouping, sql/06-subqueries, sql/15-indexes]
when_to_use: "Read before writing any query that combines two or more tables, or when results have duplicate or missing rows."
---
# Joins

## Purpose

This document defines how to combine tables with `JOIN` without multiplying or dropping
rows: choosing the right join type, writing a complete `ON` condition, and handling the
`NULL`s that outer joins introduce. Joins are where row *count* correctness is won or
lost — the difference between an accurate report and a doubled one is often a single
missing `ON` clause.

Join type is chosen by which side's non-matching rows you must keep. Get that decision
right first; everything else follows.

## Why It Matters

A wrong join is the most common source of silently incorrect SQL. Omit part of the `ON`
condition and you get a partial Cartesian product — every row explodes into many, and
every downstream `SUM` and `COUNT` is inflated. Use an `INNER JOIN` where you meant
`LEFT JOIN` and rows with no match vanish, so a "users and their orders" report silently
drops users who never ordered. Put a filter on the right table of a `LEFT JOIN` in
`WHERE` instead of `ON` and you turn it back into an inner join without noticing. Each of
these compiles, runs, and returns confident, wrong numbers.

## Core Principles

- **Choose the join type by which non-matches you keep.** `INNER` keeps only matched
  rows; `LEFT` keeps all left rows (right side `NULL` when unmatched); `RIGHT` mirrors
  `LEFT`; `FULL` keeps unmatched rows from both sides.
- **The `ON` clause must fully specify the relationship.** A missing predicate produces a
  fan-out (rows multiply). A `CROSS JOIN` (every pair) must be intentional, never
  accidental.
- **Filtering the outer side goes in `ON`, not `WHERE`.** On a `LEFT JOIN`, a condition on
  the right table in `WHERE` discards the `NULL`-extended rows and silently makes it an
  inner join. Put it in `ON` to preserve them.
- **One-to-many joins change row counts before aggregation.** A parent joined to many
  children appears once per child; aggregate carefully (see [grouping](04-grouping.md)).

## Best Practices

- Always write explicit `JOIN ... ON`; never use comma joins (`FROM a, b WHERE ...`),
  which hide the join condition and invite accidental cross products.
- Qualify every column with a table alias in multi-table queries so ambiguous columns
  fail loudly at parse time, not silently at runtime.
- Join on indexed columns (typically the foreign key and the referenced primary key);
  verify the plan uses them rather than a hash join over full scans.
- For "does a related row exist?" use `EXISTS`, and for "does none exist?" use
  `NOT EXISTS` — both avoid the row multiplication a join would cause and are null-safe.
- When a `LEFT JOIN` feeds an aggregate, remember unmatched rows contribute `NULL`;
  wrap with `COALESCE` or use `COUNT(child.id)` (which skips `NULL`) deliberately.

## Examples

**Good Example** — LEFT JOIN preserved, outer filter in ON

```sql
-- Keep every user, even those with no matching paid order. The status
-- filter is in ON, so users with only unpaid orders still appear with
-- NULL order data instead of being dropped.
SELECT u.id,
       u.email,
       COUNT(o.id) AS paid_orders   -- COUNT(col) skips NULLs → 0 for no match
FROM users AS u
LEFT JOIN orders AS o
       ON o.user_id = u.id
      AND o.status  = 'paid'        -- outer-side filter belongs in ON
GROUP BY u.id, u.email;
```

**Bad Example** — outer filter in WHERE, incomplete ON

```sql
-- Two bugs: the status filter in WHERE drops every NULL-extended row,
-- silently turning this into an INNER JOIN (users with no paid order vanish).
-- And joining orders to shipments without the full key fans out the rows.
SELECT u.email, COUNT(*) AS paid_orders
FROM users AS u
LEFT JOIN orders   AS o ON o.user_id = u.id
LEFT JOIN shipments AS s ON s.order_id = o.id  -- fine here, but...
WHERE o.status = 'paid'                        -- kills the LEFT JOIN
GROUP BY u.email;
```

## Common Mistakes

- Using an `INNER JOIN` where a `LEFT JOIN` was meant, silently dropping unmatched rows.
- Filtering the outer table of a `LEFT JOIN` in `WHERE`, collapsing it to an inner join.
- Incomplete or missing `ON` conditions, producing a fan-out or Cartesian product.
- Comma joins that obscure the join condition and default to a cross product.
- Aggregating over a one-to-many join without pre-aggregating, inflating totals.
- Unqualified columns causing ambiguous-column errors or binding to the wrong table.

## Production Tips

- If a count or sum looks doubled, look for a one-to-many join in the `FROM` list before
  suspecting the data — a fan-out is the usual culprit.
- Check `EXPLAIN` for a `Nested Loop` over a large unindexed table; add the index on the
  join key to convert it to an index or hash join.
- Prefer `NOT EXISTS` over `LEFT JOIN ... WHERE right.id IS NULL` for anti-joins when the
  intent is clarity; both are correct, but `NOT EXISTS` states the intent directly.

## AI Review Checklist

- Is the join type chosen by which non-matching rows must be kept?
- Is the `ON` clause complete, so rows cannot fan out into a partial cross product?
- Are outer-join filters on the outer table in `ON`, not `WHERE`?
- Is every one-to-many join that feeds an aggregate pre-aggregated or de-duplicated?
- Are all columns qualified with table aliases, and are join keys indexed?

## Related

- `knowledge/sql/01-select.md`
- `knowledge/sql/02-filtering.md`
- `knowledge/sql/04-grouping.md`
- `knowledge/sql/06-subqueries.md`
- `knowledge/sql/15-indexes.md`
