---
id: postgresql/100-common-antipatterns
topic: postgresql
slug: common-antipatterns
title: "PostgreSQL Common Antipatterns"
type: doc
order: 100
status: ready
tags: [postgresql, common-antipatterns, timestamp, serial, CONCURRENTLY, timestamptz, float, CHECK]
related: [postgresql/30-engineering-principles, postgresql/04-indexes, postgresql/06-transactions, postgresql/05-query-planner, postgresql/22-migrations]
when_to_use: "Read before writing schema or queries, and when reviewing a change that feels slow or fragile."
---
# PostgreSQL Common Antipatterns

## Purpose

This document catalogs the PostgreSQL mistakes that recur most often and cost the most:
each with *why it is wrong* and *the fix*. Use it as a checklist of things to not do,
and as a diagnosis guide when a query is slow or data is subtly wrong. It is the
negative-space companion to the [engineering principles](30-engineering-principles.md).

## Why It Matters

Most database pain is self-inflicted and repetitive — the same handful of anti-patterns
account for the majority of slow queries, lost updates, and painful migrations. Knowing
them by name lets an agent recognize the shape of a problem instantly and reach for the
established fix instead of rediscovering it under incident pressure.

## Anti-Patterns

### 1. Storing timestamps as `timestamp` (without time zone)

**Why it is wrong:** naive `timestamp` records a wall-clock reading with no offset.
Compare or subtract two of them across DST or across servers in different zones and the
result is silently wrong. The data looks fine until an interval calculation is off by an
hour.
**The fix:** always use `timestamptz`, store UTC, convert at the application edge.

### 2. Using `float`/`double` for money

**Why it is wrong:** binary floats cannot represent decimal fractions like `0.10`
exactly, so sums drift and cents vanish. Financial reconciliation then fails in ways no
amount of rounding fully hides.
**The fix:** use `numeric(p, s)` for money and any exact decimal. Reserve floats for
genuinely approximate physical quantities.

### 3. Enforcing invariants only in application code

**Why it is wrong:** two app instances run concurrently; a check-then-write in code
races, and a manual `INSERT` or a second service bypasses it entirely. The "impossible"
bad row appears.
**The fix:** push the invariant into the schema with `NOT NULL`, `CHECK`, `UNIQUE`, and
`FOREIGN KEY`. A constraint holds for every writer, forever.

```sql
-- Bad: hope every code path checks this.
-- Good: the database refuses the bad state.
ALTER TABLE account ADD CONSTRAINT balance_nonneg CHECK (balance >= 0);
```

### 4. Read-modify-write without a lock

**Why it is wrong:** under the default `READ COMMITTED`, two sessions both read the old
value, both compute a new one, and the second write clobbers the first — a lost update.
**The fix:** do it in one statement (`UPDATE ... SET x = x - 1 WHERE ...`), or lock the
row with `SELECT ... FOR UPDATE`, or use a `SERIALIZABLE` transaction. See
[transactions](06-transactions.md).

### 5. Missing index on a foreign key column

**Why it is wrong:** PostgreSQL does not auto-index the *referencing* side of a foreign
key. Deletes/updates on the parent then scan the child table, and locks are held longer,
compounding under load.
**The fix:** create an index on every FK column that participates in joins or cascades.

### 6. Non-sargable predicates

**Why it is wrong:** wrapping an indexed column in a function (`WHERE lower(email) = ...`,
`WHERE date(created_at) = ...`) makes the index unusable, forcing a full scan.
**The fix:** keep the column bare and transform the constant, or build a matching
expression index.

```sql
-- Bad: index on created_at is ignored.
SELECT * FROM orders WHERE date(created_at) = '2026-07-07';
-- Good: range predicate stays sargable.
SELECT * FROM orders
 WHERE created_at >= '2026-07-07' AND created_at < '2026-07-08';
```

### 7. Pagination with large `OFFSET`

**Why it is wrong:** `OFFSET 100000` still reads and discards 100,000 rows every page;
cost grows linearly with page number and late pages crawl.
**The fix:** keyset (seek) pagination — `WHERE (created_at, id) < (:last_ts, :last_id)
ORDER BY created_at DESC, id DESC LIMIT 50`.

### 8. `SELECT *` in application queries

**Why it is wrong:** it ships columns you do not need, breaks when the schema changes
column order, and prevents index-only scans.
**The fix:** list the columns you actually use.

### 9. Building SQL by string concatenation

**Why it is wrong:** interpolating user input into SQL is the classic injection hole and
also defeats plan caching.
**The fix:** always use bound parameters (`$1`, `$2` / the driver's placeholder). Never
concatenate untrusted values.

### 10. `CREATE INDEX` on a live table without `CONCURRENTLY`

**Why it is wrong:** a plain `CREATE INDEX` takes a lock that blocks writes to the table
for the whole build — an outage on a large hot table.
**The fix:** use `CREATE INDEX CONCURRENTLY` (outside a transaction block), and monitor
for an invalid index if it fails.

### 11. Long-running / idle-in-transaction transactions

**Why it is wrong:** an open transaction pins the oldest snapshot, blocking
[vacuum](20-vacuum.md) from reclaiming dead tuples and inflating bloat; it also holds
locks. An `idle in transaction` connection is the worst offender.
**The fix:** keep transactions short, never do network/HTTP calls inside one, and set
`idle_in_transaction_session_timeout`.

### 12. Unbounded connections with no pooler

**Why it is wrong:** each PostgreSQL connection is a backend process; thousands of them
exhaust memory and CPU and collapse under a connection storm.
**The fix:** cap `max_connections` and put PgBouncer (transaction pooling) in front.

### 13. EAV / free-text where a column or enum belongs

**Why it is wrong:** an entity-attribute-value blob or a `status varchar` with no
constraint loses type safety — typos become permanent distinct values and every query
needs casts and filters.
**The fix:** model real columns with real types; use a lookup table or enum for
controlled vocabularies.

### 14. Trusting `serial` / not planning for `int` overflow

**Why it is wrong:** `serial`/`int` primary keys top out at ~2.1 billion and its
sequence-ownership quirks surprise on restore; a busy table can exhaust the range.
**The fix:** use `bigint GENERATED ALWAYS AS IDENTITY` (or UUID) for keys from day one.

## AI Review Checklist

- Any naive `timestamp` or `float` money columns that should be `timestamptz`/`numeric`?
- Any invariant enforced only in code that a constraint should own?
- Any read-modify-write missing `FOR UPDATE` or a single-statement update?
- Any unindexed FK column, non-sargable predicate, or deep `OFFSET`?
- Any `SELECT *`, concatenated SQL, or `CREATE INDEX` without `CONCURRENTLY`?
- Any long/idle-in-transaction path or missing connection pooler?

## Related

- `knowledge/postgresql/30-engineering-principles.md`
- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/06-transactions.md`
- `knowledge/postgresql/05-query-planner.md`
- `knowledge/postgresql/22-migrations.md`
