---
id: databases/100-common-antipatterns
topic: databases
slug: common-antipatterns
title: "Common Antipatterns"
type: doc
order: 100
status: ready
tags: [databases, common-antipatterns]
related: [databases/08-query-optimization, databases/09-transactions, databases/23-data-integrity, databases/17-migrations, databases/07-indexing]
when_to_use: "Read when writing or reviewing data-access code to recognize and avoid the recurring failure patterns below."
---
# Common Antipatterns

## Purpose

This document catalogs the database antipatterns that appear most often in real codebases,
each with *why it is wrong* and *the fix*. These are the mistakes that pass tests and code
review by looking reasonable, then cause corruption or outages under production load and
concurrency. Learn to recognize them on sight.

## Why It Matters

Every antipattern below has a predictable, expensive failure mode: lost money, orphaned
rows, an injection breach, a locked table at peak traffic. They recur because each one is
locally convenient — fewer lines, one fewer round trip — while the cost is deferred to
production. Naming them makes them easy to reject in review.

## Antipatterns

### 1. Building SQL by string concatenation

- **Why it is wrong:** Interpolating user input into a query string is SQL injection —
  the top database security failure. It also breaks on ordinary input like an apostrophe.
- **The fix:** Always use parameterized queries / bound parameters. The driver, not string
  formatting, inserts the value.

```python
# Bad: user input becomes SQL. name = "'; DROP TABLE users; --" is now executable.
db.execute(f"SELECT * FROM users WHERE name = '{name}'")

# Good: the value is bound, never parsed as SQL.
db.execute("SELECT * FROM users WHERE name = %s", [name])
```

### 2. N+1 queries

- **Why it is wrong:** One query to fetch a list, then one query per row to fetch its
  children, means hundreds of round trips where one join or batch would do. It looks fine
  at 10 rows and melts at 10,000.
- **The fix:** Fetch related data with a `JOIN`, an `IN (...)` batch, or the ORM's eager-load
  (`select_related`/`prefetch_related`, `include`, `JOIN FETCH`).

```python
# Bad: 1 + N queries.
for order in db.query("SELECT id FROM orders"):
    items = db.query("SELECT * FROM items WHERE order_id = ?", order.id)

# Good: one query with a join, or one batched IN query.
rows = db.query("SELECT o.id, i.* FROM orders o JOIN items i ON i.order_id = o.id")
```

### 3. Enforcing invariants only in application code

- **Why it is wrong:** Application checks race under concurrency and are bypassed by any
  other writer (a script, a second service, a manual query). The rule is not actually
  enforced.
- **The fix:** Declare the invariant in the schema — `CHECK`, `UNIQUE`, `NOT NULL`,
  `FOREIGN KEY`. The database enforces it on every write, always.

### 4. Related writes without a transaction

- **Why it is wrong:** If the process crashes between two dependent writes, the data is left
  half-updated — money debited but not credited, an order with no line items. There is no
  automatic repair.
- **The fix:** Wrap the group of writes in one transaction so they commit or roll back
  atomically. See [transactions](09-transactions.md).

### 5. Storing money in floating point

- **Why it is wrong:** `float`/`double` cannot represent most decimal fractions exactly, so
  sums drift by fractions of a cent and reconciliation fails.
- **The fix:** Use `numeric`/`decimal` (or integer minor units, e.g. cents). Exact types for
  exact values.

### 6. `SELECT *` and no pagination on large tables

- **Why it is wrong:** `SELECT *` drags unused columns over the wire and defeats
  covering indexes; unbounded reads load an entire table into memory. Deep `OFFSET`
  pagination scans and discards every skipped row.
- **The fix:** Select only needed columns, always bound result size, and paginate by
  keyset (`WHERE id > :last ORDER BY id LIMIT :n`).

```sql
-- Bad: scans and throws away 100,000 rows to return 20.
SELECT * FROM events ORDER BY id LIMIT 20 OFFSET 100000;

-- Good: keyset seek uses the index and stays constant-time.
SELECT id, type, created_at FROM events WHERE id > 100000 ORDER BY id LIMIT 20;
```

### 7. Indexing by guesswork

- **Why it is wrong:** Adding indexes "just in case" slows every write and wastes storage,
  while the actual hot query may still be unindexed and table-scanning.
- **The fix:** Index the columns real queries filter/join/sort on, confirm with `EXPLAIN`,
  and drop indexes that usage stats show are unused. See [indexing](07-indexing.md).

### 8. Blocking migrations at peak

- **Why it is wrong:** A plain `CREATE INDEX`, a `NOT NULL` column with a default on an old
  engine, or a table rewrite takes an exclusive lock — writes queue behind it and the app
  effectively goes down.
- **The fix:** Use the online/concurrent path (`CREATE INDEX CONCURRENTLY`), backfill in
  batches, and split into expand → migrate → contract steps run off-peak.

### 9. Unbounded connections / no pooling

- **Why it is wrong:** Opening a connection per request exhausts the database's connection
  limit and its memory; the database falls over under exactly the load you needed it for.
- **The fix:** Use a connection pool with a bounded max the database can sustain, and set a
  statement timeout so one slow query cannot pin a connection forever.

### 10. Hard deletes with no audit for data you may need back

- **Why it is wrong:** A hard `DELETE` is irreversible; a wrong `WHERE` (or none) can erase
  rows you are legally or operationally required to keep, with no way to recover mid-day.
- **The fix:** Use [soft delete](24-soft-delete.md) or an [audit](26-auditing.md) trail
  where history matters, and always scope destructive statements with a tested `WHERE`.

## Common Mistakes

- Assuming an ORM protects you — it can still emit N+1 queries and raw string SQL.
- Testing only with a tiny seed dataset, so scan and lock problems never surface.
- Treating a backup you have never restored as a recovery plan.
- Leaving `ON DELETE` behavior to the default instead of choosing cascade vs restrict.

## AI Review Checklist

- Is any SQL built by string interpolation of untrusted input?
- Is there a query inside a loop that should be a join or a batch?
- Are multi-write operations wrapped in a transaction?
- Is money or other exact data stored in a floating-point type?
- Does a large-table query lack an index, use `SELECT *`, or paginate by deep `OFFSET`?
- Could this migration take a blocking lock under production traffic?

## Related

- `knowledge/databases/08-query-optimization.md`
- `knowledge/databases/09-transactions.md`
- `knowledge/databases/23-data-integrity.md`
- `knowledge/databases/17-migrations.md`
- `knowledge/databases/07-indexing.md`
