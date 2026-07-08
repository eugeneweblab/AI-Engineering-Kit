---
id: databases/23-data-integrity
topic: databases
slug: data-integrity
title: "Data Integrity"
type: doc
order: 23
status: ready
tags: [databases, data-integrity]
related: [databases/12-acid, databases/09-transactions, databases/04-normalization, databases/06-schema-design, databases/10-concurrency]
when_to_use: "Read before designing a schema, adding a constraint, or reviewing any code that assumes the data it reads is valid."
---
# Data Integrity

## Purpose

This document defines how to guarantee that the data in the database is *correct*: valid,
consistent, and never contradicting itself. It covers constraints (primary keys, foreign
keys, unique, check, not-null), transactional consistency, and why the database — not the
application — must be the last line of defense. It is written so an agent can design a
schema that makes invalid states impossible to store.

Integrity is about the data being *right*. It complements [security](19-security.md) (who
may touch it) and [backup](18-backup-and-recovery.md) (getting it back) — a system needs
all three, and a breach of integrity is often the hardest to detect and undo.

## Why It Matters

Corrupt data is a poison that spreads. An order that references a deleted customer, a
balance that is `NULL`, two rows that should have been one — each propagates into reports,
downstream systems, and business decisions, and by the time anyone notices, the bad data
is months deep and impossible to cleanly unwind. Unlike a crash, an integrity violation
does not announce itself; the query returns a row and the code trusts it. The application
cannot be the sole guardian, because there is always more than one writer: a second
service, a migration, a manual `psql` session, a race between two requests. Only the
database sees every write, so only the database can enforce the invariant for all of them.
Getting integrity wrong means you cannot trust your own data — the failure the whole system
rests on.

## Core Principles

- **Enforce invariants in the database, not only the application.** Constraints are checked
  for every writer, including the ones you forgot about. App-level validation is a
  usability nicety; the constraint is the guarantee.
- **Make invalid states unrepresentable.** Use `NOT NULL`, `CHECK`, `UNIQUE`, foreign keys,
  and enums/domains so the database physically rejects the bad row. A row that cannot exist
  cannot cause a bug.
- **Foreign keys with the right `ON DELETE` behavior prevent orphans.** Decide `CASCADE`,
  `RESTRICT`, or `SET NULL` deliberately per relationship — the default matters.
- **Wrap multi-row invariants in a transaction.** If two writes must both happen or
  neither, they belong in one atomic transaction. See [transactions](09-transactions.md)
  and [ACID](12-acid.md).
- **Guard against concurrent races.** A read-then-write across two statements can violate a
  uniqueness or balance invariant under concurrency; use a unique constraint, appropriate
  isolation, or explicit locking. See [concurrency](10-concurrency.md).

## Best Practices

- Give every table a **primary key**; declare **foreign keys** for every reference and pick
  the `ON DELETE`/`ON UPDATE` action on purpose (orphan prevention vs. cascade).
- Use **`CHECK` constraints** for domain rules the database can verify: `price >= 0`,
  `status IN (...)`, `end_date >= start_date`. This catches bad data from every source.
- Add **`UNIQUE` constraints** for business-unique fields (email, SKU) — never rely on a
  `SELECT ... IF NOT EXISTS ... INSERT` check, which races under concurrency.
- Prefer **`NOT NULL`** by default; a nullable column is a claim that "absent" is a valid,
  meaningful state — make that an explicit decision, not an accident.
- Enforce **atomicity**: group writes that must succeed together in one transaction so a
  partial failure rolls back cleanly and leaves no half-updated invariant.
- Validate at **write time in the DB**; use application validation for good UX and error
  messages, but treat it as a duplicate of, not a replacement for, the constraint.
- Keep the schema **normalized** enough to avoid update anomalies; when you
  [denormalize](05-denormalization.md) for performance, add a mechanism (trigger, job) to
  keep the copies consistent.
- Add constraints in **migrations**, and when adding one to existing data, clean the
  violating rows first or the migration fails. See [migrations](17-migrations.md).

## Examples

**Good Example** — the database makes the bad state impossible

```sql
CREATE TABLE orders (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id BIGINT NOT NULL
                REFERENCES customers(id) ON DELETE RESTRICT, -- no orphaned orders
  email       TEXT   NOT NULL,
  total_cents INTEGER NOT NULL CHECK (total_cents >= 0),      -- no negative totals
  status      TEXT   NOT NULL CHECK (status IN ('pending','paid','shipped')),
  UNIQUE (customer_id, email)                                 -- DB-enforced uniqueness,
);                                                            -- race-proof by construction
```

```sql
-- Two writes that must both apply or neither: one atomic transaction.
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;   -- a failure between the UPDATEs rolls back; money is never created or destroyed
```

**Bad Example** — integrity left to the application, races and orphans follow

```ts
// Uniqueness "checked" in the app: two concurrent requests both see no row and both
// insert → duplicate emails. The database would have rejected the second with UNIQUE.
if (!(await db.query("SELECT 1 FROM orders WHERE email = $1", [email])).rows.length) {
  await db.query("INSERT INTO orders (email, customer_id) VALUES ($1, $2)",
    [email, customerId]); // customerId may not exist — no FK, so an orphan is created
}

// Two separate transactions: if the second fails, money vanishes. Not atomic.
await db.query("UPDATE accounts SET balance = balance - 100 WHERE id = 1");
await db.query("UPDATE accounts SET balance = balance + 100 WHERE id = 2"); // may not run
```

## Common Mistakes

- Enforcing invariants only in application code, so a second writer or migration corrupts them.
- Missing foreign keys, leaving orphaned rows that reference deleted parents.
- Read-then-write uniqueness checks that race under concurrency instead of a `UNIQUE` constraint.
- Nullable columns by default, so "missing" data silently means several contradictory things.
- Splitting an all-or-nothing update across multiple transactions, allowing partial state.
- No `CHECK` constraints, so negative prices and invalid statuses slip in from any source.
- Denormalizing without a consistency mechanism, so the duplicated copies drift apart.
- Choosing the wrong `ON DELETE` action, silently cascading (or blocking) deletes.

## Production Tips

- Periodically run **integrity audits** (orphan-finding queries, invariant checks) even
  with constraints in place — legacy data and past bugs leave violations the constraints
  were added too late to prevent.
- When adding a constraint to a large table, use a **`NOT VALID` then `VALIDATE`** two-step
  (PostgreSQL) to avoid a long lock, and fix offending rows before validating.
- Reproduce concurrency bugs with a **two-session test** in CI (interleaved statements) —
  integrity races are invisible in single-threaded tests.

## AI Review Checklist

- Does every table have a primary key and every reference a foreign key with a chosen `ON DELETE`?
- Are business invariants enforced by DB constraints (`CHECK`, `UNIQUE`, `NOT NULL`), not just app code?
- Is uniqueness enforced by a constraint rather than a race-prone read-then-write check?
- Are multi-row all-or-nothing updates wrapped in a single transaction?
- Are nullable columns a deliberate decision, not a default?
- When adding constraints to existing data, are violating rows handled so the migration succeeds?
- Where data is denormalized, is there a mechanism keeping the copies consistent?

## Related

- `knowledge/databases/12-acid.md`
- `knowledge/databases/09-transactions.md`
- `knowledge/databases/04-normalization.md`
- `knowledge/databases/06-schema-design.md`
- `knowledge/databases/10-concurrency.md`
