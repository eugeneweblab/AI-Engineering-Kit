---
id: html/18-performance
topic: html
slug: performance
title: "HTML Performance"
type: doc
order: 18
status: ready
tags: [html, performance]
related: [html/05-images, html/09-media, html/10-metadata, html/20-browser-rendering, html/23-progressive-enhancement]
when_to_use: "Read before writing or reviewing markup that affects page load, Core Web Vitals, or resource fetching."
---
# HTML Performance

## Purpose

This document defines how to write HTML that loads fast and stays responsive. It
covers the markup-level decisions — resource hints, image and script loading
attributes, render-blocking order, and layout stability — that determine a page's
Core Web Vitals before a single line of CSS or JavaScript runs.

Performance here means the *document's* contribution to speed. It is upstream of
[browser rendering](20-browser-rendering.md): the HTML you ship decides what the
browser must fetch, in what order, and how much it reflows.

## Why It Matters

The browser starts building the page the moment the first bytes of HTML arrive, and
it acts on your markup literally: a synchronous `<script>` in the `<head>` halts
parsing, an `<img>` without dimensions shifts the whole layout when it loads, and a
missing preload delays the fonts a user is waiting to read. These costs are invisible
in a fast office network and brutal on a mid-range phone over 4G — which is most of
the real world. Markup mistakes cannot be fixed by faster hardware; they are paid on
every visit, by every user, before your application code even executes.

## Core Principles

- **The parser is a critical path — do not block it.** Anything synchronous in the
  document head delays first paint. Defer or async everything that can wait.
- **Reserve space for everything that arrives late.** Images, ads, and embeds must
  declare their dimensions so late-loading content does not shove the page around.
- **Hint the browser toward the critical resource.** The browser cannot see a
  CSS-referenced font or a JS-injected image until late; tell it early with resource
  hints so the fetch overlaps parsing.
- **Load only what the first screen needs.** Below-the-fold images and offscreen
  iframes should be lazy; the hero image should not.
- **Send less HTML.** Every byte of markup is parsed on the main thread. Deeply
  nested wrappers and inlined data cost real time on slow devices.

## Best Practices

- Add `width` and `height` (or `aspect-ratio` in CSS) to every `<img>` and `<video>`
  so the browser reserves layout space — this is the single biggest lever on
  Cumulative Layout Shift (CLS).
- Mark the largest above-the-fold image with `fetchpriority="high"` and never lazy-load
  it; it is usually the Largest Contentful Paint (LCP) element.
- Add `loading="lazy"` to below-the-fold images and iframes so they fetch only when
  near the viewport. The cost is a small delay if the user scrolls fast — acceptable
  for offscreen content, never for the LCP image.
- Load scripts with `defer` (executes in order after parsing) or `async` (executes
  ASAP, unordered). Reserve blocking `<script>` for the rare code that must run before
  first paint.
- Preconnect to critical third-party origins and preload the LCP image and web fonts:
  `<link rel="preload" as="font" crossorigin>`. Preload only a few resources — over-use
  contends with the critical path.
- Serve responsive images with `srcset`/`sizes` so phones do not download desktop-sized
  pixels. See [images](05-images.md).
- Keep the `<head>` small and put render-blocking CSS first; the browser needs the full
  head before it paints.

## Examples

**Good Example** — non-blocking scripts, sized media, prioritized LCP

```html
<head>
  <link rel="preconnect" href="https://cdn.example.com" crossorigin />
  <!-- Preload the LCP hero so its fetch overlaps HTML parsing -->
  <link rel="preload" as="image" href="/hero.avif" fetchpriority="high" />
  <link rel="stylesheet" href="/app.css" />
  <!-- defer: fetched in parallel, executed in order after the DOM is parsed -->
  <script src="/app.js" defer></script>
</head>
<body>
  <!-- Dimensions reserve space → no layout shift when the image decodes -->
  <img src="/hero.avif" width="1200" height="600" fetchpriority="high" alt="..." />
  <!-- Offscreen images fetch only when scrolled near -->
  <img src="/footer.avif" width="800" height="400" loading="lazy" alt="..." />
</body>
```

**Bad Example** — blocking script, unsized images, lazy hero

```html
<head>
  <!-- Synchronous script in head: parsing STOPS until this downloads and runs -->
  <script src="/analytics.js"></script>
</head>
<body>
  <!-- No dimensions: layout jumps when the image loads → high CLS -->
  <img src="/hero.jpg" alt="..." />
  <!-- Lazy-loading the LCP image delays the largest paint → worse LCP -->
  <img src="/hero.jpg" loading="lazy" alt="..." />
</body>
```

## Common Mistakes

- Omitting `width`/`height` on images, causing layout shift as they load.
- Lazy-loading the hero/LCP image, which delays the metric it should optimize.
- A synchronous `<script>` in `<head>` that blocks parsing and first paint.
- Preloading dozens of resources, so the browser cannot tell what is actually critical.
- Shipping one image size to all devices instead of `srcset`/`sizes`.
- Inlining large base64 blobs or JSON into the HTML, bloating the parse cost.

## Production Tips

- Measure with real-device field data (Core Web Vitals in the Chrome UX Report), not
  just lab tools — lab conditions hide slow-network regressions.
- Set a performance budget in CI (e.g. Lighthouse assertions on LCP/CLS) so a heavy
  markup change fails the build instead of shipping silently.
- Audit resource hints periodically; a stale `preconnect` to a retired CDN is wasted
  connection budget.

## AI Review Checklist

- Does every `<img>`/`<video>` declare `width`/`height` or an aspect ratio?
- Is the LCP image eagerly loaded with `fetchpriority="high"` and never `loading="lazy"`?
- Do below-the-fold images and iframes use `loading="lazy"`?
- Are scripts `defer`/`async` rather than blocking the parser in `<head>`?
- Are preload/preconnect hints limited to genuinely critical resources?
- Do images use `srcset`/`sizes` to avoid oversized downloads on small screens?

## Related

- `knowledge/html/05-images.md`
- `knowledge/html/09-media.md`
- `knowledge/html/10-metadata.md`
- `knowledge/html/20-browser-rendering.md`
- `knowledge/html/23-progressive-enhancement.md`
