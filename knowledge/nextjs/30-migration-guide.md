---
id: nextjs/30-migration-guide
topic: nextjs
slug: migration-guide
title: "Migration Guide"
type: doc
order: 30
status: ready
tags: [nextjs, migration-guide, cookies, getServerSideProps, generateStaticParams, searchParams, getStaticProps]
related: [nextjs/03-app-router, nextjs/06-server-components, nextjs/09-data-fetching, nextjs/10-caching, nextjs/11-server-actions]
when_to_use: "Read before migrating a Pages Router app to the App Router or upgrading across a major Next.js version."
---
# Migration Guide

## Purpose

This document defines how to migrate a Next.js application safely: from the Pages Router to
the App Router, and across major Next.js versions (13 → 14 → 15 → 16). It gives an agent an
incremental, reversible path instead of a risky big-bang rewrite, and calls out the
behavior changes that silently break working code.

## Why It Matters

Migrations are where correct code becomes incorrect without anyone changing a line. Next.js
15 flipped `fetch` from cached-by-default to uncached-by-default and made `cookies()`,
`headers()`, `params`, and `searchParams` asynchronous. An app that "just upgraded" can
start serving stale data, leaking a spinner where a static page used to be, or throwing at
runtime — all while types still compile. A blind rewrite of a large app is worse: it stalls
for months and ships regressions in bulk. The value here is a route-by-route path where the
old and new routers run side by side and each step is independently shippable and revertible.

## Core Principles

- **Migrate incrementally, never big-bang.** The App Router and Pages Router coexist in one
  app; move one route at a time so every step is shippable and revertible. The cost of a
  full rewrite is months of no delivery and a regression cliff at the end.
- **Read the upgrade codemods and breaking-change notes first.** Run
  `npx @next/codemod@latest upgrade` and apply official codemods before hand-editing — they
  handle the mechanical changes (async request APIs, renamed imports) correctly.
- **Assume caching defaults changed.** After upgrading to 15+, treat every `fetch` as
  uncached and every request API as async until proven otherwise. Do not assume old behavior carried over.
- **Verify behavior, not just compilation.** A green type-check means nothing about render
  mode or cache correctness. Check the build's route table and exercise the flow.
- **Keep data access framework-agnostic.** Put queries in plain functions in a `lib/` layer
  so the same code works whether called from `getServerSideProps` or a Server Component —
  migration then moves the *call site*, not the logic.

## Best Practices

- Move leaf/low-traffic routes first to build confidence before touching critical paths.
- Translate data-loading intent explicitly: `getServerSideProps` → dynamic Server Component
  fetch; `getStaticProps` → static fetch or `generateStaticParams`; `getStaticPaths` →
  `generateStaticParams`. Client-side SWR/React Query can stay in Client Components.
- Replace `pages/_app` and `pages/_document` with `app/layout.tsx` (root layout owns `<html>`/`<body>`).
- Convert API routes (`pages/api/*`) to Route Handlers (`app/**/route.ts`) or, for
  mutations, to Server Actions.
- After upgrading to 15/16, `await` the request APIs: `const cookieStore = await cookies()`.
  Opt back into caching deliberately with `cache: "force-cache"`, `next: { revalidate }`, or
  the `use cache` directive — do not rely on implicit caching.
- Delete migrated Pages routes only after the App Router equivalent is verified in production.

## Examples

**Good Example** — Pages `getServerSideProps` translated to an async Server Component

```tsx
// app/dashboard/page.tsx (App Router, Next.js 15+)
import { cookies } from "next/headers";
import { getDashboard } from "@/lib/dashboard"; // framework-agnostic data function, unchanged

export default async function Page() {
  const session = (await cookies()).get("session")?.value; // await: request APIs are async in 15+
  // No implicit cache in 15+; this is dynamic because it reads cookies — which is intended here.
  const data = await getDashboard(session);
  return <Dashboard data={data} />;
}
```

**Bad Example** — assumes old defaults, breaks silently after upgrade

```tsx
// app/dashboard/page.tsx
import { cookies } from "next/headers";

export default async function Page() {
  const session = cookies().get("session")?.value; // TypeError in 15+: cookies() returns a Promise
  // Assumes fetch still caches by default (it does not in 15+) → serves stale or refetches unexpectedly
  const data = await fetch("https://api/…/dashboard").then((r) => r.json());
  return <Dashboard data={data} />;
}
```

## Common Mistakes

- Attempting a full rewrite instead of route-by-route coexistence, blocking releases for weeks.
- Assuming `fetch` still caches by default after upgrading to 15+, causing stale or over-fetched data.
- Calling `cookies()`/`headers()`/`params` synchronously after the async change, throwing at runtime.
- Putting page logic directly in components so it cannot be reused during the move — extract to `lib/` first.
- Recreating `_app`/`_document` behavior in every route instead of the root layout.
- Deleting Pages routes before the App Router replacement is verified in production.

## Production Tips

- Run old and new routes in parallel behind the same domain; migrate by moving files, and
  keep the previous route in git history for instant rollback.
- After each upgrade, diff the `next build` route table before/after: a route flipping from
  `○` static to `ƒ` dynamic (or vice versa) is a behavior change to explain, not ignore.
- Gate the migration in CI with the same test suite running against both routers where they overlap.

## AI Review Checklist

- Is the migration incremental (route-by-route) rather than a single large rewrite?
- Were the official codemods (`@next/codemod`) run before hand-editing?
- Are `cookies()`, `headers()`, `params`, and `searchParams` awaited (Next.js 15+)?
- Is caching intent explicit for every `fetch` rather than relying on old defaults?
- Does the build route table confirm each migrated route's render mode is intended?
- Are Pages routes removed only after their App Router replacements are verified?

## Related

- `knowledge/nextjs/03-app-router.md`
- `knowledge/nextjs/06-server-components.md`
- `knowledge/nextjs/09-data-fetching.md`
- `knowledge/nextjs/10-caching.md`
- `knowledge/nextjs/11-server-actions.md`
