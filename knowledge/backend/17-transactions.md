---
id: backend/17-transactions
topic: backend
slug: transactions
title: "Backend Transactions"
type: doc
order: 17
status: ready
tags: [backend, transactions, InsufficientFundsError, transfer, transaction, send, findById, version]
related: [backend/18-database-design, backend/12-error-handling, backend/14-events, backend/07-business-logic, backend/13-caching]
when_to_use: "Read before writing code that changes more than one row, table, or system in a single logical operation."
---
# Backend Transactions

## Purpose

This document defines how to use database transactions to keep data consistent. It covers
the ACID guarantees, isolation levels and the anomalies they permit, transaction scope and
duration, optimistic vs. pessimistic concurrency, and how to coordinate changes that span
services (sagas) where a single database transaction cannot reach. The goal is that an
agent can wrap a multi-step change so the system is never left half-updated.

A transaction groups multiple operations so they either **all** commit or **all** roll
back. This is the primary tool for correctness under concurrency and failure.

## Why It Matters

Real operations touch several rows at once: transfer money (debit one account, credit
another), place an order (create order, decrement inventory, charge card). If the process
crashes or two requests race in the middle, non-transactional code leaves the database in
a state that was never valid — money debited but never credited, inventory sold twice. A
transaction is the boundary that makes "all or nothing" true. Getting scope, isolation,
and error handling right here is the difference between a system that is merely fast and
one that is *correct* under load.

## Core Principles

- **All-or-nothing is the point.** Every write in one logical operation belongs in one
  transaction. On any error, roll back the whole thing — a partial commit is a corruption.
- **Keep transactions short and focused.** A transaction holds locks; long transactions
  (and especially external calls inside them) block other writers and cause deadlocks and
  timeouts. Do slow work *outside* the transaction.
- **Never do I/O inside a transaction.** Do not call an HTTP API, send an email, or wait
  on a queue while a transaction is open. The lock is held for the duration and the remote
  call cannot be rolled back.
- **Pick the isolation level deliberately.** Higher isolation prevents more anomalies
  (dirty/non-repeatable/phantom reads) but reduces concurrency. Know which anomalies your
  logic cannot tolerate and set the level to match.
- **Concurrency needs a strategy, not luck.** Use optimistic (version column) or
  pessimistic (`SELECT ... FOR UPDATE`) locking on contended data; read-modify-write
  without one is a lost-update bug.
- **A transaction cannot span services.** Across databases or services, use a saga with
  compensating actions, not a distributed two-phase commit.

## Best Practices

- Wrap the whole operation in **one transaction** and commit only at the end; roll back on
  every error path. Ensure the transaction is released even when code throws (use the
  framework's managed/`withTransaction` helper rather than manual begin/commit).
- **Keep external calls out.** Charge the card and send the email *after* commit — reserve
  intent inside the transaction (e.g. an outbox row) and act on it afterward. See
  [events](14-events.md).
- For read-modify-write on shared rows, use **optimistic locking** (a `version` column
  checked in the `WHERE` clause) for low contention, or **`SELECT ... FOR UPDATE`** for
  high contention. Retry the optimistic path on version conflict.
- Choose isolation for the risk: **Read Committed** (common default) is fine for most
  writes; use **Repeatable Read / Serializable** when a decision depends on reading then
  writing the same rows (e.g. inventory checks) and phantom/lost-update would corrupt it.
- **Enforce invariants in the database too** (unique constraints, foreign keys, check
  constraints). Application checks race; the constraint is the last line of defense.
- Make retriable failures (deadlock, serialization conflict) **retry the whole
  transaction** with backoff — these are transient and expected under Serializable.
- For cross-service consistency, model a **saga**: a sequence of local transactions each
  with a compensating action to undo prior steps on failure.

## Examples

**Good Example** — single short transaction, locking, no I/O inside

```ts
// Transfer: both writes commit together or not at all. External work happens after.
await db.transaction({ isolation: "repeatable read" }, async (tx) => {
  const from = await tx.accounts.selectForUpdate(fromId); // lock the contended rows
  const to   = await tx.accounts.selectForUpdate(toId);
  if (from.balance < amount) throw new InsufficientFundsError(); // rolls back everything
  await tx.accounts.update(fromId, { balance: from.balance - amount });
  await tx.accounts.update(toId,   { balance: to.balance + amount });
  await tx.outbox.insert({ type: "TransferCompleted.v1", ... }); // intent, committed atomically
});
// Notify / call external systems AFTER commit — never hold a lock across a network call.
await notifier.send(fromId, "Transfer complete");
```

**Bad Example** — no transaction, external call mid-flight, lost update

```ts
async function transfer(fromId: string, toId: string, amount: number) {
  const from = await db.accounts.findById(fromId); // read, then...
  // ...another request can run between here and the update -> lost update, no lock/version.
  await db.accounts.update(fromId, { balance: from.balance - amount }); // commits alone
  await paymentApi.notify(fromId); // slow network call; if it throws, the credit below
                                   // never runs -> money debited, never credited.
  await db.accounts.update(toId, { balance: /* stale */ 0 + amount });  // no rollback path
}
```

## Common Mistakes

- Multi-step writes with no transaction, leaving partial, never-valid state on failure.
- External calls (HTTP, email, queue) inside an open transaction, holding locks and
  blocking writers.
- Long-running transactions that cause deadlocks and connection-pool exhaustion.
- Read-modify-write without optimistic version or `FOR UPDATE`, silently losing updates.
- Assuming the default isolation prevents phantoms or lost updates when it does not.
- Not rolling back on the error path, leaking the transaction and its locks.
- Trying to span services with one transaction instead of a saga with compensations.
- Relying only on application checks for uniqueness when two requests can race.

## Production Tips

- Alarm on **deadlock rate, long-running transactions, and lock wait time**; all indicate
  scope or contention problems before they page you.
- Set a **statement/transaction timeout** so a stuck transaction cannot hold locks forever.
- Keep the **connection pool** sized so transactions do not queue; a leaked (never-committed)
  transaction shows up as pool exhaustion.
- Prefer database constraints for invariants; they catch the races your code cannot.

## AI Review Checklist

- Is every multi-write operation wrapped in a single transaction with rollback on error?
- Are external/network calls kept strictly outside the transaction boundary?
- Is transaction scope as short as possible, with slow work moved out?
- Is read-modify-write on shared rows protected by optimistic version or `FOR UPDATE`?
- Is the isolation level chosen for the anomalies the logic cannot tolerate?
- Are transient conflicts (deadlock, serialization) retried with backoff?
- Are cross-service changes modeled as sagas with compensating actions, not 2PC?
- Are critical invariants also enforced by database constraints?

## Related

- `knowledge/backend/18-database-design.md`
- `knowledge/backend/12-error-handling.md`
- `knowledge/backend/14-events.md`
- `knowledge/backend/07-business-logic.md`
- `knowledge/backend/13-caching.md`
