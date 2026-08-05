---
id: sql/02-filtering
topic: sql
slug: filtering
title: "SQL Filtering"
type: doc
order: 2
status: ready
tags: [sql, filtering, UNKNOWN, BETWEEN, EXTRACT, EXISTS, HAVING]
related: [sql/01-select, sql/03-sorting, sql/04-grouping, sql/15-indexes, sql/17-query-optimization]
when_to_use: "Read before writing any WHERE clause, especially one involving NULL, IN/NOT IN, or a column that should use an index."
---
# SQL Filtering

## Purpose

This document defines how to filter rows with `WHERE`: how three-valued logic and `NULL`
work, how to write predicates that use indexes ("sargable" predicates), and how to avoid
the comparison traps that silently drop or duplicate rows. `WHERE` decides *which rows
exist* for the rest of the query, so a mistake here corrupts everything downstream.

`WHERE` runs after `FROM` and before `GROUP BY`. It filters individual rows before any
aggregation. To filter *after* aggregation, use `HAVING` — see [grouping](04-grouping.md).

## Why It Matters

SQL uses three-valued logic: `TRUE`, `FALSE`, and `UNKNOWN`. Any comparison with `NULL`
returns `UNKNOWN`, and `WHERE` keeps only rows that are `TRUE`. This means `status <> 'x'`
silently excludes rows where `status` is `NULL` — a filter you never intended. `NOT IN`
with a `NULL` in the list returns *no rows at all*. These are not edge cases; they are the
default behavior, and they produce results that look plausible and are wrong. Separately,
wrapping a column in a function (`WHERE lower(email) = ...`) disables the index on it,
turning an index seek into a full scan.

## Core Principles

- **Comparisons with `NULL` are `UNKNOWN`, and `WHERE` drops `UNKNOWN`.** Use `IS NULL`
  and `IS NOT NULL` for null tests; `= NULL` is always false.
- **`NOT IN (subquery)` is unsafe when the subquery can return `NULL`.** One `NULL` makes
  the whole predicate `UNKNOWN` for every row. Prefer `NOT EXISTS`, which handles `NULL`
  correctly.
- **Keep the indexed column bare on one side of the operator (sargable).** `col = value`
  can use an index; `func(col) = value` and `col + 1 = value` usually cannot.
- **`AND`/`OR` precedence bites.** `OR` binds looser than `AND`; parenthesize mixed
  conditions explicitly or the engine filters something other than what you meant.

## Best Practices

- Test nullable columns explicitly. If a column can be `NULL`, decide whether those rows
  belong in the result and write `IS [NOT] NULL` accordingly.
- Replace `NOT IN` with `NOT EXISTS` (or an anti-join) whenever the inner set can contain
  `NULL`; it is both null-safe and usually faster.
- Rewrite predicates to be sargable: store a normalized column or use an expression index
  instead of `WHERE lower(email) = ?` on every query.
- Use `BETWEEN` for inclusive ranges but never for timestamps against a day boundary —
  `>= start AND < next_day` avoids missing the last millisecond.
- Use `col = ANY(array)` / `IN (list)` for set membership; keep the list bounded, as very
  large `IN` lists defeat the planner.

## Examples

**Good Example** — null-safe exclusion, sargable date range

```sql
-- NOT EXISTS is correct even if some orders have a NULL user_id:
-- it evaluates row-by-row and never collapses to UNKNOWN for all rows.
SELECT u.id, u.email
FROM users AS u
WHERE NOT EXISTS (
        SELECT 1 FROM orders o WHERE o.user_id = u.id
      )
  -- Half-open range keeps `created_at` bare, so an index on it is used.
  AND u.created_at >= DATE '2026-01-01'
  AND u.created_at <  DATE '2026-02-01';
```

**Bad Example** — NOT IN with NULLs, non-sargable predicate

```sql
SELECT u.id, u.email
FROM users AS u
-- If ANY order has a NULL user_id, this returns ZERO rows, silently.
WHERE u.id NOT IN (SELECT user_id FROM orders)
  -- Wrapping the column in a function disables the index → full scan.
  AND EXTRACT(YEAR FROM u.created_at) = 2026;
```

## Common Mistakes

- Using `= NULL` or `<> NULL` instead of `IS NULL` / `IS NOT NULL`.
- Assuming `col <> 'value'` includes `NULL` rows — it excludes them.
- `NOT IN` over a subquery that can yield `NULL`, silently returning no rows.
- Wrapping the filtered column in a function or arithmetic, defeating its index.
- Mixing `AND` and `OR` without parentheses and getting the wrong grouping.
- Using `BETWEEN` on timestamps and missing rows on the final day.

## Production Tips

- Run `EXPLAIN (ANALYZE)` and confirm the plan shows an index scan, not a `Seq Scan`,
  for selective predicates on large tables.
- For case-insensitive or computed filters that must be fast, add an expression index
  (`CREATE INDEX ON users (lower(email))`) so the predicate stays sargable.
- When a filter must ignore `NULL` differences, `IS DISTINCT FROM` gives null-safe
  inequality in PostgreSQL; use `<=>` in MySQL for null-safe equality.

## AI Review Checklist

- Are all null comparisons written with `IS [NOT] NULL`, never `= NULL`?
- Could any `NOT IN` subquery return `NULL`? If so, is it rewritten as `NOT EXISTS`?
- Is every filtered column bare (sargable), or is an expression index in place?
- Are mixed `AND`/`OR` conditions parenthesized to match intent?
- Do date/time ranges use a half-open `>= .. AND < ..` form?

## Related

- `knowledge/sql/01-select.md`
- `knowledge/sql/03-sorting.md`
- `knowledge/sql/04-grouping.md`
- `knowledge/sql/15-indexes.md`
- `knowledge/sql/17-query-optimization.md`
