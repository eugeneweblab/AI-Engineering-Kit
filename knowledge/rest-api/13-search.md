---
id: rest-api/13-search
topic: rest-api
slug: search
title: "Search"
type: doc
order: 13
status: ready
tags: [rest-api, search, BadRequest, search, to_tsvector, tsvector, websearch_to_tsquery, ts_rank]
related: [rest-api/11-filtering, rest-api/12-sorting, rest-api/10-pagination, rest-api/08-validation, rest-api/25-performance]
when_to_use: "Read before adding free-text or full-text `search` to a collection endpoint."
---
# Search

## Purpose

This document defines how a REST endpoint should expose free-text search: the parameter
shape, the difference between structured filtering and full-text search, how to keep
queries bounded and injection-safe, and how to return relevance-ranked, paginated results.
It is written so an agent can add search without exposing the database to unbounded or
malicious queries.

Search answers "find records matching this text," which is fuzzy and ranked. It is
distinct from [filtering](11-filtering.md), which answers exact structured predicates
(`status=active`). Most endpoints need both, applied to the same query.

## Why It Matters

Search is the most abused parameter on any API. A naive `LIKE '%term%'` cannot use a
B-tree index, so every search is a full scan that grows linearly with the table. Attackers
probe search endpoints for injection, ReDoS via regex input, and resource exhaustion with
pathological queries. And because relevance is subjective, a search that "works" in a demo
often returns useless ordering at scale — the top result is whatever the database happened
to match first. Getting search wrong degrades the whole product experience and creates a
cheap denial-of-service vector.

## Core Principles

- **Search is not filter.** Use a dedicated `q` parameter for free text; keep structured
  predicates in their own filter parameters. Mixing them creates ambiguous, unindexable queries.
- **Parameterize everything.** Pass the search term as a bound parameter, never string
  interpolation. This holds for SQL, full-text engines, and NoSQL query builders alike.
- **Bound the query.** Enforce a minimum length, a maximum length, and a rate limit.
  Reject or trim before the query ever reaches storage.
- **Use a real search index.** Full-text search belongs in a purpose-built index (Postgres
  `tsvector`, OpenSearch/Elasticsearch, Meilisearch), not `LIKE '%...%'` on a raw column.
- **Rank, then paginate.** Return results ordered by relevance with a deterministic
  tie-breaker, and page with the same limits as any other collection.

## Best Practices

- Expose search as `?q=<text>` and combine it with filters using AND semantics:
  `?q=laptop&status=in_stock`. Document that `q` is fuzzy and filters are exact.
- Reject queries shorter than 2–3 characters with `400`; single-character search matches
  nearly everything and scans the table for no value.
- Cap query length (e.g. 256 chars) and strip control characters. Never pass raw user text
  into a regex engine — untrusted regex enables ReDoS.
- Back search with a maintained index: a Postgres GIN index over `to_tsvector`, or an
  external engine synced from the primary store. Choose based on scale and language needs.
- Return a stable, ranked order: relevance score first, then a unique key as tie-breaker,
  so [pagination](10-pagination.md) does not skip or repeat rows.
- Debounce is a client concern, but protect the server with per-client rate limiting on the
  search endpoint regardless.
- Handle "no results" as an empty `200` list, not `404`. An empty search is a valid answer.

## Examples

**Good Example** — bounded input, parameterized full-text query, ranked

```ts
async function search(q: string, limit = 20) {
  const term = q.trim();
  if (term.length < 2) throw new BadRequest("Query must be at least 2 characters");
  if (term.length > 256) throw new BadRequest("Query too long");

  // websearch_to_tsquery safely parses user text; $1 is bound, never interpolated.
  // GIN index on to_tsvector(content) keeps this off the scan path.
  return db.query(
    `SELECT id, title, ts_rank(search_vec, query) AS rank
       FROM articles, websearch_to_tsquery('english', $1) query
      WHERE search_vec @@ query
      ORDER BY rank DESC, id ASC       -- relevance, then unique tie-breaker
      LIMIT $2`,
    [term, Math.min(limit, 100)],
  );
}
```

**Bad Example** — interpolated LIKE, unbounded, no ranking

```ts
async function search(q: string) {
  // '%' + raw input: full table scan, cannot use an index, and injectable
  // if the driver does not escape. No length or rate bound at all.
  return db.query(
    `SELECT * FROM articles WHERE title LIKE '%${q}%'`, // scan + injection risk
  );
  // Order is arbitrary, so pagination is non-deterministic and "top result" is luck.
}
```

## Common Mistakes

- Implementing search as `LIKE '%term%'`, which cannot use an index and scans every row.
- Interpolating the query string into SQL or into a regex, enabling injection or ReDoS.
- No minimum length, so a one-character query scans the whole table.
- Reusing the `filter` mechanism for fuzzy text, producing unindexable, ambiguous queries.
- Returning results in database order rather than by relevance, so the best match is buried.
- Returning `404` for zero results instead of an empty `200` collection.
- Letting the search index drift out of sync with the source of truth without a reconcile job.

## Production Tips

- Track search latency and zero-result rate as product metrics; a rising zero-result rate
  signals synonym or tokenization gaps, not just a quiet catalog.
- For multi-language corpora, index per-language `tsvector` configurations or use an engine
  with language analyzers; a single English analyzer mangles other languages.
- If search fans out to an external engine, apply a strict timeout and fall back to a
  filtered list rather than hanging the request when the engine is slow.

## AI Review Checklist

- Is the search term passed as a bound parameter, never interpolated into SQL or regex?
- Are minimum and maximum query length enforced before hitting storage?
- Is full-text search backed by a real index, not `LIKE '%...%'`?
- Are results ranked by relevance with a unique tie-breaker for stable pagination?
- Is `q` (fuzzy search) kept distinct from exact [filtering](11-filtering.md) parameters?
- Is the search endpoint rate-limited against abuse?

## Related

- `knowledge/rest-api/11-filtering.md`
- `knowledge/rest-api/12-sorting.md`
- `knowledge/rest-api/10-pagination.md`
- `knowledge/rest-api/08-validation.md`
- `knowledge/rest-api/25-performance.md`
