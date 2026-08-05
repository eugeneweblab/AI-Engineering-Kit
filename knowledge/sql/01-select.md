---
id: sql/01-select
topic: sql
slug: select
title: "Select"
type: doc
order: 1
status: ready
tags: [sql, select, DISTINCT, EXTRACT, HAVING, EXISTS, email, LIMIT]
related: [sql/00-overview, sql/02-filtering, sql/03-sorting, sql/04-grouping, sql/05-joins]
when_to_use: "Read before writing any query that projects columns, uses DISTINCT, or relies on clause evaluation order."
---
# Select

## Purpose

This document defines how to project data with `SELECT`: which columns to return, how
aliases work, when `DISTINCT` is correct, and — most importantly — the logical order in
which SQL evaluates a query. Get the evaluation order right and the rest of the query
language stops surprising you.

`SELECT` names the *shape* of the result. The rows it operates on are already chosen by
`FROM`, `WHERE`, and `GROUP BY` before `SELECT` runs, which is why some references that
feel like they should work do not.

## Why It Matters

`SELECT *` in production code is a latent bug: a new column silently widens every result,
breaks positional `INSERT ... SELECT`, and ships data (PII, large blobs) no caller asked
for. Misunderstanding evaluation order produces "column does not exist" errors that look
like typos but are really scope errors. A stray `DISTINCT` added to "fix" duplicates
hides a real join bug and forces an expensive sort. These are everyday mistakes with
outsized cost, which is why the projection clause deserves its own rules.

## Core Principles

- **SQL evaluates logically, not textually.** The order is `FROM` → `WHERE` →
  `GROUP BY` → `HAVING` → `SELECT` → `DISTINCT` → `ORDER BY` → `LIMIT`. `SELECT` is
  near the end, so its aliases and computed columns do not exist yet in `WHERE` or
  `GROUP BY`.
- **Name every column you need.** Explicit column lists are a contract; `SELECT *` is
  an open-ended promise that breaks when the schema changes.
- **`DISTINCT` removes duplicate *rows*, not duplicate values.** It applies to the whole
  projected row and forces a sort or hash. Reach for it only when duplicates are real
  and expected, not to paper over a bad join.
- **An alias renames output; it does not create a variable.** `ORDER BY` can use a
  `SELECT` alias (it runs after `SELECT`); `WHERE` and `GROUP BY` cannot.

## Best Practices

- List columns explicitly and qualify them with the table name or alias in multi-table
  queries (`u.email`, not `email`) so the query survives a column being added elsewhere.
- Use `AS` for aliases and quote them only when they contain spaces or reserved words.
- Prefer `EXISTS` over `SELECT DISTINCT` when you only need to know a row matches — it
  stops at the first match instead of de-duplicating the whole set.
- Keep expressions in `SELECT` simple; push heavy computation into a CTE or the
  application layer when it obscures the query's intent.
- If you must repeat a computed column in `WHERE`, use a subquery or CTE rather than
  copying the expression — a `SELECT` alias is not visible in `WHERE`.

## Examples

**Good Example** — explicit columns, alias used only where legal

```sql
-- Columns are named and qualified, so adding a column to `users`
-- cannot change this result. The alias `signup_year` is used in ORDER BY
-- (evaluated after SELECT), which is allowed.
SELECT u.id,
       u.email,
       EXTRACT(YEAR FROM u.created_at) AS signup_year
FROM users AS u
WHERE u.created_at >= DATE '2026-01-01'  -- filters raw column, not the alias
ORDER BY signup_year DESC;
```

**Bad Example** — `SELECT *`, alias referenced before it exists

```sql
SELECT *,                                    -- ships every column, incl. future ones
       EXTRACT(YEAR FROM created_at) AS yr
FROM users
WHERE yr >= 2026;   -- ERROR: `yr` does not exist yet; SELECT runs after WHERE
```

## Common Mistakes

- Using `SELECT *` in application code, views, or `INSERT ... SELECT`, so a schema
  change silently alters behavior.
- Referencing a `SELECT` alias in `WHERE`, `GROUP BY`, or `HAVING` and expecting it to
  resolve.
- Adding `DISTINCT` to remove duplicates that a correct `JOIN` would never have created.
- Forgetting that `DISTINCT` applies to the entire row, so adding a unique-looking
  column (like `id`) makes it a no-op.
- Leaving columns unqualified in a multi-table query, causing ambiguous-column errors
  or silently binding to the wrong table.

## Production Tips

- Grep the codebase for `SELECT *` in migrations, views, and ORMs during review; each
  one is a place a future column can leak or break a caller.
- When a `DISTINCT` appears, investigate the join first — the duplicate usually means a
  missing join condition or a one-to-many relationship that needs aggregation instead.

## AI Review Checklist

- Are all needed columns named explicitly instead of `SELECT *`?
- Are columns qualified with a table alias in any multi-table query?
- Does any `WHERE`/`GROUP BY`/`HAVING` reference a `SELECT` alias (which is illegal)?
- Is every `DISTINCT` justified by real duplicates, not masking a join bug?
- Could `EXISTS` replace a `SELECT DISTINCT` used only for existence testing?

## Related

- `knowledge/sql/00-overview.md`
- `knowledge/sql/02-filtering.md`
- `knowledge/sql/03-sorting.md`
- `knowledge/sql/04-grouping.md`
- `knowledge/sql/05-joins.md`
