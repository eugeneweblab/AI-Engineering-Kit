---
id: sql/20-stored-procedures
topic: sql
slug: stored-procedures
title: "Stored Procedures"
type: doc
order: 20
status: ready
tags: [sql, stored-procedures, search_path, DEFINER]
related: [sql/21-triggers, sql/14-transactions, sql/22-security, sql/13-dml, sql/24-testing]
when_to_use: "Read before writing a stored procedure or function, or when deciding whether logic belongs in the database or the application."
---
# Stored Procedures

## Purpose

This document defines when to put logic in the database as stored procedures and
functions, and how to write them safely. It is written so an agent can move the
right logic into the database — set-based, data-adjacent, transactional — without
turning the database into an untestable business-logic dumping ground.

A stored procedure is code that runs inside the database engine, close to the data.
This is a genuine tool with real trade-offs, not a default. The question is always
*where does this logic belong*, and the answer is not "always in the database."

## Why It Matters

Logic in the database is powerful and dangerous in the same ways. Powerful: it runs
next to the data with no network round-trips, it can enforce invariants no
application can bypass, and it can wrap multi-step work in a single transaction.
Dangerous: it is harder to test, harder to version-control, harder to debug, and
easy to hide from the developers who own the feature. A pile of business rules
buried in PL/pgSQL that no one can find or test is a classic source of "haunted"
production behavior. The skill is knowing which logic earns its place there.

## Core Principles

- **Put logic in the database when it is data-shaped.** Bulk set operations,
  invariants that must hold regardless of caller, and multi-statement units that
  must be atomic are strong candidates. Feature/business orchestration usually is
  not.
- **Set-based beats row-by-row.** A procedure that loops over rows and issues one
  statement each throws away the engine's greatest strength. Express it as a single
  set operation whenever possible.
- **Own the transaction boundary explicitly.** Know whether the procedure commits,
  whether it can be called inside a caller's transaction, and what happens on error.
- **Handle errors, don't swallow them.** An exception block that catches everything
  and returns "success" corrupts data silently. Re-raise unless you can truly
  recover.
- **Treat procedures as versioned code.** They live in migrations and source
  control, are code-reviewed, and are tested — not edited live in production.

## Best Practices

- Prefer a single set-based statement over cursor/loop procedures; reach for a loop
  only when the operation is genuinely iterative and cannot be expressed in a set.
- Always parameterize. Build dynamic SQL only with proper identifier/literal
  quoting (`format(..., %I, %L)` in Postgres); never concatenate caller input into
  a statement — that is SQL injection inside the database. See
  [security](22-security.md).
- Define the security context deliberately: use `SECURITY DEFINER` only when the
  procedure must act with elevated rights, and then pin `search_path` to avoid
  hijacking. Default to `SECURITY INVOKER`.
- Make procedures idempotent or clearly not, and document which. Retries happen;
  a non-idempotent "charge card" procedure called twice is a real incident.
- Keep one responsibility per procedure and give it a verb-noun name
  (`archive_expired_carts`), so callers and reviewers know exactly what it does.
- Return meaningful results (affected row counts, status) rather than relying on
  side effects the caller cannot observe.
- Test procedures with a database test harness (see [testing](24-testing.md)):
  seed data, call the procedure, assert the resulting rows and errors.

## Examples

**Good Example** — set-based, atomic, parameterized, errors surfaced

```sql
-- Archive carts abandoned before a cutoff, in ONE set operation, atomically.
CREATE OR REPLACE PROCEDURE archive_expired_carts(p_cutoff timestamptz)
LANGUAGE plpgsql
AS $$
BEGIN
    WITH moved AS (
        DELETE FROM carts
        WHERE updated_at < p_cutoff          -- parameter, never string-concatenated
        RETURNING *
    )
    INSERT INTO carts_archive SELECT * FROM moved;   -- single set-based move
    -- No custom exception swallowing: any error rolls back the whole procedure.
END;
$$;
```

**Bad Example** — row-by-row loop, swallowed errors, injection

```sql
CREATE OR REPLACE PROCEDURE archive_expired_carts(p_cutoff text)
LANGUAGE plpgsql
AS $$
DECLARE r record;
BEGIN
    FOR r IN SELECT id FROM carts LOOP          -- row-by-row: slow, N round-trips
        BEGIN
            -- caller input concatenated into SQL -> injection inside the DB
            EXECUTE 'DELETE FROM carts WHERE id = ' || r.id
                 || ' AND updated_at < ''' || p_cutoff || '''';
        EXCEPTION WHEN OTHERS THEN
            NULL;                               -- swallows errors -> silent data loss
        END;
    END LOOP;
END;
$$;
```

## Common Mistakes

- Iterating row-by-row (cursors/loops) for work a single set statement could do.
- Concatenating caller input into dynamic SQL instead of parameterizing/quoting.
- Catch-all `EXCEPTION WHEN OTHERS THEN NULL`, hiding failures and corrupting data.
- Using `SECURITY DEFINER` without pinning `search_path`, allowing privilege
  escalation via a hijacked schema.
- Putting sprawling business/orchestration logic in the database where it is hard
  to test, review, and observe.
- Assuming a procedure is idempotent when a retry would double its effect.
- Editing procedures directly in production instead of shipping them via migrations.

## Production Tips

- Log or return affected-row counts; a procedure that silently affects zero rows is
  usually a bug the caller cannot see.
- Watch execution time and lock duration; a long procedure holding write locks can
  stall the whole application.
- Keep procedure source in migrations so `CREATE OR REPLACE` is reproducible and
  reviewable, and so rollbacks are possible.

## AI Review Checklist

- Is the logic genuinely data-shaped, or should it live in the application?
- Is the work set-based rather than a row-by-row loop where a set would do?
- Is all caller input parameterized or properly identifier/literal-quoted?
- Is the transaction boundary and error behavior explicit (no swallowed errors)?
- Is the security context correct — `SECURITY INVOKER` by default, `search_path`
  pinned when `DEFINER`?
- Is the procedure idempotent, or is its non-idempotency documented and handled?
- Is it versioned in migrations and covered by tests?

## Related

- `knowledge/sql/21-triggers.md`
- `knowledge/sql/14-transactions.md`
- `knowledge/sql/22-security.md`
- `knowledge/sql/13-dml.md`
- `knowledge/sql/24-testing.md`
