---
id: sql/04-grouping
topic: sql
slug: grouping
title: "Grouping"
type: doc
order: 4
status: ready
tags: [sql, grouping, SUM, HAVING, COALESCE, MIN, MAX, AVG, clause, report, group]
related: [sql/01-select, sql/02-filtering, sql/09-aggregate-functions, sql/08-window-functions, sql/05-joins]
when_to_use: "Read before writing any GROUP BY, aggregate query, or HAVING clause, or when a report double-counts."
---
# Grouping

## Purpose

This document defines how to aggregate rows with `GROUP BY`: which columns must appear in
the group key, how aggregate functions treat `NULL`, and the difference between `WHERE`
and `HAVING`. Grouping collapses many rows into one summary row per group, so a mistake
here changes the *number* and *meaning* of your results, not just their content.

`GROUP BY` runs after `WHERE` and before `HAVING` and `SELECT`. That order is the whole
game: `WHERE` filters rows *before* grouping; `HAVING` filters groups *after*.

## Why It Matters

Aggregates power every dashboard, invoice total, and metric. A grouping error is a
silent accounting error. Two failures dominate: joining before grouping multiplies rows
so `SUM` and `COUNT` overcount, and misunderstanding that `COUNT(*)` counts rows while
`COUNT(col)` and `AVG(col)` *ignore `NULL`* — so an average can be computed over fewer
rows than you think. Both produce a number that looks reasonable and is wrong, which is
the most dangerous kind of bug.

## Core Principles

- **Every non-aggregated `SELECT` column must be in `GROUP BY`.** Standard SQL and most
  engines reject otherwise. MySQL historically allowed it and returned an *arbitrary*
  value per group — never rely on that.
- **Aggregates ignore `NULL` (except `COUNT(*)`).** `COUNT(col)`, `SUM`, `AVG`, `MIN`,
  `MAX` skip `NULL` inputs. `AVG(col)` divides by the count of *non-null* values, not by
  the row count.
- **`WHERE` filters rows; `HAVING` filters groups.** Put row conditions in `WHERE` (it
  runs first and can use indexes) and only aggregate conditions in `HAVING`.
- **Aggregating after a one-to-many join multiplies the base rows.** Aggregate in a
  subquery/CTE, or use `COUNT(DISTINCT ...)`, to avoid overcounting.

## Best Practices

- Put non-aggregate filters in `WHERE`, not `HAVING` — filtering before grouping is
  cheaper and index-friendly. Reserve `HAVING` for conditions on aggregates like
  `HAVING COUNT(*) > 1`.
- When you need "one summary per parent" across a one-to-many relationship, aggregate the
  child table in a CTE first, then join — this keeps parent rows from being duplicated.
- Use `COUNT(DISTINCT x)` when a join may repeat `x`, but know it is more expensive than
  `COUNT(*)`; prefer pre-aggregation on hot paths.
- Return `COALESCE(SUM(total), 0)` where a group can be empty and callers expect `0`
  rather than `NULL`.
- Use `FILTER (WHERE ...)` (PostgreSQL) or `COUNT(CASE WHEN ... END)` for conditional
  aggregates instead of running multiple grouped queries.

## Examples

**Good Example** — pre-aggregate the child, then join

```sql
-- Aggregate orders per user FIRST, so joining back to users cannot
-- multiply rows. AVG here divides by non-null totals, which is intended.
WITH per_user AS (
  SELECT user_id,
         COUNT(*)                    AS order_count,
         COALESCE(SUM(total), 0)     AS lifetime_total
  FROM orders
  WHERE status = 'paid'   -- row filter belongs in WHERE, before grouping
  GROUP BY user_id
)
SELECT u.email, p.order_count, p.lifetime_total
FROM users AS u
JOIN per_user AS p ON p.user_id = u.id
WHERE p.order_count >= 5;   -- filtering an already-aggregated value
```

**Bad Example** — join then aggregate, HAVING doing WHERE's job

```sql
-- The 1-to-many join fans out each user's row per order, so SUM(total)
-- and COUNT overcount. status filter in HAVING runs after grouping and
-- cannot use an index; it also can't reference the raw row correctly.
SELECT u.email, COUNT(*) AS order_count, SUM(o.total) AS lifetime_total
FROM users AS u
JOIN orders AS o ON o.user_id = u.id
GROUP BY u.email
HAVING o.status = 'paid';   -- wrong clause: this belongs in WHERE
```

## Common Mistakes

- Selecting a non-aggregated column that is not in `GROUP BY` (or relying on MySQL to
  pick an arbitrary value).
- Aggregating after a one-to-many join, inflating `SUM`/`COUNT`.
- Putting a plain row filter in `HAVING` instead of `WHERE`.
- Assuming `COUNT(col)` counts every row — it skips `NULL`s; use `COUNT(*)` for rows.
- Forgetting that an empty group yields `NULL` from `SUM`, breaking downstream math.

## Production Tips

- When a total looks doubled, check for a one-to-many join upstream of the `GROUP BY`
  before touching the aggregate itself — that is the usual cause.
- For large grouped reports, ensure the `GROUP BY` columns are index-ordered so the
  engine can group by a stream instead of building a large hash table.

## AI Review Checklist

- Is every non-aggregated `SELECT` column present in `GROUP BY`?
- Is there a one-to-many join before the aggregate that could overcount? Is it
  pre-aggregated or using `COUNT(DISTINCT)`?
- Are row filters in `WHERE` and only aggregate filters in `HAVING`?
- Is `NULL` handling correct for `COUNT(col)` vs `COUNT(*)` and for empty-group `SUM`?
- Do empty groups return the value callers expect (e.g. `COALESCE(SUM(...), 0)`)?

## Related

- `knowledge/sql/01-select.md`
- `knowledge/sql/02-filtering.md`
- `knowledge/sql/09-aggregate-functions.md`
- `knowledge/sql/08-window-functions.md`
- `knowledge/sql/05-joins.md`
