---
id: prisma/07-crud
topic: prisma
slug: crud
title: "CRUD"
type: doc
order: 7
status: ready
tags: [prisma, crud, upsert, findFirst, findUnique, updateMany, deleteMany, P2025]
related: [prisma/06-client, prisma/08-transactions, prisma/09-filtering, prisma/11-relations-loading, prisma/18-error-handling]
when_to_use: "Read before writing create, read, update, or delete queries with the Prisma Client."
---
# CRUD

## Purpose

This document defines how to perform the four basic operations — create, read, update,
delete — with the Prisma Client so they are correct, race-safe, and efficient. It covers
choosing the right method (`findUnique` vs `findFirst`, `update` vs `updateMany`,
`upsert`), narrowing selected fields, and avoiding the query patterns that turn one logical
operation into many round-trips.

CRUD is the surface every application touches most. The rules here assume the client is a
shared singleton ([Client](06-client.md)) and compose with [filtering](09-filtering.md),
[pagination](10-pagination.md), and [transactions](08-transactions.md).

## Why It Matters

CRUD queries are where correctness and performance are quietly won or lost. Reading a whole
row when you need one column, updating by a non-unique field, or reading-then-writing
without a guard are all easy to write and pass every test — until two requests race, or a
table grows, and the bug surfaces as duplicate rows, lost updates, or a slow endpoint. Each
method also has a distinct failure mode (`findUnique` throws differently from `update`), so
picking the wrong one changes how errors must be handled downstream.

## Core Principles

- **Match the method to the guarantee you need.** `findUnique` requires a unique field and
  is cacheable; `findFirst` scans with a filter. `update`/`delete` target exactly one row
  by unique field and throw if absent; `updateMany`/`deleteMany` affect zero-or-more and
  never throw for "not found".
- **Select only what you use.** Every query returns all scalar fields by default; use
  `select` or `omit` to avoid over-fetching wide rows and sensitive columns.
- **Prefer atomic operations over read-modify-write.** Use atomic number ops (`increment`)
  and `upsert` so concurrent requests cannot clobber each other.
- **Let the database enforce uniqueness.** Guard create-or-update with `upsert` or a unique
  constraint, not with a prior `findFirst` check that a racing request invalidates.
- **Handle "not found" as a first-class outcome**, not an exception you forgot to catch.

## Best Practices

- Read by unique key with `findUnique`; use `findUniqueOrThrow`/`findFirstOrThrow` when
  absence is genuinely an error, so you do not hand-roll null checks.
- Trim payloads with `select`. Never return password hashes or tokens just because they are
  columns — omit them at the query layer.
- Use `create` with nested `connect`/`create` to build a row and its relations in one call
  instead of several sequential writes.
- Replace "check then insert" with `upsert`, and "read, add one, write" with `update` +
  `{ increment: 1 }`.
- Use `updateMany`/`deleteMany` with an explicit `where` for bulk changes; never omit
  `where` unless you truly mean the whole table.
- Return the `count` from batch operations and assert it matches expectations when a caller
  assumes exactly one row changed.

## Examples

**Good Example** — atomic, narrow, race-safe

```ts
// Read only the columns the caller needs — not the whole (possibly wide) row.
const user = await prisma.user.findUnique({
  where: { id },
  select: { id: true, email: true, name: true }, // password hash never leaves the DB
});

// Atomic increment: two concurrent requests both count, no lost update.
await prisma.post.update({
  where: { id: postId },
  data: { views: { increment: 1 } },
});

// Create-or-update in one round-trip; the DB, not app code, enforces uniqueness.
await prisma.tag.upsert({
  where: { name },
  create: { name },
  update: {}, // already exists → no-op, no duplicate row
});
```

**Bad Example** — read-modify-write and a racy manual upsert

```ts
// Lost update: two requests read views=10, both write 11. One increment vanishes.
const post = await prisma.post.findUnique({ where: { id: postId } });
await prisma.post.update({
  where: { id: postId },
  data: { views: post.views + 1 },
});

// Racy "check then insert": a concurrent request inserts between the read and create,
// producing a duplicate row or a unique-constraint crash.
const existing = await prisma.tag.findFirst({ where: { name } });
if (!existing) await prisma.tag.create({ data: { name } });
```

## Common Mistakes

- Using `findFirst` when a unique key exists — losing cacheability and readability.
- Read-modify-write on counters instead of atomic `{ increment }`, causing lost updates.
- Manual "find then create" instead of `upsert`, racing under concurrency.
- Omitting `where` on `updateMany`/`deleteMany` and mutating the entire table.
- Returning full rows (including secrets) because `select`/`omit` was skipped.
- Assuming `update` returns null on missing rows — it throws `P2025`; that must be caught.
- Firing N sequential `create` calls in a loop instead of `createMany` for bulk inserts.

## Production Tips

- For high-write counters or balances, atomic ops still race across rows; wrap multi-row
  invariants in a [transaction](08-transactions.md) with the right isolation level.
- `createMany` skips relation nesting and returns only a count; use it for flat bulk inserts
  and `skipDuplicates: true` for idempotent imports.
- Map `P2025` (record not found) and `P2002` (unique violation) to domain errors at the
  edge so callers get meaningful HTTP responses. See [error handling](18-error-handling.md).

## AI Review Checklist

- Is `findUnique` used whenever a unique key is available, instead of `findFirst`?
- Do queries `select`/`omit` fields rather than returning whole rows, including secrets?
- Are counters and balances updated with atomic operations, not read-modify-write?
- Is create-or-update expressed as `upsert` rather than a racy find-then-create?
- Do `updateMany`/`deleteMany` calls carry an explicit `where`?
- Are `P2025`/`P2002` errors handled where single-row writes can miss or collide?

## Related

- `knowledge/prisma/06-client.md`
- `knowledge/prisma/08-transactions.md`
- `knowledge/prisma/09-filtering.md`
- `knowledge/prisma/11-relations-loading.md`
- `knowledge/prisma/18-error-handling.md`
