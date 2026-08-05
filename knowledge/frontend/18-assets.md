---
id: frontend/18-assets
topic: frontend
slug: assets
title: "Assets"
type: doc
order: 18
status: ready
tags: [frontend, assets, immutable, height, width, aspect-ratio, "@font-face", loads]
related: [frontend/08-performance, frontend/19-build-tools, frontend/20-bundling, frontend/15-styling]
when_to_use: "Read before adding images, fonts, icons, or other static files to a frontend app, or reviewing how they are served."
---
# Assets

## Purpose

This document defines how to handle static assets — images, fonts, icons, videos,
and other non-code files — so they load fast, cache correctly, and never block
rendering. It is written so an agent can add or review asset handling without
regressing performance or shipping broken references.

Assets are usually the heaviest bytes on a page. Code you can minify by kilobytes;
an unoptimized hero image costs megabytes. Getting assets right is often the single
largest performance win available. See [performance](08-performance.md) for how this
fits the broader budget.

## Why It Matters

Users judge a site by how fast it *looks* loaded, and that perception is driven by
images and fonts, not by JavaScript. A 3 MB PNG that could have been a 120 KB WebP
delays the Largest Contentful Paint for everyone, on every visit, forever. A font
loaded without a fallback strategy blanks out all text until it arrives. Unlike a
subtle bug, these regressions are visible to every user and directly measured by
Core Web Vitals, which feed search ranking. Assets are also a caching problem: get
the URLs and headers wrong and you either serve stale files or defeat the cache
entirely.

## Core Principles

- **Right format, right size.** Serve modern formats (AVIF/WebP for images, WOFF2
  for fonts) and never ship an image larger than its rendered box on any device.
- **Content-hash immutable assets.** Filenames must contain a hash of their contents
  so they can be cached forever (`immutable`) and busted automatically on change.
- **Reserve space before load.** Every image and embed must declare dimensions so it
  cannot shift layout when it arrives (Cumulative Layout Shift).
- **Lazy by default, eager for the fold.** Below-the-fold media loads on demand;
  the one LCP image loads eagerly with high priority.
- **Let the build own asset URLs.** Import assets so the bundler can hash, inline,
  and optimize them — never hand-write paths into a hashed output directory.

## Best Practices

- Serve responsive images with `srcset`/`sizes` (or `<picture>` for art direction and
  format fallbacks) so each device downloads only the pixels it needs.
- Always set `width` and `height` (or a CSS `aspect-ratio`) on `<img>` to prevent CLS.
- Add `loading="lazy"` and `decoding="async"` to off-screen images; give the LCP image
  `fetchpriority="high"` and never lazy-load it.
- Self-host fonts as WOFF2, subset to the characters you use, and set
  `font-display: swap` (or `optional`) so text renders immediately with a fallback.
- Preload the critical font and LCP image with `<link rel="preload">`; preconnect to
  any third-party asset origin you cannot avoid.
- Inline tiny assets (SVG icons, <4 KB images) as data URIs or components to save a
  request; keep large ones as separate cacheable files.
- Store user-generated and large media on a CDN with `Cache-Control: public,
  max-age=31536000, immutable` for hashed files.
- Compress SVGs (SVGO) and strip metadata from raster images at build time.

## Examples

**Good Example** — responsive, sized, prioritized correctly

```html
<!-- LCP hero: eager, high priority, dimensions reserved, modern format first -->
<picture>
  <source srcset="/img/hero.avif" type="image/avif" />
  <source srcset="/img/hero.webp" type="image/webp" />
  <img
    src="/img/hero.jpg"
    width="1200" height="600"   <!-- reserves space → no layout shift -->
    fetchpriority="high"        <!-- LCP image, load it first -->
    alt="Team collaborating in an office"
  />
</picture>

<!-- Below the fold: defer the download until it is near the viewport -->
<img
  src="/img/chart.webp"
  width="640" height="360"
  loading="lazy" decoding="async"
  alt="Quarterly revenue chart"
/>
```

**Bad Example** — heavy, unsized, blocks paint

```html
<!-- 3 MB PNG, no dimensions, lazy-loaded even though it is the LCP element -->
<img src="/uploads/hero-original.png" loading="lazy" />
<!-- WHY BAD: no width/height → layout jumps when it loads (CLS);
     lazy on the LCP image delays it; PNG is 10x larger than AVIF;
     path points at an unhashed file so it can never be cached forever. -->

<style>
  /* Blocks first paint: invisible text until the webfont downloads */
  @font-face { font-family: Inter; src: url(/fonts/inter.ttf); } /* no swap, TTF not WOFF2 */
</style>
```

## Common Mistakes

- Shipping camera-original JPEG/PNG files instead of resized, modern formats.
- Omitting `width`/`height`, causing layout shift as images stream in.
- Lazy-loading the LCP image, delaying the most important paint.
- Loading fonts without `font-display`, producing invisible text (FOIT).
- Referencing assets by hand-written path instead of importing them, so the bundler
  cannot hash or optimize them and links silently break on rename.
- Serving hashed assets without `immutable` caching, wasting revalidation round-trips.
- Loading icon fonts or full SVG sprites when a handful of inline icons would do.

## Production Tips

- Set a per-page asset weight budget and fail CI when a build exceeds it.
- Generate AVIF/WebP variants at build time or via an image CDN with on-the-fly
  transforms keyed by `Accept` and device pixel ratio.
- Audit real assets with Lighthouse and WebPageTest, not local dev where the cache hides
  cost.
- Add `Cross-Origin-Resource-Policy` and correct `crossorigin` on preloaded fonts to
  avoid double downloads.

## AI Review Checklist

- Are images served in AVIF/WebP and sized to their rendered dimensions?
- Does every `<img>` declare `width`/`height` or `aspect-ratio` to prevent CLS?
- Is the LCP image eager with `fetchpriority="high"`, and everything else lazy?
- Are fonts self-hosted WOFF2, subset, with `font-display: swap`?
- Are assets imported so the build hashes them, and served `immutable`?
- Are critical font and LCP image preloaded, with preconnect to third-party origins?

## Related

- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/19-build-tools.md`
- `knowledge/frontend/20-bundling.md`
- `knowledge/frontend/15-styling.md`
