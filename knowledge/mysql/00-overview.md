---
id: mysql/00-overview
topic: mysql
slug: overview
title: "MySQL Overview"
type: doc
order: 0
status: ready
tags: [mysql, overview]
related: [mysql/01-installation, mysql/03-data-types, mysql/04-indexes, mysql/05-query-optimization, mysql/02-configuration]
when_to_use: "Read first when starting any MySQL work to learn how this topic's docs fit together."
---
# MySQL Overview

## Purpose

This document orients an agent to the MySQL knowledge base: what MySQL is, when to
reach for it, and how the individual docs in this topic connect. It is a map, not a
tutorial — read it first, then jump to the specific doc for the task at hand.

MySQL is a relational database using the InnoDB storage engine by default. These docs
assume **MySQL 8.0 or 8.4 LTS** (the current supported lines as of 2026). MySQL 5.7
reached end-of-life in October 2023; do not target it for new work.

## Why It Matters

The database is the one component you cannot casually rewrite. Schema and index
decisions made on day one constrain query performance and availability for the life of
the product, and a bad transaction or locking pattern surfaces only under production
load — never in a unit test. Getting the fundamentals right up front is far cheaper than
migrating a 500 GB table under an incident. This topic exists so an agent can make those
early decisions correctly instead of discovering the cost later.

## Core Principles

- **InnoDB is the default and the right default.** It gives you ACID transactions, row-level
  locking, and crash recovery. Do not switch engines without a specific, documented reason.
- **The schema is the contract.** Column types, constraints, and indexes encode correctness.
  Push invariants into the schema (`NOT NULL`, `FOREIGN KEY`, `UNIQUE`) rather than trusting
  application code to hold them.
- **Read the query plan, not your intuition.** `EXPLAIN` is the ground truth for how MySQL
  will execute a statement. Guessing about index usage is how full table scans reach production.
- **Everything is a trade-off between read speed, write cost, and storage.** An index speeds
  reads and slows writes; denormalization speeds reads and risks inconsistency. Name the trade.

## Best Practices

- Target a specific MySQL version and pin it in CI, staging, and production so behavior is
  reproducible. See [installation](01-installation.md).
- Treat `my.cnf` as versioned infrastructure, not a machine you hand-tune. See
  [configuration](02-configuration.md).
- Choose the narrowest correct data type; it cascades into index size and cache efficiency.
  See [data types](03-data-types.md).
- Design indexes for your actual query patterns, then verify with `EXPLAIN`. See
  [indexes](04-indexes.md) and [query optimization](05-query-optimization.md).
- Wrap multi-statement changes in explicit transactions with the right isolation level.

## How the docs fit together

Read the docs roughly in order — each builds on the last:

- **[01-installation](01-installation.md)** — pick and pin a version; get a running server.
- **[02-configuration](02-configuration.md)** — tune `my.cnf`: buffer pool, durability, charset.
- **[03-data-types](03-data-types.md)** — model columns with the narrowest correct type.
- **[04-indexes](04-indexes.md)** — B-tree indexes, composite order, covering indexes.
- **[05-query-optimization](05-query-optimization.md)** — read `EXPLAIN`, kill full scans.

Beyond these fundamentals, the topic continues with transactions, locking, storage
engines, replication, backups, security, and production operations. Return here to
navigate; go to the specific doc to act.

## Examples

**Good Example** — a table that encodes its own invariants

```sql
CREATE TABLE orders (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id    BIGINT UNSIGNED NOT NULL,
  status     ENUM('pending','paid','shipped','cancelled') NOT NULL DEFAULT 'pending',
  total_cents INT UNSIGNED NOT NULL,           -- money as integer cents, never FLOAT
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_user_created (user_id, created_at),  -- supports "orders for user, newest first"
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;        -- utf8mb4 = real UTF-8
```

**Bad Example** — vague types, no constraints, wrong charset

```sql
CREATE TABLE orders (
  id         INT,                 -- signed, nullable, no PK: rows are unidentifiable
  user_id    INT,                 -- no FK: orphan orders become possible
  status     VARCHAR(255),        -- any string is "valid"; typos slip through
  total      FLOAT,               -- rounding errors on money
  created_at VARCHAR(50)          -- dates as strings can't be indexed or compared
) CHARSET=utf8;                    -- MySQL "utf8" is 3-byte; drops emoji and some CJK
```

## Common Mistakes

- Targeting MySQL 5.7 or leaving the version unpinned, so behavior differs across environments.
- Using `CHARSET=utf8` instead of `utf8mb4`, silently corrupting 4-byte characters.
- Storing money in `FLOAT`/`DOUBLE` and hitting rounding errors on totals.
- Skipping `EXPLAIN` and shipping queries that full-scan large tables.
- Treating MySQL as a key-value store and ignoring constraints, then debugging orphaned data.

## AI Review Checklist

- Is the work targeting a supported MySQL version (8.0 or 8.4), not 5.7?
- Do new tables use `ENGINE=InnoDB` and `CHARSET=utf8mb4`?
- Does every table have an explicit `PRIMARY KEY`, and do relationships use `FOREIGN KEY`?
- Were new or changed queries checked with `EXPLAIN` before merge?
- Is money stored as an integer or `DECIMAL`, never a float?

## Related


- `knowledge/mysql/01-installation.md`
- `knowledge/mysql/03-data-types.md`
- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/02-configuration.md`
