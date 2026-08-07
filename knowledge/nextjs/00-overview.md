---
id: nextjs/00-overview
topic: nextjs
slug: overview
title: "Next.js Overview"
type: doc
order: 0
status: ready
tags: [nextjs, overview, getServerSideProps, route.ts, page.tsx, layout.tsx]
related: [nextjs/01-architecture, nextjs/03-app-router, nextjs/15-authorization, nextjs/24-security, nextjs/28-best-practices]
when_to_use: "Read first to understand how the Next.js docs fit together and where to go for a specific concern."
---
# Next.js Overview

## Purpose

This section defines how to build production-grade applications with **Next.js (App Router)**.
It is written for an AI coding agent that must implement or review Next.js code without
guessing at conventions. This overview is a map: it tells you what each document covers and
where a given concern lives, so you can jump straight to the authoritative rule instead of
inferring one.

Every document targets the App Router (the `app/` directory) with React Server Components as
the default. The Pages Router (`pages/`) is legacy; do not introduce it in new code.

## Why It Matters

Next.js blurs the server/client boundary on purpose: a single file tree contains code that
runs on the server, code that ships to the browser, and code that must never cross that line.
Most Next.js bugs — leaked secrets, broken auth, hydration errors, waterfalls — come from
misplacing code relative to that boundary. A shared, explicit set of rules keeps agents and
humans on the same mental model, so the boundary is respected by construction rather than by
luck.

## Core Principles

- **Server-first.** Default to Server Components. Add `"use client"` only when you need
  interactivity, browser APIs, or state — because every client component ships JavaScript.
- **The security boundary is the server, not the route.** Middleware, layouts, and page
  props are convenience, not enforcement. Authorization is checked next to the data (see
  [authorization](15-authorization.md)).
- **Data flows down from the server.** Fetch in Server Components and Server Actions; never
  expose data-layer secrets to the client (see [security](24-security.md)).
- **Conventions are load-bearing.** File names (`page.tsx`, `layout.tsx`, `route.ts`) and
  folder names (`(group)`, `_private`, `[param]`) change behavior. Use them deliberately.

## How the Documents Fit Together

**Fundamentals — the rendering model**
- [01 Architecture](01-architecture.md) — the server/client split and how a request renders.
- [02 Project Structure](02-project-structure.md) — how to organize the whole repository.
- [03 App Router](03-app-router.md), [04 Routing](04-routing.md), [05 Layouts](05-layouts.md) —
  routing and shared UI.
- [06 Server Components](06-server-components.md), [07 Client Components](07-client-components.md),
  [08 Rendering Strategies](08-rendering-strategies.md) — where code runs and when.

**Data layer — getting and mutating data**
- [09 Data Fetching](09-data-fetching.md), [10 Caching](10-caching.md) — reads.
- [11 Server Actions](11-server-actions.md), [12 API Routes](12-api-routes.md) — writes and
  HTTP endpoints.
- [13 Middleware](13-proxy.md) — edge-level request handling (routing, not authz).

**Production — making it safe and fast**
- [14 Authentication](14-authentication.md), [15 Authorization](15-authorization.md),
  [24 Security](24-security.md) — who you are, what you may do, and hardening.
- [16 Images](16-images.md), [17 Fonts](17-fonts.md), [20 Performance](20-performance.md) —
  Core Web Vitals.
- [18 Metadata](18-metadata.md), [19 SEO](19-seo.md) — discoverability.
- [21 Environment Variables](21-environment-variables.md) — secrets vs public config.
- [22 Testing](22-testing.md), [23 Observability](23-observability.md),
  [25 Accessibility](25-accessibility.md), [26 Deployment](26-deployment.md).

**Reference**
- [27 Folder Structure](27-folder-structure.md) — the `app/` special-file conventions.
- [28 Best Practices](28-best-practices.md), [29 Engineering Principles](29-engineering-principles.md).
- [100 Common Anti-Patterns](100-common-antipatterns.md), [98 Production Checklist](98-production-checklist.md),
  [99 AI Review Checklist](99-ai-review-checklist.md).

## Best Practices

- Start any new feature by deciding *where each piece runs* (server vs client) before writing
  it — retrofitting a `"use client"` boundary is expensive and error-prone.
- When two docs seem to overlap, the more specific one wins: e.g., [security](24-security.md)
  refines [authentication](14-authentication.md) for the Next.js runtime.
- Treat this overview as an index, not a spec. Concrete rules live in the linked documents.

## Common Mistakes

- Reaching for the Pages Router or `getServerSideProps` in new code — both are superseded by
  the App Router and Server Components.
- Assuming a rule from a generic React guide applies unchanged; the server/client split makes
  Next.js different (data fetching, effects, secrets).
- Enforcing authorization in a layout or the proxy and calling it done — see
  [authorization](15-authorization.md) for why that is not enough.

## AI Review Checklist

- Does new code target the App Router (`app/`), not the Pages Router?
- Is each component correctly server or client, with `"use client"` only where required?
- Are data access and authorization checks on the server, close to the data?
- Did you consult the specific doc for the concern rather than inferring a convention?

## Related

- `knowledge/nextjs/01-architecture.md`
- `knowledge/nextjs/03-app-router.md`
- `knowledge/nextjs/15-authorization.md`
- `knowledge/nextjs/24-security.md`
- `knowledge/nextjs/28-best-practices.md`
