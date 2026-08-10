---
id: prisma/12-seeding
topic: prisma
slug: seeding
title: "Seeding"
type: doc
order: 12
status: ready
tags: [prisma, seeding, upsert, PrismaClient, prisma.seed, createMany, NODE_ENV, package.json]
related: [prisma/05-migrations, prisma/08-transactions, prisma/19-testing, prisma/07-crud]
when_to_use: "Read before writing or reviewing a seed script that populates a database for development, tests, or first-run production data."
---
# Seeding

## Purpose

This document defines how to write a Prisma seed script: a program that inserts a
known set of rows so a fresh database is usable. Seeding covers three distinct jobs —
development fixtures, deterministic test data, and *reference data* required for the
app to run in production (roles, plans, feature flags). An agent should be able to
write a seed that is safe to run repeatedly and safe to point at any environment.

Prisma runs the seed via the `prisma db seed` command and automatically after
`prisma migrate reset` and `prisma migrate dev` on a fresh database. The script itself
is ordinary Prisma Client code.

## Why It Matters

A seed is the one script explicitly designed to *write* data, and teams run it against
whatever database their shell points at. A non-idempotent seed doubles its rows every
run; a seed with hard-coded ids collides on the second run; a seed pointed at
production by an unguarded `DATABASE_URL` can wipe or corrupt live data. Because seeds
are treated as throwaway glue, they receive little review — yet they hold real write
authority. Treat the seed as production code that happens to run rarely.

## Core Principles

- **Idempotent by construction.** Running the seed twice must leave the database in the
  same state as running it once. Use `upsert` keyed on a stable natural key, never a
  bare `create`.
- **Separate reference data from sample data.** Reference data (roles, currencies,
  plans) is required in every environment. Sample data (fake users, demo orders) belongs
  only in development and tests. Gate sample data behind an environment check.
- **Deterministic where it counts.** Seed a fixed PRNG so test data is reproducible;
  never rely on `Math.random()` or `new Date()` in data that tests assert against.
- **One transaction per logical unit.** Wrap related inserts so a mid-seed failure does
  not leave half-built relations.
- **Fail loud, never silently skip.** If a required reference row cannot be created, the
  seed must exit non-zero so CI and migrations catch it.

## Best Practices

- Configure the seed in `package.json` under `prisma.seed` (e.g.
  `"seed": "tsx prisma/seed.ts"`) so `prisma db seed` and `migrate reset` find it.
- Use `upsert` with a unique `where` for every reference row; this makes reruns safe and
  turns the seed into a live source of truth for that data.
- Bulk-insert independent sample rows with `createMany` for speed; fall back to `create`
  only when you need the returned id to build relations.
- Read an explicit env var (e.g. `SEED_ENV`) or `NODE_ENV` before inserting fake data,
  and refuse to run destructive seeds when `NODE_ENV === "production"`.
- Keep the seed's `PrismaClient` in its own instance and call `$disconnect()` in a
  `finally` block so the process exits cleanly.
- For large datasets, use `faker` with a fixed `faker.seed(n)` so re-seeding produces the
  same graph and diffs stay reviewable.
- Version reference-data changes as migrations plus an idempotent upsert, not as ad-hoc
  SQL — see [migrations](05-migrations.md).

## Examples

**Good Example** — idempotent, gated, transactional

```ts
import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient } from "@/generated/prisma/client";

const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL! });
const prisma = new PrismaClient({ adapter });

async function main() {
  // Reference data: required everywhere, keyed on a stable natural key.
  // upsert makes a second run a no-op instead of a duplicate-key error.
  const roles = ["ADMIN", "MEMBER"] as const;
  await prisma.$transaction(
    roles.map((name) =>
      prisma.role.upsert({ where: { name }, update: {}, create: { name } }),
    ),
  );

  // Sample data: only in non-production, so a stray prod seed can't inject fakes.
  if (process.env.NODE_ENV !== "production") {
    await prisma.user.upsert({
      where: { email: "demo@example.com" }, // natural key → rerun-safe
      update: {},
      create: { email: "demo@example.com", roles: { connect: { name: "MEMBER" } } },
    });
  }
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1); // fail loud so migrate/CI abort
  })
  .finally(() => prisma.$disconnect());
```

**Bad Example** — duplicates on rerun, no environment guard

```ts
async function main() {
  // Bare create → second run throws on unique email, or (worse) with no unique
  // constraint silently doubles every row each time the seed is invoked.
  await prisma.user.create({
    data: { email: "demo@example.com", role: "ADMIN" },
  });
  // Random data with no fixed seed → tests that assert on it are flaky.
  for (let i = 0; i < 100; i++) {
    await prisma.order.create({ data: { total: Math.random() * 100 } });
  }
  // No env guard: whatever DATABASE_URL points at gets demo data — including prod.
}
main(); // no error handling, no $disconnect → hangs or exits 0 on failure
```

## Common Mistakes

- Using `create` instead of `upsert`, so the second run fails or duplicates rows.
- Hard-coding primary-key ids, which collide the moment the seed runs on a non-empty DB.
- Seeding fake data unconditionally, contaminating staging or production.
- Non-deterministic data (`Math.random`, `Date.now`) that tests then assert against.
- Swallowing errors so a partial seed still exits 0 and CI reports green.
- Sequential `await` in a loop for thousands of rows instead of `createMany`.

## Production Tips

- Ship reference data through the migration pipeline, not a manual seed run: an
  idempotent upsert invoked by deploy, or a data migration, so every environment converges.
- Never wire a destructive `migrate reset` into any pipeline that can reach production.
- Log a summary (counts inserted/updated) so a seed run is auditable.

## AI Review Checklist

- Is every reference-data write an `upsert` keyed on a stable unique field?
- Is sample/fake data gated behind an environment check, and blocked in production?
- Does the script `process.exit(1)` on failure and `$disconnect()` in `finally`?
- Is randomized data seeded with a fixed PRNG so results are reproducible?
- Are related inserts wrapped in a [transaction](08-transactions.md)?
- Is the seed registered under `prisma.seed` in `package.json`?

## Related

- `knowledge/prisma/05-migrations.md`
- `knowledge/prisma/08-transactions.md`
- `knowledge/prisma/19-testing.md`
- `knowledge/prisma/07-crud.md`
