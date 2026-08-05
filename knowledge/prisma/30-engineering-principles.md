---
id: prisma/30-engineering-principles
topic: prisma
slug: engineering-principles
title: "Prisma Engineering Principles"
type: doc
order: 30
status: ready
tags: [prisma, engineering-principles]
related: [prisma/15-performance, prisma/08-transactions, prisma/05-migrations, prisma/11-relations-loading, prisma/21-security]
when_to_use: "Read before designing a data-access layer with Prisma or reviewing how the app talks to the database."
---
# Prisma Engineering Principles

## Purpose

This document defines the durable engineering principles for building a data-access
layer with Prisma ORM. It is written so an agent can make schema, query, and
transaction decisions that stay correct under load, survive migrations, and do not
leak the database into the rest of the application.

These principles are the "why" behind the rules in the sibling docs. When a specific
guide and a general principle appear to conflict, prefer the specific guide — but never
violate a principle without stating the reason.

## Why It Matters

The data layer is the one part of the system where mistakes are expensive and durable.
A bad query pattern (N+1, missing index, unbounded `findMany`) does not fail — it just
gets slower as data grows, until it takes production down at the worst time. A bad
schema decision is worse: once data is written, you can only change the shape through a
migration, and a careless migration can lose or corrupt rows irreversibly. Prisma gives
you type safety and ergonomics, but it will happily generate a catastrophic query if you
ask for one. The generated SQL is only as good as the model and the call.

## Core Principles

- **The schema is the source of truth.** `schema.prisma` defines the models, and every
  change reaches the database through a migration — never a hand-edited table, never
  `db push` in production. If the schema and the database disagree, the app is unsafe.
- **Reuse one PrismaClient.** Instantiate the client exactly once per process. Each new
  `PrismaClient` opens its own connection pool; creating them per-request exhausts
  database connections under load.
- **Ask for exactly what you need.** Use `select` and `take` on every query. Returning
  whole rows and unbounded lists wastes memory and bandwidth and leaks columns you did
  not intend to expose.
- **Loading relations is a query decision, not a convenience.** Use `include`/`select`
  to fetch relations in one round trip. Looping and lazily loading per row is the N+1
  trap — see [relations loading](11-relations-loading.md).
- **Multi-step writes belong in a transaction.** If two writes must both succeed or both
  fail, wrap them in `$transaction`. A partial write is a corrupt state that no retry can
  fix — see [transactions](08-transactions.md).
- **Never build SQL by string concatenation.** Use the query API or tagged
  `$queryRaw` templates so values are always parameterized — see [raw SQL](17-raw-sql.md).

## Best Practices

- Keep a single `PrismaClient` in a module (`src/db.ts`) and import it everywhere. In
  dev, cache it on `globalThis` so hot-reload does not spawn new pools.
- Set the connection pool (`connection_limit`) deliberately for your deployment: total
  connections across all instances must stay under the database's max.
- Always pair `findMany` with `take` and a deterministic `orderBy`. Use cursor
  pagination for large or infinite lists — see [pagination](10-pagination.md).
- Add a `@@index` for every column you filter or sort on in a hot path, and verify it is
  used — see [indexes](16-indexes.md).
- Handle `PrismaClientKnownRequestError` by code (`P2002` unique violation, `P2025`
  not found) rather than parsing messages — see [error handling](18-error-handling.md).
- Run migrations with `migrate deploy` in CI/CD; never let the app auto-migrate at boot.
- Type your boundaries with `Prisma.validator` and generated types so a schema change
  breaks the build, not production.

## Examples

**Good Example** — one client, scoped select, relation in one query, bounded list

```ts
// db.ts — a single shared client for the whole process
import { PrismaClient } from "@prisma/client";
export const prisma =
  globalThis.__prisma ?? (globalThis.__prisma = new PrismaClient());

// query.ts — ask for exactly the columns and rows you need
const posts = await prisma.post.findMany({
  where: { published: true },
  select: { id: true, title: true, author: { select: { name: true } } }, // no over-fetch, relation joined
  orderBy: { createdAt: "desc" },
  take: 20, // bounded — never unbounded on a growing table
});
```

**Bad Example** — new client per call, full rows, N+1 relation load

```ts
async function listPosts() {
  const prisma = new PrismaClient();              // new pool every call → connection exhaustion
  const posts = await prisma.post.findMany();     // no select, no take → full table, all columns
  for (const post of posts) {
    // one extra query PER post → N+1; a page of 200 posts = 201 round trips
    post.author = await prisma.user.findUnique({ where: { id: post.authorId } });
  }
  return posts; // client never disconnected either
}
```

## Common Mistakes

- Constructing `new PrismaClient()` inside a request handler or per function call.
- `findMany()` with no `take` — fine on 10 rows, fatal on 10 million.
- Loading relations in a loop instead of with `include`/`select`.
- Doing dependent writes without `$transaction`, leaving half-written state on failure.
- Editing the database directly or using `db push` in production, so the migration
  history no longer matches reality.
- Interpolating user input into `$queryRawUnsafe`, opening SQL injection.
- Catching database errors and swallowing them instead of mapping known codes.

## Production Tips

- Enable query logging in staging (`log: ["query"]`) to catch N+1 and slow queries
  before they ship; keep it off or sampled in production — see [observability](26-observability.md).
- Monitor pool saturation and query latency; a rising pool wait time is the early
  signal of connection exhaustion.
- Gate every schema change behind a reviewed, reversible migration and test it against a
  copy of production data — see [migrations](05-migrations.md).

## AI Review Checklist

- Is there exactly one `PrismaClient` per process, imported from a shared module?
- Does every `findMany` on a growing table have a `take` and an `orderBy`?
- Are relations loaded with `include`/`select` rather than in a loop?
- Are multi-step dependent writes wrapped in `$transaction`?
- Do schema changes go through a migration, never `db push` in production?
- Is all raw SQL parameterized via tagged templates, never string-concatenated?
- Are known error codes (`P2002`, `P2025`) handled explicitly?

## Related

- `knowledge/prisma/15-performance.md`
- `knowledge/prisma/08-transactions.md`
- `knowledge/prisma/05-migrations.md`
- `knowledge/prisma/11-relations-loading.md`
- `knowledge/prisma/21-security.md`
