---
id: prisma/10-pagination
topic: prisma
slug: pagination
title: "Prisma Pagination"
type: doc
order: 10
status: ready
tags: [prisma, pagination]
related: [prisma/09-filtering, prisma/07-crud, prisma/16-indexes, prisma/15-performance, prisma/11-relations-loading]
when_to_use: "Read before returning any list endpoint or query that can grow beyond a screenful of rows."
---
# Prisma Pagination

## Purpose

This document defines how to page through result sets with the Prisma Client: the two
strategies Prisma supports — offset pagination (`skip`/`take`) and cursor pagination
(`cursor`/`take`) — when to use each, and how to keep paging fast and stable as data grows.
It covers ordering, stable tie-breakers, and returning enough metadata for callers to fetch
the next page.

Pagination sits on top of [filtering](09-filtering.md) and shares its dependence on
[indexes](16-indexes.md): a page is a filtered, ordered, bounded slice, and its speed comes
from the index behind the `order by`.

## Why It Matters

Every list endpoint that returns "all rows" is a latent outage — it works until the table
grows, then transfers megabytes and times out. The naive fix, offset pagination, hides a
second trap: `skip: 1_000_000` still makes the database walk and discard a million rows, so
deep pages get linearly slower. Offset paging is also unstable — insert a row while a user
pages and results shift, duplicating or skipping items. Choosing the wrong strategy is a
performance and correctness decision, not a cosmetic one.

## Core Principles

- **Always bound result size.** Every list query needs a `take` with a sane default and a
  hard maximum; unbounded reads do not belong in production.
- **Always order deterministically.** Pagination without a total `orderBy` returns rows in
  undefined order, so pages overlap or drop items. Add a unique tie-breaker (usually `id`).
- **Prefer cursor pagination for large or infinite lists.** It seeks directly to the last
  seen row via an indexed column, so page 10,000 costs the same as page 1.
- **Use offset pagination only for small, bounded sets** with numbered pages (e.g. an admin
  table of a few thousand rows) where deep pages will never be requested.
- **Never compute totals on hot paths blindly.** `count()` on a huge filtered table is its
  own slow query; make total counts optional or approximate.

## Best Practices

- Set `take` from a validated page-size parameter, clamped to a maximum (e.g. `Math.min(n,
  100)`), so a caller cannot request a million rows.
- For cursor paging, `orderBy` an indexed unique (or unique-enough) column, pass the last
  row's value as `cursor`, and `skip: 1` to exclude the cursor row itself.
- Fetch `take + 1` rows to detect whether a next page exists without a separate `count`.
- Return the next cursor (the last item's id/sort value) in the response so the client does
  not reconstruct it.
- When sorting by a non-unique column (e.g. `createdAt`), add `id` as a secondary `orderBy`
  so the cursor is stable across ties.
- Keep the same `where` filter across every page request; changing it mid-scroll invalidates
  the cursor.

## Examples

**Good Example** — cursor pagination, stable order, next-page detection

```ts
const pageSize = Math.min(limit ?? 20, 100); // clamp: caller can't demand the whole table

const rows = await prisma.post.findMany({
  where: { published: true },
  // Deterministic order: createdAt can tie, so id breaks ties → cursor is stable.
  orderBy: [{ createdAt: "desc" }, { id: "desc" }],
  take: pageSize + 1,                         // one extra row = "is there a next page?"
  ...(cursor && { cursor: { id: cursor }, skip: 1 }), // seek past the last seen row
});

const hasNext = rows.length > pageSize;
const page = hasNext ? rows.slice(0, pageSize) : rows;
const nextCursor = hasNext ? page[page.length - 1].id : null; // hand it back to the client
```

**Bad Example** — deep offset paging with no bound or tie-breaker

```ts
// skip: 200000 makes the DB walk and throw away 200k rows before returning 50.
// No stable orderBy → inserts between requests shift rows, duplicating/skipping items.
const rows = await prisma.post.findMany({
  skip: page * 50,        // gets linearly slower the deeper the user pages
  take: 50,
  orderBy: { createdAt: "desc" }, // createdAt ties are ordered arbitrarily
});
```

## Common Mistakes

- Returning `findMany()` with no `take`, dumping an entire growing table.
- Deep offset paging (`skip` in the thousands), which scans and discards all skipped rows.
- Paginating without a total `orderBy`, so pages overlap or drop rows.
- Sorting by a non-unique column with no `id` tie-breaker, making cursors unstable.
- Running `count()` on every request over a large filtered set, doubling query cost.
- Trusting a client-supplied page size without clamping it to a maximum.

## Production Tips

- Back the `orderBy` column with an index (composite when you sort by more than one column);
  cursor paging is only fast if the seek is indexed. See [indexes](16-indexes.md).
- Prefer opaque, encoded cursors (base64 of the sort tuple) over raw ids in public APIs so
  clients cannot depend on internal shapes.
- If callers need a total count, cache it, approximate it (`reltuples` on Postgres), or make
  it a separate opt-in field rather than paying for it on every page.
- For keyset paging on composite sorts, express the cursor as a compound `where` (row-value
  comparison) when `cursor` alone cannot capture the ordering.

## AI Review Checklist

- Does every list query have a `take` bound with a clamped maximum page size?
- Is there a deterministic `orderBy` with a unique tie-breaker column?
- Is cursor pagination used for large/infinite lists instead of deep offsets?
- Is next-page existence detected via `take + 1` rather than an extra `count` when possible?
- Is the sort column indexed to support the seek?
- Are total counts made optional or approximate on hot paths?

## Related

- `knowledge/prisma/09-filtering.md`
- `knowledge/prisma/07-crud.md`
- `knowledge/prisma/16-indexes.md`
- `knowledge/prisma/15-performance.md`
- `knowledge/prisma/11-relations-loading.md`
