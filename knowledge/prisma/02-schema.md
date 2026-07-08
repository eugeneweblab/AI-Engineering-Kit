---
id: prisma/02-schema
topic: prisma
slug: schema
title: "Schema"
type: doc
order: 2
status: ready
tags: [prisma, schema]
related: [prisma/00-overview, prisma/03-models, prisma/04-relations, prisma/05-migrations]
when_to_use: "Read before editing schema.prisma or configuring the datasource and generator."
---
# Schema

## Purpose

This document defines the structure of `schema.prisma` — the datasource block, the
generator block, and how the schema functions as the single source of truth from which
the database, migrations, and the type-safe Client are all derived. It covers the file
as a whole; individual [models](03-models.md) and [relations](04-relations.md) have
their own docs.

## Why It Matters

Every other Prisma artifact is downstream of this one file. The migration SQL, the
Client's TypeScript types, and the shape of your database all come from `schema.prisma`.
A mistake here — the wrong `provider`, a missing block, an unformatted file — propagates
into generated code and applied migrations. Because the schema is small and central,
it is worth holding to a high review bar: it is read far more often than it is written,
and it is the contract the whole team codes against.

## Core Principles

- **One file, one source of truth.** The datasource, generator, models, and enums live
  together and define everything downstream.
- **Declarative, not imperative.** You describe the desired shape; Prisma computes the
  migration to reach it. Do not describe steps.
- **The `provider` is load-bearing.** It selects the database dialect and which types
  and features are available. Changing it after data exists is a migration, not an edit.
- **Formatting is normative.** `prisma format` is the canonical style; a formatted
  schema keeps diffs meaningful in review.

## Best Practices

- Keep exactly one `datasource` block; read its `url` from `env()` (see
  [01-installation](01-installation.md)).
- Keep exactly one `generator client` block; regenerate after every change.
- Run `prisma validate` in CI to catch schema errors before they reach a migration.
- Run `prisma format` before committing so schema diffs reflect real changes, not
  whitespace.
- For large schemas, split into multiple `.prisma` files under `prisma/schema/` (folder
  mode); Prisma merges them.
- Use `@@map` / `@map` to bind Prisma names to existing table/column names when
  adopting Prisma on a legacy database, rather than renaming production columns.

## Examples

**Good Example** — minimal, env-driven, single source of truth

```prisma
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL") // env-driven, never a literal
}

generator client {
  provider = "prisma-client-js"  // generates the type-safe Client
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  createdAt DateTime @default(now())

  @@map("users") // Prisma model `User` maps to legacy table `users`
}
```

**Bad Example** — literal URL, provider that fights the code

```prisma
datasource db {
  provider = "mysql"                       // app was written for Postgres features…
  url      = "mysql://root:root@db/app"    // …and the credential is hard-coded
}

// No generator block → `prisma generate` produces nothing, so `@prisma/client`
// imports resolve to stale or missing types. The build "works" until it doesn't.
```

## Common Mistakes

- Omitting or duplicating the `datasource`/`generator` block.
- Hard-coding the `url` instead of using `env()`.
- Switching `provider` on a populated database and expecting an in-place edit — that
  requires a data migration.
- Editing the schema and forgetting to run `prisma generate` and create a migration.
- Committing an unformatted schema, producing noisy, hard-to-review diffs.

## Production Tips

- Add `prisma validate && prisma format --check` to CI so malformed or unformatted
  schemas fail the build.
- When adopting Prisma on an existing database, run `prisma db pull` to introspect the
  schema instead of hand-writing it, then reconcile names with `@map`/`@@map`.

## AI Review Checklist

- Is there exactly one `datasource` and one `generator` block?
- Is `url` read from `env()` rather than a literal string?
- Does the `provider` match the database the app actually targets?
- Was `prisma format` run and `prisma validate` passing?
- Did the schema change ship with a migration and a regenerated Client?

## Related

- `knowledge/prisma/00-overview.md`
- `knowledge/prisma/03-models.md`
- `knowledge/prisma/04-relations.md`
- `knowledge/prisma/05-migrations.md`
