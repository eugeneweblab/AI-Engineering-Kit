---
id: databases/99-ai-review-checklist
topic: databases
slug: ai-review-checklist
title: "Database AI Review Checklist"
type: doc
order: 99
status: ready
tags: [databases, ai-review-checklist]
related: [databases/09-transactions, databases/08-query-optimization, databases/17-migrations, databases/19-security, databases/23-data-integrity]
when_to_use: "Read when reviewing any diff that adds or changes SQL, schema, migrations, or data-access code."
---
# Database AI Review Checklist

## Purpose

A focused checklist for an AI agent reviewing a database-related diff. It targets the
defects that are cheap to catch in review and expensive to catch in production: lost
writes, injection, unindexed queries, and unsafe migrations. Each item is a concrete
yes/no to verify against the code in front of you, not a topic to muse on.

## Why It Matters

Database bugs rarely announce themselves. A missing transaction, an `N+1` loop, or a
migration that locks a table passes tests, passes a casual read, and then corrupts data or
takes the site down under load. A disciplined review pass catches these while they are
still a comment on a pull request. Review the diff against the invariants below before
approving.

## Correctness and Transactions

- [ ] Are all writes that must succeed or fail together inside one transaction?
- [ ] Is the transaction free of network/user I/O and kept short, so it does not hold locks?
- [ ] Is the isolation level correct for any read-modify-write (does it race under
  concurrency, e.g. two requests decrementing the same balance)?
- [ ] Are retriable operations idempotent (unique key or upsert), so a retry cannot double-apply?
- [ ] Are rows touched in a consistent order to avoid deadlocks?

## Integrity

- [ ] Are new invariants enforced by database constraints, not only application code?
- [ ] Are column types correct and precise (`numeric` for money, `timestamptz` for time,
  right integer width)?
- [ ] Do foreign keys have explicit `ON DELETE`/`ON UPDATE` behavior rather than a default
  no one chose?
- [ ] Does a delete that should cascade actually cascade — or correctly restrict — instead
  of orphaning rows?

## Queries and Performance

- [ ] Is every query parameterized (no string concatenation of user input)?
- [ ] Does each new query on a large table have a supporting index for its filter/join/sort?
- [ ] Is there an `N+1` pattern — a query inside a loop that should be a join or a batch?
- [ ] Does the query select only the columns needed, avoiding `SELECT *` on wide tables?
- [ ] Is pagination keyset-based rather than deep `OFFSET` on large result sets?

## Migrations

- [ ] Is the schema change a reviewed migration with a rollback path?
- [ ] Is it backward-compatible with the currently deployed app (expand/contract)?
- [ ] Does index creation or a table rewrite use the online/concurrent path to avoid locking?
- [ ] Does adding a `NOT NULL` column to a big table backfill safely instead of blocking writes?

## Security and Data Handling

- [ ] Does the code use a least-privilege connection, not an admin role?
- [ ] Are secrets pulled from a secrets manager rather than hard-coded?
- [ ] Is sensitive data kept out of logs and error messages?
- [ ] Are deletes/updates scoped by a `WHERE` clause that cannot accidentally hit all rows?

## Red Flags — stop and require justification

- [ ] A raw SQL string interpolating a variable.
- [ ] A loop issuing one query per iteration.
- [ ] A multi-write handler with no `BEGIN`/`COMMIT`.
- [ ] A migration that renames/drops a column the running app still reads.
- [ ] `DELETE`/`UPDATE` with no `WHERE`, or a `WHERE` that could match everything.

## Related

- `knowledge/databases/09-transactions.md`
- `knowledge/databases/08-query-optimization.md`
- `knowledge/databases/17-migrations.md`
- `knowledge/databases/19-security.md`
- `knowledge/databases/23-data-integrity.md`
