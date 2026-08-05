---
id: frontend/21-code-splitting
topic: frontend
slug: code-splitting
title: "Frontend Code Splitting"
type: doc
order: 21
status: ready
tags: [frontend, code-splitting, lazy, ErrorBoundary, Suspense, DashboardRoute, RetryPanel, DashboardSkeleton]
related: [frontend/20-bundling, frontend/05-routing, frontend/07-rendering, frontend/08-performance]
when_to_use: "Read before adding lazy-loaded routes or components, or reviewing why the initial JavaScript payload is large."
---
# Frontend Code Splitting

## Purpose

This document defines how to break one large bundle into smaller chunks loaded on
demand — by route, by component, and by interaction — so users download only the code
a given view needs. It is written so an agent can add or review lazy loading without
introducing waterfalls, layout shift, or broken error states.

Code splitting is the applied technique built on [bundling](20-bundling.md): bundling
decides how modules are packaged; splitting decides *when* each package loads. It is
tightly coupled to [routing](05-routing.md), the most natural split boundary.

## Why It Matters

The initial JavaScript payload gates Time to Interactive: nothing is clickable until it
downloads, parses, and hydrates. Most users only ever touch a fraction of an app's
routes, yet a single bundle makes them pay for all of it up front. Splitting can cut the
initial payload by more than half. But naive splitting creates its own failures — a
loading spinner that shifts layout, a chunk that fails to load with no retry, or a
request waterfall where each chunk waits for the previous one. Done right it is a large
win; done carelessly it trades one problem for another.

## Core Principles

- **Split at the route first.** Route-level splitting gives the biggest win for the
  least complexity: each page loads its own chunk on navigation.
- **Split heavy, optional, or rarely-used code next.** Modals, editors, charts, admin
  panels — anything large that not every user opens — belongs behind a dynamic import.
- **Preload on intent, not just on need.** Prefetch the next chunk on hover/focus or
  when the route is likely, so it's ready before the click resolves.
- **Reserve space and handle failure.** Every lazy boundary needs a sized fallback and
  an error boundary; chunk loads *will* fail on flaky networks.
- **Avoid waterfalls.** Don't nest lazy boundaries so chunk B only starts after chunk A
  loads. Start independent loads in parallel.

## Best Practices

- Use dynamic `import()` with the framework's lazy primitive (`React.lazy` + `Suspense`,
  Vue `defineAsyncComponent`, SvelteKit/Next route-based splitting) at route boundaries.
- Give every `Suspense`/async boundary a skeleton fallback that matches the final
  layout's dimensions to avoid Cumulative Layout Shift.
- Wrap lazy boundaries in an error boundary that offers a retry, since a failed chunk
  fetch is transient and should not permanently break the view.
- Prefetch likely-next chunks on link hover/focus (`<link rel="prefetch">` or the
  framework's prefetch) so navigation feels instant.
- Split by interaction for heavy optional UI: load the rich text editor's chunk only
  when the user clicks "Edit".
- Keep chunks coarse enough to matter — dozens of tiny chunks add request overhead and
  HTTP round-trips that outweigh the savings.
- Name chunks (magic comments or config) so they're identifiable in analytics and logs.

## Examples

**Good Example** — route split with sized fallback and error boundary

```tsx
import { lazy, Suspense } from "react";
import { ErrorBoundary } from "./ErrorBoundary";

// Each route is its own chunk, fetched only when the user navigates there.
const Dashboard = lazy(() => import("./routes/Dashboard"));

function DashboardRoute() {
  return (
    // Error boundary: a failed chunk fetch offers retry instead of a blank screen.
    <ErrorBoundary fallback={<RetryPanel />}>
      {/* Skeleton matches final layout size → no layout shift when it loads. */}
      <Suspense fallback={<DashboardSkeleton />}>
        <Dashboard />
      </Suspense>
    </ErrorBoundary>
  );
}

// Prefetch on intent so the chunk is warm before the click resolves.
<Link to="/dashboard" onMouseEnter={() => import("./routes/Dashboard")}>Dashboard</Link>
```

**Bad Example** — waterfall, no fallback, no error handling

```tsx
const Dashboard = lazy(() => import("./routes/Dashboard"));

function App() {
  // WHY BAD: no Suspense boundary here forces a bare spinner higher up,
  // and the spinner has no dimensions → layout jumps when Dashboard mounts (CLS).
  return <Dashboard />;
}

// Inside Dashboard:
const Chart = lazy(() => import("./Chart"));   // starts loading only AFTER
const Table = lazy(() => import("./Table"));   // Dashboard's chunk resolves → waterfall
// No error boundary: one failed chunk fetch on a flaky network = permanently blank page.
```

## Common Mistakes

- Lazy-loading with no `Suspense`/error boundary, so a failed chunk blanks the screen.
- Fallbacks with no fixed size, causing layout shift when the real component mounts.
- Nesting lazy boundaries into a waterfall instead of loading independent chunks in parallel.
- Splitting so finely that request overhead outweighs the byte savings.
- Splitting above-the-fold critical UI, delaying the first meaningful paint.
- Never prefetching, so every navigation pays full chunk latency on click.
- Lazy-loading tiny components where the import overhead exceeds the code saved.

## Production Tips

- Measure the initial-chunk gzip size in CI and treat route-split as the first lever
  when it grows.
- Log chunk-load failures to your error tracker; a spike usually means a stale deploy
  removed a hashed chunk a client still references — keep old chunks for a grace window.
- Verify prefetch actually fires in the Network panel; framework prefetch is easy to
  misconfigure.

## AI Review Checklist

- Are routes split into separate chunks, and heavy optional UI split by interaction?
- Does every lazy boundary have a sized fallback that prevents layout shift?
- Is each lazy boundary wrapped in an error boundary with a retry path?
- Are likely-next chunks prefetched on hover/focus rather than only on click?
- Are independent chunks loaded in parallel rather than in a waterfall?
- Are chunks coarse enough that request overhead doesn't erase the savings?

## Related

- `knowledge/frontend/20-bundling.md`
- `knowledge/frontend/05-routing.md`
- `knowledge/frontend/07-rendering.md`
- `knowledge/frontend/08-performance.md`
