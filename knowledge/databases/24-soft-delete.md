---
id: databases/24-soft-delete
topic: databases
slug: soft-delete
title: "Database Soft Delete"
type: doc
order: 24
status: ready
tags: [databases, soft-delete, deleted_at, deleted, requirement, don]
related: [databases/23-data-integrity, databases/07-indexing, databases/26-auditing, databases/19-security, databases/08-query-optimization]
when_to_use: "Read before adding a deleted_at flag or any 'don't really delete it' requirement to a table."
---
# Database Soft Delete

## Purpose

This document defines how to mark rows as deleted without physically removing them, so
data can be recovered, audited, or retained for compliance. It covers the schema pattern,
how to keep queries and constraints correct once rows can be "gone but present", and when
*not* to soft-delete at all.

Soft delete trades a `DELETE` for an `UPDATE` that sets a marker column. That single change
ripples through every query, index, unique constraint, and foreign key on the table. Getting
it right means treating "deleted" as a first-class state, not an afterthought.

## Why It Matters

A hard `DELETE` is irreversible and takes referenced rows or history with it. Soft delete
exists because businesses need to undo mistakes, honor "right to be forgotten" workflows on
a schedule, and reconstruct what a record looked like at a point in time. But the pattern is
dangerous when bolted on: the moment one query forgets to filter out deleted rows, deleted
data leaks into the UI, into reports, into other tenants. Unique constraints stop working
("email already taken" by a row the user can no longer see). Foreign keys point at dead rows.
The failure is silent and data-shaped, which makes it expensive to find and worse to explain.

## Core Principles

- **Soft delete is a state, not a delete.** A row with `deleted_at` set still exists,
  still occupies unique constraints, and still satisfies foreign keys. Design for that.
- **Filter by default, opt in to include deleted.** Application code and views must exclude
  deleted rows unless a caller explicitly asks for them. The default must be safe.
- **Prefer a timestamp over a boolean.** `deleted_at TIMESTAMPTZ NULL` records *when* and
  doubles as the flag (`deleted_at IS NULL` = live). A bare `is_deleted` boolean throws away
  the audit signal for no gain.
- **Not everything should be soft-deleted.** Join tables, ephemeral rows, and high-churn data
  are usually better hard-deleted. Reserve soft delete for records with business meaning.
- **Have a purge path.** Soft-deleted rows accumulate forever unless a retention job hard-deletes
  them. Decide the retention window up front, or the table becomes unbounded.

## Best Practices

- Use `deleted_at TIMESTAMPTZ NULL` (nullable, no default). `NULL` means live; a timestamp
  means deleted at that instant. Add `deleted_by` if you need attribution.
- Add a **partial index** on the live set so hot queries stay fast:
  `CREATE INDEX ON orders (customer_id) WHERE deleted_at IS NULL`. It excludes dead rows
  from the index entirely, keeping it small.
- Make unique constraints **partial** so deleted rows don't block reuse of a value:
  `CREATE UNIQUE INDEX ON users (email) WHERE deleted_at IS NULL`.
- Enforce the filter centrally — a base repository, ORM global scope, or a view — so no
  individual query author can forget it. Central enforcement beats convention.
- Cascade soft deletes explicitly. A soft-deleted parent does not automatically hide its
  children; decide per relationship whether children are hidden, orphaned, or blocked.
- Run a scheduled purge job that hard-deletes rows past the retention window, inside a
  transaction, in batches to avoid long locks. See [migrations](17-migrations.md).

## Examples

**Good Example** — timestamp flag, partial unique index, live-only view

```sql
CREATE TABLE users (
  id         BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  email      CITEXT NOT NULL,
  deleted_at TIMESTAMPTZ,            -- NULL = live, timestamp = when soft-deleted
  deleted_by BIGINT REFERENCES users(id)
);

-- Uniqueness applies only to LIVE rows, so a deleted user frees up their email.
CREATE UNIQUE INDEX users_email_live ON users (email) WHERE deleted_at IS NULL;

-- A view is the safe default surface: callers cannot "forget" the filter.
CREATE VIEW active_users AS SELECT * FROM users WHERE deleted_at IS NULL;

-- Soft delete = UPDATE, capturing who and when for audit.
UPDATE users SET deleted_at = now(), deleted_by = :actor WHERE id = :id;
```

**Bad Example** — boolean flag, global unique constraint, ad-hoc filtering

```sql
CREATE TABLE users (
  id         BIGINT PRIMARY KEY,
  email      TEXT NOT NULL UNIQUE,   -- BUG: a soft-deleted row keeps holding the email
  is_deleted BOOLEAN DEFAULT false   -- loses WHEN it was deleted; no audit signal
);

-- Every query must remember this by hand; the one that forgets leaks deleted data.
SELECT * FROM users WHERE is_deleted = false AND email = :email;

-- "Delete" that a new signup with the same email now blocks forever.
UPDATE users SET is_deleted = true WHERE id = :id;
```

## Common Mistakes

- Forgetting the filter in one query so deleted rows leak into results, exports, or counts.
- Keeping a **global** unique constraint, so deleted rows block re-registering the same value.
- Using a plain B-tree index instead of a partial one, bloating the index with dead rows.
- Never purging, letting soft-deleted rows grow without bound and slow every scan.
- Foreign keys pointing at soft-deleted parents, so the app shows children of an invisible row.
- Soft-deleting join/link tables where a hard delete is simpler and has no recovery value.
- Treating soft delete as GDPR "erasure" — it is not; erasure requires actually removing PII.

## Production Tips

- Monitor the live-vs-deleted ratio per table; a table that is mostly dead rows needs a purge
  cadence review. See [monitoring](21-monitoring.md).
- When purging, log the operation to your [audit trail](26-auditing.md) so a hard delete is
  never truly silent.
- For compliance erasure, combine soft delete (immediate hide) with a purge/anonymize job
  (actual removal) so the UX is instant but the legal obligation is still met.

## AI Review Checklist

- Is `deleted_at` a nullable timestamp (not a boolean), so deletion time is preserved?
- Are unique constraints and hot-path indexes **partial** (`WHERE deleted_at IS NULL`)?
- Is the live-only filter enforced centrally (view, base repository, ORM scope), not per query?
- Does any query, report, or export path accidentally include deleted rows?
- Is there a retention window and a scheduled purge job for old soft-deleted rows?
- Are foreign-key relationships to potentially-deleted parents handled deliberately?
- For PII, is there a real erasure path, since soft delete alone does not satisfy GDPR?

## Related

- `knowledge/databases/23-data-integrity.md`
- `knowledge/databases/07-indexing.md`
- `knowledge/databases/26-auditing.md`
- `knowledge/databases/19-security.md`
- `knowledge/databases/08-query-optimization.md`
