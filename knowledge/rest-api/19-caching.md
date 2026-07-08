---
id: rest-api/19-caching
topic: rest-api
slug: caching
title: "Caching"
type: doc
order: 19
status: ready
tags: [rest-api, caching]
related: [rest-api/07-status-codes, rest-api/06-request-response, rest-api/18-idempotency, rest-api/25-performance, rest-api/26-monitoring]
when_to_use: "Read before adding HTTP caching, ETags, or a CDN in front of any read-heavy endpoint."
---
# Caching

## Purpose

This document defines how to cache HTTP responses correctly: which responses are
cacheable, how to signal freshness and revalidation with `Cache-Control` and `ETag`,
and how to avoid serving one user's data to another. It covers the HTTP caching model
shared by browsers, CDNs, and reverse proxies — not in-process memoization.

Caching answers "can the client or an intermediary reuse this response instead of
asking me again?". Done right it removes latency and load. Done wrong it serves stale,
wrong, or leaked data — which is worse than no cache at all.

## Why It Matters

The fastest request is the one that never reaches your server. A well-tuned cache turns
a database hit into a `304 Not Modified` or a CDN edge response, cutting latency and
cost dramatically for read-heavy APIs. But an HTTP cache is shared infrastructure you
do not fully control: once a response is cached with the wrong headers, a proxy may keep
serving it for hours, and a `Cache-Control: public` on a personalized response can leak
one user's data to the next. Caching bugs are hard to reproduce and easy to ship, so the
headers must be deliberate on every response, not an afterthought.

## Core Principles

- **Only safe methods are cacheable.** Cache `GET` (and `HEAD`) responses. `POST`,
  `PUT`, `PATCH`, and `DELETE` change state and must never be served from cache.
- **Be explicit about freshness.** Every cacheable response should carry
  `Cache-Control`. Silence forces caches to guess with heuristics you did not choose.
- **`private` vs `public` is a security boundary.** Anything tied to a user — bearer
  token, cookie, session — must be `Cache-Control: private` (or `no-store`) so shared
  caches never store it. `public` is only for identical-for-everyone responses.
- **Validators enable cheap revalidation.** An `ETag` (content fingerprint) or
  `Last-Modified` lets a client ask "still valid?" and get a bodyless `304` when it is,
  saving bandwidth without risking staleness.
- **The cache key must include everything that varies the response.** Use the `Vary`
  header (e.g. `Vary: Accept-Encoding, Authorization`) so a cache does not serve a
  gzip body to a client that wanted plain text, or one auth context's data to another.

## Best Practices

- Set `Cache-Control: no-store` on responses containing credentials, tokens, or
  personal data you never want persisted anywhere.
- Use `Cache-Control: private, max-age=<seconds>` for per-user data the browser may
  reuse but shared proxies must not.
- Use `Cache-Control: public, max-age=..., stale-while-revalidate=...` for shared,
  cacheable content; `stale-while-revalidate` serves slightly stale data instantly
  while refreshing in the background.
- Emit a strong `ETag` and honor `If-None-Match`, returning `304` when it matches —
  this is the cheapest correct response you can send.
- Prefer versioned URLs or content hashes for immutable assets and set
  `Cache-Control: public, max-age=31536000, immutable`. Change the URL to change the
  content; never mutate a cached URL in place.
- Invalidate on write: when a `PUT`/`DELETE` changes a resource, ensure its cached
  representation is purged or its `ETag` changes so clients revalidate.

## Examples

**Good Example** — conditional `GET` with an ETag and scoped cacheability

```ts
async function getProfile(req: Request, res: Response) {
  const user = await users.find(req.params.id);
  const etag = `"${user.version}"`; // fingerprint that changes when the row changes

  // Client already has this version → send an empty 304, no body, no DB serialization.
  if (req.header("If-None-Match") === etag) {
    return res.status(304).end();
  }

  res.setHeader("ETag", etag);
  // Per-user data: browser may reuse for 60s, but NO shared proxy may store it.
  res.setHeader("Cache-Control", "private, max-age=60");
  res.setHeader("Vary", "Authorization"); // different token → different cache entry
  return res.json(user);
}
```

**Bad Example** — personalized response cached publicly

```ts
async function getProfile(req: Request, res: Response) {
  const user = await users.find(req.params.id);
  // "public" lets a CDN store THIS user's profile and serve it to the next visitor.
  // No ETag → no cheap revalidation. No Vary → auth context ignored entirely.
  res.setHeader("Cache-Control", "public, max-age=3600");
  return res.json(user); // one user's private data now leaks to everyone
}
```

## Common Mistakes

- Marking user-specific responses `public`, letting a shared cache leak private data.
- Omitting `Cache-Control` entirely and letting proxies apply heuristic caching you
  never intended.
- Sending an `ETag` but never checking `If-None-Match`, so clients still download full
  bodies they already have.
- Forgetting `Vary`, so a compressed or auth-specific response is served to the wrong
  client.
- Caching error responses (`4xx`/`5xx`) with long lifetimes, pinning a transient
  failure into every downstream cache.
- Mutating content behind a long `max-age` URL instead of changing the URL, so clients
  see stale assets for the full TTL.

## Production Tips

- Put a CDN in front of `public`, cacheable `GET`s and watch the cache-hit ratio as a
  first-class metric alongside latency.
- Prefer `stale-while-revalidate` for dashboards and lists: users get instant responses
  while the cache refreshes out of band.
- Log and alert when write endpoints fail to invalidate — stale reads after writes are
  a common, silent correctness bug.

## AI Review Checklist

- Are only safe methods (`GET`/`HEAD`) cached, and never state-changing ones?
- Does every cacheable response carry an explicit `Cache-Control`?
- Is user-specific data `private` or `no-store`, never `public`?
- Are `ETag`/`Last-Modified` emitted and `If-None-Match`/`If-Modified-Since` honored?
- Does `Vary` list every header that changes the response (auth, encoding)?
- Do writes invalidate or version the cached representation they change?

## Related

- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/06-request-response.md`
- `knowledge/rest-api/18-idempotency.md`
- `knowledge/rest-api/25-performance.md`
- `knowledge/rest-api/26-monitoring.md`
