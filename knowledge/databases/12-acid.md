---
id: databases/12-acid
topic: databases
slug: acid
title: "ACID"
type: doc
order: 12
status: ready
tags: [databases, acid, COMMIT, synchronous_commit, SERIALIZABLE, ROLLBACK, fsync, BEGIN]
related: [databases/09-transactions, databases/10-concurrency, databases/11-locking, databases/13-eventual-consistency, databases/23-data-integrity]
when_to_use: "Read before writing any multi-statement write path that must not leave the database in a half-applied state."
---
# ACID

## Purpose

This document defines the four guarantees a transactional database gives you —
**Atomicity, Consistency, Isolation, Durability** — and how to write code that
actually gets them. It exists so an agent can reason about what a transaction
protects, which isolation level a given operation needs, and where those
guarantees silently stop.

ACID describes the *contract of a single transaction*. It is the opposite end of
the spectrum from [eventual consistency](13-eventual-consistency.md): ACID
prioritizes correctness on one node; eventual consistency prioritizes
availability across many. Know which one your operation requires.

## Why It Matters

The whole point of a transaction is that partial failure becomes impossible: money
leaves one account only if it arrives in the other. When ACID is misunderstood, the
database appears to work — rows get written — but invariants quietly rot. A missing
transaction boundary lets a crash leave an order paid-for but never shipped. The
wrong isolation level lets two concurrent requests both read a balance of 100, both
subtract 100, and both commit. These bugs do not throw errors; they surface weeks
later as impossible data. Because the corruption is silent and permanent, the write
path is held to a higher bar than read code.

## Core Principles

- **Atomicity — all or nothing.** Every statement in a transaction commits together
  or none does. A crash mid-transaction rolls back cleanly; there is no "half".
- **Consistency — invariants hold across the boundary.** A committed transaction
  moves the database from one valid state to another. Constraints (foreign keys,
  `CHECK`, uniqueness) are part of this contract — the database enforces them, not
  just your code.
- **Isolation — concurrent transactions do not corrupt each other.** The isolation
  *level* decides how much interference is allowed. Higher isolation costs
  throughput; the default is usually `READ COMMITTED`, which is weaker than most
  developers assume.
- **Durability — committed means committed.** Once `COMMIT` returns, the data
  survives a power loss. This depends on `fsync` and, in replicated setups, on how
  many replicas acknowledged the write.
- **The transaction boundary is a decision, not a default.** Wrap exactly the work
  that must succeed or fail as a unit — no more (long transactions block others),
  no less (missing a step breaks atomicity).

## Best Practices

- Group every set of writes that share an invariant into one transaction. If two
  updates must both hold, they belong in the same `BEGIN`/`COMMIT`.
- Choose isolation deliberately. Use `SERIALIZABLE` or `REPEATABLE READ` for
  read-modify-write on money, inventory, or counters; `READ COMMITTED` is not enough
  there because it permits lost updates and non-repeatable reads.
- Prevent lost updates explicitly: use `SELECT ... FOR UPDATE`, an atomic
  `UPDATE ... SET x = x - 1 WHERE x >= 1`, or optimistic concurrency with a version
  column. Never read a value into the app, compute, and write it back without one.
- Keep transactions short. Do no network calls, no external I/O, and no user waits
  inside a transaction — open locks stall every other writer.
- Let the database enforce invariants with constraints, not application checks
  alone. Application checks race; a `UNIQUE` constraint does not.
- Handle serialization failures (`40001`) by retrying the whole transaction with
  backoff. Under `SERIALIZABLE`, the database *expects* you to retry.
- Verify durability requirements: for critical writes, ensure `synchronous_commit`
  (or the equivalent) is on and, if replicated, that a quorum acknowledges.

## Examples

**Good Example** — atomic, correct under concurrency

```sql
-- Transfer 100 between accounts. Both updates commit together or not at all.
BEGIN;
  -- Atomic decrement with a guard: the WHERE clause makes overdraft impossible
  -- even if two transfers run at once. If it affects 0 rows, we abort.
  UPDATE accounts SET balance = balance - 100
   WHERE id = 'A' AND balance >= 100;
  -- Application checks rowcount == 1; if 0, ROLLBACK (insufficient funds).
  UPDATE accounts SET balance = balance + 100
   WHERE id = 'B';
COMMIT;
```

**Bad Example** — read-modify-write outside isolation, no atomic boundary

```ts
// Two requests read balance=100 concurrently, both pass the check,
// both write 0. One transfer vanishes. This is a lost update.
const { balance } = await db.query("SELECT balance FROM accounts WHERE id='A'");
if (balance < 100) throw new Error("insufficient");
await db.query("UPDATE accounts SET balance = $1 WHERE id='A'", [balance - 100]);
// Separate statement, no transaction: a crash here leaves money destroyed,
// never credited to B. Atomicity was never established.
await db.query("UPDATE accounts SET balance = balance + 100 WHERE id='B'");
```

## Common Mistakes

- Assuming the default isolation level prevents lost updates — `READ COMMITTED` does
  not. Read-modify-write needs locking, an atomic update, or version checks.
- Doing read-then-write across two statements without `FOR UPDATE` or a version
  column, creating a race.
- Wrapping unrelated work in one giant transaction, holding locks far too long.
- Enforcing uniqueness or referential integrity only in application code, which
  races; skipping the database constraint that would make it impossible.
- Ignoring serialization/deadlock errors instead of retrying them.
- Treating a returned `COMMIT` as durable when `synchronous_commit` is off or when
  no replica has acknowledged.

## Production Tips

- Set a `statement_timeout` and an idle-in-transaction timeout so a stuck
  transaction cannot hold locks indefinitely.
- Monitor for deadlocks and long-running transactions; they are early signals of
  bad boundaries.
- Order writes to the same tables in a consistent sequence across the codebase to
  reduce deadlocks.
- Wrap transactions in a bounded retry loop for `40001`/`40P01` error codes.

## AI Review Checklist

- Is every set of writes that share an invariant inside a single transaction?
- For read-modify-write, is there `FOR UPDATE`, an atomic `UPDATE`, or a version
  column — not a plain app-side read then write?
- Is the isolation level strong enough for the operation, and are serialization
  failures retried?
- Are invariants enforced by database constraints, not application code alone?
- Are transactions free of network calls, external I/O, and user waits?
- For critical writes, is durability (fsync / replica acknowledgment) actually
  guaranteed by the config?

## Related

- `knowledge/databases/09-transactions.md`
- `knowledge/databases/10-concurrency.md`
- `knowledge/databases/11-locking.md`
- `knowledge/databases/13-eventual-consistency.md`
- `knowledge/databases/23-data-integrity.md`
