---
id: databases/09-transactions
topic: databases
slug: transactions
title: "Transactions"
type: doc
order: 9
status: ready
tags: [databases, transactions]
related: [databases/12-acid, databases/10-concurrency, databases/11-locking, databases/23-data-integrity, databases/08-query-optimization]
when_to_use: "Read before writing any multi-statement change that must succeed or fail as a unit."
---
# Transactions

## Purpose

This document defines how to use database transactions to make a group of changes
atomic: all of them commit, or none do. It covers boundaries, error handling,
isolation choice, and keeping transactions short. It is written so an agent can wrap
a multi-step write correctly without corrupting data or wedging the database.

Transactions are the mechanism that delivers [ACID](12-acid.md) guarantees. Their
isolation level is the knob that governs [concurrency](10-concurrency.md), and their
locks are covered in [locking](11-locking.md).

## Why It Matters

Any operation that touches more than one row or table has an intermediate state where
the data is inconsistent — money debited but not yet credited, an order created but
its inventory not yet decremented. If the process crashes, the connection drops, or a
constraint fires in that window, a non-transactional write leaves the database
permanently wrong. Transactions make that window invisible: outside observers see the
before-state or the after-state, never the middle.

Transactions are also easy to misuse in the opposite direction. A transaction held
open too long — spanning a network call, a slow loop, or user think-time — holds
locks and a snapshot the whole time, blocking other writers and bloating the
database. Correctness needs the boundary in the right place; throughput needs it as
tight as possible.

## Core Principles

- **A transaction is a unit of work, not a unit of code.** Its boundary is the set of
  changes that must be all-or-nothing — draw it there, not around whatever the
  function happens to do.
- **Commit or roll back on every path.** An abandoned open transaction holds locks
  and leaks a connection. Use the language's scope guard / `with` / `defer`.
- **Keep them short.** Do all slow work — HTTP calls, file I/O, heavy computation —
  *outside* the transaction. Open, write, commit, close.
- **Choose isolation deliberately.** The default (often `READ COMMITTED`) does not
  prevent lost updates or read-modify-write races. Know what your level does and does
  not guarantee.
- **Errors abort the transaction.** After an error inside a transaction, most engines
  reject further statements until rollback. Handle the failure; don't swallow it.

## Best Practices

- Wrap the transaction in a construct that guarantees rollback on any exception and
  commit only on the clean path. Never rely on manually pairing `BEGIN`/`COMMIT`.
- Never make an external network call while a transaction is open. If you must
  coordinate with another system, use an outbox or saga, not a long transaction.
- For read-modify-write on a single row, either use an atomic expression
  (`SET balance = balance - $1`) or `SELECT ... FOR UPDATE` to lock the row first —
  otherwise two transactions lose an update. See [locking](11-locking.md).
- Raise isolation to `REPEATABLE READ` or `SERIALIZABLE` when correctness needs a
  stable multi-row view, and be ready to **retry on serialization failure**
  (Postgres `40001`, deadlock `40P01`).
- Order writes consistently across the codebase (e.g. always parent before child) to
  reduce deadlocks.
- Do not nest business logic transactions; use savepoints for partial rollback within
  one transaction if you truly need it.
- Set a `statement_timeout` / `lock_timeout` so a stuck transaction fails fast instead
  of blocking others indefinitely.

## Examples

**Good Example** — tight boundary, atomic transfer, retry on conflict

```python
def transfer(db, from_id, to_id, cents):
    for attempt in range(3):                       # retry serialization failures
        try:
            with db.transaction(isolation="repeatable_read"):  # explicit boundary
                # Atomic decrement guarded by a CHECK/constraint; no read-then-write race.
                rows = db.execute(
                    "UPDATE accounts SET balance = balance - %s "
                    "WHERE id = %s AND balance >= %s", (cents, from_id, cents))
                if rows == 0:
                    raise InsufficientFunds()       # aborts + rolls back the whole unit
                db.execute(
                    "UPDATE accounts SET balance = balance + %s "
                    "WHERE id = %s", (cents, to_id))
            return                                  # committed atomically
        except SerializationError:
            continue                                # safe: nothing was committed
    raise RetriesExhausted()
```

**Bad Example** — no boundary, slow work inside, lost-update race

```python
def transfer(db, from_id, to_id, cents):
    db.execute("BEGIN")
    src = db.query("SELECT balance FROM accounts WHERE id = %s", from_id)  # read...
    charge_gateway(from_id, cents)          # network call inside the transaction: holds locks
    db.execute("UPDATE accounts SET balance = %s WHERE id = %s",
               src.balance - cents, from_id)   # ...write: two concurrent runs lose an update
    db.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", cents, to_id)
    db.execute("COMMIT")                     # no rollback path: an exception leaks the txn open
```

## Common Mistakes

- Read-modify-write without locking or an atomic update — the classic lost update.
- Holding a transaction open across a network/API call or user interaction.
- No rollback on the error path, leaking connections and locks.
- Assuming the default isolation prevents anomalies it does not (it usually doesn't).
- Catching and ignoring a serialization/deadlock error instead of retrying the unit.
- Wrapping too much (unrelated work) or too little (part of the invariant) in the
  transaction.
- Relying on application-side "check then insert" for uniqueness instead of a
  constraint plus transaction.

## Production Tips

- Monitor for long-running and idle-in-transaction sessions; they block vacuum and
  other writers. Alert and kill past a threshold.
- Make retry-on-serialization-failure a shared helper so every write path uses it.
- Ensure operations are idempotent where retries can re-run them (idempotency key).

## AI Review Checklist

- Is the transaction boundary exactly the set of changes that must be atomic?
- Is rollback guaranteed on every error path (scope guard, not manual pairing)?
- Are all slow/external operations outside the transaction?
- Is read-modify-write protected by an atomic update or `FOR UPDATE`?
- Is the isolation level appropriate, and are serialization failures retried?
- Are `statement_timeout`/`lock_timeout` set so stuck transactions fail fast?
- Is uniqueness/consistency backed by a constraint, not just an app-side check?

## Related

- `knowledge/databases/12-acid.md`
- `knowledge/databases/10-concurrency.md`
- `knowledge/databases/11-locking.md`
- `knowledge/databases/23-data-integrity.md`
- `knowledge/databases/08-query-optimization.md`
