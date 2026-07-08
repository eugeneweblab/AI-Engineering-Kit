---
id: performance/07-loading
topic: performance
slug: loading
title: "Loading"
type: doc
order: 7
status: ready
tags: [performance, loading]
related: [performance/10-code-splitting, performance/09-lazy-loading, performance/08-caching, performance/11-images, performance/18-web-vitals]
when_to_use: "Read before building or reviewing a page's initial load path, critical rendering path, or resource fetch order."
---
# Loading

## Purpose

This document defines how to get a page to *usable* as fast as possible: the critical
rendering path, resource priority, and what to load now versus later. It is written so
an agent can structure a page's initial load without shipping a slow, blocking start.

Loading is about the first few seconds — the gap between a click and a working page.
The goal is to deliver the smallest set of resources needed to render and interact,
in the right order, and defer everything else.

## Why It Matters

First impressions are load impressions. Largest Contentful Paint and Time to
Interactive decide whether a user waits or leaves; bounce rate climbs sharply past a
few seconds. The critical path is fragile: one render-blocking stylesheet, one
synchronous script in `<head>`, or one oversized bundle stalls *everything* behind it.
Because the browser can only act on resources it has discovered, a badly ordered load
wastes the connection sitting idle. These costs land on every first visit and hit
slow networks and mobile hardest.

## Core Principles

- **Critical path first.** Identify the minimum resources needed for first render and
  interaction; load those with high priority and defer the rest.
- **Don't block rendering.** CSS blocks paint and synchronous JS blocks parsing. Inline
  critical CSS, and load scripts with `defer`/`async` or `type="module"`.
- **Discover early, fetch in parallel.** The browser can only fetch what it has parsed.
  Use `<link rel="preload">` for late-discovered critical assets and preconnect to
  required origins.
- **Ship less.** The fastest resource is the one you never send. Split bundles
  ([code-splitting](10-code-splitting.md)) and remove unused code and dependencies.
- **Show progress, not a blank screen.** Stream HTML and render meaningful content
  early so the user sees something before everything finishes.

## Best Practices

- Inline the critical CSS needed for above-the-fold content and load the rest
  asynchronously. Render-blocking CSS delays first paint for the whole page.
- Add `defer` to scripts that touch the DOM and `async` to independent third-party
  scripts. Never put a synchronous `<script>` in `<head>` that blocks the parser.
- Preload a small number of late-discovered critical resources (hero image, key font,
  main module) with `<link rel="preload">`; over-preloading contends for bandwidth.
- `preconnect` to origins you will definitely fetch from (API, CDN, font host) so the
  TLS/DNS handshake overlaps with parsing instead of blocking a later request.
- Set `fetchpriority="high"` on the LCP image and `fetchpriority="low"` on below-fold
  assets to steer the browser's scheduler.
- Prefer server-side rendering or streaming for content pages so the user sees real
  HTML before hydration; hydrate progressively.
- Keep the initial JS bundle small (a budget, see [performance-budget](23-performance-budget.md));
  route- and component-level splitting keeps the first payload lean.
- Serve compressed (Brotli) and over HTTP/2 or HTTP/3 so many small resources multiplex
  on one connection.

## Examples

**Good Example** — non-blocking, prioritized load

```html
<head>
  <style>/* critical above-the-fold CSS, inlined */</style>
  <link rel="preconnect" href="https://api.example.com" />
  <!-- Preload the LCP image so it starts before CSS finishes parsing. -->
  <link rel="preload" as="image" href="/hero.avif" fetchpriority="high" />
  <!-- defer: runs after parse, in order, without blocking rendering. -->
  <script src="/app.js" defer></script>
  <link rel="stylesheet" href="/non-critical.css" media="print" onload="this.media='all'" />
</head>
```

**Bad Example** — render-blocking, serialized start

```html
<head>
  <!-- Blocks HTML parsing until the whole bundle downloads and executes. -->
  <script src="/vendor-bundle.js"></script>
  <!-- Render-blocking: nothing paints until this large sheet arrives. -->
  <link rel="stylesheet" href="/all-styles.css" />
  <!-- Hero image only discovered after CSS parses; starts late. -->
</head>
<body><img src="/hero.png" /></body> <!-- huge PNG, no priority hint -->
```

## Common Mistakes

- A synchronous `<script>` in `<head>` that blocks parsing of the rest of the page.
- Shipping one giant CSS/JS bundle instead of splitting the critical from the deferred.
- Not preconnecting to the API/CDN, so the first request pays full DNS+TLS latency.
- Preloading too many resources, so critical assets contend for the same bandwidth.
- Client-rendering a content page that could stream server HTML, leaving a blank screen.
- Blocking first paint on web fonts instead of using `font-display: swap`
  (see [fonts](12-fonts.md)).
- Loading below-the-fold and third-party scripts at the same priority as critical code.

## Production Tips

- Measure the critical path in the field: LCP, TTFB, and total blocking time under real
  networks (see [web-vitals](18-web-vitals.md) and [monitoring](17-monitoring.md)).
- Use the browser waterfall to find serialized requests that should be parallel and
  resources fetched later than they were needed.
- Set a load performance budget in CI so a new dependency can't silently regress the
  initial payload.

## AI Review Checklist

- Is critical CSS inlined and non-critical CSS loaded asynchronously?
- Do all scripts use `defer`/`async`/modules, with no parser-blocking `<script>`?
- Are late-discovered critical assets preloaded, and required origins preconnected?
- Does the LCP resource have a high fetch priority and an appropriate format?
- Is the initial JS payload split and within a defined budget?
- Does the page render meaningful content (SSR/streaming) before full hydration?
- Are responses compressed with Brotli and served over HTTP/2 or HTTP/3?

## Related

- `knowledge/performance/10-code-splitting.md`
- `knowledge/performance/09-lazy-loading.md`
- `knowledge/performance/08-caching.md`
- `knowledge/performance/11-images.md`
- `knowledge/performance/18-web-vitals.md`
