---
id: mysql/23-full-text-search
topic: mysql
slug: full-text-search
title: "MySQL Full Text Search"
type: doc
order: 23
status: ready
tags: [mysql, full-text-search]
related: [mysql/04-indexes, mysql/05-query-optimization, mysql/03-data-types, mysql/14-performance, mysql/24-json]
when_to_use: "Read before adding text search to a MySQL table, or when reviewing a LIKE-based search that needs to scale."
---
# MySQL Full Text Search

## Purpose

This document defines how to do text search in MySQL correctly: InnoDB `FULLTEXT` indexes,
`MATCH ... AGAINST`, natural-language versus boolean mode, and — critically — when MySQL's
built-in search is the right tool versus when to reach for a dedicated engine.

Full-text search here means relevance-ranked matching over natural-language text, backed by
an inverted index. It replaces `LIKE '%term%'` scans, which cannot use a normal index and
degrade linearly with table size.

## Why It Matters

Search built on `LIKE '%term%'` is a scan: it reads every row, ignores indexes, and gets
slower with every insert until it becomes the slowest query in the system. Teams then bolt
on relevance ranking in application code, badly. MySQL's `FULLTEXT` index solves both — it
matches with an inverted index and returns a relevance score — for the common case of
searching a few text columns. Knowing it exists (and knowing its limits) is the difference
between a search that scales and one that must be rebuilt on a separate service.

## Core Principles

- **`LIKE '%term%'` does not scale.** A leading wildcard disables the index and forces a
  full scan; for anything beyond a tiny table, use a `FULLTEXT` index instead.
- **`MATCH` must reference exactly the indexed columns.** The `FULLTEXT` index covers a
  specific column list; `MATCH(...)` must name the same set or MySQL cannot use the index.
- **Choose the mode deliberately.** Natural-language mode ranks by relevance and ignores
  very common words; boolean mode gives operators (`+`, `-`, `"..."`, `*`) but no automatic
  relevance stopword handling. They answer different questions.
- **Mind the minimum token length and stopwords.** InnoDB's default
  `innodb_ft_min_token_size` is 3, so short terms are not indexed; results silently omit
  them until you change the setting and rebuild the index.
- **Know the ceiling.** For faceting, typo tolerance, multilingual stemming, or very large
  corpora, a dedicated engine (Elasticsearch, OpenSearch, Meilisearch) is the right tool —
  MySQL `FULLTEXT` is for straightforward search close to the data.

## Best Practices

- Create an InnoDB `FULLTEXT` index on the text columns you search, and query them with
  `MATCH(col1, col2) AGAINST (...)` naming the identical column list.
- Use `IN NATURAL LANGUAGE MODE` (the default) when you want relevance ranking; use
  `IN BOOLEAN MODE` when you need required/excluded terms, phrases, or prefix matching.
- Select the `MATCH ... AGAINST` expression to get the relevance score and `ORDER BY` it,
  rather than re-ranking in application code.
- Tune `innodb_ft_min_token_size` (and rebuild the index) if users search short terms like
  product codes; the default of 3 will otherwise drop them.
- For prefix / autocomplete, use boolean mode with `term*`, but understand it matches on
  word boundaries, not arbitrary substrings.
- If requirements grow to typo tolerance, synonyms, stemming across languages, or
  cross-entity faceted search, move search to a dedicated index rather than stretching
  `FULLTEXT`.

## Examples

**Good Example** — FULLTEXT index, relevance-ranked query

```sql
-- Inverted index over the searchable columns.
CREATE TABLE articles (
  id      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  title   VARCHAR(255) NOT NULL,
  body    TEXT         NOT NULL,
  FULLTEXT KEY ft_article (title, body)   -- covers exactly (title, body)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- MATCH names the same columns as the index, so the FULLTEXT index is used.
-- The AGAINST expression is also the relevance score, so we rank by it directly.
SELECT id, title,
       MATCH(title, body) AGAINST ('replication failover' IN NATURAL LANGUAGE MODE) AS score
FROM articles
WHERE MATCH(title, body) AGAINST ('replication failover' IN NATURAL LANGUAGE MODE)
ORDER BY score DESC
LIMIT 20;

-- Boolean mode when terms are required/excluded:
--   AGAINST('+replication -postgres "point in time"' IN BOOLEAN MODE)
```

**Bad Example** — LIKE scan with no ranking

```sql
-- No FULLTEXT index; the leading % makes any index unusable.
SELECT id, title
FROM articles
WHERE title LIKE '%replication%' OR body LIKE '%replication%'  -- full table scan
ORDER BY created_at DESC;                                      -- no relevance at all
-- Reads every row on every search, gets slower as the table grows, and returns
-- newest-first instead of most-relevant. This is the query that eventually times out.
```

## Common Mistakes

- Using `LIKE '%term%'` for search and forcing a full scan on every query.
- A `MATCH(a, b)` whose column list does not match the `FULLTEXT` index, so MySQL falls
  back to a scan or errors instead of using the index.
- Expecting short tokens or common words to match, unaware of `innodb_ft_min_token_size`
  and stopwords silently dropping them.
- Sorting by date or re-ranking in application code instead of ordering by the relevance
  score `MATCH ... AGAINST` already computes.
- Pushing typo tolerance, stemming, synonyms, or faceting onto `FULLTEXT` when a dedicated
  search engine is the correct tool.
- Assuming boolean-mode `term*` matches substrings; it only matches word prefixes.

## Production Tips

- Rebuild the `FULLTEXT` index after changing token-size or stopword settings; the change
  does not apply retroactively to already-indexed rows.
- For large text columns, keep the `FULLTEXT` index on just the columns users search;
  indexing huge blobs inflates the index and slows writes.
- If search becomes a core product surface, plan the migration to a dedicated engine early —
  retrofitting relevance, faceting, and typo tolerance later is far more expensive.

## AI Review Checklist

- Is text search backed by a `FULLTEXT` index rather than `LIKE '%...%'`?
- Does every `MATCH(...)` name exactly the columns covered by the `FULLTEXT` index?
- Is natural-language vs boolean mode chosen to match the actual requirement?
- Are results ordered by the relevance score instead of re-ranked in application code?
- Have token-size / stopword limits been considered for the terms users actually search?
- If needs include typo tolerance, stemming, or faceting, is a dedicated engine chosen instead?

## Related

- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/03-data-types.md`
- `knowledge/mysql/14-performance.md`
- `knowledge/mysql/24-json.md`
