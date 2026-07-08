---
id: graphql/21-caching
topic: graphql
slug: caching
title: "Caching"
type: doc
order: 21
status: ready
tags: [graphql, caching]
related: [graphql/16-dataloader, graphql/22-performance, graphql/15-n1-problem, graphql/13-pagination, graphql/19-authorization]
when_to_use: "Read before adding any caching layer to a GraphQL API, from DataLoader to a CDN."
---
# Caching

## Purpose

This document defines how to cache in a GraphQL API across its distinct layers:
per-request (DataLoader), server-side object caching, HTTP/CDN caching of responses, and
client normalized caches. It explains why GraphQL's single POST endpoint breaks naive HTTP
caching and how to restore it safely.

## Why It Matters

REST caching is mostly free: a `GET /users/1` is a stable, cacheable URL. GraphQL sends
every query as a `POST` to one URL with the query in the body, so URL-based HTTP caches and
CDNs see one uncacheable endpoint. Meanwhile a single query resolves many fields, each a
potential cache target with its own volatility and — critically — its own *authorization
scope*. Caching the wrong layer, or ignoring the caller in the cache key, either wastes the
biggest performance lever GraphQL offers or serves one user's private data to another.

## Core Principles

- **Cache per layer, deliberately.** Four independent layers exist: request-scoped
  ([DataLoader](16-dataloader.md)), server object cache, HTTP/CDN response cache, and the
  client store. Each has a different key, TTL, and invalidation story. Don't conflate them.
- **DataLoader is per-request, and only per-request.** Its cache dedupes and batches loads
  within one operation. Never reuse a DataLoader across requests — it would serve stale and
  cross-tenant data.
- **The cache key must include the authorization scope.** Any shared cache (server or CDN)
  keyed only on the query serves private data across users. Key on user/tenant/role, or
  cache only truly public fields.
- **Cacheability is a property of the field.** Per-field TTL / cache hints (static config
  vs. live inventory) beat one blanket policy on the whole response.
- **Prefer POST-with-cache-hints or persisted queries for CDN caching.** Registered
  persisted queries turn an opaque POST body into a stable, cacheable id.

## Best Practices

- Install a [DataLoader](16-dataloader.md) per request in `context` for every batchable
  entity; this is the highest-leverage, safest cache and solves the [N+1](15-n1-problem.md).
- For cross-request server caching, key on `(entity, id, viewerScope)` and set explicit
  TTLs; wire it *behind* the DataLoader so a request still dedupes.
- Emit response cache hints (`@cacheControl(maxAge, scope: PRIVATE|PUBLIC)` in Apollo, or
  the equivalent) at the field level; the response's cacheability is the minimum of its
  fields. Mark anything auth-dependent `PRIVATE`.
- Use Automatic Persisted Queries (APQ) so clients send a hash; a CDN can cache `GET` by
  that hash for public, `PUBLIC`-scoped operations.
- Invalidate on write: after a mutation, evict or update the affected entity keys. Prefer
  short TTLs over clever invalidation when correctness matters more than hit rate.
- On the client (Apollo/urql/Relay), give every cacheable type a stable `id`/keyfields so
  the normalized store can update entities across queries.

## Examples

**Good Example** — request-scoped loader plus a scoped, TTL'd shared cache

```ts
// One DataLoader per request → batches + dedupes within the operation only.
function context({ req }) {
  const viewer = getViewer(req);
  return {
    viewer,
    users: new DataLoader(async (ids: string[]) => {
      // Shared cache is keyed WITH the viewer scope, so tenants never cross.
      const cached = await redis.mget(ids.map((id) => `user:${viewer.tenantId}:${id}`));
      const missing = ids.filter((_, i) => !cached[i]);
      const fresh = await db.user.findMany({ where: { id: { in: missing } } });
      for (const u of fresh)
        await redis.set(`user:${viewer.tenantId}:${u.id}`, u, "EX", 60); // explicit TTL
      return ids.map((id) => byId(cached, fresh, id));
    }),
  };
}
```

**Bad Example** — process-wide loader, no scope in the key

```ts
// Created ONCE at module load → shared across all requests and users.
const users = new DataLoader(async (ids) => {
  // Key omits the viewer → tenant A's cached user is served to tenant B,
  // and stale rows are never refreshed because the loader never resets.
  return redis.mget(ids.map((id) => `user:${id}`));
});
function context() {
  return { users }; // same instance for everyone → data leak + staleness
}
```

## Common Mistakes

- Sharing a DataLoader across requests, serving stale and cross-tenant data.
- Caching a response (server or CDN) with a key that ignores the caller's auth scope.
- Marking auth-dependent fields `PUBLIC`, letting a CDN store private data.
- Applying one TTL to the whole response when fields have wildly different volatility.
- Never invalidating after mutations, so writes are invisible until the TTL expires.
- Missing stable `id`/keyfields on the client, so the normalized cache can't update entities.
- Trying to CDN-cache raw `POST` bodies instead of using persisted/registered queries.

## Production Tips

- Track cache hit rate per layer; a low DataLoader hit rate signals a missing loader or an
  [N+1](15-n1-problem.md) still in the path.
- Prefer short TTLs plus write-through invalidation over long TTLs you can't reliably purge.
- Load-test with a warm and cold cache; the cold path is what pages you at 3am.

## AI Review Checklist

- Is a DataLoader created per request (in `context`), never at module scope?
- Does every shared/CDN cache key include user/tenant/role scope?
- Are cache hints applied per field, with auth-dependent fields marked `PRIVATE`?
- Is there an invalidation or short-TTL strategy for data changed by mutations?
- Do cacheable client types have stable `id`/keyfields?
- Is CDN caching done via persisted queries, not raw POST bodies?

## Related

- `knowledge/graphql/16-dataloader.md`
- `knowledge/graphql/22-performance.md`
- `knowledge/graphql/15-n1-problem.md`
- `knowledge/graphql/13-pagination.md`
- `knowledge/graphql/19-authorization.md`
