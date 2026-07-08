---
id: rest-api/11-filtering
topic: rest-api
slug: filtering
title: "Filtering"
type: doc
order: 11
status: ready
tags: [rest-api, filtering]
related: [rest-api/10-pagination, rest-api/12-sorting, rest-api/13-search, rest-api/08-validation, rest-api/24-security]
when_to_use: "Read before adding query-parameter filters to a collection endpoint."
---
# Filtering

## Purpose

This document defines how clients narrow a collection with query parameters — filtering by
field values, ranges, and sets. It is written so an agent can design a filter interface
that is predictable, injection-safe, and backed by indexes rather than full scans.

Filtering turns a generic list endpoint into a precise query surface. Done well it is
ergonomic and fast; done carelessly it is an injection vector and a performance sink.

## Why It Matters

Filters are where untrusted input meets your database. A filter that interpolates query
parameters into SQL is a textbook injection hole; a filter over an unindexed column turns
every request into a table scan. And an unconstrained filter grammar — arbitrary operators
on arbitrary fields — is impossible to secure, index, or document. The discipline here is
the same as validation: allowlist exactly what can be filtered, on which fields, with
which operators, and reject the rest.

## Core Principles

- **Allowlist filterable fields and operators.** Expose a known, documented set. Never let
  the client filter on arbitrary columns — it leaks the schema and defeats indexing.
- **Never build queries by string concatenation.** Every filter value goes through
  parameterized queries or a query builder; treat all input as hostile — see
  [security](24-security.md).
- **Filtering is not searching.** Filtering is exact/structured matching on fields;
  free-text relevance search is a different concern — see [search](13-search.md).
- **Each filter maps to an index.** A filter the database cannot serve from an index is a
  latent performance bug. Design filters and indexes together.
- **Filters combine predictably.** Multiple filters are ANDed by default; document any OR
  or negation semantics explicitly rather than inventing an ad-hoc mini-language.

## Best Practices

- Use flat, documented query parameters: `?status=active&created_after=2026-01-01`. Keep
  simple cases simple.
- Encode operators explicitly and from an allowlist when you need more than equality:
  `?price[gte]=10&price[lte]=50` or `?created_at=gte:2026-01-01`. Do not accept raw
  operator strings the client invents.
- Validate every filter value by type and range before it touches the query — see
  [validation](08-validation.md). Reject unknown filter keys with `400`.
- Support multi-value (set) filters with a bounded list: `?status=active,pending` → `IN
  (...)`, capped to a maximum number of values.
- Keep filtering, [sorting](12-sorting.md), and [pagination](10-pagination.md) orthogonal
  and composable; a cursor must remain valid only while filters are unchanged.
- Prefer flat params over deeply nested filter DSLs in the URL; if you truly need a rich
  query language, define it in a spec (or accept it in a `POST /search` body), not ad hoc.
- Return `400` (not empty results) for an invalid filter, so a client typo is not mistaken
  for "no matches."

## Examples

**Good Example** — allowlisted fields, parameterized, indexed

```ts
// Only these fields/operators are filterable; everything else is rejected.
const FILTERS = {
  status:        { op: "eq",   column: "status" },
  created_after: { op: "gte",  column: "created_at" },
  price_max:     { op: "lte",  column: "price_minor" },
} as const;

function buildQuery(query) {
  const clauses = [], params = [];
  for (const [key, value] of Object.entries(query)) {
    const f = FILTERS[key];
    if (!f) throw new BadRequest(`unknown filter: ${key}`);  // reject, don't ignore
    clauses.push(`${f.column} ${SQL_OP[f.op]} ?`);           // column from allowlist
    params.push(coerce(key, value));                          // typed + validated value
  }
  // parameterized: values never concatenated into SQL
  return { where: clauses.join(" AND "), params };
}
// backed by indexes on (status), (created_at), (price_minor)
```

**Bad Example** — arbitrary fields, concatenated, unindexed

```ts
function buildQuery(query) {
  const where = Object.entries(query)
    // any field the client names, any value — schema leak + full scans
    .map(([k, v]) => `${k} = '${v}'`)   // string interpolation → SQL injection
    .join(" AND ");
  return `SELECT * FROM orders WHERE ${where}`;
  // ?status=x' OR '1'='1  → returns every row; ?internal_flag=... → probes schema
}
```

## Common Mistakes

- Interpolating filter values into SQL/NoSQL queries — direct injection risk.
- Letting clients filter on any column, leaking the schema and forcing table scans.
- Filtering on unindexed columns, so common queries scan the whole table.
- Silently ignoring an unknown filter key and returning unfiltered or empty results.
- Inventing an unbounded operator/expression language that cannot be indexed or documented.
- No cap on multi-value `IN` lists, letting a client pass thousands of values.
- Confusing filtering with search — bolting fuzzy matching onto exact filters.

## Production Tips

- Log which filter combinations are actually used; add indexes for the hot ones and retire
  filters nobody uses.
- Add a slow-query alert; an unindexed filter usually shows up there first.
- Cap total filter complexity (number of filters, `IN` list length) at the edge to bound
  worst-case query cost.
- Document the exact filterable fields and operators in OpenAPI so clients do not guess.

## AI Review Checklist

- Are filterable fields and operators restricted to a documented allowlist?
- Are all filter values parameterized, never concatenated into a query?
- Is each filter value validated by type/range, with `400` on unknown keys?
- Is every filterable field backed by an index?
- Are multi-value filters bounded in length?
- Do filters, sorting, and pagination compose without breaking cursors?
- Is structured filtering kept distinct from free-text search?

## Related

- `knowledge/rest-api/10-pagination.md`
- `knowledge/rest-api/12-sorting.md`
- `knowledge/rest-api/13-search.md`
- `knowledge/rest-api/08-validation.md`
- `knowledge/rest-api/24-security.md`
