---
id: performance/12-fonts
topic: performance
slug: fonts
title: "Fonts"
type: doc
order: 12
status: ready
tags: [performance, fonts]
related: [performance/11-images, performance/07-loading, performance/06-rendering, performance/18-web-vitals, performance/08-caching]
when_to_use: "Read before adding, changing, or reviewing web font loading, @font-face, or Google Fonts usage."
---
# Fonts

## Purpose

This document defines how to load web fonts without blocking rendering or shifting
layout. It is written so an agent can add a typeface to a page — or review one — and
know it will not delay the first paint or move text under the user's cursor.

Fonts are a delivery problem, not a design problem here. A single unoptimized font
can add hundreds of milliseconds of invisible or unstyled text and cause a large
[CLS](18-web-vitals.md) spike. The rules below make font loading fast and stable.

## Why It Matters

Text is the primary content of most pages, so a slow font directly delays the moment
the user can read. Worse, a font that swaps in late reflows the page: the browser
first renders a fallback, then re-renders in the real font at a different width and
height, pushing content around after the user has started reading. That layout shift
is both jarring and a ranking signal. Fonts are also render-blocking by default —
the browser will hide text rather than show it in the wrong face — so a font on the
critical path stalls the [Largest Contentful Paint](18-web-vitals.md) even when the
bytes are small.

## Core Principles

- **The font is on the critical path — treat it like one.** If text needs the font
  to appear, the font's download time is added to your paint time. Minimize it.
- **Never let a font block text indefinitely.** Always define fallback behavior with
  `font-display` so the user reads *something* immediately.
- **Match the fallback to the real font.** Layout shift comes from size mismatch
  between fallback and web font; align their metrics to eliminate it.
- **Ship only the glyphs you use.** Subsetting and modern formats cut font weight by
  50–90% at zero visual cost.
- **Self-host or preconnect.** A third-party font host adds a DNS + TLS round-trip
  before the download even starts.

## Best Practices

- Use **WOFF2** only. It is universally supported in 2026 and 20–30% smaller than
  WOFF. Do not ship TTF, EOT, or SVG fonts to browsers.
- Set `font-display: swap` (show fallback immediately, swap when ready) or `optional`
  (skip the swap entirely if the font is slow) — never leave the default `auto`,
  which blocks text for up to 3 seconds.
- `<link rel="preload" as="font" type="font/woff2" crossorigin>` the one or two fonts
  used above the fold. `crossorigin` is required even for same-origin fonts or the
  preload is ignored.
- **Subset** to the character ranges you actually render (`unicode-range`), and drop
  weights/styles you do not use. Each weight is a separate download.
- Reserve space with `size-adjust`, `ascent-override`, and `descent-override` on a
  fallback `@font-face` so the fallback occupies the same box as the web font,
  giving CLS of zero.
- Self-host font files behind a long `Cache-Control: max-age=31536000, immutable`
  header. If you must use a CDN font host, `preconnect` to it in `<head>`.
- Prefer a variable font when you use three or more weights — one file replaces many.

## Examples

**Good Example** — preloaded, subset, swap, metric-matched fallback

```html
<!-- Preload only the above-the-fold weight; crossorigin is mandatory for fonts -->
<link rel="preload" href="/fonts/inter-var.woff2" as="font"
      type="font/woff2" crossorigin>
```
```css
@font-face {
  font-family: "Inter";
  src: url("/fonts/inter-var.woff2") format("woff2"); /* WOFF2 only */
  font-weight: 100 900;            /* one variable file covers all weights */
  font-display: swap;              /* show fallback now, swap when ready */
  unicode-range: U+0000-00FF;      /* Latin subset — skip unused glyphs */
}
/* Fallback tuned to Inter's metrics so the swap causes no reflow */
@font-face {
  font-family: "Inter-fallback";
  src: local("Arial");
  size-adjust: 107%;
  ascent-override: 90%;
  descent-override: 22%;
}
body { font-family: "Inter", "Inter-fallback", sans-serif; }
```

**Bad Example** — third-party, render-blocking, no fallback control

```html
<!-- Blocks the render tree on a cross-origin stylesheet, then on the font itself.
     No preconnect, default font-display, ships every weight and every glyph. -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900" rel="stylesheet">
```
```css
body { font-family: "Inter", sans-serif; }
/* No font-display → text is invisible for up to 3s while Inter downloads.
   Fallback metrics differ from Inter → layout shifts when it swaps in. */
```

## Common Mistakes

- Leaving `font-display` at the default, hiding all text until the font arrives.
- Preloading a font without `crossorigin`, so the browser downloads it twice.
- Loading fonts from a third-party host without `preconnect`, adding a round-trip.
- Shipping every weight and the full Unicode range when the page uses one weight and
  Latin only.
- No metric-matched fallback, so the swap reflows the page and spikes CLS.
- Preloading every font on the page — preloading everything prioritizes nothing.

## Production Tips

- Measure font impact with a field CLS and LCP breakdown, not just lab tools; slow
  networks expose swap reflow that a fast dev machine hides.
- Generate metric overrides automatically (e.g. the Fontaine/`capsize` approach)
  rather than hand-tuning `size-adjust`.
- Watch total font weight in your [performance budget](23-performance-budget.md);
  fonts silently creep up as designers add weights.

## AI Review Checklist

- Are all fonts served as WOFF2, and nothing older?
- Does every `@font-face` set `font-display` to `swap` or `optional`?
- Are above-the-fold fonts preloaded with `crossorigin`, and only those?
- Are fonts subset (`unicode-range`) to the glyphs actually used?
- Is there a metric-matched fallback so swapping causes no layout shift?
- Are fonts self-hosted with immutable caching, or is the host `preconnect`ed?

## Related

- `knowledge/performance/11-images.md`
- `knowledge/performance/07-loading.md`
- `knowledge/performance/06-rendering.md`
- `knowledge/performance/18-web-vitals.md`
- `knowledge/performance/08-caching.md`
