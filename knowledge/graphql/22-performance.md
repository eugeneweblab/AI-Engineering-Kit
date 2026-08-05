---
id: graphql/22-performance
topic: graphql
slug: performance
title: "GraphQL Performance"
type: doc
order: 22
status: ready
tags: [graphql, performance, ApolloServer, first, findAll, depthLimit, load, findMany]
related: [graphql/15-n1-problem, graphql/16-dataloader, graphql/21-caching, graphql/13-pagination, graphql/17-security]
when_to_use: "Read before optimizing a slow GraphQL resolver, or hardening an API against expensive queries."
---
# GraphQL Performance

## Purpose

This document defines how to keep a GraphQL API fast and how to bound the cost a single
query can impose. It covers the dominant failure mode (N+1 fetches), query cost control
(depth/complexity limits), pagination, and where to measure. It is written so an agent can
diagnose and prevent GraphQL-specific performance problems.

## Why It Matters

In GraphQL the *client* decides the shape and size of each request, so worst-case cost is
not something you can bound by writing careful endpoints — a single innocent-looking query
can request a deeply nested, unbounded graph. The number-one production problem is the
[N+1](15-n1-problem.md): resolving a list of N parents fires N child queries. Add nesting
and a query can trigger thousands of database round-trips or exhaust memory. Performance in
GraphQL is therefore inseparable from [security](17-security.md): an unbounded query is
also a denial-of-service vector.

## Core Principles

- **Batch and cache data access per request.** The default fix for N+1 is a
  [DataLoader](16-dataloader.md) per entity, installed in `context`. This collapses N child
  loads into one batched call.
- **Bound every query before you run it.** Enforce maximum depth and a complexity/cost
  budget at validation time, so an expensive query is rejected before a single resolver runs.
- **Paginate all lists; never return an unbounded collection.** Use cursor-based
  [pagination](13-pagination.md) with a hard `first`/`last` cap. A field returning "all rows"
  is a latent outage.
- **Measure per resolver, not just per request.** GraphQL aggregates many resolvers; the
  slow one hides inside a fast-looking p50. Trace field-level timing.
- **Push work down to the database.** Filtering, sorting, and pagination belong in the query
  the data layer runs — not in resolvers that fetch everything and slice in memory.

## Best Practices

- Install a DataLoader per request for every relationship a list can traverse; verify with a
  query log that a nested list produces O(1) batched queries, not O(N).
- Add a validation rule capping query depth (e.g. 8–12) and a complexity estimator that
  weights list fields by their `first` argument; reject over-budget queries with a coded
  error (see [error handling](20-error-handling.md)).
- Set a default and maximum page size on every connection; ignore or clamp client requests
  that exceed the max.
- Avoid over-fetching in resolvers: select only the columns the requested fields need, using
  the resolve info or a projection, so wide rows aren't hydrated needlessly.
- Cache expensive, low-volatility fields behind the loader with an explicit TTL and a
  scoped key (see [caching](21-caching.md)).
- Set a server-side query timeout and a maximum response size so one request can't run
  unbounded.
- Disable introspection in production for public APIs if it isn't needed; it is a large,
  cacheable-but-heavy query.

## Examples

**Good Example** — batched loads, bounded query, DB-side pagination

```ts
// Depth + complexity limits reject pathological queries at validation time.
const server = new ApolloServer({
  validationRules: [depthLimit(10), complexityLimit(1000)],
});

const resolvers = {
  Query: {
    // Cursor pagination with a hard cap; the DB does the slicing.
    orders: (_p, { first = 20, after }, ctx: Ctx) => {
      const take = Math.min(first, 100); // clamp: client can't request 1e9 rows
      return db.order.findMany({ where: { tenantId: ctx.user.tenantId },
        take, cursor: after ? { id: after } : undefined });
    },
  },
  Order: {
    // Batched: N orders → ONE customer query, not N.
    customer: (order, _a, ctx: Ctx) => ctx.loaders.customer.load(order.customerId),
  },
};
```

**Bad Example** — N+1, unbounded list, in-memory slicing

```ts
const resolvers = {
  Query: {
    // No pagination, no cap → returns every row; OOMs as the table grows.
    orders: () => db.order.findAll(),
  },
  Order: {
    // Fires one query PER order → classic N+1; 500 orders = 500 round-trips.
    customer: (order) => db.customer.findById(order.customerId),
  },
};
// No depth/complexity limit → a deeply nested query is a free DoS.
```

## Common Mistakes

- Resolving a relationship with a direct DB call per parent instead of a DataLoader (N+1).
- Returning unbounded lists with no pagination or page-size cap.
- No depth or complexity limit, letting a nested query run the server out of resources.
- Slicing/filtering/sorting in the resolver after fetching everything from the DB.
- Reusing a DataLoader across requests (correctness bug) to "improve" the hit rate.
- Optimizing p50 while a single nested resolver drives the p99 nobody is tracing.
- Leaving introspection and unbounded aliasing open on a public endpoint.

## Production Tips

- Log slow *operations by name* with field-level timing so you can attribute the cost.
- Set the complexity budget from real client queries, then alert on rejections to catch both
  abuse and a budget set too tight.
- Load-test with realistic nesting and list sizes, not flat single-object queries.

## AI Review Checklist

- Is every list-traversing relationship resolved through a per-request DataLoader?
- Are depth and complexity/cost limits enforced at validation time?
- Does every list field paginate with a hard maximum page size?
- Is filtering/sorting/pagination pushed to the database, not done in memory?
- Is there a server-side query timeout and response-size bound?
- Is field-level tracing in place to find the slow resolver inside a fast request?

## Related

- `knowledge/graphql/15-n1-problem.md`
- `knowledge/graphql/16-dataloader.md`
- `knowledge/graphql/21-caching.md`
- `knowledge/graphql/13-pagination.md`
- `knowledge/graphql/17-security.md`
