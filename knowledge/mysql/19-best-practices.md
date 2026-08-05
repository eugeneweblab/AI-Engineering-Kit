---
id: mysql/19-best-practices
topic: mysql
slug: best-practices
title: "MySQL Best Practices"
type: doc
order: 19
status: ready
tags: [mysql, best-practices]
related: [mysql/03-data-types, mysql/04-indexes, mysql/05-query-optimization, mysql/06-transactions, mysql/12-security]
when_to_use: "Read before designing a schema, writing queries, or reviewing MySQL code for general correctness and durability."
---
# MySQL Best Practices

## Purpose

This document collects the defaults that make MySQL applications correct, fast, and safe
by construction: schema design, data types, query shape, transactions, and connection
handling. It is the baseline an agent should apply to *every* MySQL project unless a
specific document overrides it.

These are opinionated defaults with reasons. Each rule states the cost of ignoring it, so
you can make an informed exception when the situation genuinely warrants one — not by
accident.

## Why It Matters

MySQL forgives bad choices for a while. A table with the wrong charset, a query without an
index, or a transaction left open all work fine at low volume, then become the outage at
scale — and by then the schema has millions of rows and every fix needs a migration under
load. Getting the defaults right on day one costs minutes; getting them wrong costs a
maintenance window and a data-integrity review. The bar for a database is durability first,
speed second.

## Core Principles

- **Model the data, not the screen.** Normalize to remove update anomalies; denormalize
  deliberately and only with a measured read pattern to justify it.
- **The narrowest correct type wins.** Smaller rows mean more rows per page, more of the
  working set in the buffer pool, and faster everything.
- **Every query should have an index it can use.** An unindexed access path is a scan, and
  a scan that is fine today is an incident at 100x the rows.
- **Keep transactions short and deterministic.** A transaction holds locks for its entire
  lifetime; long ones serialize the system and cause deadlocks.
- **Let the database enforce integrity.** Constraints, foreign keys, and `NOT NULL` are
  the last line that application bugs cannot bypass.

## Best Practices

- Use `utf8mb4` charset and a `utf8mb4_0900_ai_ci` (or `_bin`) collation everywhere.
  Legacy `utf8` is 3-byte and cannot store emoji or many characters — it silently truncates.
- Give every table an explicit primary key, ideally a monotonic `BIGINT UNSIGNED
  AUTO_INCREMENT`. InnoDB clusters data on the primary key, so a random UUID PK fragments
  writes; if you need a UUID, store it as `BINARY(16)` and keep an auto-increment PK.
- Prefer `DATETIME` over `TIMESTAMP` unless you specifically want the 2038 limit and
  automatic timezone conversion. Store time in UTC; convert at the edges.
- Use `DECIMAL` for money, never `FLOAT`/`DOUBLE` — binary floats cannot represent `0.10`
  exactly and will drift.
- Declare columns `NOT NULL` with sensible defaults unless nullability is meaningful.
  `NULL` breaks equality, complicates indexes, and hides bugs.
- Always use parameterized queries / prepared statements. String-concatenated SQL is the
  root cause of injection; see [security](12-security.md).
- Set an explicit `sql_mode` including `STRICT_TRANS_TABLES` so bad data errors instead of
  being silently coerced or truncated.
- Add indexes to match your actual `WHERE`, `JOIN`, and `ORDER BY` columns; drop indexes no
  query uses — each one taxes every write.

## Examples

**Good Example** — narrow types, correct charset, explicit integrity

```sql
CREATE TABLE payments (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,  -- monotonic clustered PK
  account_id   BIGINT UNSIGNED NOT NULL,
  amount_cents DECIMAL(12,2)   NOT NULL,                 -- exact money, never FLOAT
  currency     CHAR(3)         NOT NULL,                 -- fixed-width ISO code
  status       ENUM('pending','settled','failed') NOT NULL DEFAULT 'pending',
  created_at   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_account_created (account_id, created_at),      -- serves the real query
  CONSTRAINT fk_account FOREIGN KEY (account_id) REFERENCES accounts (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

**Bad Example** — wrong types, no integrity, injection-prone access

```sql
CREATE TABLE payments (
  id       VARCHAR(36),          -- random UUID PK fragments InnoDB clustered writes
  amount   FLOAT,                -- 0.10 + 0.20 != 0.30; money silently drifts
  currency VARCHAR(255),         -- 255 bytes for a 3-char code, no constraint
  status   VARCHAR(255),         -- any string accepted, including typos like 'setled'
  created  TIMESTAMP             -- 2038 cliff, implicit timezone conversion surprises
) ENGINE=InnoDB DEFAULT CHARSET=utf8;  -- 3-byte utf8 truncates 4-byte characters
-- and the app builds queries by string concatenation → SQL injection.
```

## Common Mistakes

- Using `utf8` instead of `utf8mb4`, then losing emoji and multibyte data to truncation.
- A UUID or natural string as the InnoDB primary key, causing page splits and write
  amplification; use a surrogate auto-increment and index the UUID separately.
- `FLOAT`/`DOUBLE` for currency, quantities, or anything that must sum exactly.
- Nullable columns everywhere, so `= NULL` never matches and reports quietly drop rows.
- Building SQL with string interpolation instead of bound parameters.
- Wrapping unrelated work in one long transaction, holding locks across network calls.

## Production Tips

- Pin `sql_mode`, `character_set_server`, and `collation_server` in the server config so a
  new node cannot come up with different, silently-lossy defaults.
- Review new indexes against `performance_schema.table_io_waits_summary_by_index_usage` to
  drop indexes that no query actually uses.
- Enforce these defaults in migration review, not code review — schema mistakes are
  expensive to reverse once data exists.

## AI Review Checklist

- Is the charset `utf8mb4` with an explicit collation on every table and text column?
- Does every table have an explicit primary key, and is it monotonic for InnoDB?
- Is money `DECIMAL`, and are dates stored in UTC with an intentional type choice?
- Are columns `NOT NULL` unless nullability is genuinely meaningful?
- Does every hot query have a usable index, and does every index serve a query?
- Are all queries parameterized, with `STRICT_TRANS_TABLES` in `sql_mode`?

## Related

- `knowledge/mysql/03-data-types.md`
- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/12-security.md`
