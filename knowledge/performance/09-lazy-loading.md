---
id: performance/09-lazy-loading
topic: performance
slug: lazy-loading
title: "Lazy Loading"
type: doc
order: 9
status: ready
tags: [performance, lazy-loading]
related: [performance/10-code-splitting, performance/07-loading, performance/11-images, performance/06-rendering, performance/18-web-vitals]
when_to_use: "Read before deferring the load of any component, route, image, or module until it is actually needed."
---
# Lazy Loading

## Purpose

This document defines how to defer loading a resource until it is actually needed:
off-screen images, below-the-fold components, routes, and heavy modules. It is written
so an agent can defer work without breaking layout, accessibility, or perceived speed.

Lazy loading is the discipline of *not paying for what the user hasn't asked for yet*.
It shrinks the initial payload by moving work from "on load" to "on demand." The trade
is a small delay at the moment of need, which is worth it only when you hide it well.

## Why It Matters

Most pages load far more than the user will ever see: images below the fold, modals
never opened, routes never visited, admin panels the current user can't access. Loading
all of it upfront inflates the initial payload, delays interactivity, and wastes the
user's data and battery. Deferring it is one of the cheapest wins available — but done
carelessly it introduces layout shift, spinner flashes, and content that isn't there
when the user reaches it. The skill is deferring the *right* things and covering the gap.

## Core Principles

- **Defer what isn't needed for the first meaningful view.** Anything below the fold,
  behind an interaction, or gated by a route is a candidate. What's needed now is not.
- **Reserve space before you defer.** A lazy image or component must occupy its final
  size from the start, or it will shift layout when it arrives (harms CLS).
- **Load ahead of need, not at the moment of need.** Prefetch on hover, on idle, or as
  the item nears the viewport so the resource is ready before the user notices.
- **Degrade gracefully.** If the deferred resource fails, show a fallback or retry —
  never a broken hole. Lazy content is still required content.
- **Don't lazy-load the critical path.** The LCP image, above-the-fold content, and the
  initial route must load eagerly. Deferring them makes the page slower, not faster.

## Best Practices

- Use native `loading="lazy"` on off-screen images and iframes; it's zero-JS and honored
  by the browser's own heuristics. Never lazy-load the LCP/above-the-fold image.
- Always set `width`/`height` (or an `aspect-ratio`) on lazy media so the browser
  reserves layout space and avoids shift when it loads.
- Lazy-load route components with the framework's dynamic import + suspense boundary, so
  a route's code arrives only when navigated to (see [code-splitting](10-code-splitting.md)).
- Use `IntersectionObserver` for custom lazy content instead of scroll handlers; it's
  passive and doesn't run work on every scroll frame.
- Prefetch the next likely resource during idle time (`requestIdleCallback`) or on hover
  intent, so the transition feels instant when triggered.
- Show a skeleton sized to the real content, not a centered spinner, so the layout is
  stable and the wait reads as "loading this box," not "the page is broken."
- Defer heavy optional dependencies (charting, editors, maps) behind the interaction
  that reveals them, not at module top level.

## Examples

**Good Example** — deferred, space reserved, prefetched

```jsx
import { lazy, Suspense } from "react";

// Code for the editor is fetched only when <Editor> first renders.
const Editor = lazy(() => import("./HeavyEditor"));

function Panel({ open }) {
  return (
    <Suspense fallback={<EditorSkeleton />}> {/* skeleton sized to real editor */}
      {open && <Editor />}
    </Suspense>
  );
}

// Off-screen image: browser defers it, and dimensions reserve space (no CLS).
<img src="/chart.avif" loading="lazy" width="640" height="360" alt="Sales chart" />
```

**Bad Example** — deferred without reserving space, spinner flash

```jsx
// No dimensions: when the image loads, everything below jumps down (CLS).
<img src="/chart.png" loading="lazy" alt="" />

// Lazy-loads the hero/LCP image — the one thing that should load eagerly.
<img src="/hero.png" loading="lazy" alt="Hero" />

// Bare spinner with no sized container flashes and shifts layout on resolve.
<Suspense fallback={<Spinner />}>
  <Editor />
</Suspense>
```

## Common Mistakes

- Lazy-loading the LCP or above-the-fold image, delaying the most important paint.
- Deferring media without `width`/`height`, causing layout shift when it loads.
- Using scroll event handlers instead of `IntersectionObserver`, adding per-frame work.
- Showing a bare spinner instead of a correctly sized skeleton, so layout jumps twice.
- No fallback or retry when a deferred chunk fails to load (chunk-load errors after a
  deploy are common).
- Loading only at the exact moment of need with no prefetch, so every interaction pays
  full latency.
- Over-splitting into dozens of tiny lazy chunks, so navigation triggers a waterfall of
  requests that's slower than one bundle.

## Production Tips

- Handle dynamic-import failures explicitly: a stale client requesting a chunk that a new
  deploy removed should trigger a reload or a retry, not a blank screen.
- Watch Cumulative Layout Shift in the field — regressions here are almost always a lazy
  resource without reserved space (see [web-vitals](18-web-vitals.md)).
- Prefetch the most likely next route on link hover; measured hover-to-click time is
  usually enough to hide the whole fetch.

## AI Review Checklist

- Is only non-critical, off-screen, or on-demand content deferred (never the LCP image)?
- Does every lazy image/component reserve its final size to prevent layout shift?
- Is `IntersectionObserver` (or native `loading="lazy"`) used instead of scroll handlers?
- Are lazy boundaries given content-shaped skeletons rather than bare spinners?
- Is there a fallback/retry path when a deferred chunk or resource fails to load?
- Is the next likely resource prefetched on idle or hover to hide the latency?
- Is splitting coarse enough to avoid a request waterfall on navigation?

## Related

- `knowledge/performance/10-code-splitting.md`
- `knowledge/performance/07-loading.md`
- `knowledge/performance/11-images.md`
- `knowledge/performance/06-rendering.md`
- `knowledge/performance/18-web-vitals.md`
