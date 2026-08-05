---
id: prisma/99-ai-review-checklist
topic: prisma
slug: ai-review-checklist
title: "Prisma AI Review Checklist"
type: doc
order: 99
status: ready
tags: [prisma, ai-review-checklist]
related: [prisma/30-engineering-principles, prisma/11-relations-loading, prisma/08-transactions, prisma/17-raw-sql, prisma/18-error-handling]
when_to_use: "Read before reviewing or generating any Prisma query, schema, or migration code."
---
# Prisma AI Review Checklist

## Purpose

A focused checklist for an AI agent reviewing or writing Prisma code in a diff. Each
item is a yes/no an agent can confirm by reading the changed code alone. This is the
last gate before Prisma code merges — it targets the mistakes that pass tests and code
review yet fail under real data and concurrency.

## Why It Matters

Prisma's ergonomics hide cost. A one-line `findMany`, a relation accessed in a loop, or a
`$queryRawUnsafe` all look harmless in review and pass a small test suite. The damage
shows up only at scale: exhausted pools, table-scan latency, injection, or a half-written
transaction. An agent that checks these items deterministically catches what human review
skims past.

## Client and Connection Handling

- [ ] Is `PrismaClient` instantiated once in a shared module, not inside handlers or per call?
- [ ] Is the dev client cached on `globalThis` to survive hot-reload?
- [ ] Is `$disconnect()` wired to graceful shutdown rather than called mid-request?
- [ ] For serverless/edge, is a pooler (Accelerate, PgBouncer) configured instead of raw connections?

## Queries and Data Fetching

- [ ] Does every `findMany` on a growing table include a `take` and a deterministic `orderBy`?
- [ ] Are relations loaded via `include`/`select`, with no per-row lazy loads (N+1)?
- [ ] Does the query `select` only the columns it uses, rather than returning full rows?
- [ ] Is deep pagination done with a cursor, not a large `skip`?
- [ ] Are filtered/sorted columns backed by an index (`@@index` or `@unique`)?
- [ ] Are aggregations/counts scoped so they cannot scan an entire large table unbounded?

## Writes and Transactions

- [ ] Are dependent multi-step writes wrapped in `$transaction`?
- [ ] Do interactive transactions set `timeout`/`maxWait` and avoid external I/O inside the callback?
- [ ] Are upserts used for get-or-create instead of a read-then-write race?
- [ ] Is `updateMany`/`deleteMany` scoped by a `where` that cannot match unintended rows?

## Schema and Migrations

- [ ] Do schema changes come with a generated migration, not a `db push`?
- [ ] Is the migration reversible, or is an expand/contract sequence used for destructive changes?
- [ ] Do new relations declare the correct `onDelete`/`onUpdate` referential action?
- [ ] Are nullable-vs-required and default values chosen deliberately for existing rows?

## Security and Correctness

- [ ] Is all raw SQL written as tagged `$queryRaw`/`$executeRaw` templates, never `Unsafe` with interpolation?
- [ ] Are tenant/owner scopes applied to every query in multi-tenant code?
- [ ] Are known error codes (`P2002`, `P2025`, `P2034`) handled by code, not by message parsing?
- [ ] Are validated inputs (`Prisma.validator` or a schema library) used at the boundary before writes?
- [ ] Do errors returned to clients omit raw SQL, table names, and Prisma internals?

## Example of a Review Catch

```ts
// FLAG: new client per request + unbounded + N+1
export async function handler() {
  const prisma = new PrismaClient();               // ❌ new pool each request
  const orders = await prisma.order.findMany();    // ❌ no take, full rows
  for (const o of orders) {
    o.items = await prisma.item.findMany({ where: { orderId: o.id } }); // ❌ N+1
  }
  return orders;
}

// FIX: shared client, bounded, single query
import { prisma } from "../db";
export async function handler() {
  return prisma.order.findMany({
    select: { id: true, total: true, items: { select: { id: true, sku: true } } },
    orderBy: { createdAt: "desc" },
    take: 50,
  });
}
```

## Related

- `knowledge/prisma/30-engineering-principles.md`
- `knowledge/prisma/11-relations-loading.md`
- `knowledge/prisma/08-transactions.md`
- `knowledge/prisma/17-raw-sql.md`
- `knowledge/prisma/18-error-handling.md`
