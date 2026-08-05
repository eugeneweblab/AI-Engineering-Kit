---
id: prisma/27-tooling
topic: prisma
slug: tooling
title: "Prisma Tooling"
type: doc
order: 27
status: ready
tags: [prisma, tooling, prisma.seed, datasource, postinstall, format, DATABASE_URL, generator]
related: [prisma/05-migrations, prisma/12-seeding, prisma/19-testing, prisma/25-production, prisma/24-best-practices]
when_to_use: "Read before setting up the Prisma CLI, generator config, seeding, or CI steps for a project."
---
# Prisma Tooling

## Purpose

This document defines how to configure and use Prisma's toolchain: the CLI, the schema's
`generator` and `datasource` blocks, `prisma generate`, `migrate`, `db seed`, `studio`,
`validate`, and `format`, plus how these fit into CI. The aim is a workflow where the
generated client and the schema can never drift, and every environment runs the same
commands.

## Why It Matters

Prisma is CLI-first: the client you import is code generated from the schema, and that
generation is a build step people forget. When the generated client and the schema
disagree — a teammate pulled a schema change but did not regenerate, or CI shipped a
stale client — you get runtime type errors and missing fields that TypeScript could not
catch, because it type-checked against yesterday's client. Disciplined tooling makes the
schema the single source of truth and makes generation impossible to skip.

## Core Principles

- **The schema is the source of truth; the client is derived.** Never edit generated
  code; regenerate it.
- **Pin the CLI and client to the same version.** A mismatched CLI and `@prisma/client`
  produce subtle, hard-to-debug failures. Keep both in `devDependencies`/`dependencies`
  and pinned.
- **Automate generation.** Wire `prisma generate` into `postinstall` and CI so no
  environment ever runs a stale client.
- **Separate dev and deploy commands.** `migrate dev` authors migrations locally;
  `migrate deploy` applies them everywhere else. They are not interchangeable.
- **Keep the schema formatted and validated in CI.** `prisma format` and `prisma validate`
  catch drift and syntax errors before they merge.

## Best Practices

- Configure `generator client { provider = "prisma-client-js" }` and a `datasource` whose
  `url = env("DATABASE_URL")` — the URL is always an env var, never a literal.
- Add `"postinstall": "prisma generate"` so installs (including CI and Docker builds)
  always produce a matching client.
- Use `prisma migrate dev --name <change>` locally to create a migration + regenerate;
  commit the generated SQL in `prisma/migrations`.
- Run `prisma migrate deploy` in CI/CD release steps; run `prisma migrate status` to
  detect environments that are behind before deploying.
- Define seeding under `prisma.seed` in `package.json` and make it idempotent with
  `upsert` so `prisma db seed` can run repeatedly. See [seeding](12-seeding.md).
- Gate CI on `prisma validate` and `prisma format --check` so schema errors and unformatted
  changes fail fast.
- Use `prisma studio` for local inspection only; never expose it to a shared or production
  database — it is an unauthenticated data editor.
- Pin the version in one place and let `generate` derive everything; commit
  `package-lock.json`/`pnpm-lock.yaml` so CI resolves the identical toolchain.

## Examples

**Good Example** — schema, scripts, and CI that cannot drift

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL") // config from environment, not a literal
}
```

```jsonc
// package.json — generation and seeding are automated, not manual
{
  "scripts": {
    "postinstall": "prisma generate",              // every install regenerates
    "db:migrate": "prisma migrate deploy",          // deploy path
    "db:seed": "tsx prisma/seed.ts"
  },
  "prisma": { "seed": "tsx prisma/seed.ts" }
}
```

```yaml
# ci.yml step — fail on drift before anything ships
- run: npx prisma validate && npx prisma format --check
- run: npx prisma migrate status   # errors if the DB is behind committed migrations
```

**Bad Example** — manual, unpinned, drift-prone

```jsonc
{
  "scripts": {
    // No postinstall generate → CI ships whatever client was last committed
    "start": "node dist/server.js"
  },
  "dependencies": { "@prisma/client": "^6.0.0" }, // caret: CLI and client can diverge
  "devDependencies": { "prisma": "latest" }        // "latest": non-reproducible builds
}
```

## Common Mistakes

- Forgetting `prisma generate` after a schema change, then debugging phantom type errors.
- Version-range (`^`, `latest`) specs that let CLI and client drift apart.
- Editing files under the generated client instead of the schema.
- Using `db push` (schemaless sync) on a project that has migration history, silently
  diverging the DB from the migrations.
- A non-idempotent seed that fails or duplicates on re-run.
- Exposing Prisma Studio against a shared or production database.
- Skipping `prisma validate`/`format` in CI, so broken schemas merge.

## Production Tips

- In Docker, run `prisma generate` in the build stage and copy the generated client into
  the runtime image so the container starts without the CLI.
- Cache the Prisma engine/binary download in CI to keep `generate` fast.
- Use `prisma migrate diff` to review the SQL a migration will produce before applying it
  to a shared environment.

## AI Review Checklist

- Is `DATABASE_URL` referenced via `env(...)` in the datasource, never a literal?
- Is `prisma generate` wired into `postinstall`/build so the client can never be stale?
- Are `prisma` (CLI) and `@prisma/client` pinned to the same version?
- Does deployment use `migrate deploy` and CI check `migrate status`?
- Is the seed script idempotent and registered under `prisma.seed`?
- Do CI gates include `prisma validate` and `prisma format --check`?
- Is Studio kept off shared/production databases?

## Related

- `knowledge/prisma/05-migrations.md`
- `knowledge/prisma/12-seeding.md`
- `knowledge/prisma/19-testing.md`
- `knowledge/prisma/25-production.md`
- `knowledge/prisma/24-best-practices.md`
