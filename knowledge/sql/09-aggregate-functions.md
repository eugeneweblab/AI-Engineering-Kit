---
id: sql/09-aggregate-functions
topic: sql
slug: aggregate-functions
title: "Aggregate Functions"
type: doc
order: 9
status: ready
tags: [sql, aggregate-functions]
related: [sql/04-grouping, sql/08-window-functions, sql/06-subqueries, sql/11-data-types, sql/10-functions]
when_to_use: "Read before using COUNT, SUM, AVG, MIN, MAX, or any GROUP BY aggregation, especially over nullable or money columns."
---
# Aggregate Functions

## Purpose

This document defines how to use aggregate functions — `COUNT`, `SUM`, `AVG`, `MIN`,
`MAX`, `STRING_AGG`/`ARRAY_AGG`, and their `FILTER`/`DISTINCT` variants — that collapse
many rows into a single summary value. It pairs with [grouping](04-grouping.md), which
controls *which* rows are summarized together.

Aggregates answer "how many?", "what's the total?", "what's the average?". They run over
the whole result set or, with [`GROUP BY`](04-grouping.md), per group. When you need the
detail rows *and* the aggregate, use a [window function](08-window-functions.md) instead.

## Why It Matters

Aggregates look trivial and hide the most common silent data bug in SQL: **`NULL`
handling**. `COUNT(*)` counts rows, `COUNT(col)` skips `NULL`s, and `AVG`/`SUM` ignore
`NULL`s entirely — so an average can be computed over fewer rows than you think, and a
report can be quietly wrong for months. Add floating-point money math and integer
division, and an "obviously correct" `SUM` ships an incorrect financial number. These
functions are held to a high bar because their output is usually what a human decision is
based on.

## Core Principles

- **`COUNT(*)` counts rows; `COUNT(col)` counts non-`NULL` values; `COUNT(DISTINCT col)`
  counts distinct non-`NULL` values.** Choose deliberately — they give different numbers.
- **All aggregates except `COUNT(*)` ignore `NULL`.** `AVG` divides by the count of
  non-null values, not total rows. If `NULL` should mean zero, `COALESCE` it first.
- **Every non-aggregated column in `SELECT` must be in `GROUP BY`** (or be functionally
  dependent on the grouping key). This is a contract; violating it is an error or, in lax
  MySQL modes, undefined results.
- **Filter rows with `WHERE`, filter groups with `HAVING`.** `WHERE` runs before
  aggregation, `HAVING` after. Putting an aggregate in `WHERE` is illegal.
- **Aggregate types matter.** `SUM` of an `int` column can overflow; `AVG` of integers may
  truncate. Cast to a wider or exact type before summing money.

## Best Practices

- Use `COUNT(*)` for "how many rows"; reserve `COUNT(col)` for "how many have a value".
- `COALESCE(col, 0)` before `SUM`/`AVG` only when a missing value genuinely means zero —
  otherwise let `NULL` be excluded, which is usually correct.
- Use `FILTER (WHERE ...)` (PostgreSQL/standard) for conditional aggregates instead of
  fragile `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` — it is clearer and equally fast.
- Store and aggregate money as `NUMERIC`/`DECIMAL`, never `FLOAT`/`REAL`; see
  [data types](11-data-types.md). Floating point makes `SUM` non-deterministic.
- Guard against empty-set surprises: `SUM` over no rows returns `NULL`, not `0` — wrap in
  `COALESCE(SUM(x), 0)` when a numeric zero is required.
- For `AVG` of integers where fractional precision matters, cast: `AVG(col::numeric)`.

## Examples

**Good Example** — deliberate NULL handling, exact money type, conditional FILTER

```sql
SELECT
    region,
    COUNT(*)                              AS total_orders,      -- all rows
    COUNT(*) FILTER (WHERE status = 'paid') AS paid_orders,    -- conditional count
    COALESCE(SUM(amount), 0)              AS revenue,          -- 0, not NULL, on empty
    AVG(amount)                           AS avg_order         -- NULLs excluded on purpose
FROM orders                                                    -- amount is NUMERIC(12,2)
GROUP BY region
HAVING SUM(amount) > 10000;                                    -- filter groups, not rows
```

**Bad Example** — NULLs distort the average, float money, aggregate misused in WHERE

```sql
SELECT
    region,
    COUNT(discount_code) AS orders,   -- silently skips rows with NULL discount_code
    AVG(amount)          AS avg_order -- amount is FLOAT → non-deterministic sums/avgs
FROM orders
WHERE SUM(amount) > 10000            -- ILLEGAL: aggregates cannot appear in WHERE
GROUP BY region;
```

## Common Mistakes

- Assuming `COUNT(col)` equals `COUNT(*)` — it silently drops `NULL` rows.
- Expecting `AVG`/`SUM` to include `NULL`s as zero; they exclude them, skewing results.
- Putting an aggregate in `WHERE` instead of `HAVING`.
- Selecting a non-aggregated, non-grouped column (works in loose MySQL, wrong or errors
  elsewhere).
- Summing `FLOAT`/`REAL` money and getting rounding drift; use `NUMERIC`.
- Forgetting that `SUM`/`MAX` over an empty set returns `NULL`, breaking downstream math.
- Integer division/truncation in `AVG` when decimals were expected.

## Production Tips

- For very large tables, `COUNT(*)` is a full scan on PostgreSQL; use an approximate count
  or a maintained counter table when an exact number is not required.
- `COUNT(DISTINCT col)` is expensive (a sort/hash); consider `approx_count_distinct` /
  HyperLogLog where the engine offers it and exactness is not critical.
- Watch integer overflow on `SUM` of `INT` columns on high-volume tables — cast to
  `BIGINT`/`NUMERIC` in the aggregate.

## AI Review Checklist

- Is `COUNT(*)` vs `COUNT(col)` vs `COUNT(DISTINCT col)` the right one for the question?
- Are `NULL`s handled intentionally — excluded, or `COALESCE`d to zero where zero is meant?
- Is money aggregated as `NUMERIC`/`DECIMAL`, never a floating type?
- Are all non-aggregated `SELECT` columns present in `GROUP BY`?
- Are group filters in `HAVING` and row filters in `WHERE` (no aggregate in `WHERE`)?
- Is `SUM`/`MAX` over a possibly empty set wrapped in `COALESCE` where a value is required?
- Could a `SUM` on an `INT` column overflow at production volume?

## Related

- `knowledge/sql/04-grouping.md`
- `knowledge/sql/08-window-functions.md`
- `knowledge/sql/06-subqueries.md`
- `knowledge/sql/11-data-types.md`
- `knowledge/sql/10-functions.md`
