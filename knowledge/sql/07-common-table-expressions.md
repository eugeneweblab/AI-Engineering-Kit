---
id: sql/07-common-table-expressions
topic: sql
slug: common-table-expressions
title: "Common Table Expressions"
type: doc
order: 7
status: ready
tags: [sql, common-table-expressions]
related: [sql/06-subqueries, sql/08-window-functions, sql/17-query-optimization, sql/16-query-planning]
when_to_use: "Read before using WITH, refactoring a nested subquery for readability, or writing a recursive/hierarchical query."
---
# Common Table Expressions

## Purpose

This document defines how to use Common Table Expressions (CTEs) — named, temporary
result sets introduced with `WITH` and referenced by the query that follows. It covers
plain CTEs for readability, recursive CTEs for hierarchies, and the performance
trade-offs an agent must weigh before choosing one over a [subquery](06-subqueries.md).

A CTE lets you name an intermediate step: `WITH recent_orders AS (...) SELECT ...`. Use
it to flatten nested subqueries, to reference the same result set more than once, or to
walk a tree/graph with `WITH RECURSIVE`.

## Why It Matters

CTEs are the primary tool for making complex SQL readable, but "readable" and "fast" are
not the same. In older PostgreSQL (before 12) and some engines, a CTE was an **optimization
fence**: it was materialized once and the planner could not push filters through it,
turning a tidy query into a slow one. Since PostgreSQL 12 a non-recursive CTE is inlined
by default unless referenced multiple times or marked `MATERIALIZED`. An agent that does
not know its engine's inlining rules can write clean SQL that scans millions of rows it
should have filtered away.

## Core Principles

- **CTEs are for clarity and reuse, not a performance trick.** They rarely make a query
  faster; their value is naming steps and avoiding repetition.
- **Know your engine's fence behavior.** PostgreSQL ≥12 inlines single-use CTEs and lets
  you force materialization with `MATERIALIZED`/`NOT MATERIALIZED`. SQL Server and Oracle
  inline by default. Do not assume; check.
- **Recursive CTEs need a termination guarantee.** The recursive term must eventually
  return no rows, or the query loops forever. Cyclic data requires explicit cycle
  detection.
- **A CTE is scoped to the single statement that follows it.** It is not a view and is not
  reused across statements — for that, use a [view](18-views.md).
- **Chain, don't nest.** Multiple CTEs in one `WITH` (comma-separated) read top-to-bottom
  and are far clearer than pyramids of inline subqueries.

## Best Practices

- Name each CTE for the *concept* it produces (`active_users`, `monthly_totals`), not the
  mechanics (`t1`, `sub`).
- Prefer a CTE over a repeated subquery when the same derived set is used twice —
  computing it once is both clearer and usually cheaper.
- For recursion, always include a bounded stop condition (a depth counter or a `WHERE`
  that shrinks) and, for graphs, a `UNION` with a visited-path array to break cycles.
- On PostgreSQL, add `MATERIALIZED` only when you deliberately want a one-time evaluation
  (e.g. a CTE calling a `VOLATILE` function); otherwise let the planner inline.
- Keep the final `SELECT` thin — do filtering and aggregation inside the named CTEs so the
  data flow reads as a pipeline.
- If a CTE is referenced across many queries, promote it to a [view](18-views.md) or
  [materialized view](19-materialized-views.md).

## Examples

**Good Example** — chained CTEs express a clear pipeline; recursion terminates

```sql
-- Walk an org chart from a given manager down, capping depth to prevent runaway
-- recursion on bad data.
WITH RECURSIVE reports AS (
    SELECT id, manager_id, name, 1 AS depth
    FROM employees
    WHERE id = 42                       -- anchor: the starting manager
    UNION ALL
    SELECT e.id, e.manager_id, e.name, r.depth + 1
    FROM employees AS e
    JOIN reports AS r ON e.manager_id = r.id
    WHERE r.depth < 10                  -- termination guard: hard depth cap
)
SELECT name, depth FROM reports ORDER BY depth;
```

**Bad Example** — recursive CTE with no depth bound loops on cyclic data

```sql
WITH RECURSIVE reports AS (
    SELECT id, manager_id, name FROM employees WHERE id = 42
    UNION ALL
    SELECT e.id, e.manager_id, e.name
    FROM employees AS e
    JOIN reports AS r ON e.manager_id = r.id
    -- No depth cap and no cycle detection: if two employees report to each
    -- other, this recurses forever until the query is killed.
)
SELECT * FROM reports;
```

## Common Mistakes

- Assuming a CTE is faster than a subquery — on most engines it is inlined to the same
  plan, and on old PostgreSQL it was slower.
- Recursive CTEs with no depth cap or cycle detection, hanging on cyclic or deep data.
- Referencing a CTE in a *later* statement, expecting it to persist — its scope is one
  statement only.
- Forcing `MATERIALIZED` out of habit, defeating filter pushdown and scanning too much.
- Deeply nesting CTEs inside CTEs when a flat, comma-separated chain would read better.

## Production Tips

- Run `EXPLAIN ANALYZE` after refactoring subqueries into CTEs — confirm the plan did not
  change for the worse (an accidental materialization fence).
- Set `statement_timeout` so a runaway recursive CTE fails fast instead of exhausting the
  connection.
- For expensive multi-use CTEs that are stable across a session, consider a
  [materialized view](19-materialized-views.md) refreshed on a schedule instead.

## AI Review Checklist

- Does every recursive CTE have a bounded termination (depth cap or shrinking set)?
- Is cycle detection present when the recursion walks a graph, not a tree?
- Is a `MATERIALIZED` hint used only where a one-time evaluation is actually intended?
- Is the CTE named for its meaning, and is repeated logic computed once?
- Was the plan verified with `EXPLAIN`, not assumed faster than a [subquery](06-subqueries.md)?
- Should this be a [view](18-views.md) instead, because it is reused across statements?

## Related

- `knowledge/sql/06-subqueries.md`
- `knowledge/sql/08-window-functions.md`
- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/16-query-planning.md`
- `knowledge/sql/18-views.md`
