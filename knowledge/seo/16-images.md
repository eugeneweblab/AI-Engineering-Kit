---
id: seo/16-images
topic: seo
slug: images
title: "SEO Images"
type: doc
order: 16
status: ready
tags: [seo, images, srcset, height, width, aspect-ratio, space]
related: [seo/12-performance, seo/13-core-web-vitals, seo/09-structured-data, seo/05-metadata, seo/17-links]
when_to_use: "Read before adding images to a page, building a gallery, or optimizing image weight and Image Search visibility."
---
# SEO Images

## Purpose

This document defines how to serve images so they help rather than hurt SEO: fast to
load, discoverable in Google Images, accessible, and stable in layout. It covers formats,
sizing, `alt` text, lazy-loading, and image sitemaps so an agent can add media without
regressing performance or losing image-search traffic.

Images are the most common cause of both [Core Web Vitals](13-core-web-vitals.md) failures
(they are usually the LCP element and the top source of layout shift) and page bloat
([Performance](12-performance.md)). Handling them correctly is where those two concerns
become concrete.

## Why It Matters

Images are typically the heaviest bytes on a page, so they dominate load time and Core
Web Vitals — an unoptimized hero image alone can push LCP past the 2.5s threshold. They
are also a discovery channel: Google Images is a large search surface, and it can only
rank images it can find, understand (via `alt` text and surrounding context), and load
quickly. Get them wrong and you pay twice — slower rankings on the main results and zero
presence in image search. And because a missing dimension or a misplaced `alt` never
throws an error, the damage is invisible until a Core Web Vitals report or an
accessibility audit surfaces it.

## Core Principles

- **Modern format, right size, responsive.** Serve **AVIF** or **WebP** (with a fallback)
  instead of JPEG/PNG; they cut bytes 30–50% at equal quality. Never send a 3000px image
  to a 400px slot — serve responsive sizes with `srcset`.
- **Always reserve space.** Set `width` and `height` (or `aspect-ratio`) on every image
  so the browser reserves the box before load. Missing dimensions are the top cause of
  layout shift (CLS).
- **`alt` describes; it is not a keyword dump.** Write concise, accurate `alt` text that
  conveys the image's meaning. It drives accessibility and Image Search relevance.
  Decorative images get empty `alt=""` so screen readers skip them.
- **Lazy-load below the fold, prioritize the hero.** Add `loading="lazy"` to offscreen
  images to save bandwidth, but never to the LCP image — prioritize that one instead.
- **Images need to be crawlable.** Reference them with real `<img src>`/`srcset` (or an
  image sitemap), not only as CSS backgrounds or JS-injected blobs the crawler misses.

## Best Practices

- Use `<img srcset>` + `sizes` (or `<picture>` for art direction / format fallback) so
  the browser picks the smallest sufficient file for the device.
- Preload and set `fetchpriority="high"` on the LCP image; do not lazy-load it (see
  [Performance](12-performance.md)).
- Compress with a build-time pipeline or image CDN; strip EXIF, and target a quality that
  is visually lossless (usually AVIF q≈50 / WebP q≈75).
- Give files descriptive, hyphenated names (`red-leather-satchel.avif`, not `IMG_2931.jpg`)
  — the filename is a weak but real Image Search signal.
- Serve images over the CDN with long-lived, immutable cache headers and content hashes
  in the filename so cache-busting is safe.
- For key visual content (products, recipes, videos), add image URLs to an **image
  sitemap** or `ImageObject` [structured data](09-structured-data.md) to aid discovery.
- Keep decorative/CSS images out of the content flow; reserve `<img>` for meaningful
  imagery you want indexed.

## Examples

**Good Example** — responsive, sized, prioritized hero

```html
<!-- Modern formats with fallback; browser downloads only the size it needs -->
<picture>
  <source
    type="image/avif"
    srcset="/hero-480.avif 480w, /hero-960.avif 960w, /hero-1600.avif 1600w"
    sizes="(max-width: 600px) 100vw, 960px" />
  <img
    src="/hero-960.jpg"
    width="960" height="540"
    fetchpriority="high"
    alt="Barista pouring latte art into a white cup" />
</picture>
<!-- width/height reserve space (no CLS); fetchpriority speeds the LCP paint; no lazy here -->
```

**Bad Example** — oversized, unsized, mis-lazy-loaded

```html
<!-- 4MB PNG, no dimensions (CLS), lazy on the LCP image (delays the measured paint) -->
<img src="/hero-4000px.png" loading="lazy" alt="latte coffee drink cup cafe best coffee" />
<!-- alt is a keyword stuff, not a description; hurts accessibility and looks spammy -->
```

## Common Mistakes

- Shipping full-resolution JPEG/PNG when AVIF/WebP at a responsive size would be a
  fraction of the bytes.
- Omitting `width`/`height`, causing layout shift as images pop in.
- Lazy-loading the LCP/hero image, delaying the exact element the score measures.
- Missing or keyword-stuffed `alt` text — bad for accessibility and Image Search.
- Serving important imagery only as a CSS `background-image`, invisible to Image Search.
- Generic filenames (`IMG_1234.jpg`) that carry no relevance signal.

## Production Tips

- Enforce a per-image and per-page image-weight budget in CI; block PRs that add
  multi-megabyte assets.
- Use an image CDN with automatic format negotiation (AVIF/WebP by `Accept` header) and
  on-the-fly resizing so authors upload one master and the CDN serves the right variant.
- Monitor the Google Images performance report in [Search Console](22-search-console.md)
  and CLS/LCP field data (see [Core Web Vitals](13-core-web-vitals.md)) after image
  changes.

## AI Review Checklist

- Are images served as AVIF/WebP (with fallback) at responsive `srcset` sizes?
- Does every `<img>` have explicit `width`/`height` or `aspect-ratio`?
- Is the LCP image prioritized (preload + `fetchpriority`) and **not** lazy-loaded?
- Are offscreen images `loading="lazy"`?
- Does every meaningful image have concise, descriptive `alt` (and decorative ones `alt=""`)?
- Are important images crawlable via `<img>`/image sitemap, not only CSS backgrounds?

## Related

- `knowledge/seo/12-performance.md`
- `knowledge/seo/13-core-web-vitals.md`
- `knowledge/seo/09-structured-data.md`
- `knowledge/seo/05-metadata.md`
- `knowledge/seo/17-links.md`
