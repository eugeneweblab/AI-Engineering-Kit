---
id: graphql/16-dataloader
topic: graphql
slug: dataloader
title: "DataLoader"
type: doc
order: 16
status: ready
tags: [graphql, dataloader, ApolloServer, findMany, DataLoader, loaded, related, resolvers]
related: [graphql/15-n1-problem, graphql/08-context, graphql/07-resolvers, graphql/21-caching, graphql/22-performance]
when_to_use: "Read before wiring batching/caching into resolvers, or when reviewing how related data is loaded per request."
---
# DataLoader

## Purpose

This document defines how to use **DataLoader** — the standard batching-and-caching
utility for GraphQL resolvers — to eliminate the [N+1 problem](15-n1-problem.md). It
covers the batch function contract, per-request instantiation, caching semantics, key
design, and the mistakes that turn a loader into a data-leak or a subtle correctness
bug. It is written so an agent can wire loaders that are both fast and safe.

DataLoader is a small pattern with sharp edges: get the batch function's ordering wrong
and you serve the wrong records; share a loader across requests and you serve one user's
data to another. The rules below are not stylistic — they are correctness invariants.

## Why It Matters

DataLoader is how nearly every production GraphQL server keeps query counts flat. It
coalesces all `load(key)` calls made within a single tick of the event loop into one
`loadMany` batch call, and memoizes results per key so repeated loads of the same key in
one request cost nothing. That turns N+1 into 1 and makes deep, fan-out queries viable.

But DataLoader's caching is per-instance, and its whole value depends on that cache
being scoped to a single request. A loader that lives for the process lifetime becomes a
cross-user cache: user A loads their private profile, user B loads the same key, and B
gets A's data. And because the batch function maps keys to results positionally, an
off-by-one in the return array silently pairs the wrong record with the wrong key. These
are exactly the bugs that pass tests and fail in production.

## Core Principles

- **One DataLoader instance per request.** Create loaders in the per-request
  [context](08-context.md) factory, never as module-level singletons. The cache must die
  with the request or it leaks data across users.
- **The batch function's output must align with its input.** Given `keys`, return an
  array of the same length, in the same order, with a value (or `null`/`Error`) at each
  index. Positional mismatch = wrong data.
- **Load by a stable, primitive key.** Keys are cache keys; use scalars (an id, or a
  stably-serialized composite), not object references that compare by identity.
- **The loader caches within a request only.** It is a request-scoped memo, not a
  cross-request cache. For that, put a real cache (Redis) *behind* the batch function.
- **Handle missing keys explicitly.** A missing record must map to `null` (or an `Error`)
  at its index, never be dropped, or every later result shifts up one slot.

## Best Practices

- Instantiate loaders in context: `context: () => ({ loaders: createLoaders(db) })`, so
  each operation gets a fresh set.
- Write the batch function to fetch all keys in one query (`WHERE id IN (...)`), build a
  `Map` from key to record, then map `keys` back through the map to preserve order and
  fill gaps with `null`.
- For composite keys, pass an object and set `cacheKeyFn` to a stable serialization
  (e.g. JSON of sorted fields) so equal keys hit the cache.
- Prime the loader (`loader.prime(id, obj)`) when you already have an object in hand
  (e.g. from a list query) to avoid re-fetching it.
- Clear or bypass the cache for fields that must reflect a write made earlier in the same
  request (`loader.clear(id)` after a mutation), since the per-request cache can go stale.
- Layer a shared cache behind the batch function for hot, rarely-changing lookups —
  DataLoader batches, Redis persists; they compose.

## Examples

**Good Example** — per-request loaders, order-preserving batch, null for misses

```ts
// Created fresh for every request in the context factory → no cross-request leak.
export function createLoaders(db: Db) {
  return {
    userById: new DataLoader<string, User | null>(async (ids) => {
      const rows = await db.user.findMany({ where: { id: { in: [...ids] } } });
      const byId = new Map(rows.map((u) => [u.id, u]));
      // Map every input key to its result IN ORDER; missing → null (never dropped).
      return ids.map((id) => byId.get(id) ?? null);
    }),
  };
}

const server = new ApolloServer({ schema });
await startStandaloneServer(server, {
  context: async () => ({ loaders: createLoaders(db) }), // one set per request
});
```

**Bad Example** — module-level singleton, order-losing batch

```ts
// Singleton: cache lives for the whole process → user B can read user A's cached row.
const userById = new DataLoader<string, User>(async (ids) => {
  const rows = await db.user.findMany({ where: { id: { in: [...ids] } } });
  // Returns DB order, not `ids` order, and silently drops missing ids
  // → every key can be paired with the wrong user. Correctness bug.
  return rows;
});
```

## Common Mistakes

- Declaring loaders at module scope, turning the per-request memo into a cross-user cache.
- Returning batch results in database order instead of key order.
- Dropping missing keys from the result array, shifting every subsequent result.
- Using object keys without a `cacheKeyFn`, so equal-but-not-identical keys never
  cache-hit (and unbounded distinct keys bloat the request cache).
- Treating DataLoader as a durable cache and expecting it to survive across requests.
- Serving stale data after an in-request write because the loader cache was not cleared.

## Production Tips

- Keep batch functions total: they must always resolve an array of the input length,
  even when the data source returns fewer rows.
- Set `maxBatchSize` for data sources with a parameter limit (e.g. SQL `IN` list caps) so
  large batches split instead of failing.
- Instrument batch size and hit rate; a loader with batch size 1 everywhere means the
  fan-out you expected is not happening — likely an `await` inside a loop serializing loads.

## AI Review Checklist

- Is each DataLoader created per request in the context factory, not a singleton?
- Does the batch function return an array matching the input keys in length and order?
- Are missing keys mapped to `null`/`Error` at their index rather than dropped?
- Do composite keys use a stable `cacheKeyFn`?
- Is the loader treated as request-scoped, with any durable caching layered behind it?
- Is the loader cache cleared or bypassed after an in-request write that it would stale?

## Related

- `knowledge/graphql/15-n1-problem.md`
- `knowledge/graphql/08-context.md`
- `knowledge/graphql/07-resolvers.md`
- `knowledge/graphql/21-caching.md`
- `knowledge/graphql/22-performance.md`
