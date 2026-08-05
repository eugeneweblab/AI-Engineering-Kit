---
id: sql/00-overview
topic: sql
slug: overview
title: "SQL Overview"
type: doc
order: 0
status: ready
tags: [sql, overview]
related: [sql/01-select, sql/02-filtering, sql/05-joins, sql/17-query-optimization, sql/26-best-practices]
when_to_use: "Read before writing or reviewing any SQL query, to find the right topic doc and shared conventions."
---
# SQL Overview

## Purpose

This document is the map for the `sql` topic. It orients an agent to how a SQL query
is built, which sub-topic owns each concern, and the conventions shared across every
doc here. Read it first, then jump to the specific document for the clause you are
writing or reviewing.

SQL is *declarative*: you describe the result you want, and the engine decides how to
produce it. That gap between what you write and what runs is where correctness and
performance bugs hide. These docs close that gap by teaching the rules the engine
actually enforces.

## Why It Matters

A single query can return silently wrong results — duplicated rows from a bad join,
dropped rows from a `NULL` comparison, an average computed over the wrong set — and no
error is raised. Unlike a crash, a wrong query looks like it worked. The blast radius
is every downstream report, API response, and business decision built on that data.
SQL is also the layer where a full table scan turns a 10 ms request into a 10 s one.
Getting the query right is therefore both a correctness and a performance obligation.

## Core Principles

- **Know the logical evaluation order.** SQL clauses do not run top to bottom. They run
  `FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `DISTINCT` → `ORDER BY` →
  `LIMIT`. This order explains why a `SELECT` alias is not visible in `WHERE`, and why
  `WHERE` filters before aggregation while `HAVING` filters after.
- **`NULL` is not a value; it is "unknown".** Any comparison with `NULL` yields
  `UNKNOWN`, not `TRUE`. This single rule drives most surprising query results.
- **Sets have no inherent order.** Rows come back in whatever order is convenient for
  the engine unless you write `ORDER BY`. Never rely on insertion or index order.
- **The query optimizer decides execution, not you.** Write clear, sargable predicates
  and let indexes and the planner do their job; verify with `EXPLAIN`, not intuition.
- **Portability is a spec, not an accident.** Standard SQL and vendor dialects
  (PostgreSQL, MySQL, SQL Server, SQLite) differ. Target one dialect deliberately.

## How These Docs Fit Together

- **[Select](01-select.md)** — projecting columns, aliases, `DISTINCT`, and the logical
  clause order. Start here.
- **[Filtering](02-filtering.md)** — the `WHERE` clause, `NULL` handling, and writing
  sargable predicates that use indexes.
- **[Sorting](03-sorting.md)** — `ORDER BY`, `NULL` ordering, and correct pagination.
- **[Grouping](04-grouping.md)** — `GROUP BY`, aggregates, and `HAVING` vs `WHERE`.
- **[Joins](05-joins.md)** — combining tables without multiplying or dropping rows.

Later docs in the topic build on these five: [subqueries](06-subqueries.md),
[CTEs](07-common-table-expressions.md), [window functions](08-window-functions.md),
[indexes](15-indexes.md), and [query optimization](17-query-optimization.md).

## Conventions Used in Every Doc

- Examples target **PostgreSQL syntax** unless a doc says otherwise; dialect
  differences are called out inline where they change behavior.
- Keywords are UPPERCASE (`SELECT`, `WHERE`); identifiers are `snake_case`.
- Every example uses a small, consistent schema: `users(id, email, created_at)`,
  `orders(id, user_id, total, status, created_at)`.
- Good/Bad pairs show the *same intent*; the Bad version compiles but is wrong or slow.

## Best Practices

- Read the specific clause doc before writing that clause — the rules are non-obvious.
- Prefer explicit `JOIN ... ON` over comma joins, and name every column instead of
  `SELECT *`, so the query survives schema changes.
- Run `EXPLAIN (ANALYZE)` on any query that touches a large table before shipping it.
- Test queries against data containing `NULL`s, duplicates, and empty result sets —
  the three cases that expose most SQL bugs.

## Common Mistakes

- Assuming clauses evaluate top-to-bottom, then being surprised an alias is not visible.
- Treating `NULL` like an ordinary value in comparisons and `NOT IN` lists.
- Relying on result order without `ORDER BY`.
- Copying a query across dialects without checking behavior differences.

## AI Review Checklist

- Does the query name the correct sub-topic concern, and did you apply that doc's rules?
- Is `NULL` handled explicitly wherever a column can be null?
- Is there an `ORDER BY` anywhere the caller depends on order?
- Was the query checked with `EXPLAIN` if it hits a large table?
- Is the target SQL dialect stated and consistent?

## Related

- `knowledge/sql/01-select.md`
- `knowledge/sql/02-filtering.md`
- `knowledge/sql/05-joins.md`
- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/26-best-practices.md`
