---
id: sql/03-sorting
topic: sql
slug: sorting
title: "SQL Sorting"
type: doc
order: 3
status: ready
tags: [sql, sorting, LIMIT, OFFSET, EXPLAIN]
related: [sql/01-select, sql/02-filtering, sql/04-grouping, sql/15-indexes, sql/08-window-functions]
when_to_use: "Read before writing any ORDER BY, before paginating results, or when result order matters to the caller."
---
# SQL Sorting

## Purpose

This document defines how to order results with `ORDER BY`: guaranteeing a deterministic
order, controlling where `NULL`s land, and paginating correctly. It also states the rule
that underlies all of this — **without `ORDER BY`, a query has no defined row order**.

`ORDER BY` runs after `SELECT` and before `LIMIT`, so it can reference output aliases and
column positions, and it decides which rows a `LIMIT` actually returns.

## Why It Matters

A result set is a *set*: unordered. Engines return rows in whatever order the plan
produces — index order today, hash order after an index change, a different order under
parallel execution. Code that relies on unstated order works in testing and fails in
production non-deterministically. Pagination magnifies this: `LIMIT` without a total
order returns arbitrary rows, so page 2 can repeat or skip rows from page 1. And `NULL`
sorts differently across dialects (last in PostgreSQL by default, first in MySQL), so a
"top N" report can quietly put unknowns at the top.

## Core Principles

- **Order is undefined without `ORDER BY`.** Never rely on insertion order, primary-key
  order, or the order an index happens to yield. If order matters, state it.
- **`LIMIT` needs a *total* order to be deterministic.** Sort by enough columns that ties
  cannot occur — always include a unique tiebreaker (usually the primary key).
- **`NULL` ordering is explicit or dialect-dependent.** Use `NULLS FIRST` / `NULLS LAST`
  to make it deterministic across engines rather than trusting the default.
- **`ORDER BY` can use output aliases and positions, but positions are fragile.**
  `ORDER BY 2` breaks the moment the `SELECT` list changes; name the column instead.

## Best Practices

- Add a unique tiebreaker to every ordered query that feeds pagination or "first N"
  logic: `ORDER BY created_at DESC, id DESC`.
- Prefer keyset (cursor) pagination over `OFFSET` for large tables: `WHERE (created_at,
  id) < (:last_ts, :last_id) ORDER BY created_at DESC, id DESC LIMIT :n`. `OFFSET n`
  still scans and discards the first `n` rows, so deep pages get linearly slower.
- State `NULLS FIRST` / `NULLS LAST` explicitly whenever the sort column is nullable.
- Match the `ORDER BY` to an index (same columns, same direction) so the engine can skip
  a sort step; verify with `EXPLAIN` that no expensive `Sort` node appears.
- Sort by a stable expression, not by one whose value can change between page fetches.

## Examples

**Good Example** — total order, explicit NULL placement, keyset pagination

```sql
-- Deterministic: (created_at, id) is unique, so LIMIT always returns the
-- same rows in the same order. NULLS LAST is explicit, not dialect-dependent.
SELECT o.id, o.total, o.created_at
FROM orders AS o
WHERE (o.created_at, o.id) < (:last_created_at, :last_id)  -- keyset cursor
ORDER BY o.created_at DESC, o.id DESC NULLS LAST
LIMIT 20;
```

**Bad Example** — non-unique sort, OFFSET pagination, implicit NULLs

```sql
-- created_at is not unique, so ties resolve arbitrarily: page boundaries
-- can repeat or drop rows. OFFSET 10000 scans and throws away 10k rows.
-- NULL placement is left to the dialect default.
SELECT id, total, created_at
FROM orders
ORDER BY created_at DESC
LIMIT 20 OFFSET 10000;
```

## Common Mistakes

- Depending on row order with no `ORDER BY` at all.
- Paginating with a non-unique sort key, so pages overlap or skip rows.
- Using `OFFSET` for deep pagination and paying a growing scan cost per page.
- Leaving `NULL` ordering implicit, so it differs between PostgreSQL and MySQL.
- Sorting by column position (`ORDER BY 3`) that silently shifts when the `SELECT`
  list changes.

## Production Tips

- For infinite-scroll and API list endpoints, standardize on keyset pagination; it is
  both correct under concurrent writes and O(page size) regardless of depth.
- Confirm the sort is index-backed in `EXPLAIN`; a top-N query over a large table should
  not show a full `Sort` of the whole table.

## AI Review Checklist

- Does every query whose order matters have an explicit `ORDER BY`?
- Does any paginated or "first N" query include a unique tiebreaker column?
- Is `NULLS FIRST`/`NULLS LAST` specified for nullable sort columns?
- Is deep pagination using keyset cursors rather than large `OFFSET`?
- Does the `ORDER BY` avoid fragile column-position references?

## Related

- `knowledge/sql/01-select.md`
- `knowledge/sql/02-filtering.md`
- `knowledge/sql/04-grouping.md`
- `knowledge/sql/15-indexes.md`
- `knowledge/sql/08-window-functions.md`
