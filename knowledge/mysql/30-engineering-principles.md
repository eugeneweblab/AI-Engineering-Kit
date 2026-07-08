---
id: mysql/30-engineering-principles
topic: mysql
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [mysql, engineering-principles]
related: [mysql/04-indexes, mysql/06-transactions, mysql/05-query-optimization, mysql/19-best-practices, mysql/16-migrations]
when_to_use: "Read before designing a schema, writing queries, or reviewing any MySQL data-access code."
---
# Engineering Principles

## Purpose

This document defines the durable engineering principles for building on MySQL: how to
model data, write queries, manage transactions, and evolve a schema so the database stays
correct and fast under real production load. It is written so an agent can make schema and
query decisions without introducing data loss, lock storms, or silent corruption.

These are the invariants that survive across versions and workloads. Topic-specific rules
live in [indexes](04-indexes.md), [query optimization](05-query-optimization.md), and
[transactions](06-transactions.md); this doc is the reasoning that ties them together.

## Why It Matters

The database is the one component you cannot easily roll back. Application bugs ship a
hotfix; a bad schema migration or a lost write is permanent. MySQL will happily accept a
design that works for 10k rows and collapses at 10M — full table scans, lock contention,
and replication lag do not appear in a demo, they appear at 2am under peak traffic. Getting
the fundamentals right up front is cheaper by orders of magnitude than fixing them once
data has accumulated and every query depends on the wrong shape.

## Core Principles

- **The schema is a contract, enforce it in the database.** Use `NOT NULL`, `UNIQUE`,
  foreign keys, and `CHECK` constraints. The application is not the only writer — migrations,
  admin scripts, and future services all touch the data. The database is the last line.
- **Design for the read path, then make writes correct.** Indexes exist to serve queries.
  Know the queries before you design the table; an index you cannot name a query for is dead
  weight that slows every write.
- **Every query must be able to use an index for its `WHERE` and `JOIN`.** A full table
  scan is acceptable only on tables that are permanently small. Verify with `EXPLAIN`, never
  by assumption.
- **Transactions are for invariants, not for speed.** Wrap the set of writes that must
  succeed or fail together — no more, no less. Long transactions hold locks and bloat undo.
- **Prefer the smallest correct type.** Narrow rows fit more per page, cache better, and
  index faster. `BIGINT` where `INT` suffices, or `VARCHAR(255)` by reflex, is waste
  multiplied by every row.
- **Migrations are code and must be reversible and online.** Assume the table is huge and
  the app is live. A migration that locks a large table takes the site down.

## Best Practices

- Use `utf8mb4` (never legacy `utf8`, which is 3-byte and cannot store emoji or all of
  Unicode). Set it at the database, table, and connection level.
- Use `InnoDB` for everything transactional. It is the default; MyISAM has no crash
  recovery or row locking and should not appear in new schemas.
- Give every table a compact, monotonic primary key (`BIGINT UNSIGNED AUTO_INCREMENT` or an
  ordered UUID like UUIDv7). Random UUIDs as the PK fragment the clustered index and bloat
  every secondary index.
- Declare `FOREIGN KEY` constraints so orphan rows are impossible, and choose `ON DELETE`
  behavior explicitly rather than leaving it to application cleanup.
- Access rows through parameterized queries only. String-concatenated SQL is a
  [SQL injection](12-security.md) hole and defeats the query-plan cache.
- Set an explicit `sql_mode` including `STRICT_TRANS_TABLES` so bad data raises errors
  instead of being silently truncated or coerced.
- Store money as `DECIMAL`, never `FLOAT`/`DOUBLE` — binary floating point cannot represent
  0.10 exactly and will drift.
- Store timestamps in UTC (`TIMESTAMP` or `DATETIME`) and convert at the edge.

## Examples

**Good Example** — constrained schema, indexed access path, right-sized types

```sql
CREATE TABLE orders (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,  -- compact, monotonic PK
  user_id     BIGINT UNSIGNED NOT NULL,
  status      ENUM('pending','paid','shipped','cancelled') NOT NULL,
  total_cents INT UNSIGNED NOT NULL,                     -- integer money, no float drift
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_user_status (user_id, status),                -- serves the app's hot query
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Uses idx_user_status; verified with EXPLAIN before shipping.
SELECT id, total_cents FROM orders WHERE user_id = ? AND status = 'paid';
```

**Bad Example** — no constraints, unindexed scan, float money

```sql
CREATE TABLE orders (
  id      VARCHAR(36),          -- random UUID PK fragments the clustered index
  user_id VARCHAR(36),          -- no FK: orphan orders become possible
  status  VARCHAR(255),         -- unbounded string where a small ENUM belongs
  total   FLOAT                 -- money in float: 19.99 will not round-trip
);                              -- no PRIMARY KEY, no indexes, defaults to InnoDB but unconstrained

-- Full table scan on every lookup; O(n) that degrades as the table grows.
SELECT * FROM orders WHERE user_id = '...' AND status = 'paid';
```

## Common Mistakes

- Choosing a random UUID as the primary key, fragmenting the clustered index and inflating
  every secondary index that copies it.
- Storing money or quantities in `FLOAT`/`DOUBLE` and later discovering totals that do not
  reconcile.
- Wrapping an entire request in one long transaction, holding row locks across network calls.
- Adding indexes speculatively "for performance" without a query that uses them — each one
  taxes every `INSERT` and `UPDATE`.
- Relying on the application to enforce uniqueness or referential integrity instead of the
  database, so a second writer corrupts the data.
- Using legacy `utf8` and hitting truncation on 4-byte characters.

## Production Tips

- Run `EXPLAIN` (or `EXPLAIN ANALYZE`) on every new query against production-sized data;
  a plan that says `type: ALL` on a large table is a defect.
- Enable and watch the slow query log; treat any query over your latency budget as a bug.
- Keep migrations forward-and-backward compatible so the app can run against both schema
  versions during a rolling deploy.
- Never run schema changes with a bare `ALTER TABLE` on a large hot table; use an online
  tool (`gh-ost`, `pt-online-schema-change`, or `ALGORITHM=INPLACE, LOCK=NONE`).

## AI Review Checklist

- Does every table use `InnoDB` and `utf8mb4`, with an explicit primary key?
- Can each `WHERE`/`JOIN` in the change use an index, verified by `EXPLAIN`?
- Are `NOT NULL`, `UNIQUE`, and `FOREIGN KEY` constraints declared where invariants require them?
- Is money stored as `DECIMAL`/integer cents rather than a float?
- Are transactions scoped to exactly the writes that must be atomic, with no I/O inside?
- Is the migration reversible and safe to run online on a large table?

## Related

- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/16-migrations.md`
- `knowledge/mysql/19-best-practices.md`
