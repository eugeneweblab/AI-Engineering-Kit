---
id: graphql/14-filtering
topic: graphql
slug: filtering
title: "Filtering"
type: doc
order: 14
status: ready
tags: [graphql, filtering]
related: [graphql/13-pagination, graphql/10-input-types, graphql/17-security, graphql/22-performance, graphql/04-queries]
when_to_use: "Read before adding filter, search, or sort arguments to a list field, or when reviewing how filter inputs reach the database."
---
# Filtering

## Purpose

This document defines how to expose filtering, sorting, and search over list fields in
GraphQL: how to model filter arguments as input types, how to translate them into safe
database predicates, and how to keep the surface bounded so clients cannot construct
arbitrarily expensive or unsafe queries. It is written so an agent can design a filter
API that is expressive for clients and safe for the server.

Filtering is where untrusted client input meets your data store. Every filter argument
is an attack surface and a performance surface at once, so the design must constrain
*what* can be filtered, not just *how*.

## Why It Matters

A naive filter API hands clients a query language into your database. If a filter field
maps to a raw string interpolated into SQL, you have reinvented SQL injection through
GraphQL. If clients can filter or sort on any column, they will filter on unindexed
ones and turn every list query into a full table scan. If nested `AND`/`OR` trees are
unbounded, a single request can build a predicate expensive enough to be a
denial-of-service.

Filtering also compounds with pagination: a filter changes the result set that a cursor
pages through, so the two must be validated together. Getting filtering right means the
schema itself is the allowlist — clients can only express filters you have deliberately
enabled and indexed.

## Core Principles

- **The schema is the allowlist.** Expose a typed filter input with named fields, not a
  free-form string or JSON blob. If a field is not in the input type, it cannot be
  filtered — by construction.
- **Never build predicates by string interpolation.** Map filter fields to
  parameterized queries or a query builder; the client value is always a bound
  parameter, never concatenated SQL.
- **Only filter and sort on indexed columns.** Every filterable/sortable field should
  have index support, or its cost is unbounded. Restrict the sortable set explicitly.
- **Bound combinatorial complexity.** Cap the depth and breadth of nested `AND`/`OR`
  filters so a request cannot assemble a pathological predicate.
- **Filter, sort, and paginate as one contract.** A cursor is only valid for a fixed
  filter+sort; changing either invalidates cursors already issued.

## Best Practices

- Model filters as an input type with typed, optional fields
  (`PostFilter { authorId: ID, status: PostStatus, createdAfter: DateTime }`); combine
  them with AND semantics by default and make OR explicit and depth-limited.
- Use enums for sort keys (`enum PostSortField { CREATED_AT, TITLE }`) plus a
  `SortDirection` enum — never accept a raw column name string.
- Validate and normalize filter inputs before they reach the data layer: reject unknown
  combinations, clamp ranges, and reject sorts on non-allowlisted fields.
- Translate filters through a query builder (Prisma, Drizzle, Knex, SQLAlchemy) or
  parameterized SQL so values are always bound.
- Push filtering to the database, not application memory — never load then `Array.filter`,
  which defeats indexes and pagination.
- Document which filters are indexed; treat adding a new filterable field as a change
  that requires an index migration.

## Examples

**Good Example** — typed filter input, enum sort, parameterized query builder

```graphql
input PostFilter {
  status: PostStatus          # only enumerated, indexed fields are filterable
  authorId: ID
  createdAfter: DateTime
}
enum PostSortField { CREATED_AT, TITLE }
input PostSort { field: PostSortField!, direction: SortDirection! }

type Query { posts(filter: PostFilter, sort: PostSort, first: Int!): PostConnection! }
```

```ts
async function posts(_: unknown, { filter, sort, first }: Args) {
  const where: Prisma.PostWhereInput = {};
  // Each branch maps a known field to a bound predicate — no string building.
  if (filter?.status) where.status = filter.status;
  if (filter?.authorId) where.authorId = filter.authorId;
  if (filter?.createdAfter) where.createdAt = { gt: filter.createdAt };

  // Sort field is an enum, resolved through a fixed map → only indexed columns.
  const orderBy = SORT_MAP[sort?.field ?? "CREATED_AT"](sort?.direction ?? "DESC");

  return db.post.findMany({ where, orderBy, take: Math.min(first, 100) + 1 });
}
```

**Bad Example** — free-form filter interpolated into SQL, arbitrary sort column

```ts
async function posts(_: unknown, { where, orderBy }: { where: string; orderBy: string }) {
  // `where` is a raw client string → SQL injection.
  // `orderBy` is an arbitrary column → unindexed full scans, and injection.
  return db.query(
    `SELECT * FROM posts WHERE ${where} ORDER BY ${orderBy}`, // never do this
  );
}
```

## Common Mistakes

- Accepting a raw filter string or arbitrary JSON and interpolating it into a query.
- Letting clients sort by any column name, enabling unindexed scans and injection.
- Filtering in application memory after loading the full table, defeating indexes.
- Allowing unbounded nested `OR`/`AND` trees, enabling predicate-based DoS.
- Adding a filterable field without an accompanying index, so it works in dev and times
  out in production.
- Treating filter and pagination independently, issuing cursors that break when the
  filter changes.

## Production Tips

- Log slow filter combinations with the resolved SQL and add missing indexes; use
  `EXPLAIN` in CI on representative filters to catch sequential scans early.
- Set a statement timeout at the database so a pathological filter fails fast instead of
  holding a connection.
- Rate-limit or cost-weight expensive filters (full-text search, cross-table filters)
  more heavily than cheap key lookups.

## AI Review Checklist

- Are filters a typed input type rather than a free-form string or JSON blob?
- Are all filter values bound parameters, never interpolated into query text?
- Are sortable fields restricted to an enum backed by indexed columns?
- Is nested boolean filter depth/breadth bounded?
- Is filtering pushed to the database rather than done in memory after loading?
- Does every new filterable field have a supporting index?

## Related

- `knowledge/graphql/13-pagination.md`
- `knowledge/graphql/10-input-types.md`
- `knowledge/graphql/17-security.md`
- `knowledge/graphql/22-performance.md`
- `knowledge/graphql/04-queries.md`
