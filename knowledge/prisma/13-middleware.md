---
id: prisma/13-middleware
topic: prisma
slug: middleware
title: "Middleware"
type: doc
order: 13
status: ready
tags: [prisma, middleware]
related: [prisma/14-extensions, prisma/23-soft-delete, prisma/26-observability, prisma/06-client]
when_to_use: "Read before adding, reviewing, or migrating any `prisma.$use` middleware that intercepts queries."
---
# Middleware

## Purpose

This document defines how to use — and how to move away from — Prisma's query
middleware: functions registered with `prisma.$use()` that run around every Client
operation. Middleware sees the model, action, and args, and controls whether and how
the query proceeds. Common uses are logging, timing, soft-delete rewriting, and
audit trails.

Middleware is **legacy** as of Prisma 5+. The `$use` API still works but is superseded
by the `query` component of [Client Extensions](14-extensions.md), which is
type-safe and composable. Prefer extensions for new code; understand middleware because
existing codebases still rely on it.

## Why It Matters

Middleware runs on *every* query in the client, so a bug there is a bug everywhere. A
middleware that forgets to `await next(params)` returns `undefined` and silently breaks
every read. One that rewrites `args` incorrectly can leak soft-deleted rows or apply the
wrong tenant filter to all callers at once. Because middleware is invisible at the call
site — the developer writing `prisma.user.findMany()` cannot see it — incorrect
middleware produces confusing, system-wide failures that are hard to trace back. The
altitude that makes middleware powerful is exactly what makes it dangerous.

## Core Principles

- **Always call and return `next(params)`.** The middleware chain only continues if you
  invoke `next` and return its result. Forgetting this stops the query dead.
- **One responsibility per middleware.** Registration order is execution order; a stack
  of narrow middlewares is far easier to reason about than one that does five things.
- **Never mutate shared state or `params` in place carelessly.** Middleware runs
  concurrently across requests; captured mutable state causes cross-request bleaks.
- **Handle the actions you claim to handle.** Branch on `params.model` and
  `params.action`; pass everything else straight through untouched.
- **Prefer extensions for new work.** Middleware is untyped (`params.args` is `any`) and
  cannot see relations the way extensions can. Use it only to maintain existing code.

## Best Practices

- Guard every middleware with an explicit model/action check so unrelated queries are
  not accidentally rewritten.
- For cross-cutting reads that must exclude rows (soft delete), rewrite `params.action`
  and `params.args` deterministically and add a documented escape hatch for admin queries.
- Keep timing/logging middleware side-effect-only: measure around `next`, never alter
  the result — see [observability](26-observability.md).
- Register middleware once, at client construction, not inside request handlers, so it is
  not stacked repeatedly.
- When migrating, port each middleware to an extension `query` override and delete the
  `$use` call in the same change so behavior does not silently double up.

## Examples

**Good Example** — timing middleware that always continues the chain

```ts
prisma.$use(async (params, next) => {
  const start = Date.now();
  const result = await next(params); // MUST await + return, or every query returns undefined
  const ms = Date.now() - start;
  // Side-effect only: log, never touch `result`.
  logger.debug(`${params.model}.${params.action} took ${ms}ms`);
  return result;
});

// Soft-delete rewrite, scoped to one model + action so nothing else is affected.
prisma.$use(async (params, next) => {
  if (params.model === "Post" && params.action === "delete") {
    params.action = "update"; // turn a hard delete into a flag update
    params.args.data = { deletedAt: new Date() };
  }
  return next(params);
});
```

**Bad Example** — drops the chain and rewrites everything

```ts
prisma.$use(async (params, next) => {
  await next(params); // result computed but NOT returned → caller always gets undefined
});

prisma.$use(async (params, next) => {
  // No model/action guard: this injects `deletedAt` filter into EVERY query,
  // including creates and aggregates, corrupting unrelated operations.
  params.args = params.args ?? {};
  params.args.where = { deletedAt: null };
  return next(params);
});
```

## Common Mistakes

- Forgetting to `return next(params)`, so all queries resolve to `undefined`.
- No `params.model` / `params.action` guard, so the middleware fires on operations it
  was never meant to touch.
- Rewriting `args.where` without merging existing conditions, discarding the caller's filter.
- Registering middleware inside a request handler, stacking a new copy per request.
- Relying on middleware for security-critical filtering (tenant, soft delete) with no
  audited escape hatch — one missed action leaks data.
- Writing new middleware in 2026 instead of a Client Extension.

## Production Tips

- Treat middleware as a migration target: inventory every `$use` call and plan its move
  to [extensions](14-extensions.md).
- Keep middleware fast — it is on the hot path of every query; do no network I/O inside it.
- Emit metrics from timing middleware to a real collector, not just logs, so slow-query
  regressions are visible.

## AI Review Checklist

- Does every middleware `await` and `return next(params)` on all code paths?
- Is each middleware guarded by an explicit `params.model` / `params.action` check?
- When rewriting `args.where`, are existing conditions merged rather than replaced?
- Is middleware registered exactly once at client setup, not per request?
- Should this logic be a [Client Extension](14-extensions.md) instead?

## Related

- `knowledge/prisma/14-extensions.md`
- `knowledge/prisma/23-soft-delete.md`
- `knowledge/prisma/26-observability.md`
- `knowledge/prisma/06-client.md`
