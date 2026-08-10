---
id: prisma/28-patterns
topic: prisma
slug: patterns
title: "Prisma Patterns"
type: doc
order: 28
status: ready
tags: [prisma, patterns, updateMany, withdraw, createMany, ConflictError, TransactionClient, Serializable]
related: [prisma/08-transactions, prisma/14-extensions, prisma/22-multi-tenancy, prisma/23-soft-delete, prisma/29-architecture]
when_to_use: "Read when choosing a reusable Prisma pattern — repository wrapper, transaction scoping, pagination, upsert, extensions — for a feature."
---
# Prisma Patterns

## Purpose

This document catalogs the recurring, proven patterns for structuring Prisma code:
repository wrappers, passing a transaction client, idempotent writes, cursor pagination,
extensions for cross-cutting behavior, and safe concurrency. These are the shapes to
reach for so each team does not reinvent — often incorrectly — the same solution.

## Why It Matters

Data access is where the same problems recur in every feature: "how do I run these two
writes atomically," "how do I paginate a large list," "how do I not clobber a concurrent
update." Each has a correct pattern and several tempting wrong ones. Standardizing on the
right pattern removes a class of bugs — lost updates, offset pagination that skips rows,
partial writes — from the codebase wholesale, and makes reviews about intent rather than
re-litigating mechanics.

## Core Principles

- **Compose transactions by passing the client.** Repository methods accept a
  `Prisma.TransactionClient | PrismaClient` so callers can bundle them atomically.
- **Make writes idempotent.** Prefer `upsert` and unique constraints so a retried request
  does not create duplicates.
- **Paginate by cursor for large or infinite lists.** Offset pagination degrades and
  skips/repeats rows under concurrent writes.
- **Guard concurrent updates with a version or condition.** Use optimistic concurrency,
  not read-modify-write, when two requests can touch the same row.
- **Centralize cross-cutting rules with extensions.** Soft delete, tenant scoping, and
  audit fields belong in `$extends`, not copy-pasted into every query.

## Best Practices

- Type repository methods to accept a transaction-capable client so a service can wrap
  several calls in one `$transaction` (see the Good example).
- Use interactive transactions (`prisma.$transaction(async (tx) => …)`) for multi-step
  logic that must read-then-write atomically; keep them short to avoid holding locks.
- Set `isolationLevel` explicitly (e.g. `Serializable`) when correctness depends on it,
  and handle the resulting retry on `P2034` (write conflict).
- Use cursor pagination with a stable, unique sort key (`orderBy: { id }`, `cursor`,
  `skip: 1`, `take`) for feeds and large tables. See [pagination](10-pagination.md).
- Implement optimistic locking with a `version Int` column: update
  `where: { id, version }` and treat a zero-count result as a conflict.
- Encapsulate soft delete and tenant filters in a client extension so no query can forget
  them. See [soft delete](23-soft-delete.md) and [multi-tenancy](22-multi-tenancy.md).
- Use `createMany`/`updateMany` for bulk writes instead of a loop of single writes; the
  loop is N round-trips.

## Examples

**Good Example** — transaction-passing repository and optimistic concurrency

```ts
import { Prisma, PrismaClient } from "@/generated/prisma/client";

// Accepts either the base client or a transaction client → composable & atomic.
type Db = PrismaClient | Prisma.TransactionClient;

const accounts = {
  // Optimistic lock: the update only applies if the version is unchanged.
  async withdraw(db: Db, id: string, amount: number, version: number) {
    const r = await db.account.updateMany({
      where: { id, version, balance: { gte: amount } },
      data: { balance: { decrement: amount }, version: { increment: 1 } },
    });
    if (r.count === 0) throw new ConflictError("stale write or insufficient funds");
  },
};

// Service composes two repo calls in ONE transaction.
await prisma.$transaction(async (tx) => {
  await accounts.withdraw(tx, from, 100, fromVersion);
  await tx.account.update({ where: { id: to }, data: { balance: { increment: 100 } } });
});
```

**Bad Example** — read-modify-write race and per-row loop

```ts
// Two concurrent transfers both read balance=100, both write 0 → one debit is lost.
const acct = await prisma.account.findUnique({ where: { id } });
await prisma.account.update({
  where: { id },
  data: { balance: acct.balance - 100 }, // last write wins, other update vanishes
});

for (const row of rows) {
  await prisma.item.create({ data: row }); // N round-trips instead of createMany
}
```

## Common Mistakes

- Read-modify-write on a hot row without a version guard → lost updates.
- Repository methods that hard-code the global client, so calls cannot be composed atomically.
- Offset pagination (`skip`/`take`) on large or actively-written tables → skipped/duplicate rows.
- Non-idempotent create endpoints, so a client retry creates duplicates.
- Long-running interactive transactions that hold locks and time out under load.
- Re-implementing soft delete / tenant scoping per query instead of one extension.
- Looping single-row writes where `createMany`/`updateMany` would do one statement.

## Production Tips

- Pick a transaction timeout (`maxWait`, `timeout`) deliberately; the defaults can be too
  short for batch work and too long for hot paths.
- On `Serializable`, wrap the transaction in a bounded retry loop for `P2034` conflicts.
- Keep upserts safe under concurrency by backing them with a unique constraint; a
  race can still produce a `P2002` you should catch and retry.

## AI Review Checklist

- Do repository methods accept a `TransactionClient` so callers can compose atomically?
- Are multi-step read-then-write operations inside a single `$transaction`?
- Do updates on contended rows use a version/condition guard, not read-modify-write?
- Is large-list pagination cursor-based with a stable unique sort key?
- Are create endpoints idempotent (upsert + unique constraint)?
- Are soft delete and tenant scoping enforced by an extension, not per query?
- Are bulk writes done with `createMany`/`updateMany` rather than loops?

## Related

- `knowledge/prisma/08-transactions.md`
- `knowledge/prisma/14-extensions.md`
- `knowledge/prisma/22-multi-tenancy.md`
- `knowledge/prisma/23-soft-delete.md`
- `knowledge/prisma/29-architecture.md`
