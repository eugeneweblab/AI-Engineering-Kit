---
id: databases/01-database-fundamentals
topic: databases
slug: database-fundamentals
title: "Database Fundamentals"
type: doc
order: 1
status: ready
tags: [databases, database-fundamentals]
related: [databases/02-relational-vs-nosql, databases/03-data-modeling, databases/07-indexing, databases/09-transactions, databases/12-acid]
when_to_use: "Read before writing any code that reads from or writes to a database, to build the shared vocabulary the rest of this topic assumes."
---
# Database Fundamentals

## Purpose

This document defines the core building blocks every database interaction rests on:
tables and rows, keys, indexes, the query lifecycle, transactions, and the
guarantees an engine makes. It gives an agent the vocabulary the rest of this topic
uses, so later docs can talk about "the primary key" or "isolation level" without
re-explaining them.

It is deliberately technology-neutral. The concepts here hold whether the store is
PostgreSQL, MySQL, SQLite, or a distributed NoSQL engine; where they differ, later
docs (starting with [Relational vs NoSQL](02-relational-vs-nosql.md)) draw the line.

## Why It Matters

Data outlives the code that wrote it. A row inserted today may still be read in five
years by three services and a report. If the fundamentals are wrong — no primary
key, no constraints, the wrong type — every one of those readers inherits the
defect, and fixing it means a risky migration over live data. Getting the basics
right up front is the cheapest correctness you will ever buy. Getting them wrong is
the most expensive to undo.

## Core Principles

- **Every table has a stable primary key.** It uniquely identifies a row and never
  changes. Without it you cannot reliably update, delete, or reference a row.
- **A relation models a fact, not an object.** Each row is one true statement about
  the world. Design so that a row is either fully true or absent — never half-true.
- **The engine enforces invariants; the app requests changes.** Constraints
  (`NOT NULL`, `UNIQUE`, `FOREIGN KEY`, `CHECK`) are the last line of defense and the
  only one that cannot be bypassed by a buggy caller or a manual SQL fix.
- **Indexes speed reads and slow writes.** They are a copy of data in sorted order.
  Every index must earn its place by serving a real query.
- **Reads and writes happen inside transactions.** Even a single statement is a
  transaction. Concurrency and partial failure are always in play.

## Best Practices

- Give every table a primary key. Prefer a surrogate key (an auto-generated
  `BIGINT` identity or UUID) unless a natural key is genuinely immutable and unique.
- Choose the narrowest correct type: `TIMESTAMPTZ` for instants (never a naive
  local time), `NUMERIC` for money (never `FLOAT`), an explicit `VARCHAR(n)` or
  `TEXT` for strings. The type is a constraint — use it.
- Declare foreign keys for every real relationship, with an explicit
  `ON DELETE` action. Orphan rows are silent corruption.
- Make columns `NOT NULL` unless "unknown" is a meaningful, distinct state. `NULL`
  is not zero and not empty string; it breaks equality and aggregation.
- Add a `UNIQUE` constraint for every business-uniqueness rule (one email per user).
  Do not enforce uniqueness in application code — races defeat it.
- Read a query plan (`EXPLAIN ANALYZE`) before assuming a query is fast. A sequential
  scan over a large table is a design signal, not a detail.

## Examples

**Good Example** — keys, types, and constraints enforced by the engine

```sql
CREATE TABLE account (
  id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- stable surrogate key
  email        TEXT        NOT NULL UNIQUE,        -- uniqueness enforced by the DB, race-proof
  balance_cents BIGINT     NOT NULL DEFAULT 0
                 CHECK (balance_cents >= 0),       -- invariant the app can never violate
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()  -- instant, timezone-aware
);

-- Index the column we filter on, because lookups by email must not scan the table.
CREATE INDEX idx_account_email ON account (email);
```

**Bad Example** — no key, wrong types, invariants left to the app

```sql
CREATE TABLE account (
  email    VARCHAR(255),   -- no PRIMARY KEY: rows can duplicate, cannot be referenced
  balance  FLOAT,          -- FLOAT for money: 0.1 + 0.2 != 0.3, rounding errors accrue
  created  VARCHAR(50)     -- date stored as free text: unsortable, unvalidated
);
-- Uniqueness of email "handled in code" → two concurrent signups both succeed.
-- Negative balances "prevented in code" → one missed check and the invariant is gone.
```

## Common Mistakes

- Tables with no primary key, so rows cannot be safely updated or deduplicated.
- Storing money in `FLOAT`/`DOUBLE`, accumulating rounding error.
- Storing timestamps as strings or naive local times, losing timezone and sort order.
- Using `NULL` as a stand-in for zero, empty, or false, poisoning aggregates.
- Enforcing uniqueness or foreign-key integrity only in application code, where
  concurrent requests race past the check.
- Adding indexes speculatively, slowing every write to speed a query no one runs.
- Assuming a query is fast without ever reading its plan.

## Production Tips

- Turn on slow-query logging and review it weekly; the fundamentals problems
  (missing index, wrong type causing a cast) surface there first.
- Keep the DDL in version control as migrations (see [Migrations](17-migrations.md)),
  never as ad-hoc changes applied by hand.
- Set sane connection-pool limits; an unbounded pool turns a traffic spike into a
  database outage.

## AI Review Checklist

- Does every table have a stable primary key that never changes?
- Are money, timestamps, and enums stored in correct, precise types?
- Are business invariants enforced by DB constraints, not just app code?
- Does every real relationship have a foreign key with an explicit `ON DELETE`?
- Is `NULL` used only where "unknown" is a genuine, distinct state?
- Does each index serve a real query, and has the plan been checked?

## Related

- `knowledge/databases/02-relational-vs-nosql.md`
- `knowledge/databases/03-data-modeling.md`
- `knowledge/databases/07-indexing.md`
- `knowledge/databases/09-transactions.md`
- `knowledge/databases/12-acid.md`
