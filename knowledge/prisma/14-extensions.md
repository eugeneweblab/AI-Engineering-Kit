---
id: prisma/14-extensions
topic: prisma
slug: extensions
title: "Prisma Extensions"
type: doc
order: 14
status: ready
tags: [prisma, extensions, PrismaClient, needs, model, findMany, args.where, compute]
related: [prisma/13-middleware, prisma/23-soft-delete, prisma/06-client, prisma/22-multi-tenancy]
when_to_use: "Read before adding computed fields, custom model methods, query interception, or result shaping with Prisma Client Extensions."
---
# Prisma Extensions

## Purpose

This document defines how to use Prisma Client Extensions (`prisma.$extends()`) — the
type-safe, composable mechanism for customizing the Client. Extensions have four
components: `result` (add computed fields), `model` (add custom methods to a model),
`query` (intercept and wrap operations, the modern replacement for
[middleware](13-middleware.md)), and `client` (add top-level client methods).

`$extends` returns a **new** client instance; the original is untouched. This is the
current, recommended way to add cross-cutting behavior in Prisma 5+ and later.

## Why It Matters

Extensions concentrate cross-cutting logic — soft delete, tenant scoping, computed
fields, audit hooks — in one reviewable place while preserving full TypeScript types at
every call site. Done well, this removes whole classes of repeated, easy-to-forget code
(every query manually adding `where: { deletedAt: null }`). Done badly, an extension
becomes an invisible global mutation: a `query` override that rewrites args for the
wrong operations, or a `result` field that fires an N+1 query per row. Because
extensions apply to every consumer of the extended client, correctness here protects or
endangers the entire codebase at once.

## Core Principles

- **Extend once, export the extended client.** Build the extended instance at setup and
  have the whole app import it. Re-extending per request throws away the benefit and can
  stack behavior.
- **`query` overrides must call `query(args)` and return its result.** Like middleware,
  the chain only continues if you invoke and return the inner function.
- **Scope `query` overrides narrowly.** Target specific models/operations
  (`user: { findMany }`) or use `$allOperations` deliberately — never rewrite args for
  operations you did not intend to touch.
- **Keep `result` fields cheap.** A computed field runs per row; make it a pure function
  of already-selected columns via `needs`, not a hidden database call.
- **Extensions compose, order matters.** Chained `$extends` apply in order; later
  `query` overrides wrap earlier ones. Keep the stack small and documented.

## Best Practices

- Use `result` with `needs` to declare which scalar fields a computed property depends
  on, so Prisma selects them and the type is correct.
- Use `model` to attach domain methods (e.g. `user.signUp(...)`) instead of scattering
  helper functions, keeping intent close to the data.
- Use a `query` `$allOperations` override to enforce tenant/soft-delete filters in one
  place — the modern replacement for `$use` — and merge, never overwrite, existing `where`.
- Publish reusable extensions with `Prisma.defineExtension(...)` so they are typed and
  shareable across clients.
- Treat the extended client as the single source of truth: forbid importing the raw
  `new PrismaClient()` elsewhere so the extension cannot be bypassed.

## Examples

**Good Example** — computed field via `needs`, scoped soft-delete filter

```ts
import { PrismaClient } from "@prisma/client";

export const prisma = new PrismaClient()
  .$extends({
    result: {
      user: {
        fullName: {
          needs: { firstName: true, lastName: true }, // Prisma selects these columns
          compute: (u) => `${u.firstName} ${u.lastName}`, // pure, no DB call
        },
      },
    },
  })
  .$extends({
    query: {
      post: {
        async findMany({ args, query }) {
          // Merge, don't replace: keep the caller's filter and add the soft-delete guard.
          args.where = { ...args.where, deletedAt: null };
          return query(args); // MUST return the inner call to continue the chain
        },
      },
    },
  });
```

**Bad Example** — hidden N+1 and a chain that never continues

```ts
export const prisma = new PrismaClient().$extends({
  result: {
    user: {
      postCount: {
        needs: { id: true },
        // Fires one query PER user row — an N+1 hidden inside a "field".
        compute: (u) => prisma.post.count({ where: { authorId: u.id } }),
      },
    },
  },
  query: {
    $allModels: {
      async findMany({ args, query }) {
        await query(args); // computed but not returned → findMany resolves to undefined
      },
    },
  },
});
```

## Common Mistakes

- Not returning `query(args)` in a `query` override, so the operation returns `undefined`.
- Doing database I/O inside a `result` `compute`, creating an N+1 that is invisible at the
  call site.
- Overwriting `args.where` instead of spreading it, silently dropping the caller's filter.
- Re-running `$extends` per request, losing types and stacking overrides.
- Importing the raw `PrismaClient` somewhere, bypassing the tenant/soft-delete guard.
- Applying a `$allOperations` override without excluding operations (e.g. `create`) that
  the rewrite does not make sense for.

## Production Tips

- Migrate legacy [middleware](13-middleware.md) to extensions one behavior at a time,
  deleting the `$use` call in the same change to avoid double application.
- Unit-test extensions directly: assert that computed fields are correct and that a
  scoped `query` override injects the expected `where` and preserves caller filters.
- Keep the extension stack short; deep chains make it hard to reason about final args.

## AI Review Checklist

- Does every `query` override call and `return query(args)` on all paths?
- Do `result` computed fields avoid database calls and declare their `needs`?
- Are `where` rewrites merged with the caller's conditions, never replaced?
- Is the extended client built once and imported everywhere, with the raw client forbidden?
- Are `$allOperations` / `$allModels` overrides scoped so they skip operations they must not touch?

## Related

- `knowledge/prisma/13-middleware.md`
- `knowledge/prisma/23-soft-delete.md`
- `knowledge/prisma/06-client.md`
- `knowledge/prisma/22-multi-tenancy.md`
