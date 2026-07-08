---
id: sql/28-architecture
topic: sql
slug: architecture
title: "Architecture"
type: doc
order: 28
status: ready
tags: [sql, architecture]
related: [sql/12-ddl, sql/18-views, sql/20-stored-procedures, sql/14-transactions, sql/23-performance]
when_to_use: "Read before designing a schema, choosing where business logic lives, or planning how the database scales."
---
# Architecture

## Purpose

This document defines the structural decisions around a SQL database: how to model
data, where business logic belongs (in SQL or in the application), how the schema
evolves, and how the database fits into a larger system. These are the choices that
are cheap to make and expensive to change.

Schema is the most durable part of any system. Application code is rewritten
routinely; the tables outlive it, because data migration is hard and risky. Design the
schema as if it will be there in ten years, because it probably will.

## Why It Matters

A good schema makes correct code easy and wrong code hard: a foreign key makes an
orphaned row impossible, a `UNIQUE` constraint makes a duplicate impossible, a `CHECK`
makes an invalid state impossible. A bad schema does the opposite — it pushes
integrity into application code, where every code path must remember to enforce it and
one forgotten path corrupts the data permanently.

The other high-stakes decision is *where logic lives*. Constraints and integrity
belong in the database, close to the data, enforced for every writer. Complex business
workflows usually belong in application code, where they are testable and versioned.
Getting this split wrong yields either a database no one can reason about or an
application that cannot trust its own tables.

## Core Principles

- **Model the domain, then normalize.** Start from third normal form: every fact
  stored once, in the table it belongs to. Normalization prevents update anomalies —
  the same fact going stale in one copy and not another. Denormalize only under
  measured read pressure, deliberately.
- **The database owns integrity.** Encode every invariant you can as a constraint —
  `NOT NULL`, `UNIQUE`, `FOREIGN KEY`, `CHECK`. The database enforces these for *every*
  writer, forever; application checks only cover the paths you remembered. See
  [DDL](12-ddl.md).
- **Constraints in SQL, workflows in the app.** Put data-integrity rules in the schema
  and multi-step business processes in versioned, testable application code. Reserve
  stored procedures and triggers for logic that must be atomic with the data or shared
  across many writers. See [stored-procedures](20-stored-procedures.md).
- **Design for how data is read and written.** The access patterns drive the schema:
  indexes, partitioning, and denormalization all follow from real queries, not from a
  diagram drawn before any query exists.
- **Every schema change is additive first.** Add columns and tables before removing;
  never rename or drop in the same deploy that stops using them. Backward-compatible
  migrations let old and new code coexist during a rollout. See [DDL](12-ddl.md).

## Best Practices

- Give every table a **stable surrogate primary key** (an identity/`BIGINT` or UUID)
  and enforce natural keys with a separate `UNIQUE` constraint. Business identifiers
  change; primary keys should not.
- Encode invariants as **constraints, not comments**: a status column that allows only
  three values gets a `CHECK` (or an enum/lookup table), not a hope that the app
  behaves.
- Use **views to present a stable interface** over evolving tables, so application
  code and reporting depend on the view contract, not the physical layout. See
  [views](18-views.md).
- Do schema changes as **expand → migrate → contract**: add the new shape, backfill
  and dual-write, switch reads, then remove the old shape in a later deploy. Never
  couple a destructive change to the deploy that introduces its replacement.
- Choose **partitioning and sharding only against measured scale limits**, and prefer
  scaling reads with replicas before sharding writes — sharding is a large, hard-to-
  reverse complexity cost.
- Keep **transactions short and correctly scoped** around a unit of business work; the
  transaction boundary is an architectural decision, not an afterthought. See
  [transactions](14-transactions.md).

## Examples

**Good Example** — integrity in the schema, invariants enforced

```sql
CREATE TABLE orders (
  id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- stable surrogate key
  order_number TEXT        NOT NULL UNIQUE,          -- natural key as its own constraint
  customer_id  BIGINT      NOT NULL
                 REFERENCES customers (id),          -- FK: an orphaned order is impossible
  status       TEXT        NOT NULL DEFAULT 'open'
                 CHECK (status IN ('open','paid','shipped','cancelled')),  -- invalid state impossible
  total_cents  INTEGER     NOT NULL CHECK (total_cents >= 0),   -- no negative totals, ever
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Bad Example** — integrity pushed into application code

```sql
-- No keys, no constraints: the schema permits every invalid state, and the
-- application must remember to prevent each one on every write path.
CREATE TABLE orders (
  id           TEXT,          -- no primary key => duplicates allowed
  customer_id  TEXT,          -- no FK => orphaned orders accumulate silently
  status       TEXT,          -- any string => 'Shpiped' typo is now valid data
  total_cents  INTEGER        -- negative totals allowed => corrupt reports later
);
-- The first code path that forgets a check corrupts the table permanently.
```

## Common Mistakes

- Enforcing integrity in application code instead of constraints, so one missed path
  corrupts data.
- No foreign keys, leaving orphaned rows that no query can clean up reliably.
- Using a mutable business identifier as the primary key, so changing it cascades
  everywhere.
- Putting complex, evolving business workflows in triggers and procedures, where they
  are hard to test and version.
- Coupling destructive schema changes to the deploy that replaces them, making
  rollback impossible.
- Sharding or denormalizing prematurely, adding permanent complexity for unmeasured
  gains.

## Production Tips

- Run schema migrations with the **expand/contract** pattern and a migration tool that
  records applied versions, so environments never drift.
- Take **locking cost into account** for DDL on large tables (add indexes
  `CONCURRENTLY`, add `NOT NULL` in two steps) so a migration does not lock out writes.
- Keep a **documented ADR** for the big choices — primary-key strategy, normalization
  level, where logic lives — so later engineers inherit the reasoning, not just the
  tables.

## AI Review Checklist

- Is the schema normalized to 3NF unless denormalization is a measured, deliberate
  choice?
- Are invariants enforced by constraints (`NOT NULL`, `UNIQUE`, `FK`, `CHECK`), not by
  application code alone?
- Does every table have a stable surrogate primary key, with natural keys as separate
  `UNIQUE` constraints?
- Is integrity logic in SQL and multi-step workflow logic in versioned application
  code?
- Are schema changes backward-compatible (expand → migrate → contract)?
- Are scaling choices (partitioning, sharding) justified by measured limits?

## Related

- `knowledge/sql/12-ddl.md`
- `knowledge/sql/18-views.md`
- `knowledge/sql/20-stored-procedures.md`
- `knowledge/sql/14-transactions.md`
- `knowledge/sql/23-performance.md`
