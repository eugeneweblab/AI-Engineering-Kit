---
id: seo/12-performance
topic: seo
slug: performance
title: "SEO Performance"
type: doc
order: 12
status: ready
tags: [seo, performance, Cache-Control, no-store]
related: [seo/13-core-web-vitals, seo/16-images, seo/04-rendering, seo/19-javascript-seo, seo/24-monitoring]
when_to_use: "Read before optimizing page load speed, shipping large bundles, or diagnosing a crawl-budget or ranking drop tied to slowness."
---
# SEO Performance

## Purpose

This document defines how page performance affects search: crawl efficiency, indexing,
and ranking. It covers the load-time factors an engineer controls in code —
payload size, request count, render-blocking resources, and server response time — so an
agent can build fast pages and diagnose slow ones without guesswork.

Performance and [Core Web Vitals](13-core-web-vitals.md) are related but distinct.
Core Web Vitals are the *specific user-centric metrics* Google measures and ranks on;
this doc covers the *engineering causes* behind those metrics and the crawl-time
consequences of a slow server.

## Why It Matters

Slow pages hurt SEO in two independent ways. First, page speed is a ranking signal:
between two comparable results, the faster one wins, and a slow site loses ground on
mobile where most searches happen. Second — and easier to miss — a slow *server* burns
crawl budget: Googlebot throttles its request rate when responses lag, so a slow origin
gets fewer pages crawled per day, and new or updated content is indexed later. A page
that takes eight seconds to respond is not just a bad experience; it is a page the engine
may not fetch at all today. Speed is cheap to protect at build time and expensive to
retrofit once the bundle and the database are load-bearing.

## Core Principles

- **Server response time gates everything.** Time to First Byte (TTFB) is the floor for
  every downstream metric. Aim for TTFB under 200ms from cache, under 600ms uncached.
  A slow origin caps both user experience and crawl rate.
- **Ship less.** The fastest resource is the one you never send. Every kilobyte of JS,
  CSS, font, and image is a cost the browser and the crawler pay. Measure payload weight
  as a budget, not an afterthought.
- **Do not block the render.** Render-blocking CSS and synchronous JS in the `<head>`
  delay first paint. Defer, async, or inline-critical anything that stands between the
  request and visible content.
- **Cache aggressively, invalidate deliberately.** A CDN edge cache and correct
  `Cache-Control` headers cut TTFB and origin load. Static content should almost never
  hit your application server.
- **Measure the real world, not your laptop.** Optimize against field data (75th
  percentile, mobile) — see [Monitoring](24-monitoring.md) — not a fast local run.

## Best Practices

- Set a **performance budget** in CI (for example, ≤ 170KB compressed JS per route) and
  fail the build when a change exceeds it. Regressions are invisible without a gate.
- Serve HTML from a CDN edge cache where possible; use stale-while-revalidate so users
  and crawlers get a fast cached response while the origin refreshes in the background.
- Compress text responses with **Brotli** (fallback gzip). It is a header and a config
  line, and it typically cuts transfer size 15–20% over gzip.
- Preload the LCP resource (hero image or web font) with `<link rel="preload">` so the
  browser fetches it before it discovers it in the parse.
- Self-host fonts, subset them, and set `font-display: swap` so text is never invisible
  while a font loads.
- Code-split by route and lazy-load below-the-fold and interaction-only components. Do
  not ship the checkout bundle to the homepage.
- Use HTTP/2 or HTTP/3 so many small requests multiplex over one connection; with modern
  protocols, per-file concatenation matters less than total bytes.
- Add `loading="lazy"` to offscreen images and `fetchpriority="high"` to the LCP image
  (see [Images](16-images.md)).

## Examples

**Good Example** — cacheable, non-blocking, prioritized

```html
<head>
  <!-- Preconnect + preload the LCP image so it fetches during HTML parse -->
  <link rel="preload" as="image" href="/hero.avif" fetchpriority="high" />
  <!-- Critical CSS inlined; the rest loads without blocking first paint -->
  <style>/* above-the-fold rules only */</style>
  <link rel="stylesheet" href="/full.css" media="print" onload="this.media='all'" />
  <!-- App JS is deferred: it runs after HTML parse, never blocking render -->
  <script src="/app.js" defer></script>
</head>
```

```
Cache-Control: public, max-age=0, s-maxage=3600, stale-while-revalidate=86400
Content-Encoding: br
# CDN serves fresh HTML for an hour, then serves stale instantly while revalidating.
```

**Bad Example** — render-blocking, uncached, oversized

```html
<head>
  <!-- Synchronous script in <head> blocks the parser and delays first paint -->
  <script src="/vendor-bundle-900kb.js"></script>
  <!-- Blocking stylesheet with no critical-CSS split: nothing renders until it loads -->
  <link rel="stylesheet" href="/everything.css" />
</head>
```

```
Cache-Control: no-store   # every request hits the origin; TTFB balloons, crawl rate drops
```

## Common Mistakes

- Optimizing images and lazy-loading while the origin still returns HTML in 2–5s. Fix
  TTFB first; it caps everything else.
- Shipping one giant JS bundle for every route instead of code-splitting.
- `Cache-Control: no-store` on HTML that is identical for all users, forcing every
  crawler fetch to hit the application server.
- Lazy-loading the LCP image, which delays the single element the score is measured on.
- Blocking rendering on third-party tags (chat widgets, A/B tools) loaded synchronously
  in the `<head>`.
- Treating a fast local Lighthouse run as proof; real users on mobile networks are far
  slower.

## Production Tips

- Put a real-user monitoring (RUM) beacon on the site and watch p75 mobile TTFB and LCP
  by route; alert on regressions. See [Monitoring](24-monitoring.md).
- Watch the Crawl Stats report in [Search Console](22-search-console.md): rising average
  response time correlates with falling pages-crawled-per-day.
- Run Lighthouse (or an equivalent) in CI on key routes with mobile throttling, and fail
  the PR when the performance score or a budget regresses.

## AI Review Checklist

- Is there a JS/CSS payload budget enforced in CI for each route?
- Is HTML served from an edge cache with correct `Cache-Control`, not `no-store`?
- Are text responses Brotli/gzip compressed?
- Is all render-blocking JS deferred/async and non-critical CSS non-blocking?
- Is the LCP resource preloaded and prioritized, not lazy-loaded?
- Is TTFB measured and under target (≤ 200ms cached / ≤ 600ms uncached) at p75?

## Related

- `knowledge/seo/13-core-web-vitals.md`
- `knowledge/seo/16-images.md`
- `knowledge/seo/04-rendering.md`
- `knowledge/seo/19-javascript-seo.md`
- `knowledge/seo/24-monitoring.md`
