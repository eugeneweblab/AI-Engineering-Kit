---
id: prisma/24-best-practices
topic: prisma
slug: best-practices
title: "Prisma Best Practices"
type: doc
order: 24
status: ready
tags: [prisma, best-practices, PrismaClient, Float, findMany, findUniqueOrThrow, findFirst, PrismaClientKnownRequestError, prisma-backed, day-to-day, correct]
related: [prisma/06-client, prisma/15-performance, prisma/08-transactions, prisma/18-error-handling, prisma/29-architecture]
when_to_use: "Read before writing or reviewing any Prisma-backed data-access code, to apply the day-to-day rules that keep queries correct and cheap."
---
# Prisma Best Practices

## Purpose

This document collects the everyday rules for using Prisma Client correctly: how to
instantiate it, shape queries, select data, and handle results. It is the baseline an
agent applies to *ordinary* data-access code. Deeper topics — transactions, performance,
error handling — have their own docs; this one keeps them from being needed as often.

## Why It Matters

Prisma makes the wrong thing easy. A one-line `findMany` with a nested `include` reads
as innocent but can fetch every column of every row and every relation — a full table
scan disguised as clean code. Because the query builder hides the SQL, mistakes surface
not in review but in production, as slow endpoints and exhausted connection pools. The
cost of a bad pattern is multiplied by every request that runs it, so getting the
defaults right is the highest-leverage work in a Prisma codebase.

## Core Principles

- **One PrismaClient per process.** The client owns a connection pool. Instantiating it
  per request exhausts database connections; a singleton is mandatory.
- **Select what you use.** Default queries return every scalar column. Name the fields
  with `select` so the query cost is bounded and predictable.
- **Push work into the query.** Filter, sort, paginate, and aggregate in the database,
  not in application code after fetching everything.
- **Types come from the schema, not from you.** Let Prisma generate types; never
  hand-write interfaces that duplicate the model — they drift silently.
- **Let Prisma errors be typed.** Catch `PrismaClientKnownRequestError` and branch on
  the error code rather than string-matching messages.

## Best Practices

- Keep a single client instance in a module and reuse it. In dev with hot-reload, cache
  it on `globalThis` so reloads do not spawn new pools (see the Good example).
- Use `select` (allowlist) rather than `include` when you only need some fields.
  `include` pulls the entire related model; `select` on the relation is bounded.
- Prefer `findUniqueOrThrow` / `findFirstOrThrow` when absence is an error — they throw a
  typed `P2025` instead of returning `null` you might forget to check.
- Use `where` with unique fields for point reads so Prisma uses the index and the
  dataloader can batch. `findFirst` on a non-unique column is a scan.
- Cap every list query with `take`. An uncapped `findMany` is an unbounded response.
- Model money and precise decimals with `Decimal`, timestamps with `DateTime` and
  `@db.Timestamptz`. Never store money as `Float` — binary floating point loses cents.
- Set `onDelete` / `onUpdate` referential actions explicitly on relations so cascade
  behavior is defined in the schema, not left to database defaults.
- Run generation as part of the build (`prisma generate`) and commit the schema; never
  edit generated client code.

## Examples

**Good Example** — singleton client, bounded select, typed error handling

```ts
// db.ts — one client per process, safe across dev hot-reload
import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient, Prisma } from "@/generated/prisma/client";

const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL! });
const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };
export const prisma =
  globalForPrisma.prisma ?? new PrismaClient({ adapter, log: ["warn", "error"] });
if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;

// query.ts
export async function getUserCard(id: string) {
  try {
    return await prisma.user.findUniqueOrThrow({
      where: { id },                 // unique field → index + batchable
      select: { id: true, name: true, // only the columns the caller uses
        posts: { select: { id: true, title: true }, take: 10 } },
    });
  } catch (e) {
    if (e instanceof Prisma.PrismaClientKnownRequestError && e.code === "P2025") {
      return null; // branch on the code, not the message text
    }
    throw e;
  }
}
```

**Bad Example** — new client per call, unbounded fetch, stringly errors

```ts
export async function getUserCard(id: string) {
  const prisma = new PrismaClient();          // new pool every request → exhaustion
  const user = await prisma.user.findFirst({  // scan on a unique column
    where: { id },
    include: { posts: true },                 // every column of every post, uncapped
  });
  if (!user) throw new Error("not found");    // untyped; loses the P2025 signal
  return user;
}
```

## Common Mistakes

- Instantiating `PrismaClient` inside a request handler or per function call.
- Using `include` when `select` would fetch a fraction of the data.
- Returning entities straight to the API, leaking columns like `passwordHash`.
- Filtering or sorting in JavaScript after a `findMany` that loaded the whole table.
- Storing money or coordinates as `Float`.
- Catching all errors as `Error` and losing Prisma's error codes.
- Editing the generated client or hand-writing model types that duplicate the schema.

## Production Tips

- Enable `previewFeatures` you actually use, and pin the Prisma version; generated
  client and CLI must match exactly across the team and CI.
- Add `prisma generate` to `postinstall` so deployments never ship a stale client.
- Turn on query logging at `warn`/`error` in production and route it to your logger
  (see [observability](26-observability.md)); never log full query params with PII.

## AI Review Checklist

- Is there exactly one `PrismaClient` instance reused across the process?
- Does every read use `select` (or a bounded relation `select`) rather than blanket `include`?
- Is every `findMany` capped with `take`?
- Are point reads done on unique fields, using `...OrThrow` where absence is an error?
- Is money/precision stored as `Decimal`, not `Float`?
- Are Prisma errors caught by type and branched on `error.code`?
- Are internal columns stripped before an entity is returned to a client?

## Related

- `knowledge/prisma/06-client.md`
- `knowledge/prisma/15-performance.md`
- `knowledge/prisma/08-transactions.md`
- `knowledge/prisma/18-error-handling.md`
- `knowledge/prisma/29-architecture.md`
