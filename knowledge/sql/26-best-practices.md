---
id: sql/26-best-practices
topic: sql
slug: best-practices
title: "SQL Best Practices"
type: doc
order: 26
status: ready
tags: [sql, best-practices]
related: [sql/13-dml, sql/15-indexes, sql/22-security, sql/17-query-optimization, sql/100-common-antipatterns]
when_to_use: "Read before writing or reviewing any non-trivial query, DML statement, or schema change."
---
# SQL Best Practices

## Purpose

This document defines the day-to-day rules for writing SQL that is correct, safe, and
readable: how to write predicates, how to shape queries, and the habits that keep a
`DELETE` from wiping a table. It is the general standard the topic-specific docs
(indexes, transactions, security) build on.

These rules are not style preferences. Each one prevents a specific, common failure —
a wrong result, a data-loss accident, or an injection hole.

## Why It Matters

SQL is unforgiving because it operates on sets and writes to durable storage. A single
missing `WHERE` clause updates every row. A `SELECT *` in production code breaks the
day someone adds a column. A string-concatenated query is an injection waiting to
happen. None of these are exotic — they are the most common ways SQL goes wrong, and
every one is prevented by a simple, checkable habit.

Readable SQL matters for the same reason readable code does: the query that is easy to
read is the one whose bug you can see. Most SQL correctness bugs are visible on the
page if the query is written plainly.

## Core Principles

- **Be explicit; never rely on defaults you did not write.** Name columns instead of
  `SELECT *`, name `INNER`/`LEFT` on every `JOIN`, and always write the `ON` clause.
  Implicit behavior is where surprises hide.
- **Every destructive statement is guarded.** A `DELETE` or `UPDATE` without a `WHERE`
  is almost always a bug. Write the `WHERE` first, verify with a `SELECT`, then change
  the verb. See [DML](13-dml.md).
- **Parameterize every value; never concatenate input into SQL.** This is the single
  rule that prevents SQL injection. There is no safe way to build queries by string
  concatenation. See [security](22-security.md).
- **Let the set do the work.** SQL is set-based; a single statement over a set beats a
  row-by-row loop in application code every time, both for correctness and speed.
- **Say what you mean about `NULL`.** Use `IS NULL` / `IS NOT NULL`, `COALESCE`, and
  be aware that `NOT IN`, `<>`, and aggregates all treat `NULL` specially.

## Best Practices

- **List columns explicitly** in `SELECT` and `INSERT`. `SELECT *` breaks views and
  application code when columns change; unnamed `INSERT` columns silently shift when
  the table is altered.
- **Qualify columns with table aliases** in any multi-table query, so a column added
  to one table later cannot make a bare column name ambiguous or, worse, silently
  resolve to the wrong table.
- **Prefer `EXISTS` over `IN (subquery)`** for existence checks — it short-circuits
  and is not broken by `NULL` in the subquery the way `NOT IN` is.
- **Filter before you aggregate.** Use `WHERE` to cut rows and `HAVING` only for
  conditions on the aggregate itself; `HAVING` on a plain column scans rows you could
  have excluded.
- **Keep predicates sargable.** Compare the bare column to a value (`created_at >=
  $1`), not a function of the column (`DATE(created_at) = $1`), so an index can be
  used. See [query-optimization](17-query-optimization.md).
- **Paginate with keyset (seek) pagination** for large tables, not `OFFSET n` —
  `OFFSET` scans and discards the skipped rows and gets slower every page.
- **Set `NOT NULL` and sensible defaults in DDL**, not in application code. The
  database is the last line of defense for data integrity.
- **Format for review**: one clause per line, joins and predicates aligned. A query
  you can read in a diff is a query whose bug a reviewer can catch.

## Examples

**Good Example** — explicit, guarded, parameterized, sargable

```sql
-- Explicit columns and JOIN type; aliased; parameterized value.
SELECT o.id, o.total, c.email
FROM orders   AS o
INNER JOIN customers AS c ON c.id = o.customer_id
WHERE o.status = $1              -- bound parameter, never string-concatenated
  AND o.created_at >= $2         -- sargable: bare column, index-usable
ORDER BY o.created_at DESC, o.id DESC   -- tiebreaker => stable keyset pagination
LIMIT 50;

-- Destructive statement: WHERE written first and verified with SELECT before UPDATE.
UPDATE orders SET status = 'archived'
WHERE status = 'closed' AND created_at < $1;   -- scoped, never table-wide
```

**Bad Example** — implicit, unguarded, injectable, non-sargable

```sql
-- SELECT * breaks the day a column is added; implicit CROSS JOIN via comma.
SELECT * FROM orders, customers
WHERE orders.customer_id = customers.id
  AND DATE(orders.created_at) = '2026-07-07'   -- function on column => no index
  AND status = '" + userInput + "';            -- string-concatenated => injection

-- No WHERE: archives EVERY order, including ones that are still open.
UPDATE orders SET status = 'archived';
```

## Common Mistakes

- `SELECT *` in application code or views, which breaks on schema change.
- `UPDATE`/`DELETE` without a `WHERE`, or with a `WHERE` that was never verified by a
  `SELECT` first.
- Building queries by string concatenation instead of bound parameters.
- `NOT IN (subquery)` that returns zero rows because the subquery contains a `NULL`.
- Wrapping the indexed column in a function (`LOWER`, `DATE`, `CAST`), defeating the
  index.
- `OFFSET`-based pagination on large tables, which degrades linearly with page number.

## AI Review Checklist

- Are all columns listed explicitly, with no `SELECT *` in persistent code?
- Does every `JOIN` state its type and `ON` condition, with table-qualified columns?
- Is every value a bound parameter, with zero string concatenation of input?
- Does every `UPDATE`/`DELETE` have a deliberate, scoped `WHERE`?
- Are predicates sargable (no functions on indexed columns)?
- Is `NULL` handled correctly (`IS NULL`, `EXISTS` over `NOT IN`)?

## Related

- `knowledge/sql/13-dml.md`
- `knowledge/sql/15-indexes.md`
- `knowledge/sql/22-security.md`
- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/100-common-antipatterns.md`
