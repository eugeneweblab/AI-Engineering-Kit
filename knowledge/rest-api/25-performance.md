---
id: rest-api/25-performance
topic: rest-api
slug: performance
title: "REST API Performance"
type: doc
order: 25
status: ready
tags: [rest-api, performance]
related: [rest-api/19-caching, rest-api/10-pagination, rest-api/17-rate-limiting, rest-api/06-request-response, rest-api/26-monitoring]
when_to_use: "Read before designing a high-traffic endpoint or diagnosing a slow, memory-heavy, or database-bound REST API."
---
# REST API Performance

## Purpose

This document defines how to make a REST API fast and cheap under load: response size,
query efficiency, caching, connection reuse, and payload shaping. It covers what you can
control at the API layer. It is distinct from infrastructure scaling — the goal here is to
do less work per request so each node serves more traffic before you need more nodes.

## Why It Matters

Latency is a feature, and it compounds. A single endpoint that issues N+1 queries or
serializes a 5 MB payload does not just feel slow — it holds a connection, a DB link, and
memory hostage, so throughput collapses under concurrency long before CPU maxes out. API
performance problems are usually invisible in development (one user, warm cache, tiny
dataset) and only appear in production with real data volumes and real concurrency. The
cheapest request is the one you never make; the second cheapest is the one you serve from
cache. Design for both from the start, because retrofitting them means changing contracts.

## Core Principles

- **Measure before optimizing.** Profile real endpoints with production-shaped data.
  Guessing wastes effort on code that is not the bottleneck. See [monitoring](26-monitoring.md).
- **The database is almost always the bottleneck.** Eliminate N+1 queries, index the
  columns you filter and sort on, and never `SELECT *` when you need three fields.
- **Bound every response.** Paginate collections and cap page size so no single request
  can load an unbounded dataset. See [pagination](10-pagination.md).
- **Cache what is expensive and stable.** Use HTTP caching (`ETag`, `Cache-Control`) and a
  shared store for hot, rarely-changing data. See [caching](19-caching.md).
- **Do slow work asynchronously.** Return `202 Accepted` for long operations (email, video
  transcode) and process them off the request path. The client should never wait on it.
- **Reuse connections.** Pool database and HTTP connections; establishing a new one per
  request adds latency and exhausts limits under load.

## Best Practices

- Fix N+1 access with a join, a batched `IN` query, or a DataLoader — one query for a list,
  not one per row.
- Add composite indexes matching your filter + sort combinations; verify with the query
  planner (`EXPLAIN`), because an unused index is dead weight on writes.
- Compress responses (`gzip`/`br`) and let clients negotiate via `Accept-Encoding`; it cuts
  payload size an order of magnitude for JSON.
- Support field selection (sparse fieldsets, e.g. `?fields=id,name`) so clients fetch only
  what they render, shrinking serialization and transfer cost.
- Set `Cache-Control` and `ETag` on cacheable `GET`s so clients and CDNs can skip the
  round trip entirely with conditional requests (`304 Not Modified`).
- Stream large responses and file downloads instead of buffering them fully into memory.
- Use keyset (cursor) pagination for large or deep result sets; `OFFSET` gets linearly
  slower as the offset grows.
- Set timeouts on every outbound call (DB, cache, third-party) so one slow dependency
  cannot pile up requests and exhaust the pool.

## Examples

**Good Example** — one batched query, bounded page, cache headers

```ts
// GET /authors/:id/posts?limit=20&cursor=... — bounded, indexed, cacheable.
app.get("/authors/:id/posts", async (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 20, 100); // hard cap on page size
  const cursor = req.query.cursor as string | undefined;

  // Keyset pagination + a single indexed query (index on author_id, id).
  const posts = await db.query(
    `SELECT id, title, created_at FROM posts
     WHERE author_id = $1 AND ($2::int IS NULL OR id < $2)
     ORDER BY id DESC LIMIT $3`,
    [req.params.id, cursor ?? null, limit],
  );

  res.set("Cache-Control", "public, max-age=60"); // hot list, tolerates 60s staleness
  res.json({ data: posts, nextCursor: posts.at(-1)?.id ?? null });
});
```

**Bad Example** — N+1 queries, unbounded result, no caching

```ts
app.get("/authors/:id/posts", async (req, res) => {
  const posts = await db.query("SELECT * FROM posts WHERE author_id = $1", [req.params.id]);

  // One extra query per post: N+1. 500 posts = 501 round trips.
  for (const p of posts) {
    p.author = await db.query("SELECT * FROM authors WHERE id = $1", [p.author_id]);
  }
  // No limit → loads the whole table into memory; no cache headers → every hit re-runs it.
  res.json(posts);
});
```

## Common Mistakes

- N+1 queries hidden behind an ORM's lazy relations.
- Returning unbounded collections with no pagination or page-size cap.
- `OFFSET` pagination on deep pages, which degrades linearly with offset.
- No cache headers on stable `GET`s, forcing recomputation on every request.
- Serializing entire objects when the client needs a few fields.
- Missing timeouts on outbound calls, so one slow dependency cascades into pool exhaustion.
- Doing slow work (email, image processing) synchronously inside the request.

## Production Tips

- Track p95/p99 latency per endpoint, not averages — the tail is what users feel.
- Put a CDN in front of cacheable `GET`s to offload origin traffic entirely.
- Load-test with production-shaped data volumes before launch; small datasets hide N+1.
- Add a slow-query log and alert on queries above a threshold.

## AI Review Checklist

- Are list endpoints paginated with a hard maximum page size?
- Are there any N+1 query patterns that a join or batch could collapse?
- Are the columns used in `WHERE`/`ORDER BY` actually indexed?
- Do cacheable `GET`s set `Cache-Control` and `ETag`?
- Do responses return only needed fields, and is compression enabled?
- Do all outbound calls have timeouts and pooled connections?
- Is long-running work handed off asynchronously rather than blocking the response?

## Related

- `knowledge/rest-api/19-caching.md`
- `knowledge/rest-api/10-pagination.md`
- `knowledge/rest-api/17-rate-limiting.md`
- `knowledge/rest-api/06-request-response.md`
- `knowledge/rest-api/26-monitoring.md`
