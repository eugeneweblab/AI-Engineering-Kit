---
id: nextjs/02-project-structure
topic: nextjs
slug: project-structure
title: "Project Structure"
type: doc
order: 2
status: ready
tags: [nextjs, project-structure]
related: [nextjs/27-folder-structure, nextjs/01-architecture, nextjs/06-server-components, nextjs/24-security, nextjs/28-best-practices]
when_to_use: "Read before scaffolding a new Next.js repo or deciding where a module, component, or helper belongs."
---
# Project Structure

## Purpose

This document defines how to organize a Next.js **repository** — the top-level folders, where
domain logic lives, and how to keep the server/client boundary enforceable. It is about the
whole project. The routing conventions *inside* `app/` (special files, route groups, dynamic
segments) are covered separately in [folder structure](27-folder-structure.md).

## Why It Matters

Next.js lets server and client code sit in the same tree, so structure is a security control,
not just tidiness. A helper that imports the database can be pulled into a client bundle by a
single stray import, leaking connection strings or query logic to the browser. A predictable
layout makes the "does this run on the server?" question answerable by *location*, which is far
cheaper to review than tracing every import.

## Core Principles

- **Feature-first, not type-first.** Group by domain (`features/billing/…`) so a change touches
  one folder. A repo split into `components/`, `hooks/`, `utils/` scatters every feature across
  the tree and grows unbounded.
- **The data layer is server-only and central.** All database and secret access goes through a
  Data Access Layer (DAL) that is marked `import 'server-only'`, so a client import fails at
  build time instead of leaking at runtime.
- **`app/` is for routing, not for logic.** Route files (`page.tsx`, `route.ts`) should be thin:
  they compose feature modules and enforce auth, but business logic lives outside `app/`.
- **Colocate, then extract.** Keep a component next to the route that uses it until a second
  consumer appears; only then promote it to a shared module. Premature sharing creates coupling.

## Best Practices

- Use the `src/` directory to separate application code from config (`next.config.ts`,
  `package.json`, `tsconfig.json`) at the repo root.
- Configure a path alias (`"@/*": ["./src/*"]`) so imports are stable under refactors and
  relative-path spaghetti disappears.
- Put shared, framework-agnostic code in `src/lib/` (pure helpers) and server-only integrations
  in `src/server/` or `src/data/` marked with `server-only`.
- Give client components an explicit boundary: a `"use client"` file that imports server
  helpers is a bug waiting to happen — keep client components importing only other client or
  pure code.
- Keep environment access in one typed module (see [environment variables](21-environment-variables.md)),
  never `process.env.X` scattered across files.

## Examples

**Good Example** — feature-first, enforced server boundary

```text
src/
  app/                      # routing only: thin pages, layouts, route handlers
    (marketing)/page.tsx
    dashboard/page.tsx      # imports from features/, enforces auth
  features/
    billing/
      components/Invoice.tsx # "use client" if interactive
      actions.ts            # "use server" Server Actions
      queries.ts            # server-only reads
  server/
    db.ts                   # import 'server-only'  ← cannot reach the browser
    auth.ts                 # session + role checks (the DAL)
  lib/
    format.ts               # pure, safe on server or client
  env.ts                    # typed, validated environment access
```

```ts
// src/server/db.ts
import 'server-only'; // build error if this module is imported by a client component
import { Pool } from 'pg';
export const db = new Pool({ connectionString: process.env.DATABASE_URL });
```

**Bad Example** — type-first tree with an unguarded data layer

```text
src/
  components/   # every feature's UI dumped together, grows without bound
  hooks/
  utils/
    db.ts       # no 'server-only' guard → a client import ships the DB client
```

```ts
// src/utils/db.ts  — imported by both a page AND a "use client" chart component
import { Pool } from 'pg';
// DATABASE_URL and query code can now end up in the client bundle. Silent leak.
export const db = new Pool({ connectionString: process.env.DATABASE_URL });
```

## Common Mistakes

- Omitting `import 'server-only'` on data/secret modules, so nothing catches a client import.
- Putting business logic directly in `page.tsx`, making routes untestable and unshareable.
- Organizing by technical type (`components/`, `hooks/`) so features fragment across the repo.
- Deep relative imports (`../../../lib/x`) instead of a path alias, which break on every move.
- Mixing server and client helpers in one `utils/` file, forcing the whole file client-side.

## Production Tips

- Add an ESLint rule or `import/no-restricted-paths` boundary so `app/` and client code cannot
  import from `server/` except through approved entry points.
- Keep `app/` route segments shallow; push nesting into feature modules where it is testable.
- Store test files beside their subject (`Invoice.test.tsx`) so moving a feature moves its tests.

## AI Review Checklist

- Is domain code grouped by feature rather than by technical type?
- Do all database/secret modules include `import 'server-only'`?
- Are route files thin, delegating logic to feature modules and the DAL?
- Do client components avoid importing server-only or secret-bearing modules?
- Is there a single typed module for environment access, not scattered `process.env`?

## Related

- `knowledge/nextjs/27-folder-structure.md`
- `knowledge/nextjs/01-architecture.md`
- `knowledge/nextjs/06-server-components.md`
- `knowledge/nextjs/24-security.md`
- `knowledge/nextjs/28-best-practices.md`
