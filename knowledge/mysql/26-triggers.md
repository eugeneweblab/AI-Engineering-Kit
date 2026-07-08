---
id: mysql/26-triggers
topic: mysql
slug: triggers
title: "Triggers"
type: doc
order: 26
status: ready
tags: [mysql, triggers]
related: [mysql/27-procedures, mysql/25-events, mysql/06-transactions, mysql/19-best-practices]
when_to_use: "Read before adding a trigger, or when debugging why a simple INSERT/UPDATE has surprising side effects."
---
# Triggers

## Purpose

This document defines when a MySQL **trigger** is justified and how to write one that does
not become invisible, unbounded, or dangerous. A trigger is SQL that fires automatically
`BEFORE` or `AFTER` an `INSERT`, `UPDATE`, or `DELETE` on a table, with access to `OLD`
and `NEW` row values.

Triggers are powerful and quiet: they run inside the same transaction as the statement
that fired them, with no call site in your application code. That quietness is exactly why
they must be used sparingly and reviewed carefully.

## Why It Matters

A trigger executes on every affected row, inside the writing transaction, with no
application log line. A slow or failing trigger turns a fast `INSERT` into a slow or
failing one, and the developer staring at the `INSERT` sees no reason why. Triggers that
write to other tables create hidden data flows that break the mental model of "this
statement touches this table." Worst of all, a trigger that raises an error aborts the
whole transaction — so a logging trigger can block the business write it was meant only to
observe. The blast radius of a bad trigger is every write to the table, forever, until
someone finds the hidden code.

## Core Principles

- **Triggers run inside the firing transaction.** Their cost and their failures belong to
  the original statement. A slow trigger is a slow write; a failing trigger rolls back the
  write. See [transactions](06-transactions.md).
- **They fire per row, not per statement.** A 100k-row `UPDATE` runs the trigger 100k
  times. Anything expensive multiplies.
- **They are invisible at the call site.** Nobody reading the `INSERT` knows the trigger
  exists. Prefer explicit application logic when the behavior is business logic.
- **Keep them tiny and deterministic.** Validate a value, stamp a timestamp, maintain a
  denormalized counter — nothing that reaches outside the current tables.
- **No trigger may call out or do heavy work.** No network, no unbounded loops, no cascades
  into more triggers. The transaction is holding locks while it runs.

## Best Practices

- Use triggers only for **data-integrity invariants and bookkeeping** that must hold no
  matter which client writes: audit rows, `updated_at` stamps, maintaining a summary
  count. Put application/business logic in the application.
- Keep the body a handful of deterministic statements. Never issue queries that scan large
  tables or depend on state outside `OLD`/`NEW`.
- Fail fast and clearly: use `SIGNAL SQLSTATE '45000'` to reject invalid data in a
  `BEFORE` trigger, so the reason is explicit rather than a silent corruption.
- Avoid trigger chains — a trigger that writes a table whose own trigger writes another.
  Chains are near-impossible to reason about and can deadlock. See [locking](07-locking.md).
- Never write to the *same* table the trigger is defined on in a way that could recurse;
  MySQL forbids it for the triggering table, but cross-table cycles are still on you.
- Version-control every trigger in migrations, and document at the table's model/ORM layer
  that a trigger exists, so the hidden behavior is discoverable.

## Examples

**Good Example** — tiny, deterministic integrity + audit

```sql
-- BEFORE trigger validates and normalizes using only NEW: fast, no external reads.
CREATE TRIGGER orders_before_ins BEFORE INSERT ON orders
FOR EACH ROW
BEGIN
  IF NEW.total < 0 THEN
    -- Reject bad data explicitly so the caller gets a clear error, not corruption.
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'order total must be non-negative';
  END IF;
  SET NEW.created_at = COALESCE(NEW.created_at, NOW());
END;

-- AFTER trigger writes one bounded audit row in the same transaction.
CREATE TRIGGER orders_after_upd AFTER UPDATE ON orders
FOR EACH ROW
INSERT INTO order_audit (order_id, old_total, new_total, changed_at)
  VALUES (NEW.id, OLD.total, NEW.total, NOW());
```

**Bad Example** — heavy, hidden, and able to block the write

```sql
CREATE TRIGGER orders_after_ins AFTER INSERT ON orders
FOR EACH ROW
BEGIN
  -- Full-table scan on every single inserted row: an N-row insert does N scans,
  -- all inside the transaction, holding locks the whole time.
  UPDATE customers
    SET lifetime_value = (SELECT SUM(total) FROM orders WHERE customer_id = NEW.customer_id)
    WHERE id = NEW.customer_id;
  -- "Notifying" from a trigger: if this errors, the whole INSERT rolls back.
  INSERT INTO email_queue (to_customer, template) VALUES (NEW.customer_id, 'order_ok');
END;
```

## Common Mistakes

- Putting business logic (pricing, notifications, workflow) in triggers, where it is
  invisible and untestable.
- Expensive per-row work (scans, aggregates) that multiplies across a bulk statement.
- Letting a non-critical trigger raise an error and roll back the real write.
- Building trigger chains across tables that deadlock or are impossible to trace.
- Assuming a trigger fires for bulk loaders — `LOAD DATA` fires row triggers, but some
  replication/bulk paths differ; verify rather than assume.
- Defining triggers directly in production, so they never appear in code review.

## Production Tips

- Enumerate existing triggers with `SHOW TRIGGERS` or `information_schema.TRIGGERS` before
  debugging a "haunted" table where writes behave unexpectedly.
- If a trigger's job is really async work (emails, webhooks, aggregation), move it out:
  write an outbox row in the trigger and let a worker process it, so the write path stays
  fast and failures do not roll back business data.
- Load-test writes to a triggered table; a per-row trigger can dominate the cost of a
  bulk import.

## AI Review Checklist

- Does the trigger do only integrity/bookkeeping, with business logic kept in the app?
- Is the body small, deterministic, and free of large scans or external calls?
- Could the trigger raise an error that rolls back a write it was only meant to observe?
- Does it fire per row on bulk statements without multiplying an expensive operation?
- Are there trigger chains across tables that risk deadlock or hidden cascades?
- Is the trigger defined in a reviewed migration and documented at the model layer?

## Related

- `knowledge/mysql/27-procedures.md`
- `knowledge/mysql/25-events.md`
- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/19-best-practices.md`
