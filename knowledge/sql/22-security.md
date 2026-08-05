---
id: sql/22-security
topic: sql
slug: security
title: "SQL Security"
type: doc
order: 22
status: ready
tags: [sql, security, execute, root, connect]
related: [sql/20-stored-procedures, sql/18-views, sql/13-dml, sql/14-transactions, sql/26-best-practices]
when_to_use: "Read before writing any query that includes user input, granting database privileges, or exposing tables to an application role."
---
# SQL Security

## Purpose

This document defines how to keep SQL and the database itself secure: preventing
injection, granting least privilege, protecting sensitive data, and limiting the
blast radius of a compromised application. It is written so an agent can build a
data-access layer that an attacker cannot turn into a data breach.

The database is where the valuable data lives, which makes it the ultimate target.
Every other security control exists to keep an attacker away from this layer, so
this layer must assume they will arrive anyway.

## Why It Matters

SQL injection has topped vulnerability lists for two decades because it is easy to
introduce and catastrophic when exploited: a single unparameterized query can dump
or destroy an entire database. Beyond injection, an application that connects as a
superuser turns a minor bug into total compromise — the difference between "an
attacker read one table" and "an attacker owned the server." Database security is
about assuming the application layer will be breached and ensuring that breach
buys the attacker as little as possible.

## Core Principles

- **Parameterize every query; never build SQL by string concatenation.** The
  parameter boundary is what separates code from data. Cross it and injection
  becomes possible. This is non-negotiable.
- **Least privilege for the application role.** The app connects with a role that
  can do exactly what the app needs and nothing more — never as superuser/`root`.
- **Data is a liability; minimize what you store.** Do not store secrets or PII you
  do not need. Encrypt what you must store. Never store plaintext passwords (see
  the security topic's authentication guidance).
- **Defense in depth.** Parameterization, least privilege, row/column controls, and
  network isolation are layers; assume any one can fail and the others still hold.
- **Errors must not leak internals.** A raw database error returned to a client can
  reveal schema, queries, and data. Return generic messages; log details server-side.

## Best Practices

- Use parameterized queries / prepared statements for *all* user input. For dynamic
  identifiers (table/column names) that cannot be parameters, use an allowlist or
  the engine's identifier-quoting (`format('%I', name)`), never raw concatenation.
- Create a dedicated application role with only the needed `SELECT/INSERT/UPDATE/
  DELETE` grants on the needed tables; revoke `CREATE`, `DROP`, and access to
  system catalogs it does not need.
- Use [views](18-views.md) to expose only permitted columns and rows, and grant on
  the view instead of the base table for reporting/read-only consumers.
- Use Row-Level Security (RLS) for multi-tenant data so a query can only ever see
  its own tenant's rows, enforced by the database rather than by hope in the app.
- Store connection credentials in a secrets manager, not in code or config files;
  rotate them and use short-lived credentials where the platform supports it.
- Encrypt in transit (TLS on the connection) and at rest; encrypt or tokenize
  especially sensitive columns beyond full-disk encryption.
- Audit and log access to sensitive tables, but never log the sensitive values
  themselves or the query parameters that contain them.

## Examples

**Good Example** — parameterized query, least-privilege role

```sql
-- Role can do only what the app needs; cannot drop tables or read pg_shadow.
CREATE ROLE app_web LOGIN PASSWORD :'from_secrets_manager';
GRANT SELECT, INSERT, UPDATE ON orders, customers TO app_web;
-- No CREATE/DROP/superuser; a bug in the app cannot escalate to schema damage.
```

```python
# Parameters are bound by the driver: user input can never become SQL code.
cur.execute(
    "SELECT id, email FROM customers WHERE email = %s AND status = %s",
    (user_email, "active"),          # values, not string-concatenated
)
```

**Bad Example** — string-built SQL, superuser connection

```python
# App connects as the database superuser: any injection = full compromise.
conn = connect(user="postgres", password="postgres")  # least privilege ignored

# User input concatenated straight into SQL. Input  ' OR '1'='1  dumps the table;
#  '; DROP TABLE customers; --  destroys it.
query = "SELECT id, email FROM customers WHERE email = '" + user_email + "'"
cur.execute(query)
```

## Common Mistakes

- Concatenating or f-string-interpolating user input into SQL instead of binding
  parameters.
- Connecting the application as superuser/`root`, so any bug becomes total
  compromise.
- Assuming an ORM makes you injection-proof; raw fragments, `.raw()`, and dynamic
  order-by still concatenate unless parameterized.
- Returning raw database errors to clients, leaking schema and query structure.
- Storing plaintext secrets/PII, or logging query parameters that contain them.
- Using string building for dynamic identifiers instead of allowlists/quoting.
- Skipping RLS in multi-tenant systems and relying solely on application `WHERE`
  clauses, which one forgotten filter defeats.

## Production Tips

- Run static analysis / linters that flag string-built SQL in CI; make it a build
  failure, not a code-review hope.
- Test injection explicitly: feed `' OR '1'='1`, quotes, and `;`-terminators to
  every input in negative tests.
- Separate roles per access pattern (read-only reporting vs. read-write app) so a
  leaked reporting credential cannot mutate data.
- Keep the database off the public internet; reach it only through a private
  network / bastion, so a leaked credential still needs network access.

## AI Review Checklist

- Is every query with user input parameterized (no string concatenation/f-strings)?
- Does the application connect with a least-privilege role, never superuser?
- Are dynamic identifiers allowlisted or identifier-quoted, not concatenated?
- Are only necessary columns/rows exposed, via [views](18-views.md) or RLS where
  appropriate?
- Are database errors sanitized before reaching clients?
- Are credentials in a secrets manager and connections TLS-encrypted?
- Do logs exclude sensitive values and query parameters?

## Related

- `knowledge/sql/20-stored-procedures.md`
- `knowledge/sql/18-views.md`
- `knowledge/sql/13-dml.md`
- `knowledge/sql/14-transactions.md`
- `knowledge/sql/26-best-practices.md`
