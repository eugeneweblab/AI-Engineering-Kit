---
id: prisma/01-installation
topic: prisma
slug: installation
title: "Prisma Installation"
type: doc
order: 1
status: ready
tags: [prisma, installation, DATABASE_URL, postinstall, schema.prisma, "@prod-db", "@localhost"]
related: [prisma/00-overview, prisma/02-schema, prisma/05-migrations, prisma/06-client]
when_to_use: "Read before adding Prisma to a project or setting up DATABASE_URL and the Client."
---
# Prisma Installation

## Purpose

This document defines how to add Prisma to a Node.js/TypeScript project correctly:
which packages to install, how `prisma init` scaffolds the project, how to configure
`DATABASE_URL`, and how to generate the Client. Getting this right prevents the two most
common setup failures: a version mismatch between CLI and Client, and a leaked or
hard-coded database URL.

## Why It Matters

Prisma splits into two packages that must stay in lockstep: `prisma` (the CLI, a dev
dependency) and `@prisma/client` (the runtime library your app imports). If their
versions drift, the generated Client and the engine disagree, producing errors that
look like application bugs but are really a build-environment problem. Installation is
also where the database credential enters the project — put it in the wrong place and
it ends up in git history forever.

## Core Principles

- **Two packages, one version.** `prisma` (dev) and `@prisma/client` (runtime) must be
  pinned to the same version.
- **Credentials live in the environment, never in code.** `DATABASE_URL` belongs in
  `.env` (git-ignored), not in `schema.prisma` or source.
- **The Client is generated, not hand-written.** It lands in `node_modules/.prisma`
  after `prisma generate`; regenerate it, never edit it.
- **Generate on install and after every schema change.** Otherwise the imported types
  are stale.

## Best Practices

- Install with `npm i -D prisma` and `npm i @prisma/client`, then scaffold with
  `npx prisma init --datasource-provider postgresql`.
- Add a `postinstall` script running `prisma generate` so fresh clones and CI produce a
  Client automatically.
- Reference the URL as `env("DATABASE_URL")` in the datasource block; keep the literal
  value only in `.env`.
- Commit `.env.example` (keys, no secrets) and git-ignore `.env`.
- Pin exact versions in CI (`npm ci`) so the Client is reproducible across machines.

## Examples

**Good Example** — env-driven URL, generate wired into install

```jsonc
// package.json
{
  "scripts": {
    "postinstall": "prisma generate" // fresh clone/CI gets a Client with no manual step
  },
  "devDependencies": { "prisma": "6.5.0" },      // CLI
  "dependencies": { "@prisma/client": "6.5.0" }  // runtime — SAME version, on purpose
}
```

```prisma
// schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL") // resolved from .env at runtime, never hard-coded
}
```

```ini
# .env  (git-ignored)
DATABASE_URL="postgresql://user:pass@localhost:5432/app?schema=public"
```

**Bad Example** — hard-coded secret, mismatched versions

```prisma
datasource db {
  provider = "postgresql"
  // Credential committed to git history forever; rotates only by rewriting history.
  url      = "postgresql://user:hunter2@prod-db:5432/app"
}
```

```jsonc
// package.json — versions drift, engine/Client disagree at runtime
{ "devDependencies": { "prisma": "6.5.0" },
  "dependencies": { "@prisma/client": "5.9.0" } } // mismatch → cryptic runtime errors
```

## Common Mistakes

- Hard-coding `DATABASE_URL` in `schema.prisma` instead of using `env()`.
- Version mismatch between `prisma` and `@prisma/client`.
- Forgetting `prisma generate`, so imports resolve to a stale or missing Client.
- Committing `.env`; the secret is then in history even after deletion.
- Installing `prisma` as a runtime dependency (it is a dev tool) and bloating the image.

## Production Tips

- In CI use `npm ci` (not `npm install`) for reproducible, lockfile-exact installs.
- Set a separate `DATABASE_URL` per environment via the platform's secret store; never
  reuse the dev database for staging or prod.
- For serverless/edge, add a pooled connection string (or Prisma Accelerate) — see
  [15-performance](15-performance.md) — because per-invocation connections exhaust the
  database.

## AI Review Checklist

- Are `prisma` and `@prisma/client` the same pinned version?
- Is `DATABASE_URL` read via `env()` and stored only in a git-ignored `.env`?
- Does a `postinstall` (or CI step) run `prisma generate`?
- Is `.env` git-ignored and an `.env.example` committed instead?
- Is `prisma` a devDependency and `@prisma/client` a runtime dependency?

## Related

- `knowledge/prisma/00-overview.md`
- `knowledge/prisma/02-schema.md`
- `knowledge/prisma/05-migrations.md`
- `knowledge/prisma/06-client.md`
