---
id: sql/27-portability
topic: sql
slug: portability
title: "Portability"
type: doc
order: 27
status: ready
tags: [sql, portability, MySQL, COALESCE, CONFLICT, SUM, RETURNING, JSONB, engine, syntax, one]
related: [sql/11-data-types, sql/10-functions, sql/12-ddl, sql/26-best-practices, sql/28-architecture]
when_to_use: "Read before choosing dialect-specific syntax, or when code must run on more than one database engine."
---
# Portability

## Purpose

This document defines how to decide *when* SQL should be portable across engines and
*how* to make it so when it should. It covers the real divergences between Postgres,
MySQL, SQL Server, Oracle, and SQLite — and the far more common case where chasing
portability is a mistake.

Portability is a trade-off, not a virtue. Standard-only SQL is more widely runnable
but slower to write and often slower to run, because it forgoes the engine features
you are paying for. Choose deliberately.

## Why It Matters

Two failures come from getting this wrong. The first is *accidental* lock-in: code
that quietly depends on MySQL's lenient `GROUP BY` or Postgres's `RETURNING`, so a
future migration to another engine means rewriting queries no one flagged. The
second is *pointless* portability: an application that will only ever run on Postgres,
written in bland ANSI SQL that avoids `JSONB`, arrays, and `ON CONFLICT` — throwing
away the exact features that make Postgres worth using.

The right default is: commit to one engine and use it fully, unless a concrete
requirement (a product shipped to customers who bring their own database, a planned
migration) says otherwise.

## Core Principles

- **Decide your target engines explicitly.** "Portable" is meaningless until you name
  the set. Postgres-only and "Postgres or MySQL" lead to very different code. Write the
  decision down. See [architecture](28-architecture.md).
- **If you target one engine, use it fully.** Do not hand-cuff yourself to ANSI SQL
  for a portability you will never exercise. The cost of that discipline is real and
  the benefit is zero.
- **If you target several, isolate the differences.** Push dialect-specific SQL behind
  a repository or query-builder layer so divergences live in one place, not scattered
  across the codebase.
- **Know where dialects actually diverge.** The dangerous differences are silent:
  `NULL` sorting, identifier case-folding, integer division, string concatenation, and
  `GROUP BY` strictness. These change *results*, not just syntax.
- **Standard SQL is the tie-breaker, not the goal.** When two forms are equally clear,
  prefer the standard one — but never contort a query to avoid a useful extension.

## Best Practices

- Prefer **standard functions** when equivalent: `COALESCE` over `NVL`/`IFNULL`,
  `CAST(x AS type)` over `::type` when you need cross-engine code, `CASE` over
  engine-specific conditionals. Reach for extensions when they earn their keep.
- Use **`||` for string concat in standard SQL**, but know MySQL uses `CONCAT()` (and
  `||` means OR there unless `PIPES_AS_CONCAT` is set) — a classic silent portability
  bug.
- **Quote identifiers only when necessary**, and pick one case convention.
  Unquoted identifiers fold to lower case in Postgres and upper case in Oracle; mixed
  quoting makes a schema non-portable and confusing.
- Handle **`NULL` ordering explicitly** with `ORDER BY x NULLS LAST` where supported;
  engines disagree on the default, so relying on it produces different row order per
  engine.
- Keep **DDL and types portable-aware**: `TIMESTAMP WITH TIME ZONE` semantics,
  `BOOLEAN` support, `SERIAL`/`AUTO_INCREMENT`/`IDENTITY`, and `TEXT` limits all differ.
  Choose types with the target set in mind. See [data-types](11-data-types.md).
- Manage cross-engine schema with a **migration tool** (Flyway, Liquibase, or an ORM's
  migrations) that abstracts dialect differences rather than hand-writing per-engine
  DDL.

## Examples

**Good Example** — portability isolated, engine features used deliberately

```sql
-- Target is Postgres-only, and the decision is documented. Use the feature that
-- makes Postgres worth it: atomic upsert with RETURNING, one round trip.
INSERT INTO inventory (sku, qty) VALUES ($1, $2)
ON CONFLICT (sku) DO UPDATE SET qty = inventory.qty + EXCLUDED.qty
RETURNING sku, qty;
```

```sql
-- Cross-engine target: use only standard constructs and explicit NULL ordering,
-- so the SAME query returns the SAME rows on Postgres, MySQL, and SQL Server.
SELECT sku, COALESCE(qty, 0) AS qty      -- COALESCE is standard; NVL/IFNULL are not
FROM inventory
-- Portable NULLs-last: a CASE sort key runs identically on all three engines.
-- (NULLS LAST is Postgres/Oracle-only syntax; it is a parse error on MySQL/SQL Server.)
ORDER BY CASE WHEN qty IS NULL THEN 1 ELSE 0 END, qty DESC, sku;
```

**Bad Example** — accidental lock-in, silent divergence

```sql
-- Claims to be "portable" but is not: relies on MySQL's lenient GROUP BY, which
-- selects an arbitrary email per customer. Postgres and SQL Server REJECT this.
SELECT customer_id, email, SUM(total)
FROM orders
GROUP BY customer_id;               -- email is neither grouped nor aggregated

-- '||' means OR in default MySQL, so this silently returns a number, not a string.
SELECT first_name || ' ' || last_name AS name FROM customers;
```

## Common Mistakes

- Claiming code is portable while depending on one engine's lax `GROUP BY`, `LIMIT`
  syntax, or `NULL` ordering.
- Writing ANSI-only SQL for an app that will only ever run on one engine, forgoing
  useful features for no benefit.
- Using `||` for concatenation and having it silently mean OR (or error) on MySQL.
- Assuming identifier case and quoting behave the same across engines.
- Scattering dialect-specific SQL through the codebase instead of behind one layer.
- Relying on the default `NULL` sort order, which differs by engine.

## AI Review Checklist

- Is the target engine set named and documented, not assumed?
- If single-engine, is the code using that engine's features rather than crippling
  itself for unused portability?
- If multi-engine, is dialect-specific SQL isolated behind one layer?
- Are the silent divergences handled: `NULL` ordering, `GROUP BY` strictness, string
  concat, identifier case?
- Are standard functions (`COALESCE`, `CAST`) preferred where cross-engine?
- Is schema managed by a migration tool rather than hand-written per engine?

## Related

- `knowledge/sql/11-data-types.md`
- `knowledge/sql/10-functions.md`
- `knowledge/sql/12-ddl.md`
- `knowledge/sql/26-best-practices.md`
- `knowledge/sql/28-architecture.md`
