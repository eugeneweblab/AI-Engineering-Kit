---
id: prisma/22-multi-tenancy
topic: prisma
slug: multi-tenancy
title: "Prisma Multi Tenancy"
type: doc
order: 22
status: ready
tags: [prisma, multi-tenancy]
related: [prisma/21-security, prisma/14-extensions, prisma/23-soft-delete, prisma/06-client]
when_to_use: "Read before designing or reviewing any Prisma schema and queries where one database serves multiple customers."
---
# Prisma Multi Tenancy

## Purpose

This document defines how to isolate tenants (customers, organizations, workspaces) in a
Prisma application: the three isolation models, how to enforce the tenant boundary so it
cannot be forgotten, and how Postgres Row-Level Security backs up application code. The
central risk is one tenant reading or writing another tenant's data.

## Why It Matters

In a shared-table design, tenant isolation is *one `where` clause* away from failure.
Forget `where: { tenantId }` on a single query and that endpoint returns every tenant's
rows — a catastrophic, silent data breach that no functional test catches, because the
query works and returns data. The blast radius is every customer at once. Multi-tenancy
is therefore not a feature you sprinkle in; it is an invariant you must make impossible
to violate. The engineering question is never "did we filter by tenant here?" — it is
"can any query physically escape the tenant boundary?"

## Core Principles

- **Choose an isolation model deliberately.** Row-level (a `tenantId` column, one shared
  DB) is cheapest and scales to many tenants; schema-per-tenant and database-per-tenant
  give stronger isolation at higher operational cost. Most SaaS starts row-level.
- **Never rely on a hand-written `where` per query.** Manual filtering fails the day
  someone forgets it. Enforce the boundary structurally with a client extension and/or
  database RLS.
- **The tenant id comes from the authenticated session, never the request body.** A
  caller must not be able to name the tenant they are acting as.
- **Defense in depth.** Application-level filtering plus Postgres RLS: if code forgets,
  the database still refuses. Two independent layers, not one.
- **Every tenant-scoped table carries and indexes `tenantId`.** Composite unique
  constraints and indexes must include it, or you leak across tenants or collide.

## Best Practices

- For the row-level model, add `tenantId` to every tenant-owned model and make it the
  leading column of relevant indexes and composite uniques
  (`@@unique([tenantId, email])`, `@@index([tenantId, createdAt])`).
- Inject the filter automatically with a **Prisma Client extension** (`$extends` with a
  `query` component) that adds `where: { tenantId }` to reads and sets `tenantId` on
  writes — a request-scoped client, so no query can omit it.
- Derive the tenant id from the verified session/JWT and bind it per request; treat any
  `tenantId` in the payload as untrusted.
- Enable **Postgres RLS** on shared tables with a policy keyed on a session variable
  (`current_setting('app.tenant_id')`), and set that variable in a transaction before
  querying. Now even a raw query or a code bug cannot cross tenants.
- For schema- or database-per-tenant, manage a client (or connection) per tenant and a
  connection-pool budget; run migrations across all tenant schemas in lockstep.
- Add an integration test that asserts tenant A cannot read tenant B's rows through each
  read path — the one test that actually proves the invariant.

## Examples

**Good Example** — extension binds the tenant to every query

```ts
// Build a per-request client that CANNOT forget the tenant filter.
function forTenant(tenantId: string) {
  return prisma.$extends({
    query: {
      $allModels: {
        async $allOperations({ operation, args, query }) {
          // Filter by tenant on ops that take a `where`...
          if (
            [
              'findMany', 'findFirst', 'findUnique', 'findUniqueOrThrow',
              'findFirstOrThrow', 'count', 'aggregate', 'groupBy',
              'updateMany', 'deleteMany',
            ].includes(operation)
          ) {
            (args as any).where = { ...(args as any).where, tenantId };
          }
          // ...and stamp the tenant onto ops that write rows (no `where`).
          if (operation === 'create' || operation === 'createMany') {
            const data = (args as any).data;
            (args as any).data = Array.isArray(data)
              ? data.map((row: any) => ({ ...row, tenantId }))
              : { ...data, tenantId };
          }
          if (operation === 'upsert') {
            (args as any).where = { ...(args as any).where, tenantId };
            (args as any).create = { ...(args as any).create, tenantId };
          }
          return query(args);
        },
      },
    },
  });
}

// tenantId comes from the verified session, never from the client-supplied body.
const db = forTenant(session.tenantId);
const invoices = await db.invoice.findMany(); // scoped automatically, no manual where
```

**Bad Example** — trusting input and hand-filtering

```ts
async function listInvoices(req: Request) {
  // tenantId taken from the request: caller can pass any tenant's id and read it.
  const tenantId = req.query.tenantId as string;
  return prisma.invoice.findMany({ where: { tenantId } });
}

async function listUsers() {
  // The where clause is simply missing — returns EVERY tenant's users.
  // Compiles, passes the happy-path test, ships a cross-tenant breach.
  return prisma.user.findMany();
}
```

## Common Mistakes

- Reading `tenantId` from the request body/query instead of the authenticated session.
- Relying on developers to add `where: { tenantId }` by hand on every query.
- Composite uniques/indexes that omit `tenantId`, causing cross-tenant collisions or scans.
- Enabling application filtering but not RLS, so one forgotten filter is a full breach.
- A shared long-lived client with no per-request tenant binding, inviting leaks under load.
- Bypassing the scoped client with a raw query that has no tenant predicate.

## Production Tips

- Turn on RLS in staging and production and verify it with a test that queries as the
  app role without setting the tenant variable — it should return zero rows.
- Watch connection-pool usage carefully in database-per-tenant designs; a client per
  tenant multiplies open connections.
- Log the resolved tenant id on every request for audit, and alert on any query path that
  runs without a bound tenant context.

## AI Review Checklist

- Is the tenant id derived from the authenticated session, never from request input?
- Is tenant filtering enforced structurally (client extension and/or RLS), not by
  per-query hand-written `where`?
- Does every tenant-owned model include `tenantId` in its uniques and indexes?
- Is Postgres RLS enabled as a second layer on shared tables?
- Is there a test proving tenant A cannot read tenant B's data on each read path?
- Do raw queries also carry a tenant predicate or run under RLS?

## Related

- `knowledge/prisma/21-security.md`
- `knowledge/prisma/14-extensions.md`
- `knowledge/prisma/23-soft-delete.md`
- `knowledge/prisma/06-client.md`
