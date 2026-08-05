---
id: prisma/17-raw-sql
topic: prisma
slug: raw-sql
title: "Raw SQL"
type: doc
order: 17
status: ready
tags: [prisma, raw-sql, Prisma.sql, Unsafe, queryRawUnsafe, unknown, EXPLAIN]
related: [prisma/21-security, prisma/15-performance, prisma/08-transactions, prisma/09-filtering]
when_to_use: "Read before writing any $queryRaw, $executeRaw, or TypedSQL query, or reviewing code that drops out of the Prisma Client API."
---
# Raw SQL

## Purpose

This document defines how to run raw SQL safely through Prisma: `$queryRaw` /
`$executeRaw` (tagged-template, parameterized), their `Unsafe` variants,
`Prisma.sql` for composition, and TypedSQL for typed `.sql` files. Raw SQL is the escape
hatch for queries the Client cannot express — window functions, recursive CTEs,
database-specific features, bulk operations — and for hand-tuning hot paths.

The central rule is stated once and applies everywhere: **raw SQL is where SQL injection
lives**. Every example here is about keeping user input out of the query string.

## Why It Matters

The moment you leave the Client's typed API, you lose its automatic parameterization —
the thing that makes ordinary Prisma queries injection-proof. A single interpolated
string in a raw query hands an attacker the ability to read, modify, or destroy the
entire database. This is not a performance bug that degrades gracefully; it is a total
compromise from one line of code. Raw SQL also gives up compile-time type safety, so
results are `unknown` and easy to misuse. Both risks demand that raw SQL be rare,
reviewed, and always parameterized.

## Core Principles

- **Parameterize, never interpolate.** Use the tagged-template form (`` $queryRaw`... ${x}` ``)
  or `Prisma.sql` placeholders so values become bound parameters, never string fragments.
- **`Unsafe` means unsafe — prove the input.** `$queryRawUnsafe` / `$executeRawUnsafe`
  put you in charge of safety. Use them only with values you fully control; never pass
  user input into the SQL string.
- **Identifiers can't be parameters.** Table/column names cannot be bound. If they must be
  dynamic, validate against a fixed allow-list — never pass them through.
- **Type the result explicitly.** Raw results are untyped; provide a return type and
  validate the shape. Prefer TypedSQL when the query is stable, for real type safety.
- **Prefer the Client; drop to raw deliberately.** Every raw query is code the Client
  cannot check. Reach for it for a concrete reason, not convenience.

## Best Practices

- Default to the tagged-template `$queryRaw` / `$executeRaw`; interpolations are
  parameterized automatically and are safe.
- Compose dynamic queries with `Prisma.sql`, `Prisma.join`, and `Prisma.empty` so
  fragments stay parameterized instead of concatenating strings.
- Use TypedSQL (`.sql` files under `prisma/sql`, enabled via the `typedSql` preview/GA
  feature) for complex read queries so inputs and outputs are fully typed and checked.
- Validate any dynamic identifier against an explicit allow-list of known column/table
  names before it touches the query.
- Run multi-statement raw work inside `$transaction` so partial failures roll back — see
  [transactions](08-transactions.md).
- Keep raw SQL out of hot ORM paths unless profiling shows the Client is the bottleneck;
  then hand-tune with an index and confirm with `EXPLAIN`.

## Examples

**Good Example** — parameterized, typed, allow-listed sort

```ts
import { Prisma } from "@prisma/client";

type Row = { id: string; email: string };

// Tagged template: ${email} becomes a bound parameter, not string text → injection-proof.
const users = await prisma.$queryRaw<Row[]>`
  SELECT id, email FROM "User" WHERE email = ${email}
`;

// Dynamic sort column validated against an allow-list — identifiers can't be parameters.
const sortable = { name: "name", createdAt: "createdAt" } as const;
const col = sortable[input.sort] ?? "createdAt"; // reject anything not allow-listed
const rows = await prisma.$queryRaw<Row[]>(
  Prisma.sql`SELECT id, email FROM "User" ORDER BY ${Prisma.raw(`"${col}"`)}`,
);
```

**Bad Example** — string interpolation into `Unsafe`

```ts
// User input concatenated into the SQL string. `email = ' OR '1'='1` dumps the table;
// `'; DROP TABLE "User"; --` destroys it. Classic SQL injection.
const users = await prisma.$queryRawUnsafe(
  `SELECT id, email FROM "User" WHERE email = '${req.query.email}'`,
);

// Sort column taken straight from the request — no allow-list, injectable identifier.
await prisma.$queryRawUnsafe(
  `SELECT * FROM "User" ORDER BY ${req.query.sort}`,
);
```

## Common Mistakes

- Using `$queryRawUnsafe`/`$executeRawUnsafe` with interpolated user input — direct
  injection.
- Building the tagged template as a JS string first (`` $queryRaw(`... ${x}`) `` as a
  plain string), which defeats parameterization; the value must be interpolated in the
  literal.
- Trying to bind a table or column name as a parameter, then falling back to unsafe
  concatenation.
- Trusting raw results as a type without validating the returned shape.
- Multi-statement raw operations with no transaction, leaving partial writes on failure.
- Reaching for raw SQL to avoid learning the Client filter API, losing type safety for no
  gain — see [filtering](09-filtering.md).

## Production Tips

- Grep the codebase for `Unsafe` in CI and require justification on every hit; it is the
  highest-risk surface in the data layer — see [security](21-security.md).
- Prefer TypedSQL for durable complex queries so schema drift breaks the build, not
  production.
- Log and review raw queries; they bypass Client instrumentation and can hide slow scans.
- Confirm hand-tuned raw queries with `EXPLAIN ANALYZE` — the reason to go raw is usually
  performance, so verify you got it.

## AI Review Checklist

- Is every value a bound parameter (tagged template or `Prisma.sql`), never string-interpolated?
- Are `$queryRawUnsafe` / `$executeRawUnsafe` avoided, or fed only fully controlled input?
- Are dynamic identifiers validated against an allow-list rather than concatenated?
- Are raw results given an explicit type and their shape validated?
- Are multi-statement raw operations wrapped in a [transaction](08-transactions.md)?
- Is raw SQL justified — a query the Client genuinely cannot express or a profiled hot path?

## Related

- `knowledge/prisma/21-security.md`
- `knowledge/prisma/15-performance.md`
- `knowledge/prisma/08-transactions.md`
- `knowledge/prisma/09-filtering.md`
