---
id: prisma/21-security
topic: prisma
slug: security
title: "Prisma Security"
type: doc
order: 21
status: ready
tags: [prisma, security]
related: [prisma/17-raw-sql, prisma/09-filtering, prisma/07-crud, prisma/22-multi-tenancy]
when_to_use: "Read before accepting any user input into a Prisma query or exposing query results over an API."
---
# Prisma Security

## Purpose

This document defines how to use Prisma without opening a data-layer security hole. It
covers SQL injection through raw queries, mass assignment through unfiltered input,
over-exposure of columns, and the privileges of the database user Prisma connects as.
Prisma is safe by default; almost every Prisma security bug comes from stepping outside
those defaults.

## Why It Matters

The ORM is the last line between untrusted input and the database. The generated query
builder parameterizes everything, so `findMany({ where: { email } })` is injection-safe
no matter what `email` contains. But the moment you reach for `$queryRawUnsafe`, spread
`req.body` into `data`, or `select` more columns than the client needs, you hand the
attacker a lever. These mistakes do not fail loudly — the query works, tests pass, and
the vulnerability ships. Because the data layer touches every record at once, a single
lapse here exfiltrates or corrupts the whole table, not one request.

## Core Principles

- **Never build SQL by string concatenation.** Use the tagged-template `$queryRaw`
  (parameterized) or the query builder. `$queryRawUnsafe` with interpolated input is a
  SQL injection by construction.
- **Never trust the shape of input.** Validate and whitelist fields before they reach
  `data` or `where`; do not spread request bodies into Prisma arguments.
- **Select what the caller needs, nothing more.** Default `select` leaks every column,
  including password hashes and internal flags. Name the fields explicitly.
- **Connect with least privilege.** The application's DB user needs DML, not DDL,
  superuser, or `DROP`. Migrations run as a separate, more privileged user.
- **Keep the connection string a secret.** It contains credentials; it belongs in a
  secrets manager and env vars, never in code or the repo.

## Best Practices

- For dynamic raw SQL, use the tagged template so values are bound as parameters:
  `` prisma.$queryRaw`SELECT * FROM "User" WHERE email = ${email}` ``. Reserve
  `$queryRawUnsafe` for cases with no user input, and even then prefer `Prisma.sql`
  helpers for composition.
- Validate input with a schema (e.g. Zod) at the boundary, then pass only the validated,
  whitelisted object into Prisma — never `data: req.body`.
- Whitelist orderable/filterable fields when the client controls sorting or filtering; an
  attacker-supplied `orderBy` key or nested `where` can probe relations you did not mean
  to expose.
- Use explicit `select` for anything returned to a client, and consider a client
  extension that strips sensitive fields globally so a forgotten `select` cannot leak.
- Give Prisma a database role with only `SELECT/INSERT/UPDATE/DELETE` on application
  tables; run `migrate deploy` under a separate migration role in CI/CD.
- Combine with Postgres Row-Level Security for defense in depth when tenants or users
  share a table (see multi-tenancy).

## Examples

**Good Example** — parameterized raw SQL, validated input, explicit select

```ts
import { z } from "zod";

const CreateUser = z.object({ email: z.string().email(), name: z.string().max(80) });

async function createUser(body: unknown) {
  const data = CreateUser.parse(body); // reject unknown/extra fields before the DB

  return prisma.user.create({
    data, // only validated, whitelisted fields — no role/isAdmin smuggled in
    select: { id: true, email: true, name: true }, // never returns passwordHash
  });
}

// Dynamic filter, still injection-safe: value is bound, not concatenated.
const rows = await prisma.$queryRaw`
  SELECT id, email FROM "User" WHERE email = ${untrustedEmail}`;
```

**Bad Example** — string-built SQL and mass assignment

```ts
async function createUser(req: Request) {
  // Spreading the raw body lets a caller set { isAdmin: true } or { role: "owner" }.
  const user = await prisma.user.create({ data: req.body });

  // Interpolating input straight into SQL: classic injection.
  // email = "x'; DROP TABLE \"User\"; --" executes as SQL.
  const rows = await prisma.$queryRawUnsafe(
    `SELECT * FROM "User" WHERE email = '${req.body.email}'`
  );
  return { user, rows }; // also returns every column, including passwordHash
}
```

## Common Mistakes

- Using `$queryRawUnsafe` (or template strings) with any user-controlled value.
- `data: req.body` / spreading input, enabling mass assignment of privilege fields.
- Relying on the default full-column `select`, leaking hashes, tokens, and internal flags.
- Letting the client pass arbitrary `where`/`orderBy`/`include` objects unchecked.
- Running the app as a superuser DB role, so an injection can drop tables or read others.
- Committing the connection string, or logging queries with parameters in production.

## Production Tips

- Rotate database credentials and store them in a secrets manager; inject at runtime.
- Enable Postgres RLS on shared tables as a backstop, so a missing `where` in code still
  cannot cross a tenant boundary.
- Add a lint/CI rule that flags `$queryRawUnsafe` and `$executeRawUnsafe` for review.
- Redact query parameters in logs; they routinely contain emails, tokens, and PII.

## AI Review Checklist

- Is all raw SQL parameterized via tagged `$queryRaw` / `Prisma.sql`, with no
  `$queryRawUnsafe` on user input?
- Is input validated and whitelisted before it reaches `data`/`where`, never spread from
  `req.body`?
- Does every client-facing query use an explicit `select` that excludes secrets?
- Are client-supplied `orderBy`/`where`/`include` keys whitelisted?
- Does Prisma connect as a least-privilege role, separate from the migration role?
- Is the connection string sourced from secrets, never committed or logged?

## Related

- `knowledge/prisma/17-raw-sql.md`
- `knowledge/prisma/09-filtering.md`
- `knowledge/prisma/07-crud.md`
- `knowledge/prisma/22-multi-tenancy.md`
