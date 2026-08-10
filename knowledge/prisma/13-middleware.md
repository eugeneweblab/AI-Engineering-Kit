---
id: prisma/13-middleware
topic: prisma
slug: middleware
title: "Migrating Off Prisma Middleware"
type: doc
order: 13
status: ready
tags: [prisma, middleware, $use, $extends, args.where, PrismaClient]
related: [prisma/14-extensions, prisma/23-soft-delete, prisma/26-observability, prisma/06-client]
when_to_use: "Read when a codebase still calls `prisma.$use`, or when a Prisma 7 upgrade fails because `$use` no longer exists."
---
# Migrating Off Prisma Middleware

## Purpose

**`prisma.$use()` was removed in Prisma 7.** It is not deprecated and not discouraged —
the method is gone, and code calling it fails to compile. This document exists to move
that code to [Client Extensions](14-extensions.md), and to explain the failure modes worth
carrying across, because they do not disappear with the API.

Middleware was a function registered on the client that ran around every operation, seeing
the model, action, and args, and controlling whether and how the query proceeded. Logging,
timing, soft-delete rewriting, and audit trails were the usual jobs. Extensions do all of
them through their `query` component, with types and per-model scoping that middleware
never had.

Write nothing new here. Read it only to port what already exists.

## Why It Matters

Middleware runs on *every* query in the client, so a bug there is a bug everywhere. A
middleware that forgets to `await next(params)` returns `undefined` and silently breaks
every read. One that rewrites `args` incorrectly can leak soft-deleted rows or apply the
wrong tenant filter to all callers at once. Because middleware is invisible at the call
site — the developer writing `prisma.user.findMany()` cannot see it — incorrect
middleware produces confusing, system-wide failures that are hard to trace back. The
altitude that makes middleware powerful is exactly what makes it dangerous.

## Core Principles

- **Port one middleware at a time, and delete the `$use` call in the same change.** A
  half-migrated client that both intercepts and extends applies the logic twice.
- **`params.model` + `params.action` becomes the extension's shape, not a condition.**
  Middleware guarded itself with an `if`; an extension names the model and operation in
  its structure, so the guard cannot be forgotten. That is the main safety gain — most
  middleware bugs were a missing guard.
- **`return query(args)` is the new `return next(params)`.** The chain still only
  continues if you call it and return its result, and forgetting is still the way to make
  every read resolve to `undefined`.
- **Keep the responsibility narrow.** One concern per extension, as before; composition
  via `$extends` chains rather than registration order.
- **Never carry over shared mutable state.** Extensions run concurrently across requests
  exactly as middleware did; captured mutable state still bleeds between them.

## Best Practices

- Inventory every `$use` call before changing any of them; migrating in isolation hides
  interactions that registration order used to make explicit.
- For cross-cutting reads that must exclude rows (soft delete), express the rewrite per
  model and per operation, and keep a documented escape hatch for admin queries — see
  [soft delete](23-soft-delete.md).
- Keep timing and logging side-effect-only: measure around `query`, never alter the
  result — see [observability](26-observability.md).
- Build the extended client once, at construction, and export that. `$extends` returns a
  *new* client rather than mutating the old one, so an extension applied inside a request
  handler is silently discarded — the mirror image of middleware's stacking bug.
- Type the result. An extension knows the model's types, so a rewrite that drops a
  required field is a compile error rather than a runtime surprise.

## Examples

**Good Example** — the same two middlewares, ported

```ts
// db.ts — one extended client, built once and exported.
import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient } from "@/generated/prisma/client";

// Keep the unextended client: an extension that needs a different operation on the
// same model calls it through `base`, which is what stops the interception recursing.
const base = new PrismaClient({
  adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL! }),
});

export const prisma = base
  .$extends({
    name: "timing",
    query: {
      // `$allModels` / `$allOperations` is the deliberate way to say "everything",
      // where middleware said it by omission.
      $allModels: {
        async $allOperations({ model, operation, args, query }) {
          const start = performance.now();
          const result = await query(args); // as with next(): await it and return it
          logger.debug(`${model}.${operation} took ${performance.now() - start}ms`);
          return result;                    // side-effect only; never touch `result`
        },
      },
    },
  })
  .$extends({
    name: "soft-delete",
    query: {
      // The guard is the shape: this cannot fire on another model or operation.
      post: {
        async delete({ args }) {
          return base.post.update({
            where: args.where,
            data: { deletedAt: new Date() },
          });
        },
      },
    },
  });
```

**Bad Example** — the two failures that outlived the API

```ts
export const prisma = new PrismaClient().$extends({
  query: {
    $allModels: {
      async $allOperations({ args, query }) {
        await query(args);   // computed but NOT returned -> every caller gets undefined
      },
    },
  },
});

function handler() {
  // `$extends` returns a NEW client; extending inside a handler throws the result away,
  // so the filter never applies. Middleware's failure was stacking a copy per request;
  // this one is the opposite and just as silent.
  prisma.$extends({ query: { post: { findMany: filterDeleted } } });
  return prisma.post.findMany();
}
```

## Common Mistakes

- Forgetting to `return query(args)`, so all queries resolve to `undefined` — unchanged
  from `next(params)`.
- Discarding the value of `$extends`, which returns a new client instead of mutating the
  receiver, so the extension never applies.
- Reaching for `$allModels`/`$allOperations` when a named model and operation would do:
  it recreates exactly the unguarded blast radius that made middleware dangerous.
- Rewriting `args.where` without merging existing conditions, discarding the caller's filter.
- Relying on either mechanism for security-critical filtering (tenant, soft delete) with
  no audited escape hatch — one missed operation leaks data.
- Adding `$use` to a Prisma 7 codebase. It does not exist; the build fails.

## Production Tips

- Upgrading to Prisma 7 turns every remaining `$use` into a build failure, which is the
  good case: plan the port before the upgrade rather than under it.
- Keep extensions fast — they are on the hot path of every query they match; do no network
  I/O inside one.
- Emit metrics from the timing extension to a real collector, not just logs, so slow-query
  regressions are visible.

## AI Review Checklist

- Does any `$use` call remain? On Prisma 7 it will not compile.
- Does every extension `await` and `return query(args)` on all code paths?
- Is the result of `$extends` assigned and exported, rather than discarded?
- Is the extension scoped to named models and operations instead of
  `$allModels`/`$allOperations`, unless it genuinely applies to everything?
- When rewriting `args.where`, are existing conditions merged rather than replaced?

## Related

- `knowledge/prisma/14-extensions.md`
- `knowledge/prisma/23-soft-delete.md`
- `knowledge/prisma/26-observability.md`
- `knowledge/prisma/06-client.md`
