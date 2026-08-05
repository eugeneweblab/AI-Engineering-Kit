---
id: prisma/11-relations-loading
topic: prisma
slug: relations-loading
title: "Relations Loading"
type: doc
order: 11
status: ready
tags: [prisma, relations-loading, take, findMany, orderBy]
related: [prisma/04-relations, prisma/07-crud, prisma/09-filtering, prisma/10-pagination, prisma/15-performance]
when_to_use: "Read before loading related records with include or select, or when a query fans out into many round-trips."
---
# Relations Loading

## Purpose

This document defines how to load related records with the Prisma Client so you fetch
exactly the connected data you need, in as few queries as possible, without the N+1 blow-up.
It covers `include` vs nested `select`, filtering and paginating nested relations, counting
relations with `_count`, and recognizing when a loop of lazy loads has replaced one query
with hundreds.

This builds on how relations are modeled ([Relations](04-relations.md)) and interacts
directly with [filtering](09-filtering.md) and [pagination](10-pagination.md) applied to
nested data.

## Why It Matters

Relation loading is the single most common source of accidental performance collapse in a
Prisma app. Iterating over parents and querying each one's children — the N+1 pattern —
turns one page render into one query plus N per-row queries; it is invisible on seed data
and catastrophic on real data. The opposite mistake, `include`-ing deep relation trees you
do not render, over-fetches wide rows and floods memory. Both look correct and pass tests.
The difference between a 5 ms endpoint and a 5 s one is usually a single `include`.

## Core Principles

- **Load relations in the parent query, not in a loop.** Use `include`/`select` so Prisma
  fetches parents and children together; never query children per parent in application
  code.
- **Fetch the shape you render, nothing more.** Use nested `select` to pick relation fields;
  `include` pulls every scalar of the relation, which is often too much.
- **Bound nested collections.** A one-to-many `include` with no `take` loads every child;
  paginate and order nested lists just like top-level ones.
- **Count without loading.** When you only need "how many", use `_count`, not the full
  relation array.
- **Depth costs queries.** Each level of nesting is more data and, past a point, more
  queries; keep the loaded graph shallow and deliberate.

## Best Practices

- Replace per-row lazy loading with a single `findMany` + `include`/`select`; Prisma batches
  the relation into a second query, not N.
- Prefer nested `select` over `include` when you need a subset of relation fields, so wide
  rows and secrets stay in the database.
- Apply `where`, `orderBy`, and `take` inside the relation to filter, sort, and cap nested
  collections (e.g. the latest 5 comments per post).
- Use `include: { _count: { select: { comments: true } } }` for counts instead of loading
  and measuring the array in JavaScript.
- For large fan-outs, consider two explicit queries (parents, then children `in` the parent
  ids) and stitch in memory — sometimes clearer and faster than deep nesting.
- Combine relation loading with [pagination](10-pagination.md) at the top level so you never
  include relations for an unbounded parent set.

## Examples

**Good Example** — one query, selected fields, bounded nested list

```ts
// Parents and their children fetched together; no per-post query in a loop.
const posts = await prisma.post.findMany({
  where: { published: true },
  take: 20,
  select: {
    id: true,
    title: true,
    _count: { select: { comments: true } }, // count without loading the array
    comments: {
      select: { id: true, body: true },      // only the fields we render
      orderBy: { createdAt: "desc" },
      take: 5,                                // cap nested list — not every comment ever
    },
  },
});
```

**Bad Example** — N+1 lazy loading in a loop

```ts
const posts = await prisma.post.findMany({ where: { published: true }, take: 20 });

// One extra query PER post: 20 posts → 21 queries. At 200 posts it is 201.
for (const post of posts) {
  post.comments = await prisma.comment.findMany({ where: { postId: post.id } });
  // No take either → each post loads its entire comment history into memory.
}
```

## Common Mistakes

- Querying a relation inside a `for`/`map` over parents — the textbook N+1 pattern.
- Using `include` for a whole subtree when only a few nested fields are rendered.
- `include`-ing a one-to-many relation with no `take`, loading every child row.
- Loading full relation arrays just to call `.length`, instead of `_count`.
- Deeply nesting includes (relations of relations of relations) beyond what the view needs.
- Including relations on an unpaginated parent list, multiplying an already unbounded read.

## Production Tips

- Detect N+1 in tests and staging by logging query counts per request (Prisma `query` events
  or a middleware counter); assert a ceiling for hot endpoints.
- For very large parent sets, the two-query "load parents, then children by id `in`" pattern
  often beats a single deep `include` and is easier to cache.
- Watch relation `take` interacting with parent `take`: `20 parents × 5 children` is 100
  rows; a forgotten nested `take` makes it unbounded.
- Prisma relation loads run as separate SQL statements, not SQL joins; do not assume a single
  round-trip, and index the relation's foreign key so the child query is fast.

## AI Review Checklist

- Are relations loaded via `include`/`select` in the parent query, never in a per-row loop?
- Is nested `select` used to fetch only rendered relation fields instead of blanket
  `include`?
- Do one-to-many relation loads carry `take`/`orderBy` to bound and order children?
- Are relation counts done with `_count` rather than loading the full array?
- Is relation loading combined with top-level pagination so the parent set is bounded?
- Are foreign keys indexed so the relation query does not scan?

## Related

- `knowledge/prisma/04-relations.md`
- `knowledge/prisma/07-crud.md`
- `knowledge/prisma/09-filtering.md`
- `knowledge/prisma/10-pagination.md`
- `knowledge/prisma/15-performance.md`
