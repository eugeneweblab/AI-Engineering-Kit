---
id: html/16-svg
topic: html
slug: svg
title: "SVG"
type: doc
order: 16
status: ready
tags: [html, svg, currentColor, aria-label, aria-hidden, Content-Security-Policy, aria-labelledby, max-width]
related: [html/05-images, html/11-accessibility, html/19-security, html/18-performance, html/17-canvas]
when_to_use: "Read before adding icons, logos, or resolution-independent graphics with SVG."
---
# SVG

## Purpose

This document defines how to use Scalable Vector Graphics in HTML: when to inline
`<svg>` versus reference it as an image, how to make it accessible, how to embed
untrusted SVG safely, and how to keep it performant. SVG is resolution-independent
vector markup — ideal for icons, logos, and diagrams that must stay crisp at any size.

SVG is the right tool for line art, iconography, and anything that scales; the
[`<canvas>`](17-canvas.md) element is the right tool for pixel-level or high-frequency
rendering. This doc covers the vector, DOM-based path. Because SVG is XML that can carry
scripts, it also has a security dimension shared with [HTML security](19-security.md).

## Why It Matters

SVG is deceptively powerful: it is a live DOM subtree, not a flat image. That makes it
stylable, animatable, and accessible — but also means an SVG file can contain
`<script>`, event handlers, and external references. Rendering an untrusted `.svg` as
active markup is an XSS vector. On the other side, teams inline the same icon hundreds
of times and bloat the HTML, or ship SVGs with no accessible name so screen readers
announce nothing. Choosing the right embedding method per situation is what separates a
crisp, safe, lightweight graphic from a liability.

## Core Principles

- **Choose the embedding method by intent.** Inline `<svg>` when you need to style,
  animate, or script it; `<img src="…​.svg">` for a static decorative or content image
  that you do not manipulate.
- **Accessibility is explicit.** SVG has no default accessible name. Add `role="img"`
  plus `<title>` (or `aria-label`) for meaningful graphics; `aria-hidden="true"` for
  purely decorative ones.
- **Untrusted SVG is untrusted code.** SVG can execute script. Never inline user-
  supplied SVG without sanitizing it; serve uploaded SVGs as static files with a strict
  `Content-Security-Policy` and correct content type.
- **Optimize before shipping.** Editor exports carry metadata, comments, and excess
  precision. Run them through an optimizer; the payload often halves.
- **Reuse, do not repeat.** For repeated icons, define once and reference with `<use>`
  or a sprite rather than duplicating the same path many times.

## Best Practices

- Set a `viewBox` on every `<svg>` and size it with CSS (`width`/`height` or
  `max-width`), so it scales fluidly and does not cause layout shift.
- For meaningful inline SVG, add `role="img"` and a `<title>` as the first child (and
  reference it with `aria-labelledby`); for decorative SVG, use `aria-hidden="true"`.
- Give `<img>`-embedded SVGs real `alt` text (or `alt=""` if decorative) exactly like
  any other image — see [images](05-images.md).
- Optimize with SVGO (or equivalent) in the build: strip editor metadata, collapse
  precision, and remove unused `id`s to shrink payload.
- For icon systems, build a sprite (`<symbol>` + `<use href="#icon-x">`) so each glyph
  is defined once and referenced everywhere; it caches and keeps HTML small.
- Sanitize any user-provided SVG server-side with a vetted sanitizer (e.g. DOMPurify in
  SVG mode) before inlining; strip `<script>`, event handlers, and external refs.
- Prefer `currentColor` for icon fills so a single asset inherits the surrounding text
  color instead of shipping multiple color variants.

## Examples

**Good Example** — accessible, reusable, color-inheriting icon

```html
<!-- Define once -->
<svg width="0" height="0" aria-hidden="true">
  <symbol id="icon-check" viewBox="0 0 24 24">
    <path fill="currentColor" d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/>
  </symbol>
</svg>

<!-- Reuse anywhere; labelled for assistive tech, inherits text color -->
<svg role="img" width="24" height="24"><title>Completed</title>
  <use href="#icon-check"></use>
</svg>
```

**Bad Example** — unlabeled, unsafe, unoptimized

```html
<!-- Decorative? Meaningful? No role/title/aria → screen readers say nothing -->
<svg width="24" height="24">
  <!-- fixed color, no viewBox: won't scale, won't inherit theme color -->
  <path fill="#333" d="M9 16.2 4.8 12 3.4 13.4 9 19 21 7 19.6 5.6z"/>
</svg>

<!-- User-uploaded SVG inlined verbatim: can carry <script> → stored XSS -->
<div>{{ user.uploadedSvg }}</div>
```

## Common Mistakes

- Inlining user-uploaded SVG without sanitizing, allowing script execution (XSS).
- No `role="img"` + `<title>` on meaningful SVG, and no `aria-hidden` on decorative SVG.
- Missing `viewBox`, so the graphic does not scale and clips at other sizes.
- Duplicating the same icon path dozens of times instead of using `<symbol>`/`<use>`.
- Shipping raw editor exports with megabytes of metadata and 8-decimal coordinates.
- Hard-coding fill colors instead of `currentColor`, forcing per-theme asset copies.
- Serving user SVGs with an HTML-ish content type, letting the browser execute them.

## Production Tips

- Serve user-uploaded SVGs from a separate, cookieless origin with
  `Content-Type: image/svg+xml`, `Content-Disposition: attachment` where possible, and a
  CSP that blocks script — defense in depth beyond sanitizing.
- Put SVGO in the asset pipeline so every committed SVG is optimized automatically; do
  not rely on authors remembering to optimize.
- For large icon sets, measure whether an inline sprite, external sprite, or per-icon
  `<img>` gives the best cache behavior for your traffic pattern.

## AI Review Checklist

- Is the embedding method chosen by intent (inline to manipulate, `<img>` for static)?
- Does meaningful SVG have `role="img"` and a `<title>`/`aria-label`?
- Is decorative SVG marked `aria-hidden="true"` (or `alt=""` when an image)?
- Is user-supplied SVG sanitized before being inlined?
- Does every `<svg>` have a `viewBox` and scale correctly?
- Are repeated icons defined once and reused via `<symbol>`/`<use>`?
- Are SVGs optimized (metadata stripped) in the build?

## Related

- `knowledge/html/05-images.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/19-security.md`
- `knowledge/html/18-performance.md`
- `knowledge/html/17-canvas.md`
