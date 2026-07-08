---
id: prisma/15-performance
topic: prisma
slug: performance
title: "Performance"
type: doc
order: 15
status: ready
tags: [prisma, performance]
related: [prisma/16-indexes, prisma/11-relations-loading, prisma/10-pagination, prisma/17-raw-sql, prisma/26-observability]
when_to_use: "Read before diagnosing slow Prisma queries, N+1 problems, connection exhaustion, or high database load."
---
# Performance

## Purpose

This document defines how to make Prisma Client queries fast and how to spot the
patterns that make them slow: N+1 access, over-fetching columns, unbounded reads,
missing indexes, and connection-pool exhaustion. It covers what the Client does at the
SQL level so an agent can reason about cost, not guess. Indexing is deep enough to have
its own document — see [indexes](16-indexes.md).

## Why It Matters

Prisma's ergonomic API hides the SQL, which is exactly why performance bugs slip in: a
one-line `.map()` over a relation compiles to hundreds of round trips, and a
`findMany()` with no `take` scans an entire table that was small in development and
enormous in production. These problems are load-dependent — invisible at 100 rows,
fatal at 10 million — so they pass review and code that "worked" takes down the database
under real traffic. Performance must be reasoned about from the query shape, before the
data grows.

## Core Principles

- **Know the SQL your query becomes.** Every Client call maps to concrete SQL. If you
  cannot picture the query and its scan, you cannot judge its cost. Enable query logging
  while developing.
- **Fetch only what you use.** Use `select` (or `include` with nested `select`) to name
  the columns you need. `SELECT *` on wide rows wastes I/O and bandwidth on every request.
- **Never fetch unbounded sets.** Every list read needs a `take` limit and cursor or
  offset [pagination](10-pagination.md). "Load all rows" is a bug waiting for volume.
- **Solve N+1 with the query engine, not loops.** Use a single `include`/`select` (or
  `findMany` with `in`), not a query per parent — see [relations loading](11-relations-loading.md).
- **Push work into the database.** Filtering, counting, aggregating, and ordering belong
  in SQL, not in JavaScript after fetching everything.

## Best Practices

- Turn on `log: ["query"]` (or the query-event API) in development to see generated SQL
  and catch N+1 and full scans early.
- Prefer a single query with `include`/`select` over sequential lookups; use the
  `relationLoadStrategy: "join"` option when a database-side JOIN beats two round trips.
- Use `select` to project columns; avoid pulling large text/JSON/blob fields you do not
  render.
- Batch independent reads that must run together with `prisma.$transaction([...])` or
  `Promise.all` so they share fewer round trips.
- Use `count`, `aggregate`, and `groupBy` instead of fetching rows to count or sum them
  in memory.
- Size the connection pool deliberately with `connection_limit`; in serverless, put a
  pooler (PgBouncer / Prisma Accelerate) in front so functions do not exhaust connections.
- Add indexes for the columns you filter, sort, and join on — the single highest-leverage
  fix; see [indexes](16-indexes.md).
- Drop to [raw SQL](17-raw-sql.md) for queries the Client expresses poorly (complex
  window functions, recursive CTEs), rather than post-processing in JS.

## Examples

**Good Example** — one bounded, projected query

```ts
// Single query: relation loaded via the engine, only needed columns, hard limit.
const posts = await prisma.post.findMany({
  where: { published: true },
  select: {
    id: true,
    title: true,
    author: { select: { id: true, name: true } }, // no N+1: joined in one call
  },
  orderBy: { createdAt: "desc" },
  take: 20, // bounded read — safe as the table grows
});
```

**Bad Example** — N+1, over-fetch, unbounded

```ts
// No take → loads every published post, all columns, however many million exist.
const posts = await prisma.post.findMany({ where: { published: true } });

// One extra query PER post → N+1. 20 posts = 21 queries; 10k posts = 10,001.
for (const post of posts) {
  post.author = await prisma.user.findUnique({ where: { id: post.authorId } });
}

// Counting in JS after fetching everything, instead of prisma.post.count().
const total = posts.length;
```

## Common Mistakes

- Fetching a relation in a loop instead of a single `include`/`select` (classic N+1).
- `findMany` with no `take`, scanning and transferring an entire table.
- Selecting all columns when the response uses three of them.
- Counting or aggregating in JavaScript instead of `count` / `aggregate` / `groupBy`.
- Offset pagination with large `skip` on big tables (the DB still scans skipped rows) —
  use cursor pagination.
- Ignoring the connection pool in serverless, exhausting database connections under load.
- Assuming a query is fine because it is fast on a dev database with few rows.

## Production Tips

- Log slow queries at the database (e.g. Postgres `log_min_duration_statement`) and alert
  on regressions; correlate with Prisma query metrics via [observability](26-observability.md).
- Read `EXPLAIN ANALYZE` for hot queries to confirm they use the index you expect.
- Track pool saturation and query duration percentiles, not just averages — tail latency
  is where users feel it.
- Load-test with production-scale row counts; dev-sized data hides every scaling bug here.

## AI Review Checklist

- Does every list query have a `take` limit and real pagination?
- Are relations loaded with a single `include`/`select`, never a per-row query?
- Does the query `select` only the columns the caller uses?
- Are counts and aggregates done in SQL (`count`/`aggregate`/`groupBy`), not in JS?
- Are filtered/sorted/joined columns backed by [indexes](16-indexes.md)?
- Is the connection pool sized for the runtime, with a pooler in serverless?

## Related

- `knowledge/prisma/16-indexes.md`
- `knowledge/prisma/11-relations-loading.md`
- `knowledge/prisma/10-pagination.md`
- `knowledge/prisma/17-raw-sql.md`
- `knowledge/prisma/26-observability.md`
