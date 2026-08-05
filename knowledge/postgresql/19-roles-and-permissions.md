---
id: postgresql/19-roles-and-permissions
topic: postgresql
slug: roles-and-permissions
title: "Roles And Permissions"
type: doc
order: 19
status: ready
tags: [postgresql, roles-and-permissions, USAGE, REVOKE, SUPERUSER, app_readwrite, app_readonly, USING]
related: [postgresql/18-security, postgresql/22-migrations, postgresql/06-transactions, postgresql/26-production, postgresql/25-best-practices]
when_to_use: "Read before creating database roles, granting privileges, wiring an application's login user, or reviewing who can read or write which tables."
---
# Roles And Permissions

## Purpose

This document defines how to model access *inside* a PostgreSQL database: roles (users and
groups), privileges (`GRANT`/`REVOKE`), ownership, schema access, default privileges, and
Row-Level Security. It is written so an agent can design a privilege model that is least-
privilege by construction, rather than granting everything and hoping nothing is abused.

Getting a connection to the server — network, TLS, `pg_hba.conf` — is covered in
[security](18-security.md). This document assumes the connection exists and asks: once
connected, what is this role allowed to do?

## Why It Matters

In PostgreSQL, a role's privileges are the last line of defense when application code has a
bug. If the app's login role can only `SELECT`/`INSERT`/`UPDATE`/`DELETE` on its own tables,
a SQL-injection flaw cannot `DROP TABLE`, read `pg_authid`, or `COPY` data to disk. If that
same role is a superuser — the depressingly common default — a single injected query owns
the whole cluster. Privileges are also easy to get subtly wrong: the object *owner* bypasses
most grants and RLS, and new tables silently start with no access until default privileges
are set. These traps produce either a broken app or an over-privileged one.

## Core Principles

- **Roles are both users and groups.** A role with `LOGIN` is a "user"; a role without it is
  a "group". Grant privileges to group roles and grant *membership* to login roles.
- **Least privilege, granted explicitly.** Start from nothing. `PUBLIC` gets `CONNECT` and
  schema `USAGE` by default — revoke what you do not intend.
- **Separate ownership from use.** A migration/owner role creates and alters objects; the
  application role only reads and writes rows. Owners bypass RLS and most privilege checks.
- **Grant on the schema, then set default privileges.** A grant applies only to objects that
  exist *now*; `ALTER DEFAULT PRIVILEGES` covers objects created *later*.
- **Prefer RLS for row-scoped access** (multi-tenant, per-user data) over trusting the app to
  always add a `WHERE tenant_id = …`. The database enforces it even when a query forgets.

## Best Practices

- Create a `NOLOGIN` group role per access level (e.g. `app_readwrite`, `app_readonly`,
  `app_migrator`), grant privileges to the group, and add login roles as members. Changing
  a person's access becomes one `GRANT`/`REVOKE` of membership.
- The application logs in as a role that owns *no* objects and holds only DML privileges.
  DDL (migrations) runs as a separate owner/migrator role.
- Immediately after `CREATE DATABASE`, run `REVOKE ALL ON SCHEMA public FROM PUBLIC;` and
  grant `USAGE` deliberately. Otherwise every role can create objects in `public`.
- Set default privileges so future tables inherit access:
  `ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT SELECT ON TABLES TO app_readonly;`
- Use `SET ROLE` or `SECURITY DEFINER` functions to expose narrow, audited operations
  instead of broad table grants when only a specific action is needed.
- Enable RLS on tenant tables (`ENABLE ROW LEVEL SECURITY`) and write a `USING` policy keyed
  on a session variable (`current_setting('app.tenant_id')`). Remember owners bypass RLS
  unless you also `FORCE ROW LEVEL SECURITY`.
- Never grant `SUPERUSER`, `CREATEROLE`, or `CREATEDB` to an application login. Audit
  membership with `\du` and `pg_roles` in review.

## Examples

**Good Example** — group roles, least privilege, default privileges

```sql
-- Group role: no login, holds the privileges. App role: login, inherits them.
CREATE ROLE app_readwrite NOLOGIN;
CREATE ROLE app_user LOGIN PASSWORD 'set-via-secrets-manager' IN ROLE app_readwrite;

-- Lock down the schema, then grant exactly what the app needs.
REVOKE ALL ON SCHEMA public FROM PUBLIC;              -- no accidental object creation
GRANT USAGE ON SCHEMA app TO app_readwrite;           -- can reference objects in app.*
GRANT SELECT, INSERT, UPDATE, DELETE
  ON ALL TABLES IN SCHEMA app TO app_readwrite;       -- DML only, no DDL, no DROP

-- Future tables created by the migrator inherit the same DML grant automatically.
ALTER DEFAULT PRIVILEGES FOR ROLE app_migrator IN SCHEMA app
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;
```

**Bad Example** — one superuser for everything

```sql
-- The application logs in as this. A SQL-injection bug can now DROP anything,
-- read every other database, and COPY data to the server's filesystem.
CREATE ROLE app_user LOGIN SUPERUSER PASSWORD 'hunter2';
-- No REVOKE on public → PUBLIC can still CREATE objects and CONNECT.
-- No default privileges → the next migration's tables need manual grants, so
-- someone will "fix" it by granting ALL to app_user. The blast radius only grows.
```

## Common Mistakes

- The application login is a superuser or owns the tables, so it bypasses RLS and privilege
  checks entirely.
- Granting on existing tables but forgetting `ALTER DEFAULT PRIVILEGES`, so the next
  migration's tables are inaccessible and get "fixed" with an over-broad grant.
- Leaving `PUBLIC`'s default `CREATE`/`USAGE` on `public`, letting any role add objects.
- Enabling RLS but not `FORCE ROW LEVEL SECURITY`, so the owner (often the migrator used in
  tests) silently sees all rows and the policy appears to "work" while being untested.
- Granting to individual login roles instead of a group, so access drifts and is unauditable.
- Assuming `REVOKE` cascades — it does not revoke privileges a role re-granted onward.

## Production Tips

- Keep role and privilege definitions in version-controlled migrations, not ad-hoc `psql`
  sessions, so the privilege model is reviewable and reproducible.
- Periodically snapshot `\du` and per-table grants (`information_schema.role_table_grants`)
  and diff against the intended model in CI.
- For RLS multi-tenancy, set the tenant on each connection with `SET LOCAL app.tenant_id`
  inside the transaction so it cannot leak across pooled connections.

## AI Review Checklist

- Does the application login role hold only DML privileges — never `SUPERUSER`/`CREATEROLE`?
- Are privileges granted to group (`NOLOGIN`) roles, with login roles as members?
- Was `PUBLIC` revoked from `schema public`, with `USAGE` granted deliberately?
- Are `ALTER DEFAULT PRIVILEGES` set so future tables inherit the intended access?
- Is the app role distinct from the object owner / migrator role?
- For row-scoped data, is RLS enabled *and* `FORCE`d, keyed on a per-transaction setting?
- Are all role/grant changes captured in versioned migrations?

## Related

- `knowledge/postgresql/18-security.md`
- `knowledge/postgresql/22-migrations.md`
- `knowledge/postgresql/06-transactions.md`
- `knowledge/postgresql/26-production.md`
- `knowledge/postgresql/25-best-practices.md`
