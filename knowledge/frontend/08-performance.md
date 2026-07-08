---
id: frontend/08-performance
topic: frontend
slug: performance
title: "Performance"
type: doc
order: 8
status: ready
tags: [frontend, performance]
related: [frontend/07-rendering, frontend/21-code-splitting, frontend/18-assets, frontend/06-data-fetching, frontend/23-monitoring]
when_to_use: "Read before adding a dependency, image, or animation, or when a page feels slow to load or respond."
---
# Performance

## Purpose

This document defines how to build a fast frontend and how to keep it fast: bundle size,
loading strategy, the Core Web Vitals, runtime rendering cost, and measurement. It is
written so an agent can make a change without silently regressing load or interaction speed.

Performance is a feature with a budget, not a cleanup task for later. The primary metrics
are the **Core Web Vitals**: **LCP** (largest content paints ≤ 2.5s), **CLS** (layout shift
≤ 0.1), and **INP** (interaction responds ≤ 200ms). Optimize against these, not vibes.

## Why It Matters

Every 100ms of latency measurably reduces conversion and engagement, and slow pages rank
lower in search. The hard part is that performance decays invisibly: each added dependency,
un-sized image, or extra effect costs a few milliseconds, and no single commit looks guilty
until the page is sluggish and no one knows which change did it. The fix is to treat speed
as a budget you spend deliberately and measure continuously, not a heroic optimization pass
at the end.

## Core Principles

- **Ship less JavaScript.** The bundle is the dominant cost on mobile — it must be
  downloaded, parsed, and executed before the app responds. Every KB of JS costs more than
  a KB of any other asset. Removing code beats optimizing it.
- **Measure before and after; never optimize by guess.** Use real profiles and real-user
  data. The cost of guessing is effort spent on code that was never the bottleneck.
- **Load what's visible now; defer the rest.** Code-split by route, lazy-load below-the-fold
  content, and defer non-critical scripts. Do not make the user download the whole app to see
  one page.
- **Optimize the critical path first.** LCP is set by the largest above-the-fold element;
  make *that* fast before micro-optimizing anything else.
- **Cache aggressively, invalidate correctly.** Immutable, content-hashed assets can be cached
  forever; the only hard part is busting the cache on change, which hashing handles for you.

## Best Practices

- Set a **performance budget** (e.g. JS ≤ 170KB gzip on the main route, LCP ≤ 2.5s) and fail
  CI when a change exceeds it. A budget that is not enforced is a wish.
- **Code-split at route boundaries** and lazy-load heavy, rarely-used components (see
  [code splitting](21-code-splitting.md)). Import large libraries dynamically at point of use.
- Serve images in modern formats (AVIF/WebP), sized to the layout with `srcset`, `width`/
  `height` set, and `loading="lazy"` below the fold. Images are usually the largest bytes.
- **Preload** the LCP resource (hero image, key font) and `preconnect` to critical origins so
  the browser starts the important fetch immediately instead of discovering it late.
- Self-host fonts, subset them, and use `font-display: swap` so text is visible while the font
  loads instead of hidden (which delays LCP).
- Avoid unnecessary re-renders: stable keys, memoize expensive computations, and lift state no
  higher than needed. Do not reach for `memo` everywhere — profile, then memoize hot paths.
- Keep the main thread free: chunk or offload heavy work (Web Workers), debounce input handlers,
  and avoid long synchronous tasks that block interaction and wreck INP.
- Tree-shakeable imports only: `import { x } from "lib"`, never `import * as lib`. Audit the
  bundle with an analyzer before shipping a new dependency.

## Examples

**Good Example** — deferred heavy component, sized lazy image

```tsx
// The chart library (hundreds of KB) is only loaded when the tab is opened,
// keeping it out of the initial bundle and off the critical path.
const Chart = lazy(() => import("./HeavyChart"));

function Report() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button onClick={() => setOpen(true)}>Show chart</button>
      {open && (
        <Suspense fallback={<Skeleton />}>
          <Chart />
        </Suspense>
      )}
      {/* Dimensions reserve space (no CLS); lazy + async decode keep it off the critical path */}
      <img src="/hero.avif" width={800} height={400} loading="lazy" decoding="async" alt="" />
    </>
  );
}
```

**Bad Example** — everything eager, unsized image, blocking work

```tsx
import * as _ from "lodash";        // pulls the whole library into the initial bundle
import HeavyChart from "./HeavyChart"; // loaded even for users who never open the chart

function Report({ rows }: { rows: Row[] }) {
  // Sorting thousands of rows on every render blocks the main thread → poor INP.
  const sorted = rows.slice().sort(expensiveCompare);
  return (
    <>
      <HeavyChart data={sorted} />
      <img src="/hero.png" /> {/* no width/height → layout shift; PNG → oversized bytes */}
    </>
  );
}
```

## Common Mistakes

- Shipping the whole app in one bundle instead of code-splitting by route.
- Importing entire utility libraries (`import * as _`) instead of the used functions.
- Unsized, unoptimized images causing layout shift and bloated LCP.
- Blocking the main thread with heavy synchronous work in render or event handlers.
- Optimizing by guess without profiling, so effort lands on the wrong bottleneck.
- Sprinkling `memo`/`useMemo` everywhere, adding complexity without measuring benefit.
- No performance budget in CI, so regressions ship unnoticed.

## Production Tips

- Track Core Web Vitals from **real users** (field data), not only lab tools; a fast dev
  laptop hides what a mid-range phone on 4G experiences (see [monitoring](23-monitoring.md)).
- Add a bundle-size check to CI that comments the delta on each PR.
- Use a CDN with HTTP/2+ and Brotli compression; serve immutable hashed assets with long TTLs.
- Audit third-party scripts regularly — analytics and tag managers are frequent, invisible
  regressions.

## AI Review Checklist

- Is there an enforced JS/size and LCP budget that this change respects?
- Is code split by route, with heavy/rare components lazy-loaded?
- Are images modern-format, sized, and lazy-loaded below the fold?
- Is the LCP resource preloaded and text visible while fonts load?
- Are imports tree-shakeable, with no full-library imports added?
- Does any handler or render do heavy synchronous work that would hurt INP?
- Are Core Web Vitals measured with real-user data, not just lab runs?

## Related

- `knowledge/frontend/07-rendering.md`
- `knowledge/frontend/21-code-splitting.md`
- `knowledge/frontend/18-assets.md`
- `knowledge/frontend/06-data-fetching.md`
- `knowledge/frontend/23-monitoring.md`
