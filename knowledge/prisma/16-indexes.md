---
id: prisma/16-indexes
topic: prisma
slug: indexes
title: "Prisma Indexes"
type: doc
order: 16
status: ready
tags: [prisma, indexes]
related: [prisma/15-performance, prisma/02-schema, prisma/05-migrations, prisma/09-filtering]
when_to_use: "Read before adding indexes to a Prisma schema or diagnosing slow filters, sorts, or joins."
---
# Prisma Indexes

## Purpose

This document defines how to declare and reason about database indexes in a Prisma
schema: `@id`, `@unique`, `@@unique`, and `@@index`, including composite indexes,
column order, and index type. Indexes are the primary lever for query
[performance](15-performance.md); Prisma declares them in `schema.prisma` and
materializes them through [migrations](05-migrations.md).

An index is a sorted lookup structure the database maintains so it can find rows without
scanning the whole table. The cost is extra storage and slower writes; the payoff is
reads that stay fast as the table grows.

## Why It Matters

The difference between an indexed and unindexed query is the difference between an
O(log n) lookup and an O(n) full table scan — imperceptible at 1,000 rows, catastrophic
at 10 million. Missing indexes are the single most common cause of production database
outages, and they are invisible in development because the dataset is small. At the same
time, indexing everything is its own failure: each index slows every `INSERT`/`UPDATE`
and consumes storage. Correct indexing means matching indexes precisely to the queries
the application actually runs.

## Core Principles

- **Index what you filter, sort, and join on.** An index helps a query only if the
  planner can use it for that query's `WHERE`, `ORDER BY`, or join column. Index to the
  query, not the column in the abstract.
- **Composite index order follows the equality-then-range rule.** Put columns used with
  equality first, then the range/sort column. `@@index([tenantId, createdAt])` serves
  `WHERE tenantId = ? ORDER BY createdAt`; the reverse order does not.
- **A composite index serves left-to-right prefixes.** `[a, b, c]` covers queries on
  `a`, `a+b`, and `a+b+c` — but not `b` alone. Design one composite index to cover
  several query shapes instead of many single-column ones.
- **Uniqueness is a constraint, not just an index.** `@unique` / `@@unique` enforce data
  integrity *and* create an index. Use them where the domain requires uniqueness.
- **Every index has a write cost.** More indexes = slower writes and more storage. Add
  them for real query patterns, remove ones nothing uses.

## Best Practices

- Add `@@index` for every column that appears in a hot `where`, `orderBy`, or relation
  filter; confirm with `EXPLAIN ANALYZE` that the planner uses it.
- Use composite indexes ordered equality-first to cover common multi-column filters (e.g.
  tenant + time-range list queries) in a single structure.
- Declare uniqueness with `@unique`/`@@unique` for natural keys (email, slug,
  `[tenantId, externalId]`) — it protects integrity and speeds lookups at once.
- Prefer a partial index for queries that always filter a flag (e.g. `deletedAt IS NULL`)
  when your database supports it; Prisma expresses this via native SQL in a migration.
- For large-text search, use the database's full-text/GIN index via raw migration SQL, not
  a plain B-tree on the text column.
- Create indexes concurrently on large live tables (`CREATE INDEX CONCURRENTLY` in a
  custom migration) so the migration does not lock writes.

## Examples

**Good Example** — composite index matched to the query

```prisma
model Order {
  id        String   @id @default(cuid())
  tenantId  String
  status    String
  createdAt DateTime @default(now())

  // Serves: where tenantId = ? and status = ? order by createdAt desc
  // Equality columns (tenantId, status) first, sort column (createdAt) last.
  @@index([tenantId, status, createdAt])
  @@unique([tenantId, id]) // natural composite key: integrity + fast lookup
}
```

```ts
// This query uses the composite index end to end — no full scan.
await prisma.order.findMany({
  where: { tenantId, status: "PAID" },
  orderBy: { createdAt: "desc" },
  take: 50,
});
```

**Bad Example** — wrong order and redundant indexes

```prisma
model Order {
  id        String   @id @default(cuid())
  tenantId  String
  status    String
  createdAt DateTime @default(now())

  // Range/sort column FIRST → planner can't use it for the equality filters,
  // so `where tenantId = ?` still scans. Column order is not cosmetic.
  @@index([createdAt, tenantId, status])

  // Redundant: [tenantId] is already a left prefix of a composite above in a real
  // schema — extra index that only slows writes and wastes storage.
  @@index([tenantId])
}
```

## Common Mistakes

- No index on the column a hot query filters or sorts by, causing full table scans at scale.
- Composite index column order that does not match the query (range/sort column first).
- A single-column index that duplicates the left prefix of an existing composite index.
- Indexing low-selectivity columns (e.g. a boolean) where the planner ignores the index anyway.
- Over-indexing: an index per column, degrading every write for reads that never run.
- Adding an index to a huge production table without `CONCURRENTLY`, locking writes during
  the migration.
- Assuming an index exists because a field is `@unique` on the *relation* — check the
  actual queried table.

## Production Tips

- Use `EXPLAIN ANALYZE` on real queries to verify index usage; the planner, not intuition,
  decides.
- Find unused indexes (e.g. Postgres `pg_stat_user_indexes`) and drop them to speed writes.
- Watch for index bloat on write-heavy tables and reindex on a schedule.
- Keep index changes in reviewed [migrations](05-migrations.md); never add them by hand in
  production out of band.

## AI Review Checklist

- Does every hot `where` / `orderBy` / join column have a supporting index?
- Are composite indexes ordered equality-first, then range/sort, to match their queries?
- Is each index actually used by a real query, with no redundant left-prefix duplicates?
- Are natural keys enforced with `@unique` / `@@unique` rather than a plain index?
- On large tables, are new indexes created `CONCURRENTLY` to avoid write locks?

## Related

- `knowledge/prisma/15-performance.md`
- `knowledge/prisma/02-schema.md`
- `knowledge/prisma/05-migrations.md`
- `knowledge/prisma/09-filtering.md`
