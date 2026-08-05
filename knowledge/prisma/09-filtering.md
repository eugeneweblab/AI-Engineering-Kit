---
id: prisma/09-filtering
topic: prisma
slug: filtering
title: "Prisma Filtering"
type: doc
order: 9
status: ready
tags: [prisma, filtering]
related: [prisma/07-crud, prisma/10-pagination, prisma/11-relations-loading, prisma/16-indexes, prisma/15-performance]
when_to_use: "Read before building any query with a where clause, search, or dynamic filter."
---
# Prisma Filtering

## Purpose

This document defines how to build `where` clauses with the Prisma Client so queries are
correct, safe, and index-friendly. It covers operators (`equals`, `in`, `contains`, `gt`,
etc.), combining conditions with `AND`/`OR`/`NOT`, filtering across relations (`some`,
`every`, `none`), null handling, and the patterns that turn a filter into a full table scan.

Filtering is the input to almost every read. It composes with [pagination](10-pagination.md)
and [relation loading](11-relations-loading.md), and its performance depends directly on the
[indexes](16-indexes.md) behind it.

## Why It Matters

A `where` clause is where wrong data and slow queries originate. A subtly wrong condition
returns rows the caller should never see — a tenant's data leaking to another tenant is a
filtering bug, not an auth bug. A filter that cannot use an index scans the whole table:
fine on 100 rows in dev, a timeout on 10 million in production. And because Prisma builds
parameterized SQL, filters are safe from injection *only* while you use the query API — the
moment someone concatenates user input into raw SQL, that guarantee is gone.

## Core Principles

- **Filter in the database, not in application code.** Push every condition into `where`;
  never fetch a broad set and filter it in JavaScript — that transfers and discards rows.
- **Build for the index.** Structure `where` so its most selective, indexed columns drive
  the query. `contains` with a leading wildcard and case-insensitive text usually cannot use
  a standard index.
- **`null` is not a value — it is a state.** `equals: null` means "is null"; leaving a field
  out means "no condition". Know which you intend.
- **Combine conditions explicitly.** Multiple keys in one object are `AND`ed; use the `OR`
  and `NOT` arrays when you need anything else.
- **Trust the query builder, distrust raw interpolation.** The Prisma API parameterizes
  inputs; raw string-built SQL does not.

## Best Practices

- Use `in`/`notIn` for set membership instead of a chain of `OR` equals — it is clearer and
  compiles to a single SQL `IN`.
- For relation filters, pick the right quantifier: `some` (at least one matches), `every`
  (all match), `none` (none match). They mean different things; do not guess.
- Make text search index-aware. For case-insensitive search on Postgres, use `mode:
  "insensitive"` and back it with a functional or trigram index; a leading-wildcard
  `contains` will scan.
- Always scope multi-tenant queries by tenant id in `where` at the data layer — do not rely
  on callers to remember. Consider a client extension to enforce it.
- Build dynamic filters by composing a typed `Prisma.<Model>WhereInput` object, not by
  string concatenation, so unset filters simply become absent conditions.
- Use `AND: []` to combine independently-derived conditions cleanly rather than merging keys
  and risking accidental overwrites.

## Examples

**Good Example** — indexed, explicit, safe composition

```ts
// Typed where object: unset optional filters are simply omitted, never stringified.
const where: Prisma.OrderWhereInput = {
  tenantId,                              // ALWAYS scope tenant data at the DB layer
  status: { in: ["PAID", "SHIPPED"] },   // set membership → single SQL IN
  createdAt: { gte: since },             // range on an indexed column drives the scan
  ...(search && {
    customer: { is: { name: { contains: search, mode: "insensitive" } } },
  }),
};

const orders = await prisma.order.findMany({ where });
```

**Bad Example** — filtering in JS and leaking cross-tenant rows

```ts
// Pulls EVERY order across ALL tenants into memory, then discards most of them.
const all = await prisma.order.findMany();
const orders = all.filter(
  (o) => o.tenantId === tenantId && ["PAID", "SHIPPED"].includes(o.status),
);
// The DB did no filtering: full table scan + full transfer, and one forgotten
// tenant check away from leaking another customer's data.
```

## Common Mistakes

- Fetching broadly and filtering in JavaScript, transferring rows only to throw them away.
- Forgetting the tenant/owner condition, leaking data across accounts.
- Confusing `some`/`every`/`none` on relation filters, silently returning the wrong set.
- Assuming a missing field and `equals: null` mean the same thing.
- Relying on `contains`/case-insensitive search without a supporting index, causing scans.
- Merging condition objects by spreading and accidentally overwriting a key instead of
  `AND`-combining them.
- Building `where` from raw string interpolation and reopening SQL injection.

## Production Tips

- Add the composite index that matches your hottest filter + sort combination; run `EXPLAIN`
  on the generated SQL to confirm it is used. See [indexes](16-indexes.md).
- For full-text or fuzzy search at scale, use Postgres `tsvector`/`pg_trgm` via a database
  index rather than `contains`; expose it through `queryRaw` with parameters if needed.
- Watch out for large `in` lists (thousands of ids) — they can blow query size limits; batch
  them or join through a relation instead.

## AI Review Checklist

- Is every condition applied in `where`, with no post-fetch filtering in application code?
- Are multi-tenant/owner-scoped queries filtered by tenant id at the data layer?
- Do relation filters use the correct `some`/`every`/`none` quantifier?
- Are `null` checks intentional (`equals: null` vs field omitted)?
- Can the hot filter use an index, and is text search backed by one?
- Are dynamic filters composed as typed `WhereInput` objects, never raw-interpolated SQL?

## Related

- `knowledge/prisma/07-crud.md`
- `knowledge/prisma/10-pagination.md`
- `knowledge/prisma/11-relations-loading.md`
- `knowledge/prisma/16-indexes.md`
- `knowledge/prisma/15-performance.md`
