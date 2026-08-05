---
id: performance/11-images
topic: performance
slug: images
title: "Performance Images"
type: doc
order: 11
status: ready
tags: [performance, images]
related: [performance/07-loading, performance/09-lazy-loading, performance/08-caching, performance/18-web-vitals, performance/06-rendering]
when_to_use: "Read before adding, serving, or reviewing any image on a page — especially hero images, thumbnails, and galleries."
---
# Performance Images

## Purpose

This document defines how to deliver images that look right and cost little: modern
formats, correct sizing, responsive sources, and lazy delivery. It is written so an
agent can add images to a page without inflating its weight or shifting its layout.

Images are usually the heaviest bytes on a page. The goal is to send each user the
*smallest image that still looks sharp on their screen* — the right format, the right
dimensions, encoded well, and loaded at the right time.

## Why It Matters

Images typically dominate page weight — often more than all the JavaScript, CSS, and
fonts combined. An unoptimized hero image can be several megabytes when a well-encoded
one would be a few hundred kilobytes, and it is frequently the Largest Contentful Paint
element, so it directly sets the LCP score ([web-vitals](18-web-vitals.md)). Images are
also a top cause of layout shift when dimensions aren't reserved. Because the win is
large and mostly mechanical — format, size, compression — leaving images unoptimized is
one of the most common and most wasteful performance mistakes.

## Core Principles

- **Serve the right dimensions, not the source file.** Never ship a 4000px photo to a
  400px slot. Resize to the largest size actually displayed, per device.
- **Use modern formats.** AVIF and WebP are far smaller than JPEG/PNG at equal quality.
  Serve them with a fallback, and reserve SVG for icons/line art, not photos.
- **Reserve layout space.** Always declare `width`/`height` or `aspect-ratio` so the
  browser lays out the box before the image arrives (prevents CLS).
- **Match delivery to importance.** The LCP image loads eagerly and with high priority;
  everything below the fold loads lazily ([lazy-loading](09-lazy-loading.md)).
- **Compress deliberately.** Photos tolerate lossy compression well; there is almost
  always a quality setting that saves large bytes with no visible difference.

## Best Practices

- Encode photos as AVIF (best ratio) or WebP with a JPEG fallback via `<picture>`; the
  browser picks the first format it supports.
- Provide responsive sources with `srcset` + `sizes` so each device downloads a size
  matched to its viewport and pixel density, not one worst-case image for all.
- Always set intrinsic `width` and `height` attributes (or CSS `aspect-ratio`); this is
  the single most effective fix for image-caused layout shift.
- Lazy-load below-the-fold images with `loading="lazy"`; load the LCP/above-the-fold
  image eagerly with `fetchpriority="high"` and preload it if late-discovered.
- Compress to a target quality (roughly 60-80 for photos) and strip metadata; verify the
  result visually rather than shipping the encoder default.
- Cache images aggressively with content-hashed URLs and long `max-age, immutable`
  headers (see [caching](08-caching.md)); serve through a CDN close to users.
- Use an image CDN or build-time pipeline to generate formats and sizes automatically;
  hand-optimizing every asset doesn't scale.
- Give every meaningful image descriptive `alt` text; use empty `alt=""` for purely
  decorative images so screen readers skip them.

## Examples

**Good Example** — modern formats, responsive, sized, prioritized

```html
<picture>
  <!-- Browser picks the first supported format; AVIF is smallest. -->
  <source
    type="image/avif"
    srcset="/hero-480.avif 480w, /hero-960.avif 960w, /hero-1600.avif 1600w"
    sizes="(max-width: 600px) 100vw, 960px" />
  <source type="image/webp" srcset="/hero-960.webp 960w, /hero-1600.webp 1600w" />
  <!-- Dimensions reserve space (no CLS); high priority because this is the LCP image. -->
  <img src="/hero-960.jpg" width="960" height="540"
       fetchpriority="high" alt="Team collaborating in an office" />
</picture>
```

**Bad Example** — oversized, single format, shifts layout

```html
<!-- 4000x2250 PNG (~5 MB) scaled down by CSS: full bytes downloaded, then shrunk. -->
<!-- No width/height: layout jumps when it loads. No lazy hint, no priority, no alt. -->
<img src="/hero-original.png" style="width: 100%" />
```

## Common Mistakes

- Shipping a source-resolution image and shrinking it with CSS, wasting bandwidth.
- Using PNG/JPEG where AVIF/WebP would be a fraction of the size.
- Omitting `width`/`height`, causing layout shift as each image loads.
- Lazy-loading the LCP/hero image, delaying the most important paint.
- One fixed image for all viewports instead of `srcset`/`sizes` responsive sources.
- Skipping compression and shipping the encoder's default (often far larger than needed).
- Missing or unhelpful `alt` text, hurting accessibility and SEO.
- Not serving images through a CDN with long-lived, content-hashed caching.

## Production Tips

- Automate format/size generation in the build or via an image CDN so correctness doesn't
  depend on a human remembering to optimize each asset.
- Track the LCP element in the field; if it's an image, its format/size/priority is the
  highest-leverage fix available (see [monitoring](17-monitoring.md)).
- Add an image-weight check to the performance budget so a large asset fails CI instead of
  reaching production.

## AI Review Checklist

- Are photos served as AVIF/WebP with an appropriate fallback via `<picture>`?
- Do images use `srcset`/`sizes` so each device downloads a right-sized source?
- Does every image declare `width`/`height` or `aspect-ratio` to prevent layout shift?
- Is the LCP image eager + high priority, and are below-fold images lazy-loaded?
- Are images compressed to a sensible quality, not shipped at encoder defaults?
- Are images served via a CDN with content-hashed, long-lived cache headers?
- Does every meaningful image have descriptive `alt` (or `alt=""` if decorative)?

## Related

- `knowledge/performance/07-loading.md`
- `knowledge/performance/09-lazy-loading.md`
- `knowledge/performance/08-caching.md`
- `knowledge/performance/18-web-vitals.md`
- `knowledge/performance/06-rendering.md`
