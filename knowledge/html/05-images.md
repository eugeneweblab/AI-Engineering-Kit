---
id: html/05-images
topic: html
slug: images
title: "HTML Images"
type: doc
order: 5
status: ready
tags: [html, images, srcset, height, width, sizes, aspect-ratio]
related: [html/04-links, html/11-accessibility, html/16-svg, html/18-performance, html/12-seo]
when_to_use: "Read before adding an <img>, <picture>, or reviewing image alt text, sizing, or loading."
---
# HTML Images

## Purpose

This document defines how to embed raster images correctly with `<img>` and `<picture>`:
writing meaningful `alt` text, preventing layout shift with explicit dimensions, serving
responsive and modern formats, and loading images without hurting performance. It is written
so an agent ships images that are accessible, fast, and stable on the page.

For vector graphics and icons prefer [SVG](16-svg.md); this doc is about photographic and
bitmap content.

## Why It Matters

Images are usually the heaviest bytes on a page and the most common accessibility failure.
Missing or wrong `alt` text makes an image a black hole for screen-reader users and hurts
[SEO](12-seo.md); an image with no width and height triggers a Cumulative Layout Shift that
throws the page around as it loads, a Core Web Vital that directly affects ranking and user
frustration; and shipping a full-resolution JPEG to a phone wastes bandwidth and delays the
Largest Contentful Paint. All three are invisible on a fast desktop connection during
development and painfully visible to real users. Correct image markup is one of the highest-
impact performance and accessibility levers on a page.

## Core Principles

- **Every `<img>` needs an `alt`.** Informative images get descriptive text; purely
  decorative images get `alt=""` (empty, not missing) so assistive tech skips them. Omitting
  `alt` entirely makes a screen reader read the filename.
- **Always reserve space.** Set `width` and `height` (or an `aspect-ratio`) so the browser
  reserves the box before the image loads, preventing layout shift.
- **Serve the right bytes.** Use responsive `srcset`/`sizes` and modern formats (AVIF, WebP)
  so each device downloads an appropriately sized, compressed image.
- **Lazy-load below the fold, prioritize above it.** Off-screen images should defer; the
  hero/LCP image should load eagerly and, where possible, be preloaded.
- **Describe function, not appearance.** `alt` should convey what the image *means or does*
  in context, not a literal visual description.

## Best Practices

- Write `alt` that captures the image's purpose in context; for an image inside a link, the
  `alt` describes the link destination, not the picture. Keep it concise, no "image of…".
- Use `alt=""` for decorative images (background flourishes, spacer icons) so they are
  removed from the accessibility tree rather than announced.
- Always include intrinsic `width` and `height` attributes; combined with CSS `height: auto`
  they preserve aspect ratio while reserving space — see [performance](18-performance.md).
- Use `loading="lazy"` for below-the-fold images and `loading="eager"` (the default) for the
  LCP image; add `fetchpriority="high"` to the hero image to speed first paint.
- Use `<picture>` with `<source type>` to offer AVIF/WebP with a JPEG/PNG fallback, and to
  serve art-directed crops at different breakpoints.
- Provide `srcset` with width descriptors plus a `sizes` attribute so the browser picks the
  right resolution for the viewport and DPR.
- Set `decoding="async"` to keep image decoding off the main rendering path for non-critical images.

## Examples

**Good Example** — accessible, stable, responsive, modern format

```html
<picture>
  <!-- Modern formats first; browser picks the first it supports, falls back to JPEG -->
  <source
    type="image/avif"
    srcset="/hero-480.avif 480w, /hero-960.avif 960w, /hero-1440.avif 1440w"
    sizes="(max-width: 600px) 100vw, 960px" />
  <img
    src="/hero-960.jpg"
    alt="Warehouse team loading a delivery van at sunrise"
    width="960" height="540"
    fetchpriority="high"
    decoding="async" />
</picture>

<!-- Decorative icon: empty alt removes it from the accessibility tree -->
<img src="/divider.svg" alt="" width="200" height="4" />
```

- `src` is the fallback for browsers that support neither AVIF nor WebP.
- `alt` is meaningful in context; the decorative divider takes an empty `alt`, which
  removes it from the accessibility tree.
- `width` and `height` reserve the space, so nothing shifts as the image loads.
- `fetchpriority="high"` marks the LCP image so it is fetched first.

**Bad Example** — inaccessible, layout-shifting, oversized

```html
<img src="/hero.jpg" />
<!-- No alt: screen reader announces "hero.jpg". No width/height: layout jumps on load.
     Full-size JPEG served to every device regardless of viewport. -->

<img src="/photo.jpg" alt="image" />
<!-- alt="image" conveys nothing; "photo" and "image of" add noise, not meaning -->

<img src="/icon.png" alt="decorative divider line" />
<!-- Decorative image given descriptive alt: forces the screen reader to announce clutter -->
```

## Common Mistakes

- Omitting `alt` (filename gets read) or writing filler like `alt="image"`/`alt="photo"`.
- Giving decorative images descriptive `alt` instead of `alt=""`, cluttering screen readers.
- No `width`/`height`, causing layout shift and a poor Cumulative Layout Shift score.
- Serving one large image to all devices instead of `srcset`/`<picture>`.
- Lazy-loading the above-the-fold hero image, delaying the Largest Contentful Paint.
- Using an `<img>` for a decorative CSS-style background that belongs in CSS.
- Redundant `alt` on a linked image that repeats adjacent link text.

## Production Tips

- Generate AVIF/WebP variants and multiple widths at build time via an image pipeline or a
  CDN with on-the-fly transforms; never rely on hand-optimized one-offs.
- Preload the LCP image (`<link rel="preload" as="image">`) when it is not discoverable early
  in the HTML, to shave first-paint time.
- Audit with Lighthouse for "properly sized images", "next-gen formats", and layout-shift
  attributed to images; treat regressions as build failures.

## AI Review Checklist

- Does every `<img>` have an `alt` — descriptive for content, `alt=""` for decoration?
- Does `alt` convey the image's meaning in context, without "image of…" filler?
- Are `width` and `height` (or `aspect-ratio`) set to prevent layout shift?
- Are responsive `srcset`/`sizes` and modern formats used for content images?
- Is the LCP image loaded eagerly (and prioritized), with off-screen images lazy-loaded?
- Are decorative-only visuals moved to CSS backgrounds rather than `<img>`?

## Related

- `knowledge/html/04-links.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/16-svg.md`
- `knowledge/html/18-performance.md`
- `knowledge/html/12-seo.md`
