---
id: mysql/27-procedures
topic: mysql
slug: procedures
title: "Procedures"
type: doc
order: 27
status: ready
tags: [mysql, procedures, DEFINER, is_active, ROW_COUNT, CONCAT, DECIMAL, VARCHAR]
related: [mysql/26-triggers, mysql/25-events, mysql/06-transactions, mysql/12-security]
when_to_use: "Read before writing a stored procedure or function, or when deciding whether logic belongs in the database."
---
# Procedures

## Purpose

This document defines when to use MySQL **stored procedures and functions** and how to
write ones that are safe, testable, and not a maintenance trap. A stored procedure is a
named block of SQL invoked with `CALL`; a stored function returns a value and is used
inside expressions. Both live in the database, outside your application repository unless
you deliberately keep them in migrations.

Stored routines are a genuine tool for set-based data work that must run close to the data
(bulk maintenance, controlled write APIs), but they are a poor home for application
business logic, which belongs in version-controlled, testable application code.

## Why It Matters

Logic in stored procedures is logic your application team cannot see in code review,
cannot unit-test with their normal tooling, and cannot deploy atomically with the code
that calls it. MySQL's procedural language (`SQL/PSM`) has weak debugging, no package
manager, and no real dependency tracking, so procedures rot quietly. A stored function in
a `WHERE` clause can also destroy query performance by forcing a row-by-row call the
optimizer cannot see through. Deciding *what* goes into a procedure is therefore a
long-lived architectural commitment, not a coding convenience.

## Core Principles

- **The database is for set operations; the application is for business logic.** Put
  logic in a procedure only when it must be atomic and set-based near the data, or when it
  is the enforced, privileged interface to a table.
- **Stored functions in predicates are performance poison.** A function in `WHERE`,
  `JOIN`, or `ORDER BY` runs per row and blocks index use. See
  [query optimization](05-query-optimization.md).
- **Routines carry a security context.** `DEFINER` vs `INVOKER` decides whose privileges
  run the body. The wrong choice is a privilege-escalation bug. See [security](12-security.md).
- **Handle errors explicitly.** Without a `DECLARE ... HANDLER`, a mid-procedure error can
  leave a partial, uncommitted mess. Manage the transaction deliberately.
- **Version-control routines in migrations.** A procedure that exists only in production is
  undocumented, unreviewed infrastructure.

## Best Practices

- Reserve procedures for **set-based, atomic operations** (a multi-step maintenance job, a
  controlled transfer that must be all-or-nothing) and for a **privileged write API** where
  application accounts get `EXECUTE` but not direct `INSERT`/`UPDATE`.
- Manage transactions inside the procedure explicitly: `START TRANSACTION`, and a
  `DECLARE EXIT HANDLER FOR SQLEXCEPTION` that `ROLLBACK`s and re-signals, so a failure
  never commits half the work. See [transactions](06-transactions.md).
- Always pass data as **parameters**, never by concatenating strings into dynamic SQL. If
  you must use `PREPARE`, bind with `?` placeholders to avoid SQL injection.
- Declare the routine `SQL SECURITY INVOKER` unless it deliberately needs elevated
  `DEFINER` rights; document why when you choose `DEFINER`.
- Keep stored functions **deterministic and out of hot predicates**; if a function must
  filter rows, compute the value into a column/generated column and index that instead.
- Grant `EXECUTE` narrowly and keep the `CREATE PROCEDURE` in a migration so the routine is
  reviewed and reproducible across environments.

## Examples

**Good Example** — atomic transfer, explicit rollback, parameterized

```sql
CREATE PROCEDURE transfer_funds(IN from_acct BIGINT, IN to_acct BIGINT, IN amount DECIMAL(12,2))
  SQL SECURITY INVOKER            -- run with the caller's privileges, not the definer's
BEGIN
  -- On any error, roll back the whole transfer and re-raise: never commit half of it.
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  START TRANSACTION;
  UPDATE accounts SET balance = balance - amount WHERE id = from_acct AND balance >= amount;
  IF ROW_COUNT() = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'insufficient funds';  -- triggers rollback
  END IF;
  UPDATE accounts SET balance = balance + amount WHERE id = to_acct;
  COMMIT;
END;
```

**Bad Example** — logic in a WHERE-clause function, dynamic SQL, no error handling

```sql
CREATE FUNCTION is_active(uid BIGINT) RETURNS BOOLEAN
BEGIN
  RETURN (SELECT status FROM users WHERE id = uid) = 'active';
END;

-- Called once PER ROW of orders; the optimizer cannot use an index on users,
-- so this scans and re-queries for every order. Performance collapses at scale.
SELECT * FROM orders WHERE is_active(customer_id);

CREATE PROCEDURE find_user(IN name VARCHAR(100))
BEGIN
  -- String-concatenated SQL: 'name' flows straight into the query -> SQL injection.
  -- No handler: a failure mid-procedure leaves an open, partial transaction.
  SET @q = CONCAT('SELECT * FROM users WHERE name = "', name, '"');
  PREPARE s FROM @q; EXECUTE s;
END;
```

## Common Mistakes

- Putting application business logic in procedures, where it escapes code review, tests,
  and atomic deploys.
- Calling a stored function inside `WHERE`/`JOIN`, forcing per-row evaluation and killing
  index usage.
- Building queries by string concatenation instead of parameter binding, opening SQL
  injection.
- Omitting a `DECLARE ... HANDLER`, so an error leaves an uncommitted, partial transaction.
- Defaulting to `DEFINER` security and granting the definer broad rights, enabling
  privilege escalation.
- Editing procedures live in production so they diverge from what is in version control.

## Production Tips

- Inventory routines with `SHOW PROCEDURE STATUS` / `information_schema.ROUTINES` and check
  each `DEFINER` and `SECURITY_TYPE` during security review.
- If you use procedures as a write API, revoke direct table DML from application accounts
  and grant only `EXECUTE`; this makes the procedure the single audited entry point.
- Benchmark any query that calls a stored function in a predicate — replace it with a
  precomputed indexed column if it appears in `EXPLAIN` as a scan.

## AI Review Checklist

- Is the logic genuinely set-based/atomic, or is it business logic that belongs in the app?
- Does any stored function appear in a `WHERE`/`JOIN`/`ORDER BY`, blocking index use?
- Is every routine parameterized, with no string-concatenated dynamic SQL?
- Does the procedure manage its transaction and roll back cleanly via an error handler?
- Is `SQL SECURITY INVOKER` used unless elevated `DEFINER` rights are justified and
  documented?
- Is the routine defined in a reviewed migration, with `EXECUTE` granted narrowly?

## Related

- `knowledge/mysql/26-triggers.md`
- `knowledge/mysql/25-events.md`
- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/12-security.md`
