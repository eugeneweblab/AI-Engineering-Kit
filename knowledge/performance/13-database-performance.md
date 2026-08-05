---
id: performance/13-database-performance
topic: performance
slug: database-performance
title: "Performance — Database Access"
type: doc
order: 13
status: ready
tags: [performance, database-performance, OFFSET, log_min_duration_statement, statement_timeout, LIMIT]
related: [performance/15-query-optimization, performance/14-api-performance, performance/08-caching, performance/16-profiling, performance/05-network]
when_to_use: "Read before designing schema, adding indexes, or diagnosing a slow database-backed endpoint."
---
# Performance — Database Access

## Purpose

This document defines how to keep a database fast under real load: connection
management, indexing, schema shape, transactions, and where to spend the caching
budget. It is written so an agent can build or review data-access code without
turning the database into the bottleneck the whole system waits on.

This is the *system-level* view of the database. For rewriting a single slow
statement, see [query optimization](15-query-optimization.md); the two are meant to
be read together.

## Why It Matters

The database is the most common backend bottleneck because it is the one shared,
stateful resource every request touches. Scaling application servers is easy; scaling
a database is not. A missing index turns a millisecond lookup into a full-table scan
that gets slower as data grows, so the app that was fine in testing collapses in
production. Because the database serializes contended work, one slow query does not
just slow itself — it holds connections and locks that stall unrelated requests. Small
data-layer mistakes therefore produce system-wide, load-dependent failures that never
appear on a developer laptop.

## Core Principles

- **Every query hits an index or you have a bug.** An unindexed query on a growing
  table is a latency time bomb; it works today and pages you at 10x the rows.
- **Round-trips dominate.** Latency is mostly the count of times the app talks to the
  database, not the work per query. Fetch in sets, not in loops.
- **Fetch only what you use.** Every column and row you return costs I/O, network, and
  memory on both ends. `SELECT *` is a default to remove, not to keep.
- **Hold locks and transactions for the shortest possible time.** Long transactions
  block others and bloat the database's version history.
- **Pool connections; never open per request.** Connections are expensive and finite;
  exhausting the pool is a total outage, not a slowdown.

## Best Practices

- Use a **connection pool** sized to the database's real limit (`connections ≈ cores
  × 2–4`, not thousands). More app connections than the database can serve causes
  queueing and timeouts, not throughput.
- Index the columns in your `WHERE`, `JOIN`, and `ORDER BY` clauses. Use **composite
  indexes** in the order most-selective/equality first, range last.
- Eliminate **N+1 queries**: load related rows in one query (join or `WHERE id IN
  (...)`), never one query per parent row in a loop.
- **Paginate** every unbounded list, and prefer **keyset (seek) pagination** over
  `OFFSET` for deep pages — `OFFSET 100000` still scans 100,000 rows.
- Keep transactions short: do external calls, heavy computation, and user I/O
  *outside* the transaction, never while holding a lock.
- Cache hot, read-mostly data (see [caching](08-caching.md)) and put a bound on how
  many rows any single query can return.
- Add read replicas for read-heavy workloads, but only after indexing and caching;
  replicas add lag and complexity, not free speed.
- Watch for lock contention and long-running queries with the database's own stats
  views, and set a **statement timeout** so a runaway query cannot hold resources
  forever.

## Examples

**Good Example** — batched load, one round-trip, bounded

```ts
// Fetch all posts, then their authors in ONE query keyed by id set.
const posts = await db.query(
  "SELECT id, title, author_id FROM posts ORDER BY id DESC LIMIT 50"
);
const authorIds = [...new Set(posts.map(p => p.author_id))];
const authors = await db.query(
  "SELECT id, name FROM authors WHERE id = ANY($1)", // single set-based lookup
  [authorIds]
);
// 2 round-trips total, regardless of how many posts — no N+1, bounded to 50 rows.
```

**Bad Example** — N+1, unbounded, full row

```ts
// One query per post → 1 + N round-trips. At 50 posts that is 51 trips.
const posts = await db.query("SELECT * FROM posts");        // unbounded + SELECT *
for (const post of posts) {
  post.author = await db.query(                             // N+1: query in a loop
    "SELECT * FROM authors WHERE id = " + post.author_id    // also SQL injection
  );
}
// Latency grows linearly with row count; the table doubling doubles the pain.
```

## Common Mistakes

- Querying inside a loop (N+1) instead of a single set-based query.
- No index on filtered/joined/sorted columns, so queries scan the whole table.
- `SELECT *` and no `LIMIT`, pulling far more data than the response needs.
- `OFFSET`-based pagination that degrades linearly as users page deeper.
- Opening a connection per request instead of pooling, exhausting the database.
- Doing network calls or heavy work inside an open transaction, holding locks.
- Adding a read replica or more caching before fixing the missing index.

## Production Tips

- Log and alert on slow queries (`log_min_duration_statement` or equivalent); the
  slow-query log is the fastest path to the real bottleneck.
- Enforce a `statement_timeout` and a pool-checkout timeout so a stuck query fails
  fast instead of cascading into a connection pileup.
- Track pool saturation and replication lag as first-class [monitoring](17-monitoring.md)
  signals; both fail silently until they fail totally.

## AI Review Checklist

- Does every filtered, joined, or sorted column have a supporting index?
- Is there any query inside a loop that should be a single set-based query?
- Are lists paginated and bounded, using keyset pagination for deep pages?
- Are connections pooled and the pool sized to the database's real limit?
- Are transactions short, with no external calls or heavy work inside them?
- Is a statement/query timeout set so a runaway query cannot hang resources?

## Related

- `knowledge/performance/15-query-optimization.md`
- `knowledge/performance/14-api-performance.md`
- `knowledge/performance/08-caching.md`
- `knowledge/performance/16-profiling.md`
- `knowledge/performance/05-network.md`
