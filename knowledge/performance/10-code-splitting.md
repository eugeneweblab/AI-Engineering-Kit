---
id: performance/10-code-splitting
topic: performance
slug: code-splitting
title: "Performance Code Splitting"
type: doc
order: 10
status: ready
tags: [performance, code-splitting, lazy]
related: [performance/07-loading, performance/09-lazy-loading, performance/08-caching, performance/23-performance-budget, performance/18-web-vitals]
when_to_use: "Read before structuring a JavaScript bundle, adding a heavy dependency, or configuring a bundler's chunking."
---
# Performance Code Splitting

## Purpose

This document defines how to break a JavaScript application into chunks that load on
demand instead of shipping one monolithic bundle. It covers split points, vendor
chunking, and cache-friendly hashing. It is written so an agent can keep the initial
payload small without creating a load waterfall.

Code splitting is how [loading](07-loading.md) and [lazy loading](09-lazy-loading.md)
become real: it produces the separate files that let you defer code. The goal is that
each page downloads roughly the code it uses — no more, no less.

## Why It Matters

JavaScript is the most expensive resource a page loads: unlike an image, every byte
must be downloaded, parsed, compiled, and executed on the main thread before the page is
interactive. A single 2 MB bundle blocks interactivity even for a user who only visits
the login page. Splitting lets the initial route ship only its own code, so Time to
Interactive tracks the size of the current page rather than the size of the whole app.
The failure modes are subtle, though: split too finely and you trade one big download
for a slow cascade of tiny ones; split without stable hashing and every deploy busts the
whole cache.

## Core Principles

- **Split along boundaries the user crosses.** Routes are the natural primary split:
  each route loads its own code on navigation. Split further only where it pays off.
- **Initial bundle = critical path only.** The first payload should contain what's needed
  to render and interact with the entry route, nothing more.
- **Separate stable code from volatile code.** Put rarely-changing vendor libraries in
  their own chunk so an app-code change doesn't invalidate the whole cache.
- **Avoid the waterfall.** A chunk that imports another chunk that imports another
  serializes the network. Keep the dependency graph of chunks shallow.
- **Content-hash every chunk.** Filenames like `route.a1b2c3.js` let you cache
  aggressively and invalidate precisely (see [caching](08-caching.md)).

## Best Practices

- Split at the route level first with dynamic `import()`; this gives the biggest win for
  the least complexity — each route pays only for itself.
- Split heavy, optional, or interaction-gated dependencies (rich text editors, charting,
  date pickers, maps) into their own chunk loaded on demand.
- Isolate large third-party libraries into a vendor chunk so they cache across deploys
  and across routes that share them.
- Use content hashing in chunk filenames and keep a stable module ID strategy so an
  unrelated change doesn't rename every chunk and bust caches.
- Preload or prefetch the chunks for the *next* likely navigation during idle time, so
  splitting doesn't add a visible delay at the moment of navigation.
- Set a bundle-size budget in CI ([performance-budget](23-performance-budget.md)) that
  fails the build when the initial payload grows past the threshold.
- Deduplicate shared modules into a common chunk so two routes don't each bundle their
  own copy of the same library.
- Analyze the bundle regularly (a treemap visualizer) to catch a heavy dependency that
  accidentally landed in the initial chunk.

## Examples

**Good Example** — route-level split with prefetch

```jsx
import { lazy } from "react";

// Each route is its own chunk; only the entered route's code downloads.
const Dashboard = lazy(() => import("./routes/Dashboard"));
const Reports   = lazy(() => import(/* webpackPrefetch: true */ "./routes/Reports"));
// Prefetch hint warms the Reports chunk during idle time, before the user clicks.

const routes = [
  { path: "/", element: <Dashboard /> },
  { path: "/reports", element: <Reports /> },
];
```

**Bad Example** — eager monolith and a hidden waterfall

```jsx
// Static imports pull every route into the initial bundle — login users pay for reports.
import Dashboard from "./routes/Dashboard";
import Reports from "./routes/Reports";
import { Chart } from "heavy-charting-lib"; // 400 KB in the entry chunk, always

// Or: a chunk that only imports another chunk at runtime → serialized round trips.
const A = lazy(() => import("./A")); // A's module then dynamically imports B, then C
```

## Common Mistakes

- Statically importing every route/component into the entry bundle, defeating splitting.
- Pulling a large optional dependency (charts, editor) into the initial chunk instead of
  loading it on demand.
- Over-splitting into many tiny chunks, turning one download into a slow request cascade.
- Nesting dynamic imports so chunks load in series (waterfall) instead of parallel.
- No content hashing, so every deploy invalidates all cached chunks.
- Unstable module IDs, so an unrelated edit renames unrelated chunks and busts their cache.
- Not deduplicating shared libraries, so multiple chunks each ship their own copy.

## Production Tips

- Run a bundle analyzer in CI and on the initial chunk specifically; the first payload is
  the one that gates interactivity.
- Add a retry/reload path for `ChunkLoadError`: after a deploy, a stale client may request
  a chunk hash that no longer exists.
- Measure the real effect on Time to Interactive and total blocking time, not just total
  bytes — parse/execute cost matters more than download size on mobile.

## AI Review Checklist

- Is the app split at least at the route level, with routes loaded via dynamic `import()`?
- Does the initial bundle contain only critical-path code for the entry route?
- Are heavy/optional dependencies in on-demand chunks, not the entry bundle?
- Are stable vendor libraries in a separate chunk that survives app-code deploys?
- Are chunks content-hashed with a stable module-ID strategy for precise cache busting?
- Are next-likely chunks prefetched on idle/hover to hide navigation latency?
- Is there a bundle-size budget enforced in CI and a `ChunkLoadError` recovery path?

## Related

- `knowledge/performance/07-loading.md`
- `knowledge/performance/09-lazy-loading.md`
- `knowledge/performance/08-caching.md`
- `knowledge/performance/23-performance-budget.md`
- `knowledge/performance/18-web-vitals.md`
