---
id: postgresql/10-full-text-search
topic: postgresql
slug: full-text-search
title: "PostgreSQL Full Text Search"
type: doc
order: 10
status: ready
tags: [postgresql, full-text-search, tsvector, websearch_to_tsquery, to_tsvector, pg_trgm, ts_rank, docs]
related: [postgresql/04-indexes, postgresql/08-jsonb, postgresql/15-extensions, postgresql/05-query-planner]
when_to_use: "Read before building search over text columns, or when LIKE '%term%' queries are slow or matching poorly."
---
# PostgreSQL Full Text Search

## Purpose

This document defines how to implement full-text search (FTS) in PostgreSQL correctly:
`tsvector`/`tsquery`, indexing, ranking, and the boundary where a dedicated search engine
becomes the right call. It is written so an agent can add real search — stemming, ranking,
language awareness — instead of shipping a slow `LIKE '%term%'`.

FTS converts text into a `tsvector` (normalized, stemmed lexemes with positions) and matches
it against a `tsquery` using the `@@` operator. Unlike `LIKE`, it understands word
boundaries, stemming ("running" matches "run"), and stop words, and it is indexable.

## Why It Matters

`LIKE '%term%'` and naive substring matching are the default reach for search, and they are
wrong on two axes at once: correctness and performance. They match substrings inside words,
ignore stemming and stop words, are case- and accent-sensitive by default, and — because a
leading wildcard cannot use a B-tree index — force a sequential scan that scales linearly
with table size. As data grows, search latency grows with it and results stay bad. FTS
fixes both: it matches words the way users expect and it is backed by a GIN index that keeps
search fast at millions of rows. Knowing when to stop at FTS versus move to Elasticsearch is
part of getting this right.

## Core Principles

- **Search a `tsvector`, not raw text.** Convert with `to_tsvector('english', body)` and query
  with `to_tsquery`/`plainto_tsquery`/`websearch_to_tsquery`. The `@@` match operator ties them.
- **Always name the language configuration explicitly.** `to_tsvector('english', ...)` picks
  the stemmer and stop-word list. Relying on the database default makes results depend on a
  server setting and breaks reproducibility.
- **Index the vector, not the column.** A GIN index on the `tsvector` is what makes FTS fast;
  without it, `@@` still scans every row.
- **Store the vector, don't recompute it per query.** Use a generated column (or a trigger) so
  the `tsvector` is computed once on write and indexed, not rebuilt on every search.
- **Match query parser to input source.** Use `websearch_to_tsquery` for user-typed search
  boxes (it tolerates arbitrary input); reserve `to_tsquery` for controlled, operator-bearing input.

## Best Practices

- Add a stored generated column and index it:
  `tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(body,''))) STORED`,
  then `CREATE INDEX ... USING GIN (tsv)`.
- Rank results with `ts_rank` or `ts_rank_cd(tsv, query)` and `ORDER BY rank DESC`; weight
  fields with `setweight` so title matches outrank body matches.
- Use `websearch_to_tsquery('english', :input)` for end-user queries — it never throws on
  punctuation and supports `"quoted phrases"` and `-exclusion`.
- Generate highlighted snippets with `ts_headline`, but do it only for the page of results you
  return, since it re-parses the source text.
- For typo tolerance / autocomplete, combine FTS with the `pg_trgm` extension (trigram
  similarity) or prefix matching (`to_tsquery('term:*')`); FTS alone does not do fuzzy matching.
- Normalize accents with the `unaccent` extension in the vector expression if your users
  search without diacritics.

## Examples

**Good Example** — stored, weighted, GIN-indexed vector with ranking

```sql
CREATE TABLE docs (
  id    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title text NOT NULL,
  body  text NOT NULL,
  -- Computed once on write, in a fixed language config, title weighted above body.
  tsv tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(title,'')), 'A') ||
    setweight(to_tsvector('english', coalesce(body ,'')), 'B')
  ) STORED
);
CREATE INDEX docs_tsv_gin ON docs USING GIN (tsv);  -- makes @@ an index scan

SELECT id, title, ts_rank_cd(tsv, q) AS rank
FROM   docs, websearch_to_tsquery('english', :input) AS q  -- tolerant of raw user input
WHERE  tsv @@ q
ORDER  BY rank DESC
LIMIT  20;
```

**Bad Example** — LIKE substring search

```sql
-- Leading wildcard cannot use an index -> sequential scan over every row.
-- Case-sensitive, no stemming ("running" won't match "run"), matches inside words
-- ("cat" matches "category"), no ranking. Wrong AND slow.
SELECT id, title FROM docs
 WHERE body LIKE '%' || :input || '%'
    OR title LIKE '%' || :input || '%';
```

## Common Mistakes

- Using `LIKE '%x%'` for search: sequential scans plus incorrect word matching.
- Calling `to_tsvector(body)` inside the `WHERE` clause on every query instead of a stored, indexed column.
- Omitting the language config, so stemming/results depend on an implicit server default.
- Building a GIN index but still filtering on the raw column, so the index is never used.
- Feeding raw user input to `to_tsquery` (which throws on stray punctuation) instead of `websearch_to_tsquery`.
- Expecting fuzzy/typo matching from FTS alone — that needs `pg_trgm` or explicit prefix queries.

## Production Tips

- Run `EXPLAIN` to confirm the query hits the GIN index; a sequential scan means the indexed
  expression and the query expression do not match exactly. See [query planner](05-query-planner.md).
- GIN indexes are slower to update than B-trees; for write-heavy tables tune `gin_pending_list_limit`
  or accept the `fastupdate` pending-list trade-off.
- When you need faceting, relevance tuning, cross-field scoring, or multi-language analysis
  beyond what FTS offers, that is the signal to move search to a dedicated engine — but most
  applications never cross that line, and FTS saves a whole moving part.

## AI Review Checklist

- Is search done via `tsvector @@ tsquery`, not `LIKE '%...%'`?
- Is the `tsvector` a stored generated column (or trigger-maintained), not recomputed per query?
- Is there a GIN index on the vector, and does `EXPLAIN` confirm it is used?
- Is the language configuration named explicitly in every `to_tsvector`/`to_tsquery` call?
- Does user-facing input go through `websearch_to_tsquery` (or `plainto_tsquery`) to avoid parse errors?
- Are results ranked (`ts_rank`/`ts_rank_cd`) and fields weighted where relevance matters?
- Is fuzzy matching handled with `pg_trgm`/prefix queries rather than expected from FTS?

## Related

- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/08-jsonb.md`
- `knowledge/postgresql/15-extensions.md`
- `knowledge/postgresql/05-query-planner.md`
