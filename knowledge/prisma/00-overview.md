---
id: prisma/00-overview
topic: prisma
slug: overview
title: "Overview"
type: doc
order: 0
status: ready
tags: [prisma, overview]
related: [prisma/01-installation, prisma/02-schema, prisma/04-relations, prisma/05-migrations, prisma/06-client]
when_to_use: "Read first when starting Prisma work or deciding which Prisma doc answers your question."
---
# Overview

## Purpose

This document orients you to Prisma — a type-safe ORM for Node.js and TypeScript —
and maps how the topic's docs fit together. Read it first, then jump to the specific
doc for your task. Prisma has three moving parts an agent must keep straight: the
**schema** (`schema.prisma`, the single source of truth), **Migrate** (turns schema
changes into versioned SQL), and **Client** (the generated, type-safe query API).

## Why It Matters

Prisma's guarantees only hold if you respect its workflow. The generated Client is
only as correct as the schema it was generated from, and the database is only correct
if every schema change went through a migration. Agents that edit the schema without
regenerating the Client, or that push schema changes straight to production without a
migration, produce code that compiles locally but corrupts data or drifts from the
live database. Knowing which tool owns which responsibility prevents that whole class
of failure.

## Core Principles

- **The schema is the source of truth.** The database, the Client, and the types all
  derive from `schema.prisma`. Never hand-edit the generated Client or the database
  out of band — regenerate or migrate instead.
- **Schema change → migration → generate.** These three steps happen in order, every
  time. Skipping the migration means the code and the database disagree.
- **The Client is type-safe by construction.** If a query compiles, its shape matches
  the schema. Lean on that; do not cast away the types with `as any`.
- **One PrismaClient instance per process.** It manages a connection pool; creating
  many instances exhausts database connections.

## How the Docs Fit Together

- **[01-installation](01-installation.md)** — install the CLI and Client, run
  `prisma init`, set `DATABASE_URL`. Start here on a new project.
- **[02-schema](02-schema.md)** — the `schema.prisma` file: datasource, generator,
  and how the schema drives everything else.
- **[03-models](03-models.md)** — define tables as models: fields, types, IDs,
  attributes, enums, and constraints.
- **[04-relations](04-relations.md)** — one-to-many, many-to-many, and one-to-one
  relations, foreign keys, and referential actions.
- **[05-migrations](05-migrations.md)** — evolve the database safely with Prisma
  Migrate in dev and production.
- **06-client** and **07-crud** — the generated query API and create/read/update/
  delete operations.
- **08-transactions**, **09-filtering**, **10-pagination**, **11-relations-loading**
  — day-to-day querying at scale.
- **15-performance**, **16-indexes**, **21-security** — hardening for production.

## Best Practices

- Read [01-installation](01-installation.md) before running any `prisma` command so
  the CLI and Client versions match.
- Keep `schema.prisma` in version control; treat it as reviewed code, not config.
- Run `prisma generate` after every schema change and commit the migration alongside
  the schema edit that caused it.
- Pin `prisma` and `@prisma/client` to the **same** version — a mismatch produces
  confusing runtime errors.

## Examples

**Good Example** — the standard change loop

```bash
# 1. Edit schema.prisma (add a model or field)
# 2. Create and apply a migration in dev
npx prisma migrate dev --name add_post_model
# 3. migrate dev regenerates the Client automatically; types now reflect the change
```

**Bad Example** — schema edited, everything else skipped

```bash
# Edited schema.prisma to add a `Post` model, then only did:
npx prisma db push    # forces schema onto the DB with NO migration history
# Result: no versioned migration to replay in CI/prod, and teammates' databases
# silently diverge. db push is for prototyping only, never for shared environments.
```

## Common Mistakes

- Treating `prisma db push` and `prisma migrate` as interchangeable — `db push` has no
  migration history and is unsafe for shared or production databases.
- Forgetting `prisma generate`, so the Client types lag behind the schema.
- Instantiating `new PrismaClient()` per request instead of once per process.
- Version-mismatched `prisma` (CLI) and `@prisma/client`.

## AI Review Checklist

- Is `schema.prisma` the only place models are defined (no hand-edited Client/SQL)?
- Did every schema change ship with a migration and a `prisma generate`?
- Is there exactly one `PrismaClient` instance shared across the process?
- Are `prisma` and `@prisma/client` pinned to the same version?
- Was the reader pointed to the specific doc for their task rather than guessing?

## Related

- `knowledge/prisma/01-installation.md`
- `knowledge/prisma/02-schema.md`
- `knowledge/prisma/04-relations.md`
- `knowledge/prisma/05-migrations.md`
- `knowledge/prisma/06-client.md`
