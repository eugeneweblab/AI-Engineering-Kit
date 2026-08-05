---
id: databases/19-security
topic: databases
slug: security
title: "Database Security"
type: doc
order: 19
status: ready
tags: [databases, security]
related: [databases/18-backup-and-recovery, databases/26-auditing, databases/25-multi-tenancy, databases/17-migrations, databases/08-query-optimization]
when_to_use: "Read before granting database access, wiring credentials, storing sensitive columns, or reviewing any query that touches user input."
---
# Database Security

## Purpose

This document defines how to keep a database from becoming the source of a breach:
authentication to the engine, least-privilege access, encryption, injection defense, and
protecting data at rest and in backups. It is written so an agent can provision access or
review data-layer code without opening a hole that exposes every row at once.

The database is where the crown jewels live. Application bugs leak a request; a database
misconfiguration leaks the entire dataset. This is the topic's highest-stakes surface.

## Why It Matters

A database breach is rarely a single stolen record — it is the whole table. One overly
broad grant, one string-concatenated query, one unencrypted backup, and an attacker walks
away with every customer's data. These failures are silent: the app behaves normally while
credentials are being exfiltrated, and you learn about it from a third party months later.
Regulators, customers, and courts treat a data breach as an unrecoverable failure of
trust. Because the blast radius is total, database security is held to a higher standard
than ordinary code — assume every connection string, query input, and backup file is a
target.

## Core Principles

- **Least privilege, always.** The application role should hold only the rights it uses —
  `SELECT/INSERT/UPDATE/DELETE` on named tables, never `SUPERUSER`, `DROP`, or ownership.
  A compromised app credential must not be able to destroy or exfiltrate the schema.
- **Never build queries by string concatenation.** Use parameterized queries / prepared
  statements so user input can never change the query's structure. This closes SQL
  injection completely; escaping does not.
- **Encrypt in transit and at rest.** Require TLS on every connection; enable
  transparent data encryption or disk encryption and encrypt backups.
- **Secrets live in a secret manager, never in code or images.** Rotate credentials; scope
  them per service; never commit a connection string.
- **Defense in depth.** Network isolation, engine auth, row/column controls, and app-level
  checks are layers. Assume any one of them can fail and design so the next still holds.

## Best Practices

- Give each service its **own database user** with a scoped grant; separate the migration
  role (DDL) from the runtime role (DML) so runtime cannot alter the schema.
- Put the database on a **private network**; never expose it to the public internet. Reach
  it through a bastion, VPC peering, or a proxy — not `0.0.0.0/0`.
- Enforce **TLS** and reject non-TLS connections at the server (`ssl = on`,
  `require_secure_transport`). Verify the server certificate from the client.
- Encrypt sensitive columns (PII, tokens, secrets) at the application layer when the DB's
  at-rest encryption is not enough — the DBA should not be able to read them in the clear.
- Use **Row-Level Security** (RLS) or an equivalent tenant filter for multi-tenant data so
  a query bug cannot cross tenant boundaries. See [multi-tenancy](25-multi-tenancy.md).
- **Mask or exclude** sensitive data in non-production copies; never restore a raw prod
  backup into a dev environment.
- Keep an **audit trail** of privileged access and schema changes. See [auditing](26-auditing.md).
- **Patch** the engine promptly; database CVEs are actively exploited.

## Examples

**Good Example** — parameterized query, scoped role, TLS enforced

```sql
-- Provision a runtime role with exactly the rights the app uses. No DDL, no superuser.
CREATE ROLE app_runtime LOGIN PASSWORD :'from_secret_manager';
GRANT SELECT, INSERT, UPDATE, DELETE ON orders, customers TO app_runtime;
-- Migrations run as a *different* role; runtime cannot DROP or ALTER.
```

```ts
// Parameterized query: user input is data, never code. Injection is impossible here.
const rows = await db.query(
  "SELECT id, email FROM customers WHERE tenant_id = $1 AND email = $2",
  [tenantId, email], // driver binds params; the query text is fixed
);
// Connection requires TLS and verifies the server cert:
//   { ssl: { rejectUnauthorized: true, ca: fs.readFileSync("rds-ca.pem") } }
```

**Bad Example** — string-built query, god-mode credential

```ts
// The app connects as the database owner/superuser — a leak = total compromise.
const db = new Client({ user: "postgres", ssl: false }); // plaintext on the wire, too

// User input is concatenated straight into SQL. Classic injection:
//   email = "x'; DROP TABLE customers; --"
const rows = await db.query(
  `SELECT * FROM customers WHERE email = '${email}'`, // attacker controls the query
);
// SELECT * also over-fetches columns (password hashes, tokens) the caller never needs.
```

## Common Mistakes

- Concatenating user input into SQL instead of using bound parameters.
- Running the application as `SUPERUSER`/owner, so one leaked credential owns everything.
- Exposing the database port to the public internet, or disabling TLS "to make it work".
- Hardcoding connection strings in source, images, or CI logs instead of a secret manager.
- Storing PII, tokens, or secrets in plaintext columns.
- Copying production data into dev/staging without masking.
- Ignoring engine security patches because upgrades are inconvenient.
- Assuming an ORM makes you injection-proof — raw fragments and `LIKE` builders still bite.

## Production Tips

- Alert on privilege escalation, new roles, failed logins, and connections from unexpected
  networks — these are the early signals of a compromise.
- Rotate database credentials on a schedule and immediately after any suspected exposure;
  short-lived, dynamically issued credentials (e.g. Vault) beat static passwords.
- Run a periodic grant audit: dump `information_schema` privileges and diff against the
  intended least-privilege baseline. Drift accumulates silently.

## AI Review Checklist

- Is every query that touches user input parameterized (no string concatenation)?
- Does the application role hold least privilege — no superuser, no unused DDL rights?
- Is TLS required and the server certificate verified on every connection?
- Are credentials sourced from a secret manager and rotated, not committed to code?
- Are data at rest and backups encrypted, and is sensitive PII protected column-level?
- Is the database on a private network, not reachable from the public internet?
- For multi-tenant data, is there an enforced tenant filter (RLS) a query bug cannot bypass?

## Related

- `knowledge/databases/18-backup-and-recovery.md`
- `knowledge/databases/26-auditing.md`
- `knowledge/databases/25-multi-tenancy.md`
- `knowledge/databases/17-migrations.md`
- `knowledge/databases/08-query-optimization.md`
