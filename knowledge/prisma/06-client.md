---
id: prisma/06-client
topic: prisma
slug: client
title: "Client"
type: doc
order: 6
status: ready
tags: [prisma, client]
related: [prisma/07-crud, prisma/08-transactions, prisma/15-performance, prisma/18-error-handling, prisma/19-testing]
when_to_use: "Read before instantiating PrismaClient or wiring it into an application's lifecycle."
---
# Client

## Purpose

This document defines how to instantiate, share, and shut down `PrismaClient` — the
generated query engine you call for every database operation. It covers the single
correct instantiation pattern, connection-pool behavior, logging, and clean shutdown, so
an agent can wire Prisma into an application without exhausting connections or leaking
resources.

The client is the runtime half of Prisma. The [schema](02-schema.md) and generated types
describe your data; the client executes against it. Get the client's lifecycle wrong and
the app fails under load, not in development.

## Why It Matters

`PrismaClient` owns a connection pool. Each instance opens its own pool, so creating a new
client per request or per module silently multiplies open connections until the database
refuses new ones — a failure that only appears under concurrency, in production, and looks
like an unrelated outage. In serverless and hot-reloading dev environments the same
mistake surfaces as "too many connections" within minutes. Because the cost is invisible
until scale, the client must be treated as a long-lived singleton from day one.

## Core Principles

- **One client per process.** Instantiate `PrismaClient` exactly once and share that
  instance everywhere. It is safe for concurrent use across the whole application.
- **Own the lifecycle explicitly.** The client connects lazily on first query; you are
  responsible for calling `$disconnect()` on shutdown so pooled connections drain.
- **Configure the pool for your runtime.** A long-running server and a serverless function
  need very different `connection_limit` values; the default is not universal.
- **The client is not the transport.** Never expose `PrismaClient` to the browser or embed
  it in edge/client bundles — it holds credentials and speaks directly to the database.
- **Instantiate once, configure once.** Log levels, error formatting, and datasource
  overrides are set at construction; do not mutate the client after creating it.

## Best Practices

- Export a single shared instance from one module and import it everywhere. Do not `new
  PrismaClient()` in request handlers, tests-under-load, or per-feature modules.
- In dev, cache the instance on `globalThis` so hot-reload does not spawn a new pool on
  every file save (a classic Next.js connection leak).
- Register a shutdown handler (`process.on('beforeExit'|'SIGINT'|'SIGTERM')`) that calls
  `await prisma.$disconnect()` so connections close cleanly on deploy/restart.
- Set the pool size via the connection string (`?connection_limit=N`). On serverless keep
  it low (often 1) and put a pooler (PgBouncer/Prisma Accelerate) in front.
- Configure `log` events explicitly. In production log `warn` and `error`; enable `query`
  logging only behind a flag — it is verbose and can leak parameter values.
- Type your log config as `Prisma.LogLevel[]` and forward events to your real logger
  rather than `console`, so query logs are structured and sampled.

## Examples

**Good Example** — shared singleton, hot-reload safe, clean shutdown

```ts
// db.ts — the ONE place PrismaClient is constructed
import { PrismaClient } from "@prisma/client";

// Reuse across hot reloads in dev so we do not open a new pool per file save.
const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    // Structured, minimal logging: noisy `query` stays off in prod.
    log: [{ level: "warn", emit: "stdout" }, { level: "error", emit: "stdout" }],
  });

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;

// Drain pooled connections on shutdown so deploys/restarts are clean.
process.on("beforeExit", async () => {
  await prisma.$disconnect();
});
```

**Bad Example** — a new client per call, no shutdown

```ts
import { PrismaClient } from "@prisma/client";

export async function getUser(id: string) {
  const prisma = new PrismaClient();          // new pool on EVERY request
  const user = await prisma.user.findUnique({ id }); // pool never released...
  return user;                                 // ...connections leak until DB refuses more
}
// Under load this exhausts the database's max_connections and takes the app down.
```

## Common Mistakes

- Calling `new PrismaClient()` inside a request handler, loop, or per-feature module,
  multiplying connection pools.
- Forgetting the `globalThis` cache in Next.js/dev, so every hot reload leaks a pool.
- Never calling `$disconnect()`, leaving connections open across restarts.
- Leaving the default `connection_limit` on serverless, then overwhelming the database
  without a pooler in front.
- Enabling `query` logging in production, flooding logs and exposing parameter values.
- Importing the client into edge/browser bundles, shipping database credentials to
  untrusted environments.

## Production Tips

- Put a connection pooler (PgBouncer in transaction mode, or Prisma Accelerate) between
  serverless functions and Postgres; set Prisma's `connection_limit=1` per function.
- Expose pool metrics via `prisma.$metrics` and alert on saturation before the DB does.
- Pin `@prisma/client` and the `prisma` CLI to the same version; a client generated
  against a mismatched engine version can fail at runtime.
- Run `prisma generate` in your build step (and postinstall) so the client is never stale.

## AI Review Checklist

- Is `PrismaClient` instantiated exactly once and shared, not created per request?
- Is there a `globalThis` cache guard for dev/hot-reload environments?
- Is `$disconnect()` called on a shutdown signal?
- Is `connection_limit` set appropriately for the runtime (server vs serverless)?
- Is production logging limited to `warn`/`error`, with `query` logging gated?
- Is the client kept out of any client-side or edge bundle?

## Related

- `knowledge/prisma/07-crud.md`
- `knowledge/prisma/08-transactions.md`
- `knowledge/prisma/15-performance.md`
- `knowledge/prisma/18-error-handling.md`
- `knowledge/prisma/19-testing.md`
