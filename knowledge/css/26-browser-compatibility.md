---
id: css/26-browser-compatibility
topic: css
slug: browser-compatibility
title: "Browser Compatibility"
type: doc
order: 26
status: ready
tags: [css, browser-compatibility, browserslist, supports, minmax, repeat, subgrid, grid-template-rows]
related: [css/25-modern-css, css/18-media-queries, css/22-performance, css/27-debugging]
when_to_use: "Read before shipping a CSS feature you are unsure is supported, or when a layout works in one browser and breaks in another."
---
# Browser Compatibility

## Purpose

This document defines how to ship CSS that works across the browsers your users actually
run, without either freezing on ancient syntax or shipping features that silently fail.
The goal is *graceful degradation and progressive enhancement*: the page must be usable
everywhere, and better where the browser can do more. This is about deciding what to use,
how to guard it, and how to know it is safe.

## Why It Matters

CSS fails silently. An unknown property or value is ignored — no error, no console warning
— so a broken layout in an untested browser looks fine to the developer who only checks
Chrome. Users on Safari, an in-app WebView, or a locked-down corporate browser get a
degraded or unusable page, and you never hear about it. Unlike JavaScript, you cannot
`try/catch` your way out; correctness has to be designed in with feature detection and
sensible defaults. The cost of getting this wrong is invisible churn.

## Core Principles

- **Progressive enhancement, not graceful hope.** Start from a layout that works with basic
  CSS, then layer enhancements guarded by `@supports`. The base must stand on its own.
- **Detect features, never sniff browsers.** `@supports (feature)` asks the real question;
  user-agent strings lie, change, and are spoofed. Never gate CSS on a browser name.
- **"Ignored" must mean "still usable".** Because unknown CSS is skipped, order declarations
  so the fallback comes first and the enhancement overrides it only where supported.
- **Define your support target explicitly.** "Baseline Widely available" plus your analytics'
  real browser share is the contract; without it, "compatible" is undefined.
- **Test on real engines.** Chromium, Gecko (Firefox), and WebKit (Safari) are three distinct
  engines; passing in one proves nothing about the others.

## Best Practices

- Anchor decisions to **Baseline** (web.dev/baseline) and **caniuse.com**. Treat "Baseline
  Widely available" as ship-freely; guard "Baseline Newly available" features with `@supports`.
- Use **`@supports (property: value)`** to enable enhancements, and `@supports not (...)`
  or a plain preceding declaration for the fallback. Write the fallback first so the cascade
  favors the enhancement only when it works.
- Provide **fallback declarations** for graceful degradation: a `background: #333` before a
  `background: color-mix(...)`, a flex layout before a `subgrid`, a solid color before a
  gradient. Old browsers keep the first valid value they understand.
- Keep **autoprefixer** in the build for vendor-prefixed properties, but do not hand-write
  prefixes — they go stale. Configure it from a `browserslist` that matches your support target.
- Use **`browserslist`** as the single source of truth shared by autoprefixer, bundlers, and
  linters, so "which browsers" is declared once.
- Prefer features with **wide, uniform support** for anything load-bearing (grid, flexbox,
  custom properties, `clamp()` are all safe); reserve the newest features for enhancement.

## Examples

**Good Example** — feature detection with a working fallback

```css
/* Fallback first: every browser understands this and gets a usable single column. */
.gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

/* Enhancement: only browsers that support grid apply the richer layout. */
@supports (display: grid) {
  .gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  }
}

/* Guard a newer value; browsers without it keep the flex/grid layout above. */
@supports (grid-template-rows: masonry) {
  .gallery { grid-template-rows: masonry; }
}
```

**Bad Example** — browser sniffing and unguarded features

```css
/* Gated on a UA class set by JavaScript — brittle, wrong for WebViews, and unmaintainable. */
.is-safari .gallery { display: block; }

/* No fallback: browsers without masonry get NOTHING — items collapse into one column
   with no gap, and there is no console error to reveal it. */
.gallery {
  display: grid;
  grid-template-rows: masonry; /* silently ignored where unsupported */
}
```

## Common Mistakes

- Testing only in Chrome (or only Chromium browsers) and assuming Safari/Firefox match.
- Sniffing the user-agent string to branch CSS instead of using `@supports`.
- Writing the enhancement before the fallback, so unsupported browsers apply the wrong
  value or none.
- Hand-writing vendor prefixes that later go stale, or shipping prefixes autoprefixer would
  add for free.
- Using a bleeding-edge feature for a load-bearing layout with no degradation path.
- Treating in-app WebViews (Instagram, Gmail, embedded) as "just Chrome/Safari" — they lag
  and disable features.

## Production Tips

- Wire a real cross-engine test into CI (Playwright drives Chromium, Firefox, and WebKit)
  and add visual snapshots for critical pages so a regression in one engine fails the build.
- Keep `browserslist` in version control and review it when analytics shift; it silently
  controls how much your build transpiles and prefixes.
- When a bug is engine-specific, reproduce it in that engine's devtools before guessing —
  see [debugging](27-debugging.md) — and check caniuse "known issues" for that feature.

## AI Review Checklist

- Is there a defined support target (Baseline level + `browserslist`)?
- Are newer features guarded with `@supports`, with the fallback declared first?
- Does the base layout work with no enhancements applied?
- Is feature detection used instead of any user-agent sniffing?
- Are vendor prefixes handled by autoprefixer from `browserslist`, not hand-written?
- Has the change been verified on Chromium, Gecko, and WebKit, not just one engine?

## Related

- `knowledge/css/25-modern-css.md`
- `knowledge/css/18-media-queries.md`
- `knowledge/css/22-performance.md`
- `knowledge/css/27-debugging.md`
