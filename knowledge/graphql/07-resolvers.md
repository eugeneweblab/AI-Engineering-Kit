---
id: graphql/07-resolvers
topic: graphql
slug: resolvers
title: "Resolvers"
type: doc
order: 7
status: ready
tags: [graphql, resolvers]
related: [graphql/08-context, graphql/15-n1-problem, graphql/16-dataloader, graphql/19-authorization, graphql/20-error-handling]
when_to_use: "Read before writing or reviewing any resolver function that fetches or mutates data behind a GraphQL field."
---
# Resolvers

## Purpose

This document defines how to write GraphQL **resolvers**: the functions that produce the
value for each field in the schema. It is written so an agent can implement resolvers that
are correct, fast, and safe — avoiding the N+1 explosions, unauthorized reads, and leaked
internals that resolvers make easy to introduce.

A resolver receives four arguments — `(parent, args, context, info)` — and returns the
field's value (or a promise for it). The engine walks the query tree, calling one resolver
per field per object. Understanding that shape is the whole game.

## Why It Matters

Resolvers are where the schema meets reality — the database, other services, the file
system. Because GraphQL calls a resolver *per field per object*, an innocent-looking
one-line resolver can fire thousands of queries when a list is requested: the classic
[N+1 problem](15-n1-problem.md). Resolvers are also the real authorization boundary; the
schema describes what *can* be asked, but only the resolver decides what *this user* may
see. Get a resolver wrong and you either melt the database or hand one tenant another's
data. The failure is proportional to traffic, so it hides in dev and erupts in production.

## Core Principles

- **A resolver returns data; it does not orchestrate transport.** No HTTP status codes, no
  response headers — those belong to the server layer. Return values or throw
  `GraphQLError`s.
- **Batch and cache per request.** Never issue a query inside a loop of resolver calls. Use
  a [DataLoader](16-dataloader.md) so N sibling fields collapse into one round trip.
- **Keep resolvers thin; push logic into a service/domain layer.** The resolver adapts
  GraphQL args to a use case and back. Business rules living in resolvers cannot be reused
  or tested outside GraphQL.
- **Authorize inside the resolver, on the resolved object.** Field-level checks must run
  where the data is; you cannot enforce "owner only" in the schema alone.
- **Resolve from `parent` first.** If the parent object already carries a field's value,
  return it directly — do not re-fetch. Default resolvers already do this.

## Best Practices

- Type the four arguments explicitly (`parent`, `args`, `context`, `info`) and read shared
  dependencies (db, loaders, user) from [context](08-context.md), never from module globals.
- Put every cross-object fetch (author of a post, items of an order) behind a DataLoader
  created per request; this is the single most important resolver-performance rule.
- Return `null` for an absent nullable field; throw a typed `GraphQLError` (with a stable
  `extensions.code`) for real failures. See [error handling](20-error-handling.md).
- Do authorization as early as possible and deny by default; never rely on the client not
  asking for a field.
- Only inspect `info` for legitimate needs (projection, requested-fields optimization).
  Deep coupling to the AST makes resolvers brittle.
- Make mutation resolvers do exactly one unit of work and return the affected object so the
  client can re-read updated fields in the same round trip.
- Keep resolvers synchronous-looking with `async/await`; never mix callbacks and promises.

## Examples

**Good Example** — thin, batched, authorized

```ts
const resolvers = {
  Query: {
    // Adapts args -> service call; no business logic inline.
    order: (_p, { id }, ctx) => ctx.services.orders.getForUser(id, ctx.user),
  },
  Order: {
    // Batched: 50 orders in a list => ONE user query, not 50 (no N+1).
    customer: (order, _a, ctx) => ctx.loaders.userById.load(order.customerId),

    // Field-level authz on the resolved object: only the owner sees the total.
    total: (order, _a, ctx) => {
      if (order.customerId !== ctx.user.id && !ctx.user.isAdmin) {
        throw new GraphQLError("Forbidden", { extensions: { code: "FORBIDDEN" } });
      }
      return order.totalCents;
    },
  },
};
```

**Bad Example** — N+1, fat resolver, no authz

```ts
const resolvers = {
  Query: {
    order: async (_p, { id }) => {
      const order = await db.query("SELECT * FROM orders WHERE id=$1", [id]);
      // Business logic + tax math wedged into the resolver: untestable, unreusable.
      order.total = order.items.reduce((s, i) => s + i.price * 1.2, 0);
      return order; // no ownership check — any user can read any order
    },
  },
  Order: {
    // Fires one query PER order in a list: the N+1 explosion.
    customer: (order) => db.query("SELECT * FROM users WHERE id=$1", [order.customerId]),
  },
};
```

## Common Mistakes

- Querying the database inside a per-object resolver instead of batching with DataLoader.
- Putting business logic, tax/pricing math, or transactions directly in the resolver.
- Skipping authorization because "the client's UI won't request that field".
- Re-fetching a value the `parent` object already contains.
- Throwing raw errors that leak stack traces or SQL instead of typed `GraphQLError`s.
- Reading db/user from module-level globals instead of `context`, breaking per-request isolation.
- Returning transport concerns (status codes, headers) from a resolver.

## Production Tips

- Add resolver-level tracing (Apollo/OpenTelemetry) so you can see which field, not just
  which operation, is slow. N+1s show up as one field with a huge call count.
- Fail CI on resolvers that call the db module directly outside a loader, via a lint rule
  or code-review checklist item — it is the highest-leverage guardrail.

## AI Review Checklist

- Does every cross-object fetch go through a per-request DataLoader (no query in a loop)?
- Is the resolver thin, delegating business logic to a service/domain layer?
- Is authorization enforced in the resolver, on the resolved object, deny-by-default?
- Does it return the value from `parent` when already present rather than re-fetching?
- Are errors typed `GraphQLError`s with stable `extensions.code`, leaking no internals?
- Are db, loaders, and user read from `context`, not module globals?
- Do mutation resolvers return the affected object for same-round-trip re-read?

## Related

- `knowledge/graphql/08-context.md`
- `knowledge/graphql/15-n1-problem.md`
- `knowledge/graphql/16-dataloader.md`
- `knowledge/graphql/19-authorization.md`
- `knowledge/graphql/20-error-handling.md`
