---
id: postgresql/00-overview
topic: postgresql
slug: overview
title: "PostgreSQL Overview"
type: doc
order: 0
status: ready
tags: [postgresql, overview]
related: [postgresql/03-data-types, postgresql/04-indexes, postgresql/05-query-planner, postgresql/06-transactions, postgresql/16-performance]
when_to_use: "Read first when starting any PostgreSQL work, to find which doc covers your problem."
---
# PostgreSQL Overview

## Purpose

This document is the map for the PostgreSQL topic. It explains what PostgreSQL
is, the mental model an agent needs to use it correctly, and where each sibling
doc lives so you can jump straight to the one that answers your question. It is a
map, not a tutorial — read the linked doc for depth.

PostgreSQL is a relational database with strong ACID guarantees, MVCC
concurrency, a mature cost-based query planner, and first-class extensibility
(custom types, index methods, extensions like PostGIS and `pgvector`). It rewards
using its native features — real data types, constraints, indexes — over pushing
that logic into application code.

## Why It Matters

The database outlives every service in front of it. Application code is rewritten
every few years; the schema and the data survive. A mistake in a query is a slow
page; a mistake in the schema, an index, or a transaction boundary is data
corruption, lock storms, or a rewrite migration under load. Getting the database
layer right is the highest-leverage correctness work in most systems, and the
hardest to undo later. Treat schema and query design as decisions with the same
weight as an API contract.

## Core Principles

- **Let the database enforce truth.** Constraints (`NOT NULL`, `CHECK`, `UNIQUE`,
  foreign keys) belong in the schema, not only in application code. The database
  is the last line of defense and the only one that sees every writer.
- **Model with real types.** Use the type that matches the domain (`timestamptz`,
  `numeric`, `uuid`, `jsonb`, enums) instead of storing everything as `text`.
- **Measure, do not guess.** `EXPLAIN (ANALYZE, BUFFERS)` is the source of truth
  for query behavior. Intuition about what is slow is usually wrong.
- **Transactions are correctness boundaries.** Group writes that must be atomic;
  keep transactions short so they do not hold locks or bloat MVCC.
- **Indexes are a trade-off, not free speed.** Each one speeds reads and slows
  writes. Add them deliberately, verify they are used, and drop dead ones.

## Best Practices

- Pin a specific major version and read its release notes before upgrading;
  behavior (planner, defaults, locking) changes between majors.
- Keep DDL in versioned migrations, never applied by hand in production.
- Give every table a primary key; prefer `bigint` identity or `uuid` (v7) keys.
- Turn on `pg_stat_statements` early so you have query telemetry before you need it.
- Reproduce a slow query with `EXPLAIN (ANALYZE, BUFFERS)` before changing anything.

## How the Docs Fit Together

- **Set up** — start here to get a correct, secure instance running:
  [installation](01-installation.md), [configuration](02-configuration.md).
- **Model** — design the schema so data is correct by construction:
  [data-types](03-data-types.md), [jsonb](08-jsonb.md), [arrays](09-arrays.md).
- **Make it fast** — read paths and the planner:
  [indexes](04-indexes.md), [query-planner](05-query-planner.md),
  [performance](16-performance.md), [tuning](27-tuning.md).
- **Concurrency & correctness** — how writers coexist safely:
  [transactions](06-transactions.md), [locking](07-locking.md),
  [vacuum](20-vacuum.md), [analyze](21-analyze.md).
- **Scale & availability** — grow beyond one node:
  [partitioning](11-partitioning.md), [replication](12-replication.md),
  [high-availability](13-high-availability.md), [backups](14-backups.md).
- **Operate** — run it in production:
  [monitoring](17-monitoring.md), [security](18-security.md),
  [roles-and-permissions](19-roles-and-permissions.md), [migrations](22-migrations.md).
- **Ship well** — cross-cutting guidance:
  [best-practices](25-best-practices.md), [production](26-production.md),
  [common-antipatterns](100-common-antipatterns.md).

## Common Mistakes

- Treating PostgreSQL as a dumb key-value store: no constraints, everything `text`,
  all logic in the app. You lose the main reason to run a relational database.
- Skipping `EXPLAIN` and adding indexes by superstition until writes crawl.
- Long-running or idle-in-transaction sessions that block VACUUM and hold locks.
- Copying MySQL habits (e.g. relying on implicit casts or `datetime` without zone).
- Running a stock `postgresql.conf` on real hardware and wondering why it is slow.

## AI Review Checklist

- Does every table have a primary key and appropriate `NOT NULL`/`CHECK`/FK constraints?
- Are columns modeled with precise types (`timestamptz`, `numeric`, `jsonb`) not `text`?
- Are new queries backed by `EXPLAIN (ANALYZE, BUFFERS)` evidence, not a guess?
- Are schema changes delivered as versioned, reversible migrations?
- Is the change scoped to the right sibling doc's concern, and does it link to it?

## Related

- `knowledge/postgresql/03-data-types.md`
- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/05-query-planner.md`
- `knowledge/postgresql/06-transactions.md`
- `knowledge/postgresql/16-performance.md`
