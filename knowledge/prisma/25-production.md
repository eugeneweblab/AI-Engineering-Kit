---
id: prisma/25-production
topic: prisma
slug: production
title: "Prisma Production"
type: doc
order: 25
status: ready
tags: [prisma, production, PrismaClient, max_connections, DATABASE_URL, SIGTERM, connection_limit, SIGINT]
related: [prisma/05-migrations, prisma/15-performance, prisma/26-observability, prisma/18-error-handling, prisma/98-production-checklist]
when_to_use: "Read before deploying a Prisma app or reviewing its connection, migration, and runtime configuration for production."
---
# Prisma Production

## Purpose

This document defines how to run Prisma safely in production: how migrations reach the
database, how connections are pooled and sized, how the client is configured at runtime,
and how a deploy fails safe. It covers the operational surface, not query authoring
(see [best practices](24-best-practices.md)).

## Why It Matters

The gap between "works on my machine" and "works under load" is almost entirely
operational. A dev workflow uses `migrate dev`, one client, and a database with no other
traffic; production has migration ordering, connection limits, serverless cold starts,
and a pool shared with every other instance. The classic production incident is
connection exhaustion: each container opens a pool, the pools sum past the database's
`max_connections`, and every new request hangs. These failures appear only at scale, so
they must be designed for before the first deploy, not diagnosed after.

## Core Principles

- **Never apply migrations at runtime with `migrate dev`.** Production uses
  `prisma migrate deploy`, which applies committed migrations only and never generates or
  resets. `migrate dev` can drop data.
- **Size the pool for the topology.** `connection_limit × instances` must stay under the
  database's `max_connections`, with headroom for admin and other clients.
- **Serverless needs a pooler.** Functions scale to many short-lived instances; put a
  connection pooler (PgBouncer, Prisma Accelerate, Data Proxy) between them and Postgres.
- **Fail deploys forward, gated on migrations.** Run `migrate deploy` as a separate,
  ordered step before the new app version serves traffic.
- **Configuration comes from the environment.** The connection string, pool size, and log
  level are env vars, never hard-coded.

## Best Practices

- Deploy migrations with `prisma migrate deploy` in a release step that runs once, before
  new instances start — not from application boot, where N instances race.
- Set pool size explicitly via the connection string: `?connection_limit=10&pool_timeout=20`.
  Compute it as `(max_connections − reserved) / expected_instances`.
- On serverless/edge, connect through a pooler and set a low per-instance
  `connection_limit` (often 1); let the pooler multiplex.
- Make migrations backward compatible for zero-downtime deploys: add columns nullable or
  with defaults first, backfill, then tighten — never rename-in-place while old code runs.
- Reuse the client across warm invocations in serverless (cache on module/`globalThis`)
  and avoid `$disconnect()` on every request; only disconnect on shutdown.
- Handle `SIGTERM`/`SIGINT` by draining and calling `prisma.$disconnect()` so connections
  close cleanly and the pool does not leak on redeploy.
- Keep secrets in a secrets manager; the `DATABASE_URL` must never appear in logs, error
  messages, or the client repo.
- Test the exact migration set against a production-like copy in CI before release.

## Examples

**Good Example** — deploy-time migration, sized pool, graceful shutdown

```bash
# release.sh — runs once per deploy, before app instances start serving
npx prisma migrate deploy        # applies committed migrations only; no reset, no data loss
```

```ts
// db.ts — pool size and logging from the environment; clean shutdown
import { PrismaClient } from "@prisma/client";

export const prisma = new PrismaClient({
  // DATABASE_URL="postgresql://…/app?connection_limit=10&pool_timeout=20"
  log: (process.env.PRISMA_LOG ?? "warn,error").split(",") as any,
});

for (const sig of ["SIGTERM", "SIGINT"]) {
  process.once(sig, async () => {
    await prisma.$disconnect(); // drain the pool so a redeploy doesn't leak connections
    process.exit(0);
  });
}
```

**Bad Example** — runtime migration race and unbounded pools

```ts
// server startup — every instance does this on boot
await prisma.$executeRawUnsafe("..."); // ad-hoc DDL, no migration history
await runMigrateDev();                 // migrate dev in prod: can drop/reset data

// 40 serverless instances × default pool of ~13 = 520 connections
// Postgres max_connections is 100 → the 101st request hangs until pool_timeout, then errors
const prisma = new PrismaClient();     // no connection_limit, no pooler
```

## Common Mistakes

- Running `migrate dev` or `db push` against production.
- Instances applying migrations on boot, racing each other on the same history.
- Ignoring the pool math, so `instances × connection_limit` exceeds `max_connections`.
- Serverless without a pooler, opening a fresh Postgres connection per cold start.
- Destructive migrations (drop/rename) shipped in the same release as the code change,
  breaking the still-running old version.
- Never handling `SIGTERM`, leaking connections on every redeploy.
- Logging the connection string or leaving `DATABASE_URL` in the image.

## Production Tips

- Keep a migration lock/advisory so only one process can apply migrations at a time.
- Alert on pool saturation and `pool_timeout` errors; they are the leading indicator of
  under-sized connections. See [observability](26-observability.md).
- For blue/green or canary, ensure the schema is compatible with *both* app versions for
  the overlap window.
- Rehearse rollback: a forward "revert" migration, since Prisma migrations are not
  auto-reversible.

## AI Review Checklist

- Do deploys use `prisma migrate deploy`, run once before instances serve traffic?
- Is `connection_limit` set so `instances × limit` stays under `max_connections`?
- Is there a connection pooler in front of any serverless/edge deployment?
- Are migrations backward compatible with the currently running app version?
- Is `prisma.$disconnect()` called on `SIGTERM`/`SIGINT`?
- Is the client reused across warm invocations rather than reconnected per request?
- Is `DATABASE_URL` sourced from secrets and kept out of logs and images?

## Related

- `knowledge/prisma/05-migrations.md`
- `knowledge/prisma/15-performance.md`
- `knowledge/prisma/26-observability.md`
- `knowledge/prisma/18-error-handling.md`
- `knowledge/prisma/98-production-checklist.md`
