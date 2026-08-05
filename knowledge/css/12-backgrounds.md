---
id: css/12-backgrounds
topic: css
slug: backgrounds
title: "Backgrounds"
type: doc
order: 12
status: ready
tags: [css, backgrounds, background-color, contain, background-image, rgba, background]
related: [css/11-colors, css/13-borders, css/22-performance, css/23-accessibility]
when_to_use: "Read before applying background colors, images, gradients, or layered fills to any element."
---
# Backgrounds

## Purpose

This document defines how to fill an element's painting area: solid colors, images,
gradients, and layered combinations. It covers the `background` shorthand and its
longhands, the box the background paints into, and how to keep backgrounds performant
and accessible. It is written so an agent can apply a background without breaking text
contrast, layout, or paint performance.

A background is decoration painted *behind* content, inside the border box. It never
affects layout or element size — that is the job of the [box model](04-box-model.md).

## Why It Matters

Backgrounds are where visual design meets two hard constraints: readability and
performance. A background image or gradient placed behind text can silently destroy
contrast, making the page unusable for low-vision users while looking fine on the
designer's monitor. A large or animated background can force the browser to repaint
huge regions every frame, dropping frame rate. Because backgrounds are "just styling,"
these regressions ship unnoticed until an accessibility audit or a performance profile
catches them.

## Core Principles

- **Background is decoration, not content.** Meaningful images belong in `<img>` with
  `alt` text; use CSS backgrounds only for decoration a screen reader can ignore.
- **Always pair a background-image with a fallback background-color.** If the image
  fails to load or is slow, text must still be readable against the color.
- **Guarantee contrast against the darkest and lightest pixels** the text can overlap,
  not the average. A photo with bright and dark regions needs a scrim or overlay.
- **Prefer the shorthand, but know it resets.** `background: red;` clears every other
  background longhand. Set longhands individually when you only mean to change one.
- **Layer with commas, paint front-to-back.** In a multi-value `background`, the first
  layer is on top. Only the last layer may include a `background-color`.

## Best Practices

- Use `background-color` as the base and always declare it, even under an image, so a
  failed or transparent image never leaves unreadable text.
- Size responsive images with `background-size: cover` (fill, may crop) or `contain`
  (fit, may letterbox) rather than fixed pixels, because the element's size varies.
- Reach for CSS `linear-gradient()` / `radial-gradient()` instead of image files for
  simple gradients — they scale, cost no request, and stay crisp at any resolution.
- Darken photos behind text with a gradient overlay layer instead of editing the image,
  so the same asset works on light and dark themes.
- Avoid `background-attachment: fixed` on large areas; it triggers expensive repaints on
  scroll, especially on mobile. Use `position: sticky` or a fixed element instead.
- Set `background-repeat: no-repeat` explicitly whenever you use `cover`/`contain` — the
  default is `repeat`, which can tile a partially loaded image.

## Examples

**Good Example** — fallback color, single-request overlay, readable text

```css
.hero {
  /* Base color guarantees contrast if the image is slow or fails. */
  background-color: #1a1a2e;
  /* Layer 1 (top): a dark scrim so white text stays readable over any photo.
     Layer 2 (bottom): the photo + its fallback color. */
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.55), rgba(0, 0, 0, 0.55)),
    url("/img/hero.jpg");
  background-size: cover;      /* fill the box; crop rather than distort */
  background-position: center; /* keep the focal point visible when cropped */
  background-repeat: no-repeat;/* cover implies one tile; be explicit */
  color: #fff;
}
```

**Bad Example** — no fallback, contrast depends on the image loading

```css
.hero {
  /* No background-color: if hero.jpg is missing or slow, white text sits on
     the page's default background and can vanish entirely. */
  background: url("/img/hero.jpg");
  /* Default is repeat + auto size, so a small image tiles across the hero. */
  color: #fff; /* contrast is unverified against the photo's bright regions */
}
```

## Common Mistakes

- Declaring `background-image` with no `background-color` fallback, so a failed load
  leaves invisible text.
- Using the `background` shorthand to change one property and accidentally wiping the
  rest (position, size, repeat).
- Putting meaningful content (logos, charts, informative photos) in a CSS background,
  where assistive tech cannot read it.
- Assuming `cover` never distorts — it can crop off important parts of an image if
  `background-position` is not set to the focal point.
- Using `background-attachment: fixed` for parallax on mobile, causing jank.
- Checking text contrast against the image's average color instead of its extremes.

## Production Tips

- Serve background photos in a modern format (AVIF/WebP) with an `image-set()` so
  high-DPI screens get a sharper source without over-serving low-DPI ones.
- For large hero images, preload the source (`<link rel="preload" as="image">`) so the
  fallback color is not visible for long.
- Verify contrast with an automated checker at the *lightest* and *darkest* overlap
  points, not a single sample.

## AI Review Checklist

- Does every `background-image` have a `background-color` fallback beneath it?
- Is text contrast verified against the brightest and darkest pixels it can overlap?
- Are decorative-only images in CSS, and meaningful images in `<img>` with `alt`?
- Is `background-repeat: no-repeat` set wherever `cover`/`contain` is used?
- Are simple gradients done in CSS rather than shipped as image files?
- Is `background-attachment: fixed` avoided on large, scrollable surfaces?

## Related

- `knowledge/css/11-colors.md`
- `knowledge/css/13-borders.md`
- `knowledge/css/22-performance.md`
- `knowledge/css/23-accessibility.md`
