---
id: prisma/20-debugging
topic: prisma
slug: debugging
title: "Prisma Debugging"
type: doc
order: 20
status: ready
tags: [prisma, debugging]
related: [prisma/15-performance, prisma/17-raw-sql, prisma/18-error-handling, prisma/26-observability]
when_to_use: "Read when a Prisma query returns wrong data, runs slow, or fails and you need to see the actual SQL."
---
# Prisma Debugging

## Purpose

This document defines how to make Prisma Client observable when something is wrong: how
to see the exact SQL it generates, time each query, trace connection and engine
problems, and inspect data directly. The aim is to turn "the query is weird" into a
concrete, reproducible SQL statement you can run and explain.

## Why It Matters

Prisma is an abstraction: you write `findMany` and it emits SQL you never see. That is a
feature until a query returns the wrong rows or takes two seconds, and then the gap
between what you wrote and what ran is exactly where the bug lives. Guessing at the SQL
wastes hours. The fastest path is always the same — make Prisma print the real query and
its parameters, run that SQL against the database with `EXPLAIN`, and reason about the
plan. Every debugging technique below exists to shrink that loop.

## Core Principles

- **See the real SQL first.** Before theorizing, enable query logging and read the exact
  statement and parameters Prisma sent. Most bugs are obvious once you can see them.
- **Reproduce in the database.** Copy the logged SQL into `psql` or Studio and run it.
  If it misbehaves there, the bug is your query, not your code.
- **Measure, don't guess, for slowness.** Time queries and run `EXPLAIN ANALYZE`; a slow
  query is almost always a missing index or an accidental N+1, both visible in the plan.
- **Separate the layers.** A failure is either in the query, the connection pool, or the
  engine. Logging tells you which; do not fix the wrong one.
- **Turn verbose logging off in production.** Query logging is a debugging tool and a
  performance and PII cost; it belongs behind a flag.

## Best Practices

- Enable structured logging on the client and subscribe to events so you get SQL,
  parameters, and duration you can filter — not just noise on stdout.
- For a one-off, set `DEBUG="prisma:query"` (or `prisma:*` for engine/connection detail)
  in the environment; it needs no code change and is ideal in a scratch reproduction.
- Use **Prisma Studio** (`npx prisma studio`) to inspect and edit rows directly when you
  suspect the data, not the query, is wrong.
- For slow queries, log the `duration` field, take the SQL Prisma emitted, and run
  `EXPLAIN ANALYZE` on it; look for `Seq Scan` on large tables (missing index) and
  repeated identical queries (N+1 — fix with `include`/`select` or a single query).
- Debug relation-loading N+1 by watching the query log: dozens of near-identical
  `SELECT` statements in a loop is the signature.
- For connection problems (`PrismaClientInitializationError`, pool timeouts), log at
  `prisma:client` / `prisma:engine` level and check pool size against concurrency.

## Examples

**Good Example** — event-based query logging behind a flag

```ts
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient({
  // Emit as events so we can format, filter, and route them — not raw stdout spam.
  log: process.env.DEBUG_SQL
    ? [{ level: "query", emit: "event" }, "warn", "error"]
    : ["warn", "error"], // production: warnings and errors only, no query text
});

if (process.env.DEBUG_SQL) {
  prisma.$on("query", (e) => {
    // The exact SQL + params + duration: paste this straight into psql / EXPLAIN.
    console.log(`${e.duration}ms  ${e.query}  ${e.params}`);
  });
}
```

**Bad Example** — always-on logging and print-debugging the wrong layer

```ts
const prisma = new PrismaClient({
  log: ["query"], // fires in production too: leaks PII in params, floods logs, slows I/O
});

async function getOrders(userId: number) {
  const user = await prisma.user.findUnique({ where: { id: userId } });
  console.log("got user", user); // guessing at data instead of reading the emitted SQL
  // The real bug (a missing index causing a Seq Scan) is invisible to console.log —
  // only EXPLAIN on the logged query would reveal it.
  return prisma.order.findMany({ where: { userId } });
}
```

## Common Mistakes

- Print-debugging JavaScript variables instead of reading the SQL Prisma actually ran.
- Leaving `log: ["query"]` on in production, leaking parameter values (often PII) and
  degrading throughput.
- Diagnosing slowness by staring at code instead of running `EXPLAIN ANALYZE` on the
  emitted query.
- Confusing an N+1 (many small queries) with a slow query (one expensive query) — the
  fixes are opposite; the query log distinguishes them at a glance.
- Editing data in Studio on a production database while "just checking".
- Blaming Prisma for a plan the database chose; the SQL is standard and inspectable.

## Production Tips

- Ship query timing to your metrics/tracing backend (see observability) with the query
  redacted of parameters, so you can spot regressions without logging PII.
- Keep a `DEBUG_SQL` env flag so any engineer can turn on full SQL logging in a staging
  reproduction without a code change or redeploy.
- Capture slow queries above a threshold from the `duration` event and alert on them,
  rather than logging every query.

## AI Review Checklist

- Is query logging gated behind an env flag and off by default in production?
- Are query events emitted (`emit: "event"`) so SQL, params, and duration are captured
  structurally rather than dumped to stdout?
- When a slow query is reported, is the fix based on `EXPLAIN ANALYZE` of the real SQL?
- Are N+1 patterns diagnosed from the query log and fixed with `include`/`select`?
- Are parameter values (potential PII) kept out of production logs?
- Is Studio used only against safe, non-production databases?

## Related

- `knowledge/prisma/15-performance.md`
- `knowledge/prisma/17-raw-sql.md`
- `knowledge/prisma/18-error-handling.md`
- `knowledge/prisma/26-observability.md`
