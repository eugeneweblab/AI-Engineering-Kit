---
id: prisma/08-transactions
topic: prisma
slug: transactions
title: "Prisma Transactions"
type: doc
order: 8
status: ready
tags: [prisma, transactions, Serializable, timeout, transaction, maxWait, P2034, prisma]
related: [prisma/07-crud, prisma/06-client, prisma/15-performance, prisma/18-error-handling, prisma/09-filtering]
when_to_use: "Read before writing any operation where multiple database changes must succeed or fail together."
---
# Prisma Transactions

## Purpose

This document defines how to use Prisma transactions so a group of writes is atomic — all
succeed or all roll back — and so concurrent transactions do not corrupt shared state. It
covers the two transaction APIs (the `$transaction([...])` batch and the interactive
`$transaction(async (tx) => ...)` callback), isolation levels, timeouts, and the rules that
keep transactions short and deadlock-free.

Transactions build on ordinary [CRUD](07-crud.md) but add the guarantee that partial
failure is impossible. Reach for them whenever an invariant spans more than one row.

## Why It Matters

Without a transaction, a two-step change can fail halfway: money leaves one account and
never arrives in the other, or an order is created but its inventory is never decremented.
These half-completed states are permanent data corruption, not transient errors, and they
are almost impossible to reproduce afterward. Transactions also hold locks, so a
transaction that does slow work — an HTTP call, a large scan — blocks others and produces
deadlocks and timeouts under load. Correctness and performance are both decided by how the
transaction is scoped.

## Core Principles

- **Group writes that share an invariant.** If two writes must both hold for the data to be
  valid, they belong in one transaction.
- **Use the callback API when a later write depends on an earlier read.** The array form
  runs independent operations atomically; the interactive form lets you read, branch, then
  write on the same connection.
- **Always use the `tx` client inside a callback.** Queries issued on the outer `prisma`
  run outside the transaction and defeat its atomicity.
- **Keep transactions short and side-effect free.** No network calls, no user I/O, no
  `sleep` inside the boundary — locks are held the entire time.
- **Choose the isolation level for the invariant you are protecting.** The default may
  allow write skew; `Serializable` prevents it but requires retrying on conflict.

## Best Practices

- Prefer the interactive callback form for read-then-write logic; return early or `throw`
  to roll back — any thrown error aborts and rolls back the whole transaction.
- Do every query inside the callback on `tx`, never on the captured outer client.
- Set an explicit `timeout` and `maxWait`; a runaway transaction should fail fast, not pin
  a connection indefinitely.
- Raise isolation to `Serializable` for balance/inventory invariants and wrap the call in a
  retry loop that catches serialization failures (`P2034`).
- Move all slow work (external APIs, heavy computation) *outside* the transaction; only the
  atomic writes belong inside.
- Enforce invariants with database constraints too (unique, check, foreign key) so a bug in
  transaction scope still cannot persist invalid data.

## Examples

**Good Example** — interactive transaction, `tx` client, checked invariant

```ts
await prisma.$transaction(
  async (tx) => {
    // Read and write on the SAME transactional connection via `tx`.
    const from = await tx.account.update({
      where: { id: fromId },
      data: { balance: { decrement: amount } },
    });

    // Enforce the invariant inside the boundary; throwing rolls everything back.
    if (from.balance < 0) throw new Error("Insufficient funds");

    await tx.account.update({
      where: { id: toId },
      data: { balance: { increment: amount } },
    });
  },
  { isolationLevel: "Serializable", timeout: 5_000 }, // fail fast; prevent write skew
);
```

**Bad Example** — outer client inside the callback, slow work under lock

```ts
await prisma.$transaction(async (tx) => {
  // BUG: uses `prisma`, not `tx` → this write is NOT part of the transaction.
  await prisma.account.update({
    where: { id: fromId },
    data: { balance: { decrement: amount } },
  });

  // Holds DB locks while waiting on a third party → deadlocks and timeouts under load.
  await fetch("https://payments.example.com/charge", { method: "POST" });

  await tx.account.update({
    where: { id: toId },
    data: { balance: { increment: amount } },
  });
});
```

## Common Mistakes

- Querying the outer `prisma` client inside an interactive transaction, so those writes are
  not atomic with the rest.
- Performing network calls or long computation inside the transaction, holding locks and
  causing deadlocks.
- Relying on the default isolation level for balance/inventory logic, allowing write skew.
- Using `Serializable` without a retry loop, so legitimate conflicts surface as hard errors.
- Wrapping a single write in `$transaction` — a lone statement is already atomic; the
  wrapper only adds overhead.
- Forgetting that a thrown error rolls back; swallowing the error commits a partial change.

## Production Tips

- Retry serialization failures (`P2034`) with jittered backoff and a small cap; treat
  repeated failure as a real conflict to surface, not to loop forever.
- Keep transaction `timeout` well below the request timeout so a stuck transaction fails the
  request cleanly instead of piling up connections.
- On serverless with a pooler, ensure the pooler runs in *session* or *transaction* mode
  compatible with interactive transactions; some poolers break them.
- Log transaction duration and retry counts; rising values signal lock contention to fix
  before it becomes an outage.

## AI Review Checklist

- Are all writes that share an invariant grouped in one transaction?
- Does interactive-transaction code use `tx` for every query, never the outer client?
- Are network calls and heavy work kept outside the transaction boundary?
- Is the isolation level appropriate, with a retry loop where `Serializable` is used?
- Are `timeout` and `maxWait` set so a stuck transaction fails fast?
- Do database constraints back up the invariant the transaction enforces?

## Related

- `knowledge/prisma/07-crud.md`
- `knowledge/prisma/06-client.md`
- `knowledge/prisma/15-performance.md`
- `knowledge/prisma/18-error-handling.md`
- `knowledge/prisma/09-filtering.md`
