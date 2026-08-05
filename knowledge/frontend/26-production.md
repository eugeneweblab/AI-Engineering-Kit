---
id: frontend/26-production
topic: frontend
slug: production
title: "Frontend Production"
type: doc
order: 26
status: ready
tags: [frontend, production, ErrorBoundary, reportError, reload, console.debug, addEventListener, STRIPE_SECRET]
related: [frontend/08-performance, frontend/13-error-handling, frontend/23-monitoring, frontend/20-bundling, frontend/98-production-checklist]
when_to_use: "Read before shipping a frontend build to real users or promoting it to a production environment."
---
# Frontend Production

## Purpose

This document defines what "production-ready" means for a frontend and how to get a build
there safely: build configuration, environment handling, caching and cache-busting,
resilience to failures, observability, and safe rollout. It is written so an agent can
prepare or review a release without shipping a broken, slow, or unmonitored app to real
users.

## Why It Matters

In production the network is hostile, devices are slow, third-party scripts fail, and
users do things your dev machine never will. Code that "works locally" routinely breaks
under a cold cache, a flaky CDN, an ad blocker, or a mid-deploy version skew. Frontend
failures are also uniquely visible — a white screen or a broken checkout is seen by every
user immediately, and there is no server log to hide behind. The difference between a dev
build and a production build is not a flag; it is a set of decisions about failure,
caching, secrets, and observability that must be made deliberately.

## Core Principles

- **Fail visibly to you, gracefully to the user.** A crash must render a recovery UI and
  report to your monitoring — never a blank page and a silent error.
- **The client is public.** Anything shipped to the browser is readable by anyone. No
  secrets, no private keys, no trust in client-side checks for security.
- **Immutable assets, mutable entry.** Hash-fingerprint every asset and cache it forever;
  keep only the HTML entry point uncacheable. This makes deploys atomic and instant.
- **Deploys overlap.** During a rollout, old and new clients hit the API at once. Assets
  and APIs must stay backward-compatible across a deploy window.
- **You cannot fix what you cannot see.** Production without error tracking and real-user
  performance data is flying blind.

## Best Practices

- Ship a production build: minified, tree-shaken, source maps generated but uploaded to
  the monitoring tool (not served publicly). Strip `console.debug` and dev-only code via
  `NODE_ENV`.
- Inject configuration at build/deploy time from environment, and expose only public
  values (prefix-scoped, e.g. `NEXT_PUBLIC_*`/`VITE_*`). Never bundle a private token.
- Fingerprint filenames (`app.4f9a.js`) and serve them with `Cache-Control: immutable,
  max-age=31536000`; serve `index.html` with `no-cache` so new deploys are picked up.
- Wrap the app (and each risky route/widget) in an error boundary that shows a retry UI
  and reports the error with release version and user context.
- Handle the offline/degraded case: retry failed fetches with backoff, show a reconnect
  banner, and never leave the UI stuck on a spinner forever (time out and show an error).
- Guard against version skew: on a chunk-load failure (stale hashed chunk after a deploy),
  prompt a reload rather than crashing.
- Set a strict Content-Security-Policy and other security headers; audit third-party
  scripts — each one can crash or slow your app and sees your users.
- Gate the release: performance budgets and error-rate checks in CI, then a staged/canary
  rollout with the ability to roll back instantly.

## Examples

**Good Example** — error boundary reports and recovers; skew is handled

```tsx
<ErrorBoundary
  fallback={<AppCrashScreen onRetry={reload} />}
  onError={(e, info) =>
    // Report with the release so you can tie crashes to a deploy.
    reportError(e, { release: __APP_VERSION__, componentStack: info.componentStack })
  }
>
  <App />
</ErrorBoundary>;

// A stale hashed chunk after a deploy → prompt reload instead of a white screen.
window.addEventListener("vite:preloadError", () => location.reload());
```

**Bad Example** — secrets leak, failures are invisible, cache is broken

```ts
// Shipped to the browser — readable by every user; the "secret" is now public.
const STRIPE_SECRET = "sk_live_9f...";

fetch("/api/orders").then((r) => r.json()).then(render);
// No catch: a failed request leaves a permanent spinner and reports nothing.

// index.html cached for a year → users are stuck on the old build after every deploy.
```

## Common Mistakes

- Bundling private API keys or secrets into client code.
- No error boundary, so one render error blanks the whole app with no report.
- Caching the HTML entry aggressively, stranding users on stale builds.
- Serving public, un-minified source maps that expose your source to anyone.
- Assuming the network succeeds — no timeouts, retries, or offline handling.
- Deploying with breaking asset/API changes while old clients are still live.
- No real-user monitoring, so regressions are discovered via user complaints.

## Production Tips

- Track Core Web Vitals (LCP, INP, CLS) from real users, not just lab tests, and alert on
  regressions per release.
- Tag every error and metric with the release/commit so you can bisect a regression to a
  deploy and roll back precisely.
- Use feature flags to decouple deploy from release; ship dark, enable gradually, kill
  instantly on incident.

## AI Review Checklist

- Are all secrets kept server-side, with only public-prefixed config in the bundle?
- Is the app wrapped in an error boundary that reports (with release) and recovers?
- Are assets content-hashed and immutable, with the HTML entry left uncacheable?
- Are network calls guarded with timeout, retry, and a user-visible failure state?
- Is version skew (stale chunk load) handled with a reload rather than a crash?
- Is real-user error and performance monitoring wired up and tagged by release?
- Are security headers (CSP) set and third-party scripts audited?

## Related

- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/13-error-handling.md`
- `knowledge/frontend/23-monitoring.md`
- `knowledge/frontend/20-bundling.md`
- `knowledge/frontend/98-production-checklist.md`
