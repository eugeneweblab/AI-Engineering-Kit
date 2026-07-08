---
id: sql/18-views
topic: sql
slug: views
title: "Views"
type: doc
order: 18
status: ready
tags: [sql, views]
related: [sql/19-materialized-views, sql/07-common-table-expressions, sql/22-security, sql/23-performance, sql/17-query-optimization]
when_to_use: "Read before creating a view, replacing repeated query logic with a named abstraction, or exposing a curated subset of tables to consumers."
---
# Views

## Purpose

This document defines when and how to use SQL views: named, stored `SELECT`
statements that behave like read-only (sometimes writable) virtual tables. It is
written so an agent can introduce a view that simplifies consumers without hiding
a performance cliff or a security hole.

A view stores a *query*, not data. Every time you read a view the engine expands
its definition and runs the underlying query. This is the opposite of a
[materialized view](19-materialized-views.md), which stores the *result*.

## Why It Matters

Views are the primary tool for encapsulation in SQL. They let you name a complex
join, hide sensitive columns, and present a stable interface while the physical
schema changes underneath. Used well, they remove duplicated query logic from
dozens of call sites. Used badly, they become invisible performance traps: a
five-table join wrapped in a view looks like a single innocent table to the
developer who queries it, then joins it to three more views. The cost compounds
silently because nothing at the call site reveals the work being done.

## Core Principles

- **A view is a query, so it costs what its query costs.** Reading a view every
  time re-runs its definition. Treat `SELECT * FROM my_view` as running the whole
  underlying statement, because it does.
- **Views abstract, they do not accelerate.** If you need speed, you need indexes
  on the base tables or a [materialized view](19-materialized-views.md) — never a
  plain view.
- **Keep view definitions shallow.** Views built on views built on views defeat
  the planner and hide cost. Prefer one layer over base tables.
- **Views are a security boundary, not just a convenience.** Granting `SELECT` on
  a view instead of the base table is a standard way to expose only chosen
  columns and rows.
- **Name the contract.** Consumers depend on a view's column names and types.
  Changing them is a breaking API change, so version and communicate it.

## Best Practices

- Use views to eliminate a query that is copy-pasted across the codebase; the view
  becomes the single source of truth for that shape.
- List columns explicitly in the view definition (`SELECT id, email, ...`) rather
  than `SELECT *`, so adding a base-table column does not silently change the
  view's contract or leak new data.
- Grant `SELECT` on a view and revoke it on the base table when the goal is to
  restrict column or row access; combine with a `WHERE` clause for row filtering.
- Prefer views for read paths only. Updatable views are supported for simple
  single-table cases, but multi-table or aggregated views are not updatable and
  the restrictions vary by engine — write to base tables directly instead.
- In PostgreSQL, use `CREATE OR REPLACE VIEW` for non-breaking changes; you cannot
  drop or reorder existing columns this way, which protects consumers.
- Add `WITH CHECK OPTION` to an updatable view so writes that would fall outside
  the view's `WHERE` clause are rejected instead of silently vanishing from view.
- Document each view's underlying cost (row counts, joins) in a comment so callers
  understand what a "simple" `SELECT` really triggers.

## Examples

**Good Example** — a view as a curated, secure read interface

```sql
-- Purpose: expose active customers WITHOUT their password hash or PII columns.
-- Callers get a stable, safe shape; base table can change underneath.
CREATE VIEW active_customers AS
SELECT
    id,
    display_name,
    country_code,
    created_at
FROM customers
WHERE status = 'active'
WITH CHECK OPTION;   -- an insert/update via the view must keep status='active'

-- Grant read on the view, not the table, so consumers never see password_hash.
GRANT SELECT ON active_customers TO reporting_role;
REVOKE SELECT ON customers      FROM reporting_role;
```

**Bad Example** — stacked views hiding a runaway query

```sql
-- Each layer looks cheap; together they force a 4-table join on every read
-- and the planner cannot see through the nesting to optimize well.
CREATE VIEW v_orders     AS SELECT * FROM orders;              -- SELECT * leaks new cols
CREATE VIEW v_enriched   AS SELECT * FROM v_orders  o JOIN customers c ON c.id = o.customer_id;
CREATE VIEW v_reporting  AS SELECT * FROM v_enriched e JOIN products  p ON p.id = e.product_id;

-- Caller thinks this is one table; it is a 4-way join with no supporting index hint.
SELECT * FROM v_reporting WHERE country_code = 'US';
```

## Common Mistakes

- Treating a view as if it caches or speeds up its query; it does neither.
- Using `SELECT *` in the definition, so new base columns silently join the
  contract and can leak sensitive data to view consumers.
- Nesting views several layers deep, hiding cost and confusing the query planner.
- Filtering on a view whose definition already aggregates or windows, forcing the
  engine to materialize the full inner result before applying your `WHERE`.
- Assuming a multi-table view is updatable; inserts/updates fail or behave
  unexpectedly across engines.
- Changing a view's column names or types without treating it as a breaking change
  to every downstream consumer.

## Production Tips

- Before shipping a view, run `EXPLAIN` on a representative query *against the
  view* to confirm predicates push down to the base tables and use indexes.
- Track view dependencies (Postgres: `pg_depend`) before dropping a base column;
  a `DROP` or type change can break views in ways migrations won't flag until run.
- If a heavily read view repeatedly re-computes an expensive aggregate, that is the
  signal to convert it to a [materialized view](19-materialized-views.md).

## AI Review Checklist

- Does the view list columns explicitly rather than using `SELECT *`?
- Is the view being used for abstraction/security, not mistaken for a cache?
- Are views nested more than one level deep (a smell to flatten)?
- If used as a security boundary, is `SELECT` revoked on the base table?
- For an updatable view, is `WITH CHECK OPTION` present where writes must stay in
  scope?
- Has `EXPLAIN` confirmed predicates push down and indexes are used?
- Would a [materialized view](19-materialized-views.md) be the correct tool if the
  goal is actually speed?

## Related

- `knowledge/sql/19-materialized-views.md`
- `knowledge/sql/07-common-table-expressions.md`
- `knowledge/sql/22-security.md`
- `knowledge/sql/23-performance.md`
- `knowledge/sql/17-query-optimization.md`
