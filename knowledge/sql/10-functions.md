---
id: sql/10-functions
topic: sql
slug: functions
title: "SQL Functions"
type: doc
order: 10
status: ready
tags: [sql, functions]
related: [sql/11-data-types, sql/09-aggregate-functions, sql/15-indexes, sql/27-portability, sql/02-filtering]
when_to_use: "Read before using scalar functions on strings, dates, numbers, or NULLs — especially inside a WHERE clause or on money."
---
# SQL Functions

## Purpose

This document defines how to use SQL's built-in scalar functions — string
(`LOWER`, `TRIM`, `SUBSTRING`), numeric (`ROUND`, `CEIL`, `MOD`), date/time (`NOW`,
`DATE_TRUNC`, `EXTRACT`, `AGE`), null-handling (`COALESCE`, `NULLIF`), and conditional
(`CASE`, `CAST`). These operate on individual values, unlike
[aggregates](09-aggregate-functions.md) which collapse rows.

Use scalar functions to normalize, format, convert, and branch on values. The rules here
keep function use both correct (timezones, rounding, `NULL`) and fast (indexes).

## Why It Matters

A single function call in the wrong place turns a millisecond index lookup into a
full-table scan: wrapping an indexed column in `LOWER()` or `DATE(...)` makes the index
unusable, and nobody notices until the table grows. Meanwhile date functions are a
correctness minefield — `NOW()` in one timezone, a `DATE` cast in another, and reports are
off by a day at month boundaries. And every function propagates `NULL` unless you
explicitly stop it. Functions are small but they sit on the hot path of both performance
and correctness.

## Core Principles

- **A function on an indexed column in `WHERE` disables the index** (unless a matching
  expression/functional index exists). Transform the *constant*, not the column.
- **`NULL` poisons most functions.** `CONCAT` differs from `||` on `NULL`; arithmetic and
  comparisons with `NULL` yield `NULL`/`UNKNOWN`. Use `COALESCE` and `NULLIF` deliberately.
- **Date/time is timezone- and type-sensitive.** Prefer `TIMESTAMPTZ`, know whether `NOW()`
  is transaction-stable, and truncate with `DATE_TRUNC` rather than string slicing.
- **`CAST` can silently lose data or error.** Narrowing casts truncate; bad text-to-number
  casts throw. Validate or use safe-cast variants (`TRY_CAST` where available).
- **Function names and behavior are not portable.** `SUBSTRING`, `||` vs `CONCAT`, date
  math, and `LIMIT` vs `TOP` differ by engine; see [portability](27-portability.md).

## Best Practices

- Compare case-insensitively by indexing the expression (`CREATE INDEX ... ON t (LOWER(email))`)
  or using a case-insensitive collation / `CITEXT`, not by wrapping the column at query time
  on an unindexed expression.
- Filter date ranges with half-open bounds on the raw column
  (`ts >= '2026-01-01' AND ts < '2026-02-01'`) instead of `DATE_TRUNC('month', ts) = ...`,
  so the index on `ts` is used.
- Use `COALESCE(a, b, default)` for fallbacks and `NULLIF(x, 0)` to guard division by zero.
- Round money explicitly with `ROUND(x, 2)` on a `NUMERIC`; never rely on display rounding
  of a float ([data types](11-data-types.md)).
- Prefer `CASE` over nested `COALESCE`/`NULLIF` when branching on more than null-ness — it
  is clearer and standard.
- Standardize on `TIMESTAMPTZ` and `DATE_TRUNC`/`EXTRACT`; avoid parsing dates out of
  strings.

## Examples

**Good Example** — sargable date filter and safe null/division handling

```sql
-- Half-open range keeps the index on created_at usable and is DST-safe.
-- NULLIF prevents a divide-by-zero; COALESCE supplies a sane default.
SELECT
    id,
    COALESCE(nickname, email)          AS display_name,   -- fallback when nickname NULL
    ROUND(revenue / NULLIF(orders, 0), 2) AS avg_value    -- NULL, not error, if orders = 0
FROM customers
WHERE created_at >= '2026-01-01'
  AND created_at <  '2026-02-01';                          -- sargable; index is used
```

**Bad Example** — function on the indexed column kills the index; div-by-zero risk

```sql
-- LOWER() and DATE() wrap the indexed columns, so neither index can be used:
-- this becomes a full-table scan. revenue/orders can also throw on orders = 0.
SELECT id, revenue / orders AS avg_value
FROM customers
WHERE LOWER(email) = 'a@b.com'                 -- index on email unusable
  AND DATE(created_at) = '2026-01-15';         -- index on created_at unusable
```

## Common Mistakes

- Wrapping an indexed column in `LOWER`, `DATE`, `CAST`, etc. in `WHERE`, forcing a scan.
- Comparing `= NULL` instead of `IS NULL`, which is always `UNKNOWN`.
- Assuming `CONCAT` and `||` treat `NULL` the same (they don't across engines).
- Dividing without `NULLIF(denominator, 0)`, throwing at runtime on zero.
- Using `NOW()`/`CURRENT_DATE` without accounting for the session/server timezone, causing
  off-by-one-day bugs.
- Narrowing `CAST`s that truncate silently, or text casts that throw on bad input.
- Porting engine-specific function names verbatim and getting a syntax error elsewhere.

## Production Tips

- If case-insensitive or truncated-date lookups are common, create a matching **functional
  index** (`ON t (LOWER(col))`) so the transform stays fast at scale.
- Pin timezone behavior explicitly (`AT TIME ZONE`, `TIMESTAMPTZ`) rather than trusting the
  server default, which differs between environments.
- Prefer `TRY_CAST`/`SAFE_CAST` (engine-dependent) in ETL so one bad row does not abort the
  whole batch.

## AI Review Checklist

- Is any function applied to an indexed column in `WHERE`? Move the transform to the
  constant or add a functional index.
- Are date ranges expressed as half-open bounds on the raw timestamp column?
- Is every division guarded against zero with `NULLIF`?
- Are `NULL` fallbacks handled with `COALESCE`, and equality-to-null written as `IS NULL`?
- Is money rounded with `ROUND` on a `NUMERIC`, not a float?
- Are timezone and cast behaviors explicit and engine-appropriate?

## Related


- `knowledge/sql/11-data-types.md`
- `knowledge/sql/09-aggregate-functions.md`
- `knowledge/sql/15-indexes.md`
- `knowledge/sql/27-portability.md`
- `knowledge/sql/02-filtering.md`
