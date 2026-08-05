---
id: sql/100-common-antipatterns
topic: sql
slug: common-antipatterns
title: "SQL Common Antipatterns"
type: doc
order: 100
status: ready
tags: [sql, common-antipatterns, NUMERIC, date, CHECK, REAL, TIMESTAMPTZ, FLOAT]
related: [sql/15-indexes, sql/17-query-optimization, sql/22-security, sql/14-transactions, sql/30-engineering-principles]
when_to_use: "Read when writing or reviewing SQL to recognize and avoid the recurring mistakes that fail at scale."
---
# SQL Common Antipatterns

## Purpose

A catalog of the SQL antipatterns that most often reach production and cause incidents.
Each entry names the pattern, explains why it is wrong (the concrete failure it
produces), and gives the fix. Use it as a checklist of things to *not* write and to
flag in review.

## Why It Matters

These patterns share a trait: they work on small data and in a single-user test, then
fail under real volume or concurrency. Because they pass the demo, they slip through
review unless you recognize them on sight. Knowing the failure mode of each turns a
vague "this looks off" into a specific, actionable finding.

## Anti-Patterns

### 1. String-concatenated queries
**Why it is wrong:** Interpolating user input into SQL is the direct cause of SQL
injection — an attacker can read, alter, or drop any data the connection can reach.
**The fix:** Always use parameterized queries / bind variables. For dynamic identifiers,
validate against an allowlist.
```sql
-- Bad: input becomes executable SQL
-- "SELECT * FROM users WHERE email = '" + input + "'"
-- Good: the driver sends value and query separately
SELECT * FROM users WHERE email = $1;
```

### 2. `SELECT *` in application queries
**Why it is wrong:** It fetches every column — including large/PII fields — over the
wire, breaks when columns are added or reordered, and prevents index-only scans.
**The fix:** List the exact columns the code uses.

### 3. Unbounded or unverified `UPDATE`/`DELETE`
**Why it is wrong:** A missing or wrong `WHERE` rewrites or deletes the whole table, and
the change is not recoverable without a backup.
**The fix:** Write the `WHERE` first, verify the row set with a `SELECT`, then run the
write inside a transaction you can roll back.

### 4. N+1 queries
**Why it is wrong:** Looping in application code to issue one query per parent row turns
a single join into thousands of round trips, dominating latency.
**The fix:** Fetch with a `JOIN` or a single batched `WHERE id = ANY(...)`.
```sql
-- Bad: one query per order, in an app loop
-- for id in order_ids: SELECT * FROM items WHERE order_id = id
-- Good: one query for all
SELECT * FROM items WHERE order_id = ANY($1);
```

### 5. Non-sargable predicates
**Why it is wrong:** Wrapping an indexed column in a function or arithmetic
(`WHERE date(created_at) = '2026-07-07'`, `WHERE col + 0 = 5`) forces a full scan
because the index is on the raw column, not the expression.
**The fix:** Rewrite as a range on the bare column, or add an expression index.
```sql
-- Bad: index on created_at is unusable
WHERE date(created_at) = '2026-07-07'
-- Good: range on the raw column uses the index
WHERE created_at >= '2026-07-07' AND created_at < '2026-07-08';
```

### 6. Deep `OFFSET` pagination
**Why it is wrong:** `LIMIT 20 OFFSET 100000` still reads and discards 100,000 rows, so
later pages get linearly slower.
**The fix:** Use keyset (seek) pagination: `WHERE id > $last_id ORDER BY id LIMIT 20`.

### 7. Integrity enforced only in the application
**Why it is wrong:** Uniqueness or referential checks done with a read-then-write race
under concurrency, producing duplicates or orphaned rows.
**The fix:** Enforce with `UNIQUE`, `FOREIGN KEY`, and `CHECK` constraints; the engine
applies them atomically for every writer.

### 8. `NULL` misuse
**Why it is wrong:** `col = NULL` is never true, `NOT IN (subquery-with-null)` returns no
rows, and aggregates silently skip `NULL`s — each yields wrong results that look valid.
**The fix:** Use `IS NULL`/`IS NOT NULL`, prefer `NOT EXISTS` over `NOT IN`, and make
columns `NOT NULL` when absence is not a real state.

### 9. Floating-point for money
**Why it is wrong:** `FLOAT`/`REAL` cannot represent decimal fractions exactly, so sums
drift by fractions of a cent and reconciliations fail.
**The fix:** Store money as `NUMERIC`/`DECIMAL` (or integer minor units like cents).

### 10. Storing typed data as text
**Why it is wrong:** Dates, numbers, or enums in `VARCHAR` cannot be validated, sorted,
or computed correctly, and permit malformed values.
**The fix:** Use the real type — `TIMESTAMPTZ`, `NUMERIC`, native enum or `CHECK`.

### 11. Missing index on a foreign key column
**Why it is wrong:** A `FOREIGN KEY` does not create an index on the referencing column,
so joins and cascading deletes scan the child table.
**The fix:** Add an index on every FK column used in joins or cascades.

### 12. Long-running / idle-in-transaction transactions
**Why it is wrong:** Holding a transaction open across user think-time or an external
HTTP call keeps locks and bloats MVCC row versions, starving other writers.
**The fix:** Keep transactions short; do external I/O outside the transaction.

### 13. Correlated subquery where a join or window fits
**Why it is wrong:** A subquery that re-executes per outer row (e.g. `SELECT ... (SELECT
MAX(...) WHERE ...)`) runs O(n) times instead of once.
**The fix:** Rewrite as a `JOIN` or a window function that computes the value in one pass.

### 14. Building on implicit ordering
**Why it is wrong:** Without `ORDER BY`, row order is undefined; a query that "always"
returns sorted rows will reorder after a plan or version change.
**The fix:** State `ORDER BY` explicitly whenever order matters.

## Common Mistakes

- Treating any of the above as acceptable "because it works on the test dataset".
- Fixing the symptom (adding a `LIMIT`) instead of the cause (a non-sargable predicate).
- Adding indexes for every antipattern without measuring — indexes cost write speed too.

## AI Review Checklist

- Is any query built by string concatenation instead of parameters?
- Does any predicate wrap an indexed column in a function?
- Does any `UPDATE`/`DELETE` lack a verified `WHERE`?
- Is money stored as a floating type, or a date/enum stored as text?
- Are foreign key columns indexed?
- Is any transaction held open across external I/O?

## Related

- `knowledge/sql/15-indexes.md`
- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/22-security.md`
- `knowledge/sql/14-transactions.md`
- `knowledge/sql/30-engineering-principles.md`
