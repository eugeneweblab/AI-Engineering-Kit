---
id: rest-api/10-pagination
topic: rest-api
slug: pagination
title: "REST API Pagination"
type: doc
order: 10
status: ready
tags: [rest-api, pagination]
related: [rest-api/11-filtering, rest-api/12-sorting, rest-api/06-request-response, rest-api/25-performance, rest-api/19-caching]
when_to_use: "Read before building or reviewing any endpoint that returns a list or collection."
---
# REST API Pagination

## Purpose

This document defines how a collection endpoint returns results in bounded pages instead
of all at once. It is written so an agent can choose the right pagination strategy and
implement it so the API stays fast and stable as the dataset grows.

Every list endpoint is paginated or is a future outage. The only question is which
strategy — the choice has real trade-offs in correctness, performance, and client
ergonomics.

## Why It Matters

An unpaginated list works perfectly in development with ten rows and falls over in
production with ten million: the query scans the whole table, the JSON serializer blows
the heap, and the request times out. Worse, the naive fix — `LIMIT/OFFSET` — degrades
linearly as clients page deeper and silently skips or duplicates rows when the underlying
data changes mid-scroll. Pagination is not a nicety; it is the difference between an
endpoint that scales and one that becomes a reliability incident.

## Core Principles

- **Always paginate collections, with a default and a hard maximum page size.** Never let
  a client request unbounded results. Default modestly (e.g. 20), cap firmly (e.g. 100).
- **Prefer cursor (keyset) pagination for large or live data.** A cursor points at "the
  last item you saw," so cost is constant regardless of depth and inserts/deletes do not
  shift the window.
- **Use offset pagination only for small, stable, or jump-to-page datasets.** It is simple
  and allows random page access, but is slow at depth and unstable under writes.
- **Pagination metadata is part of the contract.** Return how to get the next page
  explicitly; never make the client guess or construct cursors itself.
- **Order is mandatory and total.** Pagination over an unordered or non-unique sort is
  undefined — always sort by a unique, stable key (often the id) as the tiebreaker.

## Best Practices

- Envelope results: `{ "data": [...], "pagination": { ... } }` so metadata has a home —
  see [request/response](06-request-response.md).
- For cursor pagination, return an opaque `next_cursor` (base64-encoded, treat as a
  black box on the client) and echo the `limit`. Return `null`/absent cursor at the end.
- Encode the sort key(s) and direction into the cursor so decoding is unambiguous and the
  cursor is self-describing; validate/reject tampered cursors.
- For offset pagination, accept `page`/`per_page` (or `limit`/`offset`), validate them as
  bounded integers, and reject absurd offsets.
- Avoid returning a total count on large tables — `COUNT(*)` can be as expensive as the
  page query. Offer it opt-in, or return an estimate, when clients truly need it.
- Keep sort/filter parameters stable across pages; changing them invalidates a cursor —
  see [sorting](12-sorting.md) and [filtering](11-filtering.md).
- Make paginated GETs cacheable where possible — see [caching](19-caching.md).

## Examples

**Good Example** — cursor pagination, bounded, stable ordering

```http
GET /v1/events?limit=20&cursor=eyJpZCI6IjAxSDgifQ HTTP/1.1
```

```sql
-- keyset: seek past the last id seen; constant cost at any depth,
-- stable even if rows are inserted/deleted between pages
SELECT id, type, created_at
FROM events
WHERE (created_at, id) < (:cursor_created_at, :cursor_id)  -- unique tiebreaker
ORDER BY created_at DESC, id DESC
LIMIT :limit + 1;  -- fetch one extra to know if a next page exists
```

```json
{
  "data": [ /* 20 events */ ],
  "pagination": { "limit": 20, "next_cursor": "eyJpZCI6IjAxSDkifQ" }
}
```

**Bad Example** — deep offset, no bound, no tiebreaker

```http
GET /v1/events?page=50000&per_page=100 HTTP/1.1
```

```sql
-- OFFSET must count and discard 5,000,000 rows before returning 100:
-- latency grows with page number; a slow, memory-heavy full scan.
SELECT id, type FROM events
ORDER BY created_at DESC          -- created_at not unique → rows can repeat/skip
LIMIT 100 OFFSET 5000000;         -- no max page size: client can demand millions
```

## Common Mistakes

- Shipping a list endpoint with no pagination at all ("it's fine, there aren't many").
- No maximum page size, letting a client request the entire table in one call.
- Deep `OFFSET` on large tables, causing latency that grows with page depth.
- Sorting by a non-unique column with no tiebreaker, so rows skip or duplicate.
- Running `COUNT(*)` on every request just to populate a total the client ignores.
- Exposing raw offsets/ids as cursors so clients build their own and couple to internals.
- Changing sort/filter mid-pagination and invalidating the cursor without an error.

## Production Tips

- Load-test list endpoints at realistic depth, not just page 1; offset problems only
  appear far in.
- Add a covering index on the exact `(sort_key, id)` used by the cursor so keyset seeks
  stay index-only.
- Return `Link` headers (`rel="next"`) in addition to the body for HTTP-native clients.
- Set the max page size at the framework/middleware layer so no handler can forget it.

## AI Review Checklist

- Is every collection endpoint paginated with a default and enforced maximum page size?
- Is the strategy appropriate — cursor for large/live data, offset only for small/stable?
- Is the sort order total (unique tiebreaker) so pages neither skip nor duplicate rows?
- Is pagination metadata (next cursor / page info) returned explicitly in an envelope?
- Are cursors opaque and validated against tampering?
- Is `COUNT(*)` avoided or opt-in on large datasets?
- Is there an index backing the keyset seek?

## Related

- `knowledge/rest-api/11-filtering.md`
- `knowledge/rest-api/12-sorting.md`
- `knowledge/rest-api/06-request-response.md`
- `knowledge/rest-api/25-performance.md`
- `knowledge/rest-api/19-caching.md`
