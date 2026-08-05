---
id: mysql/100-common-antipatterns
topic: mysql
slug: common-antipatterns
title: "MySQL Common Antipatterns"
type: doc
order: 100
status: ready
tags: [mysql, common-antipatterns]
related: [mysql/04-indexes, mysql/05-query-optimization, mysql/06-transactions, mysql/16-migrations, mysql/30-engineering-principles]
when_to_use: "Read when writing or reviewing MySQL code to recognize and avoid the recurring failure patterns below."
---
# MySQL Common Antipatterns

## Purpose

This document catalogs the MySQL antipatterns that recur in real codebases, each with why it
is wrong and the concrete fix. These are the mistakes that pass tests and fail in production.
An agent should recognize them on sight and refuse to write or approve them.

## Why It Matters

Every antipattern here has a common thread: it works at small scale and breaks at large
scale, or it works today and corrupts data tomorrow. They are cheap to avoid at authoring
time and enormously expensive to unwind once data and dependent code have accumulated. Naming
them makes them catchable in review.

## Antipatterns

### 1. The N+1 query

**Why it is wrong:** Loading a list, then firing one query per row for related data, turns
one round trip into hundreds. Latency is dominated by round-trip count, so this is invisible
locally and crippling under real network latency.

**The fix:** Fetch related rows in a single query with a `JOIN`, or one `IN (...)` batch:

```sql
-- Bad: 1 + N queries
SELECT id FROM users;                       -- then, per user:
SELECT * FROM orders WHERE user_id = ?;

-- Good: one query
SELECT u.id, o.* FROM users u
JOIN orders o ON o.user_id = u.id;
```

### 2. `SELECT *`

**Why it is wrong:** It fetches every column, defeats covering indexes, breaks when columns
are added/reordered, and ships large `TEXT`/`BLOB` payloads you did not need.

**The fix:** List the exact columns the code uses. This lets an index cover the query and
makes the read intent explicit.

### 3. Function on an indexed column in `WHERE`

**Why it is wrong:** Wrapping an indexed column in a function forces a full scan — the index
is on the raw value, not the computed one.

**The fix:** Rewrite to compare the bare column against a computed bound:

```sql
-- Bad: index on created_at is unused
SELECT * FROM orders WHERE DATE(created_at) = '2026-07-07';

-- Good: sargable range, uses the index
SELECT * FROM orders
WHERE created_at >= '2026-07-07' AND created_at < '2026-07-08';
```

### 4. Deep `OFFSET` pagination

**Why it is wrong:** `LIMIT 100000, 20` makes MySQL read and discard 100,000 rows first.
Cost grows with page depth, so late pages time out.

**The fix:** Use keyset (seek) pagination on an indexed, ordered key:

```sql
-- Good: O(1) regardless of depth
SELECT * FROM orders WHERE id > ? ORDER BY id LIMIT 20;
```

### 5. Storing money in `FLOAT`/`DOUBLE`

**Why it is wrong:** Binary floating point cannot represent decimal fractions like 0.10
exactly, so sums drift and totals fail to reconcile.

**The fix:** Use `DECIMAL(p,s)` or store integer minor units (cents) in a `BIGINT`.

### 6. Random UUID as the primary key

**Why it is wrong:** InnoDB clusters the table on the PK. Random UUIDs insert in random
order, fragmenting the clustered index with page splits, and every secondary index copies
the 16-byte PK, bloating them all.

**The fix:** Use `BIGINT AUTO_INCREMENT`, or an ordered UUIDv7/ULID if you need a
distributed identifier. Keep random UUIDs in a separate indexed column if externally required.

### 7. No index on a foreign key or join column

**Why it is wrong:** Joins and constraint checks on an unindexed column scan the whole
table, and InnoDB may take broader locks during FK checks.

**The fix:** Index every column used in a `JOIN`, `WHERE`, or foreign key. Confirm with
`EXPLAIN` that the plan uses it.

### 8. Legacy `utf8` instead of `utf8mb4`

**Why it is wrong:** MySQL's `utf8` is a 3-byte subset that cannot store emoji or all of
Unicode; inserting 4-byte characters truncates or errors.

**The fix:** Use `utf8mb4` at the column, table, database, and connection level. There is no
correctness reason to use `utf8` in a new schema.

### 9. Long-lived transactions

**Why it is wrong:** A transaction left open across API calls or user think-time holds row
locks and grows the undo log, blocking other writers and stalling purge.

**The fix:** Open the transaction immediately before the writes, commit right after, and
never perform network I/O inside it. Keep transactions short and lock in a consistent order.

### 10. String-concatenated (injectable) SQL

**Why it is wrong:** Interpolating user input into SQL is a [SQL injection](12-security.md)
vulnerability and also prevents the server from caching the prepared statement plan.

**The fix:** Always use parameterized queries / prepared statements. Never build SQL by
concatenation, even for "trusted" internal values.

```sql
-- Bad (pseudocode): query = "SELECT * FROM users WHERE email = '" + input + "'"
-- Good: prepared statement with a bound parameter
SELECT * FROM users WHERE email = ?;
```

### 11. `ALTER TABLE` on a large hot table without an online strategy

**Why it is wrong:** A naive `ALTER` can lock or rebuild the table, blocking reads/writes
for the duration and taking the site down.

**The fix:** Use an online schema-change tool (`gh-ost`, `pt-online-schema-change`) or
`ALGORITHM=INPLACE, LOCK=NONE`, and ensure disk headroom for the table copy.

### 12. Relying on the application for uniqueness or integrity

**Why it is wrong:** "Check then insert" in application code has a race: two concurrent
requests both pass the check and both insert. The app is never the only writer.

**The fix:** Declare a `UNIQUE` constraint and a `FOREIGN KEY`, and let the database reject
the duplicate. Handle the resulting error rather than pre-checking.

## AI Review Checklist

- Are lists loaded with a `JOIN`/`IN` batch rather than one query per row (no N+1)?
- Do queries select explicit columns and keep indexed columns bare in `WHERE`?
- Is pagination keyset-based, not deep `OFFSET`?
- Is money `DECIMAL`/integer, the PK compact and ordered, and every join column indexed?
- Are all queries parameterized and transactions short with no I/O inside?
- Are uniqueness and referential integrity enforced by database constraints?

## Related

- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/16-migrations.md`
- `knowledge/mysql/30-engineering-principles.md`
