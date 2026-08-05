---
id: nextjs/99-ai-review-checklist
topic: nextjs
slug: ai-review-checklist
title: "Next.js AI Review Checklist"
type: doc
order: 99
status: ready
tags: [nextjs, ai-review-checklist]
related: [nextjs/06-server-components, nextjs/10-caching, nextjs/11-server-actions, nextjs/24-security, nextjs/100-common-antipatterns]
when_to_use: "Read when reviewing or self-reviewing any Next.js App Router pull request before it merges."
---
# Next.js AI Review Checklist

## Purpose

This is the checklist an agent runs against a Next.js App Router change before approving it.
Every item is a verifiable yes/no question tied to a concrete failure mode documented
elsewhere in this section. Prefer this list over ad-hoc judgment: it catches the class of
bugs that compile cleanly and pass a happy-path test but break security, caching, or
performance in production.

## Why It Matters

In the App Router, the most damaging mistakes are invisible in a diff read casually. A
secret crossing the client boundary, an accidental dynamic render, an unvalidated Server
Action — none of these throw during review. A checklist forces the reviewer to look at the
exact places where the framework's flexibility turns into a silent hazard, so the defect is
caught at review time instead of in an incident.

## How To Use

Work top to bottom. Any unchecked box is a blocking comment unless the author gives an
explicit, written justification. Skip a group only when the change provably does not touch
that surface (e.g. no data fetching).

## Server / Client Boundary

**Rules:** [Server Components](06-server-components.md) · [Client Components](07-client-components.md)

- [ ] Is every `"use client"` at an interactive leaf, not on a page or layout by default?
- [ ] Is the client bundle free of server-only imports (db clients, secret config, private logic)?
- [ ] Are Server Components composed into Client Components via `children` rather than imported into client modules?
- [ ] Do all props crossing the server→client boundary serialize (no functions, class instances, or raw Dates passed unsafely)?
- [ ] Are `useEffect`/`useState` used only where genuine client interactivity requires them?

## Data Fetching & Caching

**Rules:** [Data Fetching](09-data-fetching.md) · [Caching](10-caching.md)

- [ ] Is data fetched on the server and passed down, rather than fetched client-side to hydrate static content?
- [ ] Is each `fetch` caching behavior explicit (Next.js 15+ defaults to uncached)?
- [ ] Is each route's static vs dynamic render mode intentional and matches the build route table?
- [ ] Are independent fetches concurrent (no accidental request waterfalls)?
- [ ] Are `cookies()`, `headers()`, `params`, and `searchParams` awaited (async in Next.js 15+)?
- [ ] Is `revalidatePath`/`revalidateTag` called after mutations that change cached data?

## Mutations & Server Actions

**Rules:** [Server Actions](11-server-actions.md)

- [ ] Does every Server Action / Route Handler validate its input with a schema before use?
- [ ] Does every mutation re-check authentication and authorization on the server?
- [ ] Are Server Actions never used to expose read endpoints that should be plain data fetches?
- [ ] Is user-controlled input never interpolated into raw SQL or shell commands?

## Security

**Rules:** [Security](24-security.md) · [Authorization](15-authorization.md)

- [ ] Are only `NEXT_PUBLIC_`-prefixed env vars referenced in client code, and no secrets among them?
- [ ] Are auth checks enforced in the data/action layer, not only in middleware or UI?
- [ ] Are external URLs, redirects, and image `remotePatterns` restricted to an allowlist?
- [ ] Is user-generated HTML sanitized before any `dangerouslySetInnerHTML`?

## Rendering, Routing & UX

**Rules:** [Rendering Strategies](08-rendering-strategies.md) · [Routing](04-routing.md)

- [ ] Does every route segment that can fail have an `error.tsx`, and every async boundary a `loading.tsx` or `<Suspense>`?
- [ ] Are `generateStaticParams` and `generateMetadata` present where static generation or SEO requires them?
- [ ] Do navigations use `<Link>` (not raw `<a>`) for internal routes to keep client-side transitions?
- [ ] Is `notFound()` / correct status returned for missing resources instead of rendering empty UI?

## Performance & Assets

**Rules:** [Performance](20-performance.md) · [Images](16-images.md)

- [ ] Are images rendered via `next/image` with explicit `width`/`height` (or `fill`) to prevent layout shift?
- [ ] Are fonts loaded via `next/font` rather than a render-blocking external stylesheet?
- [ ] Are heavy client-only dependencies `dynamic()`-imported with SSR disabled where appropriate?
- [ ] Was the bundle checked for a dependency that accidentally crossed the client boundary?

## Testing & Verification

**Rules:** [Testing](22-testing.md)

- [ ] Does `next build` pass with no new warnings, and does the route table look as intended?
- [ ] Are there tests for the mutation's negative paths (invalid input, unauthorized, not found)?
- [ ] Was the changed flow exercised end-to-end, not just type-checked?

## AI Review Checklist

- [ ] Have all applicable groups above been reviewed, with every unchecked box either fixed or explicitly justified in writing?
- [ ] Do the changes conform to [engineering principles](29-engineering-principles.md) and avoid the [common anti-patterns](100-common-antipatterns.md)?

## Related

- `knowledge/nextjs/06-server-components.md`
- `knowledge/nextjs/10-caching.md`
- `knowledge/nextjs/11-server-actions.md`
- `knowledge/nextjs/24-security.md`
- `knowledge/nextjs/100-common-antipatterns.md`
