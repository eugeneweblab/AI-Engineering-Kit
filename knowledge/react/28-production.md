---
id: react/28-production
topic: react
slug: production
title: "React Production"
type: doc
order: 28
status: ready
tags: [react, production]
related: [react/12-performance, react/19-error-handling, react/25-security, react/29-tooling, react/98-production-checklist]
when_to_use: "Read before shipping a React build to real users or setting up its deploy pipeline."
---
# React Production

## Purpose

This document defines what a React app must satisfy before it serves real users:
an optimized build, resilient runtime behavior, monitoring, and a safe deploy. It
covers the gap between "works on localhost" and "works for thousands of users on
flaky networks and old devices." The concern is not features — it is what happens
when the network is slow, a chunk fails to load, or a render throws in the wild.

Development mode and production mode are different programs. React strips warnings,
enables minification, and removes dev-only checks in production. Test what you ship.

## Why It Matters

Localhost hides every production failure mode: no latency, no bundle-size cost, no
concurrent users, modern hardware, and verbose error overlays. Ship the development
build and users download megabytes of unminified code with dev warnings running on
every render. Skip error boundaries and one thrown render turns the whole app white.
Skip monitoring and you learn about outages from users. Production readiness is the
set of safeguards that make failures graceful and visible instead of catastrophic and silent.

## Core Principles

- **Ship the production build.** Minified, tree-shaken, `NODE_ENV=production`. The
  dev build is larger and slower by design and must never reach users.
- **Fail gracefully, always.** Every route and async boundary needs an error and a
  loading state; an uncaught render error must degrade a section, not the whole app.
- **Make the app observable.** If you cannot see errors, performance, and Core Web
  Vitals from real users, you are flying blind.
- **Budget the bundle.** Code-split by route and lazy-load heavy features; an
  ever-growing bundle silently degrades every first load.
- **Deploys are reversible.** Version assets, cache them immutably, and keep the
  ability to roll back fast when a release regresses.

## Best Practices

- Build with the framework's production command (`vite build`, `next build`) and verify
  `NODE_ENV=production`; confirm the output is minified. See [tooling](29-tooling.md).
- Route-level code-split with `React.lazy` + `Suspense` (or the framework router) so
  users download only what the current view needs.
- Wrap the app and each major route in [error boundaries](19-error-handling.md) that
  render a fallback and report to an error tracker.
- Serve hashed asset filenames with long-lived immutable cache headers; serve
  `index.html` with no-cache so new deploys are picked up.
- Measure Core Web Vitals (LCP, CLS, INP) from real users, not just lab tools.
- Guard against stale clients: on chunk-load failure after a deploy, prompt a reload
  rather than showing a broken screen.
- Set a bundle-size budget in CI and fail the build when it regresses. See [performance](12-performance.md).

## Examples

**Good Example** — code-split route with loading and error fallbacks

```tsx
import { lazy, Suspense } from "react";
import { ErrorBoundary } from "./ErrorBoundary";

// Loaded only when the route is visited → smaller initial bundle.
const Dashboard = lazy(() => import("./Dashboard"));

function DashboardRoute() {
  return (
    <ErrorBoundary fallback={<RouteError />}>   {/* one crash stays contained */}
      <Suspense fallback={<Spinner />}>          {/* graceful load state */}
        <Dashboard />
      </Suspense>
    </ErrorBoundary>
  );
}
```

**Bad Example** — everything eager, no failure handling

```tsx
import Dashboard from "./Dashboard";
import Reports from "./Reports";
import Admin from "./Admin"; // all shipped up front → huge first load

function App() {
  // No error boundary: a throw in Dashboard blanks the entire app.
  // No Suspense: data-heavy routes block with no feedback.
  return <Dashboard />;
}
```

## Common Mistakes

- Deploying the development build (unminified, dev warnings, `NODE_ENV` unset).
- No error boundary, so one render error white-screens the whole app.
- Loading every route and library up front instead of code-splitting.
- Caching `index.html` immutably, so users are stuck on an old build.
- No real-user monitoring — outages are discovered by customers.
- No rollback path, turning a bad release into an extended outage.

## Production Tips

- Smoke-test the production build locally (`vite preview`, `next start`) before deploy.
- Upload source maps privately so tracked errors have readable stack traces.
- Roll out behind a flag or canary for risky changes; watch error rate before full release.
- Alert on error-rate and Core-Web-Vitals regressions, not just on hard downtime.

## AI Review Checklist

- Is the app built and served in production mode, minified?
- Are routes and heavy features code-split and lazy-loaded?
- Is every route wrapped in an error boundary with a fallback?
- Are errors and Core Web Vitals reported from real users?
- Are assets content-hashed and cached immutably, with `index.html` non-cached?
- Is there a fast, tested rollback path?

## Related

- `knowledge/react/12-performance.md`
- `knowledge/react/19-error-handling.md`
- `knowledge/react/25-security.md`
- `knowledge/react/29-tooling.md`
- `knowledge/react/98-production-checklist.md`
