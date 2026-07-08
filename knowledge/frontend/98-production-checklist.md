---
id: frontend/98-production-checklist
topic: frontend
slug: production-checklist
title: "Production Checklist"
type: doc
order: 98
status: ready
tags: [frontend, production-checklist]
related: [frontend/26-production, frontend/08-performance, frontend/09-accessibility, frontend/14-security, frontend/23-monitoring]
when_to_use: "Read before shipping a frontend app or feature to production, and use as the pre-release gate in review."
---
# Production Checklist

## Purpose

This is the gate a frontend app or feature passes before it reaches real users on real
devices. Each item is a verifiable yes/no an agent can check against the code, the build
output, or a running deploy. If an item cannot be confirmed, treat it as failed — "probably
fine" is how regressions ship.

## Why It Matters

Production is where the assumptions break: the network is slow, the device is old, the input
is malformed, and the user does something you never tested. Most frontend incidents are not
exotic — they are a missing error state, an unbounded bundle, a broken keyboard path, or a
secret compiled into the client. A checklist converts hard-won incident lessons into a
repeatable pre-flight so the same failure does not ship twice.

## Correctness and State

- [ ] Every async read renders an explicit loading, empty, and error state — not just the happy path.
- [ ] Failures surface a retry or recovery path; the UI never dead-ends on a spinner.
- [ ] Route and feature subtrees are wrapped in error boundaries so one crash does not blank the page.
- [ ] No duplicated or stale derived state; computed values are computed, not stored and synced.
- [ ] Forms validate on the client for UX and are re-validated on the server for correctness.
- [ ] Optimistic updates roll back correctly when the server rejects the change.

## Performance

- [ ] The route bundle is under an agreed budget, enforced in CI, with no unexpected regressions.
- [ ] Code is split at the route level; interaction- and viewport-gated code is lazy-loaded.
- [ ] Core Web Vitals meet targets on a mid-tier device: LCP < 2.5s, INP < 200ms, CLS < 0.1.
- [ ] Images are responsive (`srcset`/`sizes`), lazy-loaded below the fold, and correctly sized.
- [ ] Fonts use `font-display: swap` and are preloaded; no invisible-text flash on load.
- [ ] No large synchronous work on the main thread blocks first interaction.
- [ ] Third-party scripts are audited, deferred, and budgeted — each one is a shared main thread.

## Accessibility

- [ ] Every interactive element is reachable and operable by keyboard, with a visible focus ring.
- [ ] Semantic HTML is used; ARIA is added only where native elements cannot express the role.
- [ ] Images have meaningful `alt` text; decorative images have empty `alt`.
- [ ] Color contrast meets WCAG AA (4.5:1 for body text, 3:1 for large text and UI).
- [ ] Forms have associated labels and error messages linked via `aria-describedby`.
- [ ] Content is usable at 200% zoom and respects `prefers-reduced-motion`.

## Security

- [ ] No secrets, API keys, or tokens are embedded in client bundles or environment output.
- [ ] All user-supplied content is escaped; `dangerouslySetInnerHTML`/`v-html` is sanitized or absent.
- [ ] Auth tokens live in `HttpOnly`, `Secure`, `SameSite` cookies, not `localStorage`.
- [ ] A Content-Security-Policy is set and blocks inline script by default.
- [ ] External links use `rel="noopener noreferrer"`; dependencies pass an audit with no known criticals.

## SEO and Metadata

- [ ] Each route sets a unique `<title>`, meta description, and canonical URL.
- [ ] Open Graph and structured data are present where content is shared or indexed.
- [ ] Content that must be indexed is server-rendered or pre-rendered, not client-only.

## Build and Deploy

- [ ] Production build runs with source maps uploaded to error tracking but not served publicly.
- [ ] Static assets are content-hashed and served with long-lived immutable cache headers.
- [ ] Environment config is injected at build/deploy time, not hardcoded per environment.
- [ ] The app degrades gracefully when JavaScript fails to load or a chunk 404s after a deploy.

## Observability

- [ ] Client error tracking is wired up and reporting with release/version tags.
- [ ] Real-user monitoring captures Core Web Vitals in the field, not just in CI.
- [ ] Key user flows emit analytics or logs sufficient to debug a production report.

## AI Review Checklist

- Does every network-dependent view handle loading, empty, and error without dead-ending?
- Is the shipped JavaScript within budget and split by route?
- Can the whole feature be operated with a keyboard and a screen reader?
- Is any secret or unescaped user input present in the client bundle?
- Are error tracking and real-user monitoring active and release-tagged before launch?

## Related

- `knowledge/frontend/26-production.md`
- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/14-security.md`
- `knowledge/frontend/23-monitoring.md`
