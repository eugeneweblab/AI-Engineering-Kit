---
id: prisma/03-models
topic: prisma
slug: models
title: "Models"
type: doc
order: 3
status: ready
tags: [prisma, models]
related: [prisma/02-schema, prisma/04-relations, prisma/05-migrations, prisma/16-indexes]
when_to_use: "Read before defining or changing a model's fields, IDs, types, or constraints."
---
# Models

## Purpose

This document defines how to write a Prisma **model** — the declaration that maps to a
database table. It covers scalar fields and types, primary keys (`@id`), default values,
optional vs. required, unique constraints, enums, and the field/model attributes that
turn a model into a correct table. Relations between models are covered separately in
[04-relations](04-relations.md).

## Why It Matters

A model is a schema contract that generates both a database table and a TypeScript type.
Get a field's nullability, uniqueness, or default wrong and the error surfaces two ways
at once: bad data in the database and misleading types in your code. Because a model is
read constantly and changed rarely, precision here pays off repeatedly — an accurate
`@unique` or `?` prevents a whole category of runtime bugs before any query is written.

## Core Principles

- **Every model needs a stable identity.** Use `@id`; prefer a collision-resistant
  default (`cuid()`/`uuid()`) over an auto-increment integer when IDs are exposed
  externally, so you do not leak row counts or invite enumeration.
- **Nullability is a decision, not a default.** A field is required unless marked `?`.
  Make it optional only when "no value" is genuinely valid, because optionality
  propagates into every query type.
- **Constraints belong in the schema.** `@unique`, `@@unique`, and enums are enforced by
  the database, not by hopeful application code that can be bypassed.
- **Map, don't rename.** Bind Prisma names to existing columns with `@map`/`@@map`
  rather than renaming production columns.

## Best Practices

- Give every model `@id`, and add `createdAt DateTime @default(now())` plus
  `updatedAt DateTime @updatedAt` for auditability.
- Use `@default(cuid())` (or `uuid()`) for externally visible identifiers; reserve
  `autoincrement()` for internal, non-exposed keys.
- Use enums for closed sets of values instead of free-form strings — the database
  rejects invalid values and the Client narrows the type.
- Use `@@unique([a, b])` for composite uniqueness (e.g. one membership per user per org)
  and `@@index` for columns you filter or sort on (see [16-indexes](16-indexes.md)).
- Choose precise scalar types: `Decimal` for money (never `Float`), `DateTime` for time,
  `Json` only when the shape is genuinely dynamic.

## Examples

**Good Example** — stable ID, explicit constraints, correct types

```prisma
enum Role {
  USER
  ADMIN
}

model User {
  id        String   @id @default(cuid()) // opaque ID: no row-count leak, no enumeration
  email     String   @unique              // DB-enforced uniqueness, not app-checked
  name      String?                       // optional on purpose: signup collects it later
  role      Role     @default(USER)       // closed set; DB rejects invalid values
  balance   Decimal  @default(0)          // Decimal, not Float — money must not drift
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt           // auto-touched on every update

  @@index([role]) // we filter users by role in the admin dashboard
}
```

**Bad Example** — leaky ID, unenforced uniqueness, wrong numeric type

```prisma
model User {
  id      Int     @id @default(autoincrement()) // exposes row counts; enumerable /users/1,2,3
  email   String                                // no @unique → duplicate accounts slip in
  role    String  @default("user")              // free-form string; "amdin" typo passes silently
  balance Float   @default(0)                   // Float rounds money → cents disappear over time
}
// No createdAt/updatedAt → no audit trail when data goes wrong.
```

## Common Mistakes

- Using auto-increment integer IDs for externally exposed resources, leaking counts and
  enabling enumeration.
- Forgetting `@unique`, then deduping in application code (a race condition waiting to
  happen).
- Storing money as `Float` instead of `Decimal`.
- Modeling a closed value set as `String` instead of an enum.
- Making fields optional by habit, so every consumer must handle a `null` that never
  legitimately occurs.

## Production Tips

- Adding a required field to a populated table needs a default or a backfill — otherwise
  the migration fails on existing rows (see [05-migrations](05-migrations.md)).
- Index the columns you actually filter or sort on; each index costs write throughput,
  so add them deliberately, not preemptively.

## AI Review Checklist

- Does every model have an `@id` with an appropriate default strategy?
- Are externally exposed IDs opaque (`cuid`/`uuid`), not sequential integers?
- Are uniqueness rules enforced with `@unique`/`@@unique`, not application code?
- Is money `Decimal`, are closed value sets enums, and are dates `DateTime`?
- Is each `?` deliberate, and do models carry `createdAt`/`updatedAt`?

## Related

- `knowledge/prisma/02-schema.md`
- `knowledge/prisma/04-relations.md`
- `knowledge/prisma/05-migrations.md`
- `knowledge/prisma/16-indexes.md`
