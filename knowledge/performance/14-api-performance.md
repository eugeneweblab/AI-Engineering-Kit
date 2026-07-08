---
id: performance/14-api-performance
topic: performance
slug: api-performance
title: "API Performance"
type: doc
order: 14
status: ready
tags: [performance, api-performance]
related: [performance/13-database-performance, performance/08-caching, performance/05-network, performance/17-monitoring, performance/02-metrics]
when_to_use: "Read before designing or reviewing an HTTP/RPC endpoint's latency, payload, or concurrency behavior."
---
# API Performance

## Purpose

This document defines how to make an API fast and predictable: payload shape, caching
and compression, concurrency, pagination, and how to keep tail latency low. It is
written so an agent can design or review an endpoint and know it will hold up under
concurrent load, not just in a single-request test.

An API's speed is mostly the sum of what it *waits on* — usually the
[database](13-database-performance.md) and downstream services — plus the bytes it
ships over the [network](05-network.md). This doc governs the request/response layer
that sits between them.

## Why It Matters

The API is the contract every client depends on, so its latency is felt everywhere at
once: a mobile app, a web page, and every internal service inherit the endpoint's p99.
Because clients call APIs concurrently, a small per-request cost multiplies — an extra
50ms of serial work becomes the reason a whole page feels slow. APIs also fail in the
tail: the average looks fine while p99 users time out, retry, and amplify the load
that caused the slowness. Getting the request layer right — payloads, caching,
concurrency, backpressure — is what keeps the system stable when traffic spikes.

## Core Principles

- **Parallelize independent waits.** Most API latency is waiting on I/O. Two
  independent calls run concurrently cost the max, not the sum.
- **Ship the smallest correct payload.** Every field the client does not use costs
  serialization, bandwidth, and parse time on a device you do not control.
- **Cache at the edge of the work.** The fastest request is one your server never
  computes. Use HTTP caching and validators before adding server-side caches.
- **Protect the tail.** Timeouts, retries with backoff, and concurrency limits keep
  one slow dependency from taking down the endpoint.
- **Never do unbounded work per request.** Unpaginated lists and unbounded fan-out
  turn a normal request into an outage under real data volume.

## Best Practices

- Run independent downstream calls **concurrently** (`Promise.all`, `errgroup`,
  `asyncio.gather`), and set a **per-call timeout** so one slow dependency cannot
  stall the response.
- Enable **compression** (Brotli or gzip) for text responses over ~1KB; it typically
  cuts JSON payloads 60–80% for the cost of a little CPU.
- Support HTTP caching: set `Cache-Control` and `ETag`/`Last-Modified` so clients and
  CDNs can serve `304 Not Modified` instead of a full response.
- **Paginate** every collection endpoint with a hard maximum page size; never return
  "all rows." Prefer cursor pagination for stable, deep paging.
- Let clients request only the fields they need (sparse fieldsets or GraphQL), and
  avoid over-fetching related resources they will not render.
- Add **backpressure**: bounded concurrency to downstreams, a request queue limit, and
  load shedding (`429`/`503`) so overload degrades instead of collapsing.
- Make retries safe with **idempotency keys** on writes; retries without idempotency
  duplicate work and corrupt data under load.
- Measure and alert on **p95/p99 latency and error rate** per endpoint (see
  [metrics](02-metrics.md)), not average latency.

## Examples

**Good Example** — concurrent waits, bounded, cacheable

```ts
app.get("/dashboard", async (req, res) => {
  // Independent I/O runs in parallel → total ≈ slowest call, not the sum.
  const [user, orders] = await Promise.all([
    withTimeout(getUser(req.userId), 300),      // per-call timeout caps the tail
    withTimeout(getRecentOrders(req.userId, { limit: 20 }), 300), // bounded page
  ]);
  res.set("Cache-Control", "private, max-age=30"); // client can reuse for 30s
  res.json({ user, orders }); // returns only the fields the dashboard renders
});
```

**Bad Example** — serial waits, unbounded, no protection

```ts
app.get("/dashboard", async (req, res) => {
  const user = await getUser(req.userId);         // waits fully...
  const orders = await getAllOrders(req.userId);  // ...then waits again (serial)
  // No timeout: a slow orders service hangs the request until the socket dies.
  // getAllOrders returns every order ever → unbounded payload and DB work.
  res.json({ user, orders, raw: buildEverything() });
});
```

## Common Mistakes

- Awaiting independent calls one after another instead of in parallel.
- No per-call timeout, so a slow dependency hangs the whole endpoint.
- Returning unpaginated collections that grow without bound.
- Over-fetching: returning entire objects or graphs the client does not use.
- No compression or HTTP caching headers on cacheable responses.
- Retrying non-idempotent writes, duplicating work and data under load.
- Alerting on average latency, hiding the p99 users who actually suffer.

## Production Tips

- Put a CDN or reverse-proxy cache in front of read-heavy, cacheable endpoints; it
  removes load from the origin entirely, not just speeds it up.
- Track per-dependency latency inside each endpoint so you can attribute the tail to
  the right downstream (see [monitoring](17-monitoring.md)).
- Load-test at expected peak concurrency, not one request at a time — serialization
  and pool limits only show up under contention.

## AI Review Checklist

- Are independent downstream calls run concurrently rather than serially?
- Does every external/downstream call have a timeout and a retry/backoff policy?
- Is every collection endpoint paginated with a hard maximum page size?
- Does the response include only the fields the client needs?
- Are compression and HTTP caching headers (`Cache-Control`, `ETag`) set where valid?
- Are write endpoints idempotent so retries are safe under load?
- Are p95/p99 latency and error rate monitored per endpoint?

## Related

- `knowledge/performance/13-database-performance.md`
- `knowledge/performance/08-caching.md`
- `knowledge/performance/05-network.md`
- `knowledge/performance/17-monitoring.md`
- `knowledge/performance/02-metrics.md`
