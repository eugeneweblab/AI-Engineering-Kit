---
id: prisma/05-migrations
topic: prisma
slug: migrations
title: "Prisma Migrations"
type: doc
order: 5
status: ready
tags: [prisma, migrations, "@default", cuid, migrate]
applies_to: [prisma]
related: [prisma/02-schema, prisma/03-models, prisma/04-relations, prisma/25-production]
when_to_use: "Read before changing a Prisma schema, generating a Prisma migration, or wiring `prisma migrate` into CI/CD."
---
# Prisma Migrations

## Purpose

This document defines how to evolve a database with Prisma Migrate: how `migrate dev`
works locally, how `migrate deploy` applies migrations in CI/CD and production, when
`db push` is (and is not) acceptable, and how to handle drift, backfills, and
destructive changes. A migration is the versioned, reviewable record of every schema
change — treat it as production code, because it is.

## Why It Matters

The schema and the live database can silently disagree. Migrations are the mechanism
that keeps them in sync across every environment and every teammate. Skip them, or apply
them by hand, and you get *drift*: code expecting columns the database does not have, or
a production database no one can reproduce. Migrations are also where data is destroyed —
a dropped column or a tightened constraint runs against real rows. Because these changes
are irreversible and run against live data, they demand more care than any query.

## Core Principles

- **`db push` is for prototyping, `migrate` is for everything shared.** `db push` forces
  the schema onto the database with no migration history — fine for a throwaway local
  branch, unacceptable for any database a teammate or user touches.
- **Migrations are forward-only and versioned.** Each is committed alongside the schema
  change that produced it, and applied in order in every environment.
- **Generate in dev, apply in prod.** Use `migrate dev` locally to author and apply
  migrations; use `migrate deploy` in CI/CD, which only applies already-committed
  migrations and never edits the schema.
- **Destructive changes need a plan.** Dropping or narrowing a column runs against real
  data; sequence it (expand → backfill → contract) so no deploy loses data.

## Best Practices

- Author migrations with `npx prisma migrate dev --name <change>`; review the generated
  SQL before committing it — do not trust it blindly.
- Apply migrations in production with `npx prisma migrate deploy` (idempotent, no
  prompts), run as a deploy step before the new app code starts.
- Never edit an already-applied migration; write a new one. Editing history causes
  Prisma to detect drift and refuse to proceed.
- For a required new column on a populated table, add it with a default or as optional,
  backfill, then tighten — a bare `NOT NULL` add fails on existing rows.
- Do risky changes in two deploys (expand/contract): add the new shape, migrate the code
  and data, then remove the old shape once nothing reads it.
- If drift is detected, resolve it deliberately with `prisma migrate resolve`; never
  hand-edit the `_prisma_migrations` table.

## Examples

**Good Example** — dev authoring then safe prod apply

```bash
# Local: author + apply the migration, regenerate the Client, commit the SQL
npx prisma migrate dev --name add_post_published_flag

# CI/CD deploy step: apply committed migrations only, no schema edits, no prompts
npx prisma migrate deploy
```

```prisma
// Safe required-column add on a populated table: give it a default so existing rows fill in
model Post {
  id        String  @id @default(cuid())
  published Boolean @default(false) // no default → migration fails on existing NULL rows
}
```

**Bad Example** — pushing straight to a shared database

```bash
# On the shared staging database:
npx prisma db push           # no migration file → nothing to replay in CI or prod,
                             # and teammates' schemas silently diverge from this one.

# Later, "fixing" drift by editing an already-applied migration file and forcing it:
# → Prisma flags the checksum mismatch and refuses; the database is now unreproducible.
```

## Common Mistakes

- Using `db push` on staging/production instead of `migrate deploy`, leaving no history.
- Running `migrate dev` in production — it can prompt, reset, or alter schema state.
- Editing an already-applied migration, causing checksum drift Prisma will not accept.
- Adding a `NOT NULL` column with no default to a populated table, breaking the migration.
- Dropping a column in the same deploy that stops reading it, instead of expand/contract.
- Hand-editing the database, so the next migration diff includes unexpected changes.

## Production Tips

- Run `migrate deploy` as a gated release step (its own job), not from inside app boot —
  concurrent instances must not race to migrate.
- Take a backup (or snapshot) immediately before destructive migrations; they are not
  reversible by Prisma.
- Wrap large backfills in batches to avoid long locks; keep the migration itself fast and
  do heavy data movement in a separate, resumable job.
- In CI, fail the build if `prisma migrate diff` shows the schema and migrations disagree.

## AI Review Checklist

- Are all shared/production schema changes done via `migrate deploy`, never `db push`?
- Is each migration committed with the schema change that produced it, and unedited after
  being applied?
- Do new required columns on populated tables have a default or a backfill step?
- Are destructive changes sequenced as expand → backfill → contract across deploys?
- Is `migrate deploy` a discrete release step (not app boot), with a pre-migration backup?

## Related

- `knowledge/prisma/02-schema.md`
- `knowledge/prisma/03-models.md`
- `knowledge/prisma/04-relations.md`
- `knowledge/prisma/25-production.md`
