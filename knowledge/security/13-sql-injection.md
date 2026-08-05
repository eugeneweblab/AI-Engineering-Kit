---
id: security/13-sql-injection
topic: security
slug: sql-injection
title: "SQL Injection"
type: doc
order: 13
status: ready
tags: [security, sql-injection, execute]
related: [security/09-input-validation, security/10-output-encoding, security/14-command-injection, security/28-owasp-top10]
when_to_use: "Read before writing or reviewing any code that builds a database query from data the caller can influence."
---
# SQL Injection

## Purpose

This document defines how to keep untrusted data out of the *code* portion of a
database query. SQL injection (SQLi) happens when input the attacker controls is
concatenated into a query string and the database parses it as SQL rather than as
data. The fix is structural, not cosmetic: separate the query text from its
parameters so the database never treats input as code.

The same class of bug — mixing untrusted data into an interpreter's instruction
stream — appears in [command injection](14-command-injection.md), NoSQL queries,
LDAP filters, and ORM `raw()` calls. Treat all of them the same way.

## Why It Matters

A single injectable query can dump every row in the database, bypass
authentication, or run administrative commands (`DROP TABLE`, `xp_cmdshell`). SQLi
has topped the OWASP list for two decades because it is easy to introduce and
catastrophic to exploit — one unparameterized query in one endpoint compromises
the whole datastore. It is also invisible in normal use: the app returns correct
results for honest input and only misbehaves for crafted input, so it survives
manual testing and ships to production.

## Core Principles

- **Data is never code.** The query structure must be fixed at development time;
  runtime input may only fill in bound parameter slots.
- **Parameterize everything, always.** Use prepared statements / bound parameters
  for every value, even ones that "look safe" like integers or enums.
- **Escaping is a last resort, not a strategy.** Manual escaping is fragile and
  charset-dependent; a single missed branch reintroduces the hole. Prefer binding.
- **Least privilege limits blast radius.** The app's database account should hold
  only the rights it needs, so a successful injection cannot drop tables or read
  other schemas.
- **Identifiers cannot be bound — allowlist them.** Table and column names can't be
  parameters; validate them against a fixed allowlist, never interpolate raw input.

## Best Practices

- Use parameterized queries or an ORM's parameter binding for every value. Bound
  parameters are sent to the database separately from the SQL text, so input can
  never change the query's meaning.
- When you must build dynamic SQL (sorting, filtering), map user input through an
  **allowlist** to known-safe column names and directions — do not interpolate the
  raw string.
- Give the application a database role with only `SELECT/INSERT/UPDATE/DELETE` on
  the tables it uses; deny DDL and access to system schemas. This caps damage if a
  query is ever injectable.
- Validate and constrain input at the edge (type, length, format) as defense in
  depth — but never rely on validation *instead of* parameterization.
- Prefer stored procedures or query builders that parameterize by default; audit
  every `raw`, `literal`, `unsafe`, or string-format escape hatch.
- Disable verbose database errors in production; leaked error text helps an
  attacker map the schema and confirm an injection.

## Examples

**Good Example** — bound parameters and an allowlisted sort column

```python
ALLOWED_SORT = {"name": "name", "created": "created_at"}  # allowlist, not interpolation

def find_users(search: str, sort_key: str, db):
    column = ALLOWED_SORT.get(sort_key, "created_at")  # user input maps to a fixed identifier
    # %s is a bound parameter: `search` is sent as data, never parsed as SQL.
    return db.execute(
        f"SELECT id, name FROM users WHERE name ILIKE %s ORDER BY {column}",
        [f"%{search}%"],  # even the wildcard pattern is a parameter, not concatenated SQL
    )
```

**Bad Example** — string concatenation lets input become SQL

```python
def find_users(search, sort_key, db):
    # `search` is spliced into the query text. Input `'; DROP TABLE users; --`
    # is now executable SQL, not a search term.
    query = "SELECT id, name FROM users WHERE name ILIKE '%" + search + \
            "%' ORDER BY " + sort_key  # sort_key is unvalidated too
    return db.execute(query)
```

## Common Mistakes

- Assuming an ORM is automatically safe, then dropping into `raw()` / `query()` /
  string-formatted `.where()` and concatenating input.
- Parameterizing values but interpolating table/column/`ORDER BY` names from input.
- Trusting numeric or enum inputs and skipping binding for them.
- Relying on client-side validation or a WAF as the primary defense — both are
  bypassable; only server-side parameterization actually removes the bug.
- Blocklist "sanitizing" (stripping quotes, `--`, keywords). Attackers route around
  blocklists with encoding and alternate syntax.
- Reusing one high-privilege DB superuser for the app, so any injection is total.

## Production Tips

- Run static analysis / SAST that flags string-built SQL, and add a lint rule
  banning raw query builders outside a reviewed data-access layer.
- Log parameterized query *shape* and duration, never the interpolated values, so
  logs don't themselves become a leak.
- Add regression tests that fire classic payloads (`' OR '1'='1`, stacked queries,
  UNION probes) at each endpoint and assert they return no extra rows.

## AI Review Checklist

- Is every value passed as a bound parameter rather than concatenated into SQL?
- Are table/column/sort/direction inputs mapped through an allowlist?
- Are all `raw` / `literal` / `unsafe` escape hatches justified and reviewed?
- Does the app connect with a least-privilege database role (no DDL, no superuser)?
- Are verbose database errors suppressed in production responses?
- Is input validation present as defense in depth, not as the sole control?

## Related

- `knowledge/security/09-input-validation.md`
- `knowledge/security/10-output-encoding.md`
- `knowledge/security/14-command-injection.md`
- `knowledge/security/28-owasp-top10.md`
