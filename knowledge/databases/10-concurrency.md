---
id: databases/10-concurrency
topic: databases
slug: concurrency
title: "Concurrency"
type: doc
order: 10
status: ready
tags: [databases, concurrency, SERIALIZABLE, updated_at, version, UNIQUE, CHECK]
related: [databases/09-transactions, databases/11-locking, databases/12-acid, databases/23-data-integrity, databases/08-query-optimization]
when_to_use: "Read before writing code where two requests can update the same row, or when choosing an isolation level."
---
# Concurrency

## Purpose

This document defines how to keep data correct when many transactions run at once:
the anomalies that concurrency causes (lost update, dirty/non-repeatable/phantom
reads, write skew), what each isolation level prevents, and how to choose between
optimistic and pessimistic strategies. It is written so an agent can reason about
races instead of discovering them in production.

Concurrency is governed by transaction isolation ([transactions](09-transactions.md))
and enforced with [locks](11-locking.md); it is the practical face of the "I" in
[ACID](12-acid.md).

## Why It Matters

Every real system runs concurrent requests, and the bugs they cause are the hardest
to find: they depend on exact timing, never reproduce in a single-threaded test, and
corrupt data silently. Two users buying the last item, two admins editing the same
record, a counter incremented from two requests — each can lose a write with no error
raised. The code looks correct because in isolation it *is* correct; only the
interleaving is wrong.

Choosing an isolation level or concurrency strategy is therefore a correctness
decision, not a performance tuning knob. Pick too weak a level and you ship silent
data loss; pick too strong and you serialize everything and deadlock under load.

## Core Principles

- **Concurrency anomalies are the default, not the exception.** Assume two copies of
  every request run simultaneously. If that breaks your logic, the logic is wrong.
- **Isolation level defines which anomalies are possible.** `READ COMMITTED` (common
  default) still allows lost updates and non-repeatable reads. Know your level's
  guarantees precisely.
- **Read-modify-write is unsafe by default.** `SELECT` then `UPDATE` based on the read
  value races. Make it atomic, lock the row, or use a version check.
- **Optimistic vs pessimistic is a contention trade-off.** Low contention favors
  optimistic (version column, retry). High contention favors pessimistic (`FOR
  UPDATE`) to avoid retry storms.
- **Higher isolation trades throughput for safety — and requires retry.**
  `SERIALIZABLE` prevents write skew but aborts conflicting transactions; you must
  retry them.

## Best Practices

- Never do `SELECT x; compute; UPDATE x = new`. Instead: `UPDATE ... SET x = x + $1`
  (atomic), `SELECT ... FOR UPDATE` (pessimistic), or a `WHERE version = $expected`
  guard (optimistic).
- Use **optimistic concurrency** for user-edited records: add a `version` (or
  `updated_at`) column, and on save do `UPDATE ... SET ..., version = version + 1
  WHERE id = $1 AND version = $expected`. Zero rows updated means someone else won —
  surface a conflict, don't overwrite.
- Use **pessimistic locking** (`SELECT ... FOR UPDATE`) when the same hot rows are
  contended and retrying would thrash — e.g. decrementing shared inventory.
- Raise isolation to `SERIALIZABLE` for invariants that span multiple rows (write
  skew), and wrap the transaction in a retry loop for `40001`.
- Enforce cross-request invariants with database constraints (unique, exclusion,
  `CHECK`) so the engine rejects the second conflicting write regardless of timing.
- Keep transactions short — the smaller the window, the smaller the chance of conflict.

## Examples

**Good Example** — optimistic concurrency detects the lost update

```sql
-- Client read this row earlier and saw version = 7.
UPDATE documents
SET    title   = $new_title,
       version = version + 1
WHERE  id = $1
  AND  version = 7;          -- guard: only succeeds if no one else wrote since the read
-- rows affected = 0  -> a concurrent edit won; return 409 Conflict, don't clobber it.
-- rows affected = 1  -> our update applied atomically.
```

**Bad Example** — read-modify-write with no guard: silent lost update

```sql
-- Request A and Request B both run these two statements interleaved.
SELECT stock FROM products WHERE id = 42;   -- both read stock = 1
-- (application checks stock >= 1, both pass)
UPDATE products SET stock = 0 WHERE id = 42; -- both write 0; two items sold, one in stock
-- No error anywhere. Inventory is now wrong and the second sale is unfulfillable.
```

## Common Mistakes

- Read-modify-write without atomic update, row lock, or version guard.
- Assuming `READ COMMITTED` prevents lost updates or gives a stable multi-statement
  view — it does neither.
- Enforcing uniqueness with "SELECT to check, then INSERT" — two requests both see
  "not found" and both insert. Use a `UNIQUE` constraint.
- Choosing `SERIALIZABLE` but not retrying serialization failures, so users get raw
  errors under load.
- Over-locking (`FOR UPDATE` on wide ranges) causing deadlocks and lock waits under
  contention.
- Testing only single-threaded, so races never surface until production traffic.

## Production Tips

- Load-test the contended paths concurrently; single-user tests hide every race.
- Track serialization-failure and deadlock rates as a health signal — a spike means a
  hot row or a lock-ordering problem.
- Make retries idempotent (idempotency keys) so re-running a conflicted unit is safe.

## AI Review Checklist

- Does any code path read a value, compute, then write it back without protection?
- Is the isolation level sufficient for the invariant this code relies on?
- For user edits, is there an optimistic version/`updated_at` guard that returns a
  conflict instead of overwriting?
- Are contended hot rows locked pessimistically to avoid retry storms?
- Are `SERIALIZABLE`/deadlock failures caught and retried?
- Are cross-request invariants (uniqueness, limits) backed by constraints?
- Was the path tested under real concurrency, not just single-threaded?

## Related

- `knowledge/databases/09-transactions.md`
- `knowledge/databases/11-locking.md`
- `knowledge/databases/12-acid.md`
- `knowledge/databases/23-data-integrity.md`
- `knowledge/databases/08-query-optimization.md`
