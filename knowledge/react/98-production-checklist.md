---
id: react/98-production-checklist
topic: react
slug: production-checklist
title: "React Production Checklist"
type: doc
order: 98
status: ready
tags: [react, production-checklist]
related: [react/12-performance, react/16-data-fetching, react/19-error-handling, react/20-accessibility, react/99-ai-review-checklist]
when_to_use: "Read before shipping a React app or a significant feature to production."
---
# React Production Checklist

## Purpose

This is the go/no-go checklist for shipping a React application to production. Every item
is a verifiable yes/no an agent or reviewer can confirm against the code, the production
build, or the running app — not advice, but a gate. If an item is "no", the honest answer
is either fix it or consciously accept the risk in writing. Use it alongside the
[AI review checklist](99-ai-review-checklist.md), which reviews component-level code; this
one reviews whole-app release readiness.

## Why It Matters

React apps fail in production for boringly repetitive reasons: a single unhandled render
error blanks the whole page, an API key ends up in the client bundle, a missing loading
state flashes broken UI, `console.log`s ship to users, or an unmemoized context repaints
the entire tree on every keystroke. Each is trivially preventable and each has shipped in
real apps. A checklist turns "we probably handled that" into "we verified that", and moves
the cost of finding a gap from a user's bug report to five minutes during review.

## Build & Bundle

- [ ] The app is served as a **production build** (`NODE_ENV=production`); React dev
  warnings, prop-type checks, and the slower dev renderer are compiled out.
- [ ] The **bundle is analyzed** and large dependencies are justified; heavy or
  route-specific code is **code-split** with `React.lazy` + `Suspense` or the router's
  lazy loading (see [performance](12-performance.md)).
- [ ] **Source maps** are generated and uploaded to the error tracker, but **not** served
  publicly, so stack traces are readable without exposing source.
- [ ] Assets are **content-hashed** and served with long-lived cache headers; `index.html`
  is served uncached so new deploys are picked up.
- [ ] No `console.log` / `debugger` statements ship to users (strip via build config or a
  lint rule).

## Rendering & Performance

- [ ] Every list rendered from data uses a **stable, unique `key`** — never the array
  index for lists that reorder, insert, or delete.
- [ ] Context values that change are **memoized** (`useMemo`), and unrelated concerns live
  in separate contexts, so a change does not re-render the entire subtree.
- [ ] Expensive components only re-render when their inputs change (`React.memo` +
  stable props/callbacks); `useEffect` dependency arrays are correct and complete.
- [ ] No render-time side effects (fetching, subscriptions, DOM writes) — those belong in
  effects or event handlers.
- [ ] Above-the-fold content renders fast; long lists are virtualized rather than mounting
  thousands of nodes.

## Error Handling & Resilience

- [ ] **Error boundaries** wrap route-level or feature-level subtrees so one failed render
  degrades a section, not the whole page (see [error handling](19-error-handling.md)).
- [ ] Every async data path has explicit **loading, error, and empty** states — no
  perpetual spinner and no crash on an empty array.
- [ ] Failed requests are surfaced to the user with a retry path, not swallowed silently.
- [ ] A top-level fallback UI plus an error reporter (e.g. Sentry) captures unhandled
  render and async errors in production.

## Data Fetching

- [ ] Server state is managed by a dedicated library (TanStack Query, RTK Query, or the
  framework's loaders) — not hand-rolled `useEffect` fetches — so caching, retries, and
  race conditions are handled (see [data fetching](16-data-fetching.md)).
- [ ] Requests are **cancelled or ignored** on unmount / dependency change so a late
  response cannot overwrite fresh state (no "setState on unmounted" races).
- [ ] Mutations invalidate or update the relevant cache; the UI reflects server truth after
  a write.

## Accessibility

- [ ] Interactive elements are real semantic elements (`<button>`, `<a href>`) — not
  `onClick` on a `<div>` — so keyboard and screen-reader users can use them (see
  [accessibility](20-accessibility.md)).
- [ ] Every input has an associated `<label>`; images have `alt`; icon-only buttons have
  `aria-label`.
- [ ] Keyboard navigation works end to end, focus is visible, and focus is managed on route
  change and modal open/close.
- [ ] Color contrast meets WCAG AA and no information is conveyed by color alone.

## Security

- [ ] **No secrets in the client bundle** — API keys, tokens, and private config are never
  shipped to the browser (see [security](25-security.md)).
- [ ] User-supplied HTML is never passed to `dangerouslySetInnerHTML` without sanitizing;
  URLs are validated to block `javascript:` schemes.
- [ ] Auth tokens live in `HttpOnly` cookies rather than `localStorage` where the threat
  model allows; the app assumes the server enforces authorization, never the client.
- [ ] Dependencies are scanned for known vulnerabilities and pinned via a lockfile.

## Testing & CI

- [ ] Critical user flows have tests that assert **behavior** (React Testing Library),
  and CI runs them plus lint and type-check on every PR (see [testing](21-testing.md)).
- [ ] TypeScript (or PropTypes) passes with no errors; `strict` mode is on for TS projects.
- [ ] The production build is exercised in CI (build succeeds, no new console warnings).

## Deployment & Runtime

- [ ] Environment configuration is injected per environment at build/deploy time; the same
  artifact is promoted, not rebuilt per environment.
- [ ] Client-side routing has a server/CDN fallback to `index.html` so deep links don't
  404 on refresh.
- [ ] A deploy strategy handles **stale clients** gracefully (users on the old bundle get a
  prompt or safe failure when the API changes), and rollback is possible.

## AI Review Checklist

- Is this a production build with dev warnings compiled out and no `console.log`s shipped?
- Do route/feature subtrees have error boundaries, and does every async path have loading,
  error, and empty states?
- Are list `key`s stable and unique, and are changing context values memoized?
- Is server state handled by a real data library with cancellation on unmount?
- Are interactive elements semantic and keyboard-accessible with labels?
- Are there zero secrets in the client bundle and no unsanitized `dangerouslySetInnerHTML`?

## Related

- `knowledge/react/12-performance.md`
- `knowledge/react/16-data-fetching.md`
- `knowledge/react/19-error-handling.md`
- `knowledge/react/20-accessibility.md`
- `knowledge/react/99-ai-review-checklist.md`
