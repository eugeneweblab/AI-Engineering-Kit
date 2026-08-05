---
id: sql/15-indexes
topic: sql
slug: indexes
title: "SQL Indexes"
type: doc
order: 15
status: ready
tags: [sql, indexes]
related: [sql/16-query-planning, sql/17-query-optimization, sql/12-ddl, sql/23-performance, sql/100-common-antipatterns]
when_to_use: "Read before adding or removing an index, or when a query is slow and you suspect it is scanning too many rows."
---
# SQL Indexes

## Purpose

This document defines how to design indexes that make reads fast without making writes
slow or wasting storage. It is written so an agent can decide *which* index a query needs,
in *what column order*, and when an index is a liability rather than a fix.

An index is a secondary data structure (usually a B-tree) that lets the planner find rows
without scanning the whole table. It trades write cost and disk for read speed. Indexing
well means knowing your access patterns; indexing blindly means paying that cost for no
benefit.

## Why It Matters

The difference between an indexed and unindexed query on a large table is often
milliseconds versus minutes — and the unindexed version gets linearly worse as the table
grows, so a query that was fine at launch times out at scale. But indexes are not free:
every index must be updated on every `INSERT`/`UPDATE`/`DELETE`, so an over-indexed table
has slow writes and bloated storage. The goal is the *minimum* set of indexes that serves
the real query workload.

## Core Principles

- **Index to match how you query, not how you store.** The columns in your `WHERE`,
  `JOIN`, and `ORDER BY` clauses drive index design, not the table definition.
- **Composite index column order follows the equality-range-sort rule.** Equality-filtered
  columns first, then one range column, then columns needed for ordering. Order is not
  arbitrary; a wrong order makes the index unusable for the query.
- **The index must be sargable to be used.** Wrapping an indexed column in a function or
  a leading wildcard (`LIKE '%x'`) forces a full scan (see [query planning](16-query-planning.md)).
- **Every index is a write tax.** Add one only when a real query needs it; drop unused
  and redundant ones.
- **Verify with the plan, never by intuition.** Confirm the index is actually used with
  `EXPLAIN`; an "obvious" index is often ignored for good reasons.

## Best Practices

- Index foreign keys — they are the join and cascade-delete columns and are almost always
  needed, yet the database does not create them automatically.
- Prefer covering indexes (`INCLUDE` columns, or all needed columns in the index) for hot
  read paths so the query is served index-only, skipping the table (heap) lookup.
- Use a partial index (`WHERE status = 'active'`) when queries only ever touch a subset;
  it is smaller and cheaper to maintain than a full index.
- Match the index type to the operator: B-tree for equality/range/sort, GIN for full-text
  and JSONB containment, GiST for geometric/range overlap, hash rarely.
- Build and drop indexes concurrently on live tables (`CREATE INDEX CONCURRENTLY`) to
  avoid blocking writes; it cannot run inside a transaction.
- Drop redundant indexes: an index on `(a)` is redundant when `(a, b)` exists, because the
  composite serves leading-column lookups too.
- Reassess after every access-pattern change; yesterday's index can become dead weight.

## Examples

**Good Example** — composite order matches the query, and it is sargable

```sql
-- Query: WHERE tenant_id = $1 AND created_at >= $2 ORDER BY created_at DESC
CREATE INDEX idx_events_tenant_created
  ON events (tenant_id, created_at DESC);   -- equality col first, then range/sort col
-- The planner seeks tenant_id, then range-scans created_at already in sort order:
-- no separate sort step, no heap scan of unrelated tenants.
SELECT * FROM events
 WHERE tenant_id = $1 AND created_at >= $2
 ORDER BY created_at DESC;
```

**Bad Example** — non-sargable predicate defeats the index

```sql
CREATE INDEX idx_users_email ON users (email);

-- Wrapping the column in a function makes the index unusable → full table scan.
SELECT * FROM users WHERE lower(email) = 'a@b.com';
-- Fix: index the expression instead, e.g. CREATE INDEX ... ON users (lower(email)),
-- or store email normalized so the raw column is queried directly.
```

## Common Mistakes

- No index on foreign-key columns, making joins and cascade deletes scan the child table.
- Wrong composite column order, so the index cannot serve the query's leading predicate.
- Non-sargable `WHERE` (function on the column, leading `%`, implicit type cast) that
  silently forces a sequential scan.
- Over-indexing: many single-column indexes that duplicate a composite and tax writes.
- Adding indexes without checking `EXPLAIN`, so the "fix" is never actually used.
- Indexing very low-cardinality columns (a boolean) where a scan is cheaper than the seek.
- Building indexes non-concurrently on a hot table, blocking all writes during the build.

## Production Tips

- Query `pg_stat_user_indexes` (or the equivalent) for `idx_scan = 0` to find and drop
  never-used indexes that only slow writes.
- Watch for index bloat after heavy update/delete churn; rebuild with
  `REINDEX CONCURRENTLY` when the index grows far beyond its data.
- Before adding an index to fix one slow query, confirm no existing index can be reordered
  or extended to serve it — fewer, wider indexes beat many narrow ones.

## AI Review Checklist

- Does an index exist for each hot query's `WHERE`/`JOIN`/`ORDER BY` columns?
- Is composite column order equality-then-range-then-sort?
- Are all `WHERE` predicates sargable (no function/cast on the indexed column, no leading `%`)?
- Are foreign-key columns indexed?
- Was the index confirmed as used via `EXPLAIN`, not assumed?
- Are redundant and never-scanned indexes removed to protect write speed?
- Are indexes on live tables built/dropped concurrently?

## Related

- `knowledge/sql/16-query-planning.md`
- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/12-ddl.md`
- `knowledge/sql/23-performance.md`
- `knowledge/sql/100-common-antipatterns.md`
