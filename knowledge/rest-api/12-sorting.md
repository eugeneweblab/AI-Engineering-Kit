---
id: rest-api/12-sorting
topic: rest-api
slug: sorting
title: "REST API Sorting"
type: doc
order: 12
status: ready
tags: [rest-api, sorting, BadRequest, startsWith, created_at]
related: [rest-api/10-pagination, rest-api/11-filtering, rest-api/13-search, rest-api/08-validation, rest-api/25-performance]
when_to_use: "Read before adding a `sort` parameter to any list or collection endpoint."
---
# REST API Sorting

## Purpose

This document defines how a REST collection endpoint should expose ordering: the shape
of the `sort` parameter, how to allowlist sortable fields, how to keep ordering stable,
and how sorting must cooperate with pagination. It is written so an agent can add sorting
to a list endpoint without opening a performance hole or a full-table scan.

Sorting decides the *order* of a result set. It is separate from
[filtering](11-filtering.md) (which rows) and [pagination](10-pagination.md) (how many
per page), but all three share one query and must be designed together.

## Why It Matters

Sorting looks trivial and is not. An unbounded `sort` parameter lets a client order by
any column, including unindexed ones, turning a cheap query into a table scan that pins a
database CPU. Worse, sorting on a non-unique column (like `created_at` with duplicate
timestamps) produces a *non-deterministic* order, which silently breaks keyset pagination:
rows are skipped or shown twice as the client pages through. Because the endpoint still
returns 200 OK with plausible data, these bugs reach production unnoticed and corrupt the
client's view of the collection.

## Core Principles

- **Allowlist, never reflect.** Map client sort tokens to a fixed set of known columns.
  Never interpolate a client string into `ORDER BY` — that is SQL injection and a scan risk.
- **Always break ties with a unique key.** Append a unique, immutable column (usually the
  primary key) as the last sort term so the order is fully deterministic.
- **One documented syntax.** Pick a single `sort` grammar and use it on every endpoint.
  Consistency lets a client reuse code across resources.
- **Sortable ⊆ indexed.** Only expose fields that are backed by an index in the primary
  sort direction. If it is not indexed, it is not sortable.
- **Sorting and pagination are one decision.** The sort order must match the pagination
  cursor's order, or paging returns wrong results.

## Best Practices

- Use one query parameter, `sort`, with a comma-separated list and a `-` prefix for
  descending: `?sort=-createdAt,name`. This is compact, URL-safe, and self-describing.
- Maintain an explicit map from public field names to internal columns:
  `{ createdAt: "created_at" }`. Reject any token not in the map with `400`, listing the
  allowed fields in the error body.
- Define a **default sort** for every collection (e.g. `-createdAt, id`) so results are
  stable when the client omits `sort`. Never rely on the database's natural order.
- Cap the number of sort terms (2–3 is plenty) to bound query cost and index requirements.
- When offering keyset/cursor pagination, derive the cursor from the *exact* sort columns,
  tie-breaker included, so the boundary comparison is unambiguous.
- Document, per field, the collation for text sorts (case sensitivity, locale). Sorting
  "Zebra" before "apple" surprises clients unless you state the rule.

## Examples

**Good Example** — allowlisted fields, deterministic tie-breaker

```ts
// Public token -> real column. Only these are sortable, and each is indexed.
const SORTABLE = { createdAt: "created_at", name: "name", price: "price" } as const;

function parseSort(raw = "-createdAt"): string[] {
  const terms = raw.split(",").slice(0, 3).map((t) => {
    const desc = t.startsWith("-");
    const key = desc ? t.slice(1) : t;
    const col = SORTABLE[key as keyof typeof SORTABLE];
    if (!col) throw new BadRequest(`Unsortable field: ${key}`); // reject, don't reflect
    return `${col} ${desc ? "DESC" : "ASC"}`;
  });
  terms.push("id ASC"); // unique tie-breaker => fully deterministic order
  return terms;
}
// ORDER BY created_at DESC, id ASC  -> safe input, stable for keyset paging
```

**Bad Example** — reflects client input, non-deterministic order

```ts
function buildOrderBy(sort: string) {
  // Interpolates raw client text: SQL injection AND arbitrary-column scans.
  return `ORDER BY ${sort}`;
}
// GET /orders?sort=created_at DESC
// created_at has duplicate timestamps and no tie-breaker, so keyset pagination
// skips and repeats rows. No error is raised; the client just sees corrupt pages.
```

## Common Mistakes

- Concatenating the `sort` string straight into `ORDER BY` (injection + full scans).
- Omitting a unique tie-breaker, so equal values order non-deterministically and paging
  drops or duplicates rows.
- Allowing sorts on unindexed columns, letting a client trigger table scans at will.
- No default sort, so an omitted `sort` yields whatever order the storage engine returns
  today — which changes after a migration or index rebuild.
- A sort order that disagrees with the cursor order in keyset pagination.
- Case-sensitive text sorts that the client did not expect, with no documented collation.

## Production Tips

- Add a slow-query alert and log the `sort` value with it, so an expensive ordering is
  traceable to the field a client requested.
- Prefer composite indexes that cover `filter columns + sort columns` together; a sort
  that cannot use the filter's index still scans.
- If a highly requested sort field is not indexable cheaply (e.g. a computed value),
  precompute and store it rather than sorting on the fly.

## AI Review Checklist

- Are sortable fields allowlisted and mapped to real columns, never reflected from input?
- Does every sort end with a unique, immutable tie-breaker (usually the primary key)?
- Is there an explicit default sort for the collection?
- Is every sortable field backed by an index in the sort direction?
- Does the sort order exactly match the [pagination](10-pagination.md) cursor order?
- Are unknown or excess sort fields rejected with `400` and a helpful message?

## Related

- `knowledge/rest-api/10-pagination.md`
- `knowledge/rest-api/11-filtering.md`
- `knowledge/rest-api/13-search.md`
- `knowledge/rest-api/08-validation.md`
- `knowledge/rest-api/25-performance.md`
