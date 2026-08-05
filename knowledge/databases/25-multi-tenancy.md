---
id: databases/25-multi-tenancy
topic: databases
slug: multi-tenancy
title: "Database Multi Tenancy"
type: doc
order: 25
status: ready
tags: [databases, multi-tenancy, tenant_id, invoices, current_setting, USING]
related: [databases/19-security, databases/15-sharding, databases/06-schema-design, databases/24-soft-delete, databases/23-data-integrity]
when_to_use: "Read before designing how one database serves multiple customers/organizations without leaking data between them."
---
# Database Multi Tenancy

## Purpose

This document defines how to store data for multiple isolated tenants (customers,
organizations, workspaces) in one system without one tenant ever seeing another's data.
It covers the three isolation models — shared table, schema-per-tenant, database-per-tenant —
their trade-offs, and how to make tenant isolation a property the database enforces rather
than a rule the application hopes it followed.

The central risk of multi-tenancy is *cross-tenant data leakage*: a missing `WHERE tenant_id`
returns another customer's records. This is simultaneously a correctness bug and a security
breach, so the pattern is chosen for how strongly it prevents that, not just how cheaply it scales.

## Why It Matters

A cross-tenant leak is one of the worst failures a SaaS product can have: it exposes one
customer's data to another, is often reportable as a breach, and destroys trust instantly.
Unlike a crash, it is silent — the query succeeds and returns rows, just the wrong ones. The
model you pick determines whether that failure is *possible*. Application-level filtering
means every single query is a potential leak; database-enforced isolation (row-level security,
separate schemas, separate databases) makes the leak structurally impossible or contained.
The choice also drives cost, noisy-neighbor performance, per-tenant backup/restore, and how
hard it is to run migrations across thousands of tenants.

## Core Principles

- **Isolation must be enforced by the database, not remembered by the developer.** A rule that
  lives only in application code fails the day one query forgets it.
- **Every tenant-scoped row carries its tenant key, and every access is scoped by it.** No query
  touches a tenant table without a tenant predicate.
- **Pick the model by required isolation strength, then by scale.** Strong isolation
  (database-per-tenant) costs more and scales to fewer tenants; shared-table scales to many but
  demands the most discipline.
- **The tenant identity comes from the trusted session, never from client input.** A
  request-supplied `tenant_id` is an authorization decision an attacker can forge.
- **Design for the whole lifecycle:** onboarding, per-tenant backup/restore, export, and
  offboarding/deletion must all be tenant-scoped from day one.

## Best Practices

- Default to **shared table with a `tenant_id` column plus Postgres Row-Level Security (RLS)**
  for most SaaS: it scales to many tenants and RLS makes the filter mandatory at the engine level.
- Set the tenant context per connection/transaction (`SET LOCAL app.tenant_id = ...`) from the
  authenticated session, and write RLS policies against that setting. Never interpolate a
  client-provided tenant id into SQL.
- Put `tenant_id` **first** in composite primary keys and indexes
  (`PRIMARY KEY (tenant_id, id)`), so lookups and locality are tenant-aligned.
- Use **schema-per-tenant** when tenants need customizable schemas or moderate isolation with
  hundreds (not millions) of tenants; **database-per-tenant** for strict isolation, per-tenant
  encryption keys, or per-tenant backup/restore SLAs.
- Include `tenant_id` in every foreign key relationship so a child can never reference a parent
  in another tenant. See [data integrity](23-data-integrity.md).
- Plan migrations for the model: shared-table migrates once; schema/database-per-tenant must
  fan out across every tenant with rollback per tenant. See [sharding](15-sharding.md).

## Examples

**Good Example** — shared table with RLS enforcing isolation in the engine

```sql
CREATE TABLE invoices (
  tenant_id BIGINT NOT NULL,
  id        BIGINT NOT NULL,
  amount    NUMERIC NOT NULL,
  PRIMARY KEY (tenant_id, id)        -- tenant-first key: locality + no cross-tenant collisions
);

ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- The database itself refuses to return rows outside the current tenant.
CREATE POLICY tenant_isolation ON invoices
  USING (tenant_id = current_setting('app.tenant_id')::BIGINT);

-- Per request, set from the AUTHENTICATED session, scoped to the transaction:
SET LOCAL app.tenant_id = '42';
SELECT * FROM invoices;             -- returns only tenant 42, even if the query "forgot" WHERE
```

**Bad Example** — isolation left to application discipline and client input

```sql
-- No RLS, no tenant_id in the key. Isolation depends on every query being perfect.
CREATE TABLE invoices (id BIGINT PRIMARY KEY, tenant_id BIGINT, amount NUMERIC);
```
```ts
// tenantId comes from the request body — an attacker sets it to someone else's tenant.
const rows = await db.query(
  "SELECT * FROM invoices WHERE tenant_id = $1", [req.body.tenantId]
);
// And the reporting query over here simply forgot the filter → full cross-tenant leak.
```

## Common Mistakes

- Trusting a `tenant_id` from the request body/query string instead of the authenticated session.
- Relying on application `WHERE tenant_id` filters with no database-level backstop (RLS/schema/db).
- Leaving `tenant_id` out of composite keys/indexes, hurting locality and allowing id collisions.
- Forgetting tenant scoping in aggregate/reporting queries, background jobs, or admin tools.
- Shared sequences or caches keyed without tenant, leaking counts or values across tenants.
- Choosing database-per-tenant for a product that will have 100k tenants (operationally unmanageable).
- No per-tenant export/delete path, making offboarding and "return my data" requests impossible.

## Production Tips

- Test isolation adversarially in CI: run a query as tenant A and assert zero tenant-B rows come
  back, including through views, joins, and reports. See [testing](27-testing.md).
- Connection poolers reuse connections — always `SET LOCAL` inside the transaction so tenant
  context cannot bleed between pooled requests.
- Monitor per-tenant query cost to catch a noisy neighbor before it degrades everyone.
- Keep a tenant-scoped [audit trail](26-auditing.md) so access can be reconstructed per customer.

## AI Review Checklist

- Is tenant isolation enforced by the database (RLS, separate schema, or separate database),
  not only by application-side filters?
- Does `tenant_id` come exclusively from the authenticated session, never from client input?
- Is `tenant_id` the leading column of primary keys and hot-path indexes?
- Do all foreign keys keep child and parent in the same tenant?
- Are reporting queries, background jobs, and admin tools tenant-scoped too?
- With a connection pooler, is tenant context set with `SET LOCAL` inside each transaction?
- Are there tenant-scoped backup/restore, export, and deletion paths?

## Related

- `knowledge/databases/19-security.md`
- `knowledge/databases/15-sharding.md`
- `knowledge/databases/06-schema-design.md`
- `knowledge/databases/24-soft-delete.md`
- `knowledge/databases/23-data-integrity.md`
