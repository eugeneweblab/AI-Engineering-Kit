---
id: graphql/15-n1-problem
topic: graphql
slug: n1-problem
title: "N+1 Problem"
type: doc
order: 15
status: ready
tags: [graphql, n1-problem]
related: [graphql/16-dataloader, graphql/07-resolvers, graphql/22-performance, graphql/13-pagination, graphql/25-monitoring]
when_to_use: "Read before implementing resolvers that fetch related data per item, or when a list query issues far more database calls than expected."
---
# N+1 Problem

## Purpose

This document defines the **N+1 query problem** in GraphQL: what it is, why the
resolver execution model makes it the default failure mode, how to detect it, and the
strategies that fix it. It is written so an agent can recognize an N+1 pattern in a
resolver and choose the right remedy — batching, joins, or precomputation — before it
reaches production.

N+1 is not an edge case; it is what happens automatically when a field resolver fetches
related data one parent at a time. Every GraphQL server author will meet it, so
recognizing and preventing it is baseline competence, not an optimization.

## Why It Matters

GraphQL executes resolvers per field, per object. For a query that returns 100 posts
and asks each post's author, the naive server runs 1 query for the posts and then 100
more — one per post — to fetch authors: N+1 database round trips for what should be 2.
The query looks innocent in the schema and small in the response, but the cost is
hidden in the resolver tree.

The damage is nonlinear. N+1 multiplies with nesting (posts → author → author's
organization is N×M) and with pagination (bigger pages mean more queries), so a change
that doubles page size can 10× the database load. These queries also monopolize the
connection pool, so one expensive request degrades every concurrent request. Because
the symptom is latency and pool exhaustion rather than a wrong answer, N+1 is easy to
ship and hard to trace.

## Core Principles

- **Assume every relational field is N+1 until proven batched.** A resolver that hits a
  data source per parent object is N+1 by default; treat it as a defect to fix.
- **Batch, don't loop.** Collect the keys needed across all siblings in a tick and fetch
  them in one call. This is exactly what [DataLoader](16-dataloader.md) automates.
- **Measure queries per request, not just latency.** The definitive signal is the count
  of data-source calls; a request that scales its query count with result size is N+1.
- **Fix at the resolver boundary, not the client.** Clients cannot avoid N+1 — it is a
  server-side execution property. The server owns the remedy.
- **Prefer the cheapest remedy that fits.** Batching (DataLoader) for general relations,
  a join for a single hot path, precomputation for expensive aggregates.

## Best Practices

- Route every "fetch related record by key" resolver through a per-request DataLoader so
  the framework coalesces keys into one batched fetch.
- Return foreign keys from parent resolvers and resolve the related object in the child
  resolver via a loader — do not eagerly join everything in the parent, which over-fetches
  when the child field is not requested.
- For a single dominant access path, a SQL `JOIN` or `IN (...)` batch can beat a loader;
  choose it deliberately, not by default, because it couples the two levels.
- Cache-or-precompute expensive derived fields (counts, aggregates) rather than computing
  them per parent inside a hot resolver.
- Add an assertion in tests or CI that a representative list query stays under a query
  budget, so a regression fails the build instead of paging on-call.
- Watch nested relations specifically — N+1 hides one level down (author → organization)
  where it is easy to miss.

## Examples

**Good Example** — batched author lookup, constant query count

```ts
// One loader per request. All author ids requested during this tick are
// collected and fetched in a SINGLE query, regardless of how many posts.
const authorLoader = new DataLoader<string, User>(async (ids) => {
  const users = await db.user.findMany({ where: { id: { in: [...ids] } } });
  const byId = new Map(users.map((u) => [u.id, u]));
  return ids.map((id) => byId.get(id)!); // must return in the same order as ids
});

const resolvers = {
  Post: {
    // Called 100 times, but the loader batches into 1 query → 2 queries total.
    author: (post, _args, ctx) => ctx.authorLoader.load(post.authorId),
  },
};
```

**Bad Example** — one query per post, N+1

```ts
const resolvers = {
  Post: {
    // Called once per post. 100 posts → 100 separate author queries (+1 for posts).
    author: (post) => db.user.findUnique({ where: { id: post.authorId } }),
  },
};
```

## Common Mistakes

- Fetching a related record with a direct data-source call inside a per-item resolver.
- Sharing a DataLoader across requests, so its cache leaks data between users (loaders
  must be created per request in [context](08-context.md)).
- Returning batched results in the wrong order or with missing entries — a loader's
  result array must align one-to-one with the input keys.
- Only measuring latency and missing N+1 that hides under a warm cache in development.
- Solving N+1 with a blanket eager join, over-fetching when the nested field is not
  requested.
- Introducing N+1 one level deeper than the field you optimized (the grandchild
  relation).

## Production Tips

- Enable query logging or an APM trace that counts data-source calls per GraphQL
  operation; alert when the count scales with result size.
- Add a development-time N+1 detector (Sequelize/Prisma logging, `graphql-no-n-plus-one`
  style checks) that flags repeated identical queries within one request.
- Include a query-budget assertion in integration tests for your heaviest list endpoints.

## AI Review Checklist

- Does any per-item resolver call a data source directly instead of a batched loader?
- Are DataLoaders created per request, never shared across requests?
- Does the loader batch function return results in the same order as its input keys?
- Is the query count per operation bounded independent of result size?
- Are nested relations (child-of-child) also batched, not just the first level?
- Is there a test or monitor that catches an N+1 regression before production?

## Related

- `knowledge/graphql/16-dataloader.md`
- `knowledge/graphql/07-resolvers.md`
- `knowledge/graphql/22-performance.md`
- `knowledge/graphql/13-pagination.md`
- `knowledge/graphql/25-monitoring.md`
