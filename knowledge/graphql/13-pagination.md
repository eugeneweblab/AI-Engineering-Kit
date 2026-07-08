---
id: graphql/13-pagination
topic: graphql
slug: pagination
title: "Pagination"
type: doc
order: 13
status: ready
tags: [graphql, pagination]
related: [graphql/14-filtering, graphql/04-queries, graphql/15-n1-problem, graphql/22-performance, graphql/02-schema]
when_to_use: "Read before exposing any list field that can grow unbounded, or when choosing between offset and cursor pagination."
---
# Pagination

## Purpose

This document defines how to paginate list fields in a GraphQL schema: when to use
cursor-based (Relay Connections) versus offset-based pagination, how to shape the
types, and how to implement stable, efficient paging on the resolver side. It is
written so an agent can design a list field that stays correct and performant as the
underlying dataset grows to millions of rows.

Any field that returns a list which can grow without bound must be paginated. An
unpaginated `posts: [Post!]!` is a latent outage — it works in development with ten
rows and times out in production with ten million.

## Why It Matters

Lists are where GraphQL performance goes to die. An unbounded list lets a single query
load an entire table into memory, serialize it, and ship it over the wire — one client
can exhaust the database connection pool for everyone. Pagination bounds the cost of
every request to a predictable page size.

The *choice* of pagination style also determines correctness under concurrent writes.
Offset pagination (`LIMIT 20 OFFSET 40`) skips or repeats rows when items are inserted
or deleted between page loads, and its cost grows linearly with the offset — page 5000
scans 100,000 rows to return 20. Cursor pagination pages relative to a stable key, so
it neither drifts nor degrades. Picking the wrong model bakes these failures into your
public API, where they are expensive to change.

## Core Principles

- **Every unbounded list is paginated.** Treat `[T!]!` on a growing collection as a
  bug. The only lists exempt are ones with a small, fixed maximum (e.g. a user's roles).
- **Prefer cursor (keyset) pagination for feeds and large tables.** It is stable under
  concurrent writes and its cost is independent of how deep you page.
- **A cursor is an opaque token, not an index.** Encode the sort key(s) of the boundary
  row; never expose it as a decodable offset clients can arithmetic on.
- **Pagination and ordering are inseparable.** A cursor is only meaningful against a
  deterministic sort. Always sort by a unique, stable key (or tuple ending in one).
- **Enforce a maximum page size on the server.** Clamp `first`/`last` to a hard ceiling;
  never let the client dictate an unbounded page.

## Best Practices

- Adopt the **Relay Connection** spec for cursor pagination: `edges { node, cursor }`,
  `pageInfo { hasNextPage, hasPreviousPage, startCursor, endCursor }`, and `first/after`,
  `last/before` arguments. It is the interoperable standard clients already understand.
- Require a directional argument pair (`first`+`after` or `last`+`before`) and reject
  requests that mix directions or omit a limit.
- Build cursors from the tuple you sort by, e.g. `(createdAt, id)`, and query with a
  keyset predicate: `WHERE (created_at, id) < (:ts, :id) ORDER BY created_at DESC, id DESC LIMIT :n+1`.
- Fetch `first + 1` rows to compute `hasNextPage` without a second `COUNT` query.
- Expose `totalCount` only when it is cheap or genuinely needed — an exact count on a
  huge, filtered table is often more expensive than the page itself.
- Keep offset pagination for small, bounded admin tables where jump-to-page matters and
  the dataset cannot realistically drift or grow.

## Examples

**Good Example** — Relay connection with keyset cursor and a clamped page size

```graphql
type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
}
type PostEdge { node: Post!, cursor: String! }
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
type Query { posts(first: Int!, after: String): PostConnection! }
```

```ts
async function posts(_: unknown, { first, after }: Args) {
  const limit = Math.min(first, 100);                 // hard server-side ceiling
  const { ts, id } = after ? decodeCursor(after) : END; // opaque cursor → sort tuple
  // Keyset predicate: cost is O(page size), independent of how deep we page.
  const rows = await db.query(
    `SELECT * FROM posts
       WHERE (created_at, id) < ($1, $2)
       ORDER BY created_at DESC, id DESC
       LIMIT $3`,
    [ts, id, limit + 1],                              // +1 row tells us hasNextPage
  );
  const hasNextPage = rows.length > limit;
  const page = rows.slice(0, limit);
  return toConnection(page, hasNextPage);
}
```

**Bad Example** — offset pagination, no ceiling, drifts and degrades

```ts
async function posts(_: unknown, { limit, offset }: Args) {
  // No clamp: client can ask for limit = 1_000_000.
  // OFFSET scans and discards `offset` rows → page 5000 reads 100k rows.
  // Concurrent inserts shift every row, so pages skip and repeat items.
  return db.query(
    `SELECT * FROM posts ORDER BY created_at DESC LIMIT $1 OFFSET $2`,
    [limit, offset],
  );
}
```

## Common Mistakes

- Returning an unbounded `[T!]!` for a collection that grows in production.
- Letting the client set page size with no server-side maximum.
- Using offset pagination for feeds, causing skipped/duplicated rows under writes.
- Sorting by a non-unique column (e.g. `createdAt` alone), so cursors are ambiguous and
  ties are unstable — always break ties with a unique key.
- Making the cursor a decodable offset, letting clients jump or scrape arbitrarily.
- Running a `COUNT(*)` on every page for a `totalCount` nobody displays.

## Production Tips

- Ensure the sort tuple is backed by a composite index; keyset pagination is only fast
  when `(created_at, id)` is indexed in the same order it is queried.
- Version cursor encoding (include a scheme byte) so you can change the sort tuple later
  without breaking cursors already held by clients.
- Alert on p99 latency of list resolvers segmented by page depth to catch offset misuse.

## AI Review Checklist

- Is every unbounded list field paginated rather than returning a raw array?
- Is the page size clamped to a hard server-side maximum?
- Does cursor pagination sort by a unique, stable tuple with a matching index?
- Are cursors opaque tokens, not client-decodable offsets?
- Is `hasNextPage` derived from a `+1` fetch rather than a separate count?
- Is offset pagination confined to small, bounded datasets?

## Related

- `knowledge/graphql/14-filtering.md`
- `knowledge/graphql/04-queries.md`
- `knowledge/graphql/15-n1-problem.md`
- `knowledge/graphql/22-performance.md`
- `knowledge/graphql/02-schema.md`
