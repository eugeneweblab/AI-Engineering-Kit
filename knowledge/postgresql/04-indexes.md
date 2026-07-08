---
id: postgresql/04-indexes
topic: postgresql
slug: indexes
title: "Indexes"
type: doc
order: 4
status: ready
tags: [postgresql, indexes]
related: [postgresql/05-query-planner, postgresql/03-data-types, postgresql/16-performance, postgresql/08-jsonb, postgresql/20-vacuum]
when_to_use: "Read before adding, removing, or diagnosing an index, or when a query is slow."
---
# Indexes

## Purpose

This document defines how to design indexes so reads are fast without making writes
slow or the database bloated. It covers the index types PostgreSQL offers (B-tree,
GIN, GiST, BRIN, hash), composite and partial indexes, covering indexes, and how to
verify an index is actually used. An index is a deliberate trade of write cost and
storage for read speed — make each trade on purpose.

## Why It Matters

Indexes are the single biggest lever on query performance and one of the easiest
things to get wrong in both directions. Too few, and queries do sequential scans
that get slower as the table grows. Too many, or the wrong ones, and every
`INSERT`/`UPDATE`/`DELETE` pays to maintain indexes nobody reads, VACUUM works
harder, and disk fills. Worse, an index the query cannot use looks like insurance
but does nothing — the planner ignores it and you are slow *and* paying for it.
Indexing is where measured intent beats intuition every time.

## Core Principles

- **Index for the query, not the column.** Design indexes from the actual `WHERE`,
  `JOIN`, and `ORDER BY` clauses your workload runs, verified with `EXPLAIN`.
- **Every index has a write cost.** Reads get faster; writes get slower and the table
  grows. An unused index is pure overhead — find and drop it.
- **Order matters in composite indexes.** Put equality columns first, then the range
  or sort column. A `(a, b)` index serves `WHERE a = ?` but not `WHERE b = ?` alone.
- **Match the index type to the operator.** B-tree for equality/range/sort, GIN for
  `jsonb`/arrays/full-text containment, GiST for geometry/ranges, BRIN for huge
  naturally-ordered tables.
- **Verify usage, do not assume it.** A function on a column, a type mismatch, or low
  selectivity all cause the planner to skip an index you thought applied.

## Best Practices

- Build indexes with `CREATE INDEX CONCURRENTLY` in production so you do not hold an
  `ACCESS EXCLUSIVE` lock and block writes for the duration.
- Use a **partial index** (`WHERE ...`) when queries only ever touch a subset (e.g.
  `WHERE deleted_at IS NULL`); it is smaller, faster, and cheaper to maintain.
- Use an **expression index** when you always query a transformed value
  (`lower(email)`); otherwise the raw-column index cannot be used.
- Use a **covering index** (`INCLUDE (...)`) to enable index-only scans for hot,
  read-heavy queries, avoiding heap fetches.
- Add a **GIN index** for `jsonb` containment (`@>`), array membership, and full-text.
- Consider **BRIN** for very large append-only tables ordered by a column (e.g.
  time-series `created_at`); it is tiny compared to B-tree.
- Find unused indexes via `pg_stat_user_indexes` (`idx_scan = 0`) and drop them.
- After bulk loads or big data shifts, run `ANALYZE` so the planner has stats to pick indexes.

## Examples

**Good Example** — composite order, partial predicate, concurrent build

```sql
-- Workload: SELECT ... WHERE tenant_id = $1 AND status = 'open' ORDER BY created_at DESC
-- Equality columns first (tenant_id, status), sort column last (created_at).
-- Partial predicate matches the query, so the index stays small and hot.
CREATE INDEX CONCURRENTLY idx_tickets_open
  ON tickets (tenant_id, status, created_at DESC)
  WHERE status = 'open';                 -- excludes closed rows: smaller, faster

-- Expression index: the app filters on lower(email), so index the expression.
CREATE INDEX CONCURRENTLY idx_users_email_lower ON users (lower(email));
```

**Bad Example** — unusable and redundant indexes

```sql
-- Query filters lower(email) but the index is on the raw column → never used.
CREATE INDEX idx_users_email ON users (email);
SELECT * FROM users WHERE lower(email) = 'a@b.com';  -- seq scan despite the index

-- Wrong column order: serves WHERE tenant_id=?, useless for WHERE status=? alone.
CREATE INDEX idx_a ON tickets (tenant_id, status);
-- Redundant: (tenant_id) is already a left prefix of idx_a above → pure write overhead.
CREATE INDEX idx_b ON tickets (tenant_id);
```

## Common Mistakes

- Indexing a column but querying a function of it (`lower(col)`, `col::text`), so the
  index is never used.
- Getting composite column order wrong — leading with the range/sort column instead of equality.
- Creating redundant indexes where one is a left-prefix of another.
- Running plain `CREATE INDEX` in production and locking writes on a large table.
- Adding indexes speculatively and never checking `pg_stat_user_indexes` for `idx_scan = 0`.
- Using B-tree for `jsonb`/array containment where GIN is required, or vice versa.
- Forgetting to `ANALYZE` after a bulk load, so stale stats make the planner ignore new indexes.

## Production Tips

- Watch index bloat; heavily updated indexes accumulate dead entries — `REINDEX
  CONCURRENTLY` reclaims space without downtime.
- A dropped index cannot be un-dropped instantly on a huge table; before removing one,
  confirm zero scans over a full traffic cycle, not just a quiet hour.
- Index-only scans require the table to be well-vacuumed (visibility map current); a
  neglected VACUUM turns them back into heap fetches.

## AI Review Checklist

- Is each new index justified by a real query's `WHERE`/`JOIN`/`ORDER BY`?
- In composite indexes, do equality columns precede the range/sort column?
- Does `EXPLAIN (ANALYZE)` confirm the index is actually used (not a seq scan)?
- Is the query free of functions/casts on the indexed column that would disable it?
- Is `CREATE INDEX CONCURRENTLY` used for production builds on large tables?
- Is the index type right for the operator (GIN for `jsonb`/arrays, BRIN for huge ordered tables)?
- Have unused indexes (`idx_scan = 0`) been identified and removed?

## Related

- `knowledge/postgresql/05-query-planner.md`
- `knowledge/postgresql/03-data-types.md`
- `knowledge/postgresql/16-performance.md`
- `knowledge/postgresql/08-jsonb.md`
- `knowledge/postgresql/20-vacuum.md`
