---
id: sql/21-triggers
topic: sql
slug: triggers
title: "SQL Triggers"
type: doc
order: 21
status: ready
tags: [sql, triggers, AFTER, BEFORE, CHECK, UNIQUE, updated_at, constraint, trigger, whether]
related: [sql/20-stored-procedures, sql/14-transactions, sql/13-dml, sql/22-security, sql/23-performance]
when_to_use: "Read before adding a trigger, or when deciding whether an invariant should be enforced by a trigger, a constraint, or application code."
---
# SQL Triggers

## Purpose

This document defines when a trigger is the right tool and how to write one that
does not surprise the next developer. A trigger is code the database runs
automatically in response to `INSERT`, `UPDATE`, or `DELETE` on a table. It is
written so an agent can enforce a genuine data-layer invariant without hiding
important behavior in an invisible side effect.

Triggers are the most implicit construct in SQL: they fire without any call site
naming them. That power is exactly why they are so often misused.

## Why It Matters

A trigger runs inside the same transaction as the statement that fired it, so it
can enforce invariants no application can bypass — a strong guarantee. But because
nothing at the call site mentions the trigger, a developer doing an ordinary
`UPDATE` may unknowingly cascade into audit writes, denormalization updates, or
even other triggers. This "action at a distance" makes bugs extremely hard to
trace: the code you are reading is not the code doing the work. A trigger is worth
its opacity only when the invariant genuinely must hold for *every* writer,
including ad-hoc ones.

## Core Principles

- **Prefer a constraint over a trigger.** If a `CHECK`, `UNIQUE`, `FOREIGN KEY`, or
  `NOT NULL` can enforce the rule, use it — constraints are declarative, faster,
  and visible in the schema. Reach for a trigger only when a constraint cannot
  express the rule.
- **Triggers run in the firing transaction.** Their work is atomic with the
  statement and rolls back with it. A slow or failing trigger slows or fails every
  write to that table.
- **Keep triggers small, fast, and side-effect-honest.** They should do one clear
  thing (stamp a timestamp, write an audit row) — not run business workflows.
- **Never call external systems from a trigger.** No HTTP, no email, no queue
  publish inside the transaction; it couples your commit to a third party and can
  hang every write.
- **Make trigger existence discoverable.** Document triggers where developers will
  look, because the call site never reveals them.

## Best Practices

- Use triggers for cross-cutting, must-always-hold data behavior: audit trails,
  `updated_at` stamping, maintaining a denormalized counter, enforcing rules a
  `CHECK` cannot express (e.g. spanning rows).
- Beware order and recursion: multiple triggers on one table fire in a defined but
  easy-to-forget order, and a trigger that writes to its own table can re-fire.
  Guard against unintended recursion.
- Use `BEFORE` triggers to modify the row being written (e.g. set `updated_at`),
  and `AFTER` triggers for effects that depend on the committed row (e.g. audit
  logging). Do not do row mutation in `AFTER`.
- Prefer statement-level triggers over row-level when the action is the same
  regardless of row count; a row-level trigger on a 1M-row bulk update fires a
  million times.
- Keep the trigger function parameterized and injection-safe just like any
  [stored procedure](20-stored-procedures.md); dynamic SQL in a trigger is still a
  risk.
- If the behavior is optional, orchestration, or can tolerate eventual consistency,
  put it in the application or a background job — not a trigger.

## Examples

**Good Example** — small, declarative-adjacent, single responsibility

```sql
-- One job: stamp updated_at on every modification. BEFORE, so it edits the row
-- in-flight with no extra write. Cannot be bypassed by any caller.
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := now();   -- modify the row being written; no side effects
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();
```

**Bad Example** — hidden business logic and an external call in-transaction

```sql
CREATE OR REPLACE FUNCTION on_order_insert()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- Business workflow hidden behind an INSERT: no call site reveals any of this.
    UPDATE inventory SET qty = qty - NEW.qty WHERE sku = NEW.sku;  -- can deadlock
    -- External HTTP inside the txn: commit now waits on a third party and can hang
    -- every insert into orders if the endpoint is slow or down.
    PERFORM http_post('https://mail.example.com/send', NEW.customer_email);
    RETURN NEW;
END;
$$;
CREATE TRIGGER trg_orders_ai AFTER INSERT ON orders
    FOR EACH ROW EXECUTE FUNCTION on_order_insert();
```

## Common Mistakes

- Using a trigger where a `CHECK`/`UNIQUE`/`FK` constraint would enforce the rule
  declaratively.
- Performing external I/O (HTTP, email, queue) inside a trigger, coupling commits
  to outside systems.
- Hiding business/orchestration logic in triggers, making behavior untraceable from
  the code that triggered it.
- Row-level triggers on bulk operations, firing once per row and crippling
  throughput.
- Unintended recursion or fragile inter-trigger ordering causing surprising results.
- Doing row mutation in an `AFTER` trigger (too late) or heavy work in `BEFORE`.
- Leaving triggers undocumented, so the next developer cannot find the source of a
  side effect.

## Production Tips

- Inventory triggers per table in schema docs and code review; an "unexplained"
  extra write is almost always a trigger.
- Measure write latency after adding a trigger — you have added work to every
  matching statement.
- For denormalized counters maintained by triggers, add a periodic reconciliation
  job; triggers drift under edge cases and bulk loads.

## AI Review Checklist

- Could a constraint (`CHECK`/`UNIQUE`/`FK`/`NOT NULL`) enforce this instead?
- Does the trigger do external I/O inside the transaction (it must not)?
- Is it a single, small, fast responsibility rather than a business workflow?
- Is it `BEFORE` for row mutation and `AFTER` for post-write effects?
- Is it statement-level where row-level would fire needlessly per row?
- Is recursion / multi-trigger ordering considered and safe?
- Is the trigger's existence documented where developers will find it?

## Related

- `knowledge/sql/20-stored-procedures.md`
- `knowledge/sql/14-transactions.md`
- `knowledge/sql/13-dml.md`
- `knowledge/sql/22-security.md`
- `knowledge/sql/23-performance.md`
