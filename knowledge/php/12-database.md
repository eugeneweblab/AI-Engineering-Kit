---
id: php/12-database
topic: php
slug: database
title: "Database"
type: doc
order: 12
status: ready
tags: [php, database]
related: [php/13-security, php/09-exceptions, php/14-performance, php/08-error-handling]
when_to_use: "Read before writing or reviewing any PHP code that queries, writes to, or opens a connection to a database."
---
# Database

## Purpose

This document defines how PHP talks to a relational database safely and efficiently:
how to connect, how to send parameters, how to control transactions, and how to avoid
the injection and resource bugs that dominate PHP database code. It targets **PDO** —
the standard, driver-agnostic API — because it forces the correct habits by default.
The rules also hold for query builders and ORMs (Doctrine, Eloquent), which wrap PDO.

## Why It Matters

The database is where PHP applications keep the truth, and it is the single most common
place they get breached. SQL injection has topped vulnerability lists for two decades
because string-built queries look correct in review and pass every functional test —
they only fail when an attacker supplies the input you never tried. Beyond security, a
misconfigured connection silently reveals credentials in a stack trace, a missing
transaction leaves half-written data, and an N+1 loop turns a fast page into a timeout
under real load. These faults are invisible in development and total in production.

## Core Principles

- **Never interpolate input into SQL.** Values go through bound parameters, always.
  String concatenation of any user-influenced value is a bug, not a style choice.
- **Let PDO throw.** Configure `PDO::ERRMODE_EXCEPTION` so a failed query raises a
  `PDOException` instead of returning `false` you might forget to check.
- **Fetch as associative arrays or objects, not both.** Set a default fetch mode once;
  do not rely on the numeric-plus-associative default that doubles memory.
- **Wrap multi-statement writes in a transaction.** Either all rows change or none do.
- **Bound parameters are for values, not identifiers.** Table and column names cannot be
  parameterized — validate them against an allow-list instead.

## Best Practices

- Create one PDO instance per request and inject it; do not open a connection per query.
  Pass `PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION`, `PDO::ATTR_DEFAULT_FETCH_MODE =>
  PDO::FETCH_ASSOC`, and `PDO::ATTR_EMULATE_PREPARES => false` in the constructor options.
- Keep credentials in environment variables, never in source. A leaked DSN with a
  password in a stack trace or committed config compromises the whole database.
- Use **native** prepared statements (`ATTR_EMULATE_PREPARES => false`) so parameters are
  sent to the server separately from the SQL text and typed correctly.
- Prefer named placeholders (`:email`) over positional (`?`) for queries with several
  parameters — they are order-independent and self-documenting.
- Set `charset=utf8mb4` in the DSN for MySQL so text and emoji store without corruption.
- For large result sets, iterate the `PDOStatement` directly (it is `Traversable`)
  instead of `fetchAll()`, which loads every row into memory at once.
- Catch `PDOException` at a boundary, log the real message server-side, and return a
  generic error to the client — the raw message can disclose schema and query structure.
- Solve N+1 by selecting related rows in one query with a `JOIN` or a single
  `WHERE id IN (...)`, not by querying inside a loop.

## Examples

**Good Example** — prepared statement, exceptions, transaction

```php
$pdo = new PDO($dsn, $user, $pass, [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION, // fail loud, not silent
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,       // one predictable shape
    PDO::ATTR_EMULATE_PREPARES   => false,                  // real server-side params
]);

function transfer(PDO $pdo, int $from, int $to, int $cents): void
{
    $pdo->beginTransaction();
    try {
        // Value is bound, never concatenated — injection is impossible here.
        $debit = $pdo->prepare('UPDATE accounts SET balance = balance - :c WHERE id = :id');
        $debit->execute(['c' => $cents, 'id' => $from]);

        $credit = $pdo->prepare('UPDATE accounts SET balance = balance + :c WHERE id = :id');
        $credit->execute(['c' => $cents, 'id' => $to]);

        $pdo->commit(); // both rows change together, or neither does
    } catch (PDOException $e) {
        $pdo->rollBack();
        throw $e; // let a boundary log it and return a generic message
    }
}
```

**Bad Example** — interpolated SQL, silent failure, no transaction

```php
$pdo = new PDO($dsn, $user, $pass); // default: errors are silent, returns false

function transfer(PDO $pdo, $from, $to, $cents): void
{
    // User-controlled values spliced straight into SQL → classic injection.
    $pdo->query("UPDATE accounts SET balance = balance - $cents WHERE id = $from");
    // If this second statement fails, the first already committed → money vanishes.
    $pdo->query("UPDATE accounts SET balance = balance + $cents WHERE id = $to");
}
```

## Common Mistakes

- Building SQL with `"... WHERE name = '$name'"` — the number-one PHP vulnerability.
- Passing a column or table name as a bound parameter (it will not work) and then
  concatenating it instead, reopening the injection hole.
- Leaving `ATTR_EMULATE_PREPARES` at its `true` default, which quietly re-enables string
  interpolation on the driver side and breaks parameter typing.
- Not setting `ERRMODE_EXCEPTION`, so a failed `execute()` returns `false` and the code
  proceeds as if it succeeded.
- Calling `fetchAll()` on an unbounded query and exhausting memory on large tables.
- Querying inside a `foreach` (N+1), turning one page load into hundreds of round-trips.
- Echoing `$e->getMessage()` to the browser, leaking table names and query shape.

## Production Tips

- Enforce connection, statement, and lock timeouts so a stuck query cannot pin a worker.
- Use a connection pool / persistent connections only with a clear per-request reset
  strategy; a leaked transaction on a reused connection corrupts the next request.
- Route reads to replicas where available, but keep read-after-write on the primary.
- Add indexes for every column used in `WHERE`, `JOIN`, and `ORDER BY`; verify with
  `EXPLAIN`. Log slow queries and treat them as bugs, not noise.

## AI Review Checklist

- Is every user-influenced value bound as a parameter, with zero SQL concatenation?
- Is `PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION` set on the connection?
- Is `PDO::ATTR_EMULATE_PREPARES => false` set so prepares are native?
- Are multi-statement writes wrapped in a transaction with rollback on failure?
- Are identifiers (table/column names) validated against an allow-list, not bound?
- Are credentials read from the environment rather than committed to source?
- Do errors log server-side and return a generic message instead of the raw exception?
- Are large result sets streamed instead of loaded with `fetchAll()`?

## Related

- `knowledge/php/13-security.md`
- `knowledge/php/09-exceptions.md`
- `knowledge/php/14-performance.md`
- `knowledge/php/08-error-handling.md`
