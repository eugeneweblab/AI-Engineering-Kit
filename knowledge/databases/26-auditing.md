---
id: databases/26-auditing
topic: databases
slug: auditing
title: "Auditing"
type: doc
order: 26
status: ready
tags: [databases, auditing]
related: [databases/24-soft-delete, databases/09-transactions, databases/19-security, databases/25-multi-tenancy, databases/23-data-integrity]
when_to_use: "Read before adding change history, an audit log, or 'who changed this and when' tracking to a database."
---
# Auditing

## Purpose

This document defines how to record *who* changed *what*, *when*, and *from what to what* in a
database, so that data changes can be reconstructed, attributed, and defended in a compliance
or incident review. It covers the difference between an operational change-history table and a
security audit log, where to capture changes (application vs. database triggers), and how to
make the record itself trustworthy — append-only and tamper-evident.

An audit trail is only useful if it is complete and unforgeable. A log that the same code path
can silently skip, or that an admin can quietly edit, provides false assurance, which is worse
than no audit at all.

## Why It Matters

Auditing is what lets you answer "who deleted this customer?", "was this record changed before
the breach?", and "prove this value was correct on that date". Regulations (SOX, HIPAA, GDPR,
PCI) require it; incident response depends on it; and internal trust erodes fast when no one can
explain how data got into a bad state. The failure mode is subtle: the audit table exists and
looks populated, but a bulk update bypassed it, or the timestamps are the app server's clock and
skewed, or someone with table access edited history. Each gap is invisible until the one moment
you need the record and it is wrong. Audit code is therefore held to the same "assume it will be
scrutinized" bar as [security](19-security.md) code.

## Core Principles

- **Audit records are append-only.** Never `UPDATE` or `DELETE` an audit row in normal operation.
  History that can be rewritten is not evidence.
- **Capture the actor, the action, the time, and the before/after — every time.** A row that says
  "something changed" without who and what is not an audit trail.
- **Enforce capture where it cannot be bypassed.** If any write path can skip the audit, it will.
  Database triggers or CDC catch writes that application code misses.
- **Use a trusted, single-source timestamp.** Prefer the database clock (`now()`), so entries are
  comparable and not subject to per-server drift.
- **Separate operational history from security audit.** Change history (versioning a business
  record) and a security/access log (who read/exported sensitive data) have different retention,
  access, and integrity needs.

## Best Practices

- Record, per change: `table_name`, `row_id`, `action` (INSERT/UPDATE/DELETE), `changed_by`,
  `changed_at DEFAULT now()`, and the `old`/`new` values (JSONB is a clean, schema-flexible store).
- Capture changes with **database triggers or CDC** (e.g., logical replication / the outbox
  pattern) for a complete trail, and/or at a **central application layer** (ORM hook, repository
  base class) for rich context like request id and business intent. Triggers guarantee coverage;
  the app layer adds meaning — many systems use both.
- Pass the acting user into the database session (`SET LOCAL app.actor_id = ...`) so triggers can
  attribute the change; do not rely on the DB login user, which is usually a shared service account.
- Make the audit table **write-only to the application**: grant `INSERT` but not `UPDATE`/`DELETE`,
  and keep it out of reach of the roles that can edit business data.
- Wrap the business change and its audit write in the **same transaction**, so you never keep a
  change without its record or vice versa. See [transactions](09-transactions.md).
- Set retention and, for tamper-evidence on high-value logs, hash-chain rows or ship them to a
  write-once store (append-only object storage, a dedicated audit service).

## Examples

**Good Example** — trigger-based, append-only, before/after captured atomically

```sql
CREATE TABLE audit_log (
  id         BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  table_name TEXT        NOT NULL,
  row_id     BIGINT      NOT NULL,
  action     TEXT        NOT NULL,        -- INSERT | UPDATE | DELETE
  changed_by BIGINT      NOT NULL,
  changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),  -- trusted DB clock, comparable across servers
  old_data   JSONB,
  new_data   JSONB
);

CREATE FUNCTION audit_accounts() RETURNS trigger AS $$
BEGIN
  INSERT INTO audit_log(table_name, row_id, action, changed_by, old_data, new_data)
  VALUES ('accounts', COALESCE(NEW.id, OLD.id), TG_OP,
          current_setting('app.actor_id')::BIGINT,   -- actor from the app session, not DB login
          to_jsonb(OLD), to_jsonb(NEW));             -- full before/after snapshot
  RETURN COALESCE(NEW, OLD);
END; $$ LANGUAGE plpgsql;

-- Fires for EVERY write, including bulk updates the application layer might miss.
CREATE TRIGGER accounts_audit
  AFTER INSERT OR UPDATE OR DELETE ON accounts
  FOR EACH ROW EXECUTE FUNCTION audit_accounts();
```

**Bad Example** — best-effort app logging, mutable, wrong clock, no old value

```ts
async function updateAccount(id: number, patch: Patch) {
  await db.update("accounts", id, patch);
  // Separate, non-transactional write: a crash here loses the audit but keeps the change.
  await db.insert("audit_log", {
    row_id: id,
    changed_at: new Date(),   // app server clock — drifts, not comparable across instances
    new_data: patch,          // no OLD snapshot, so you cannot see what it changed FROM
  });
  // Bulk/admin/ETL writes to `accounts` skip this function entirely → silent gaps.
}
// audit_log is a normal table the app can UPDATE/DELETE → history is rewritable.
```

## Common Mistakes

- Logging in the application only, so bulk updates, migrations, and admin tools bypass the trail.
- Storing only the new value, making it impossible to see what a field changed *from*.
- Using the app server's clock instead of the database clock, producing unorderable timestamps.
- Attributing changes to the shared DB service account instead of the real end user.
- Leaving the audit table editable (or truncatable) by roles that also edit business data.
- Writing the change and the audit entry in separate transactions, so they can diverge.
- Logging sensitive values (passwords, full card numbers) into the audit table in clear text.
- Never setting retention, so the audit table grows unbounded and eventually can't be queried.

## Production Tips

- Keep audit data on a retention schedule aligned to the governing regulation; archive to
  write-once storage before purge. Coordinate with [backup and recovery](18-backup-and-recovery.md).
- In multi-tenant systems, stamp `tenant_id` on every audit row so access can be reviewed
  per customer. See [multi-tenancy](25-multi-tenancy.md).
- For the highest-value logs, hash-chain each row (`hash = H(prev_hash || row)`) so any later
  edit or deletion is detectable.
- Alert on audit-write failures loudly; a silently failing audit trail is a compliance gap.

## AI Review Checklist

- Does every audit entry capture actor, action, timestamp, and before/after values?
- Is the timestamp the database clock (`now()`), not an application-supplied time?
- Is capture enforced where it cannot be bypassed (triggers/CDC), covering bulk and admin writes?
- Is the actor the real end user (from session context), not the shared DB login?
- Is the audit table append-only — no `UPDATE`/`DELETE` grants to application roles?
- Are the business change and its audit record written in the same transaction?
- Is retention defined, and are sensitive values excluded or masked in the log?

## Related

- `knowledge/databases/24-soft-delete.md`
- `knowledge/databases/09-transactions.md`
- `knowledge/databases/19-security.md`
- `knowledge/databases/25-multi-tenancy.md`
- `knowledge/databases/23-data-integrity.md`
