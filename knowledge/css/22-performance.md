---
id: css/22-performance
topic: css
slug: performance
title: "CSS Performance"
type: doc
order: 22
status: ready
tags: [css, performance, will-change, opacity, transform, box-shadow, content-visibility]
related: [css/16-animations, css/14-transforms, css/21-architecture, css/15-transitions, css/26-browser-compatibility]
when_to_use: "Read before shipping CSS that could affect load time or runtime smoothness — large stylesheets, animations, or anything on the critical rendering path."
---
# CSS Performance

## Purpose

This document defines how to write CSS that renders fast and animates smoothly. It
covers the critical rendering path, render-blocking stylesheets, the layout →
paint → composite pipeline, and which properties are cheap to animate versus which
cause jank. It is written so an agent avoids the CSS decisions that visibly slow a page.

CSS performance splits into two questions: *load performance* (how fast the first paint
happens, dominated by render-blocking CSS) and *runtime performance* (how smoothly the
page scrolls and animates, dominated by what the browser must recompute per frame).

## Why It Matters

CSS is render-blocking by default: the browser will not paint until it has downloaded
and parsed the CSS the page needs, so a bloated or slow stylesheet directly delays First
Contentful Paint and hurts Core Web Vitals (and therefore SEO and conversion). At
runtime, animating the wrong property forces the browser to re-run layout for every
element on the page 60 times a second, dropping frames and producing the "janky" feel
users notice immediately. Both failures are invisible in a fast dev environment and only
appear on real devices and networks — which is exactly where users are.

## Core Principles

- **Animate only `transform` and `opacity` for 60fps.** These run on the compositor and
  skip layout and paint. Animating `width`, `top`, `margin`, or `box-shadow` forces
  layout or paint every frame across affected elements — the main cause of jank.
- **Understand the pipeline: layout → paint → composite.** Changing geometry triggers
  layout (most expensive); changing color/shadow triggers paint; changing transform/
  opacity triggers only composite (cheapest). Prefer changes lower in that chain.
- **CSS is render-blocking; ship less of it, sooner.** The critical CSS for above-the-
  fold content should be small and inline or preloaded; defer the rest.
- **`will-change` is a scalpel, not a hammer.** It promotes an element to its own layer
  to prep an animation, but every promoted layer costs memory. Apply it just before an
  animation and remove it after; blanket use degrades performance.
- **Selector cost is real but rarely the bottleneck.** Modern engines match right-to-
  left efficiently; stylesheet *size* and *layout thrash* matter far more than selector
  complexity in practice.

## Best Practices

- Move animations to `transform`/`opacity`; replace `top`/`left` motion with
  `translate()` and size changes with `scale()`.
- Add `content-visibility: auto` (with a `contain-intrinsic-size` estimate) to long,
  off-screen sections so the browser skips their layout and paint until near the
  viewport.
- Inline critical above-the-fold CSS and load the rest with `media`/`preload` tricks or
  route-level splitting so the first paint is not blocked by the whole bundle.
- Reduce shipped CSS: remove dead rules, avoid shipping an entire utility framework
  unpurged, and split by route. Smaller CSS parses faster and blocks less.
- Use `contain: layout paint` on independent components so a change inside one cannot
  invalidate layout for the whole page.
- Respect `prefers-reduced-motion` — the fastest animation is the one you do not run for
  users who asked to avoid motion. See [accessibility](23-accessibility.md).

## Examples

**Good Example** — compositor-only animation, scoped promotion

```css
.panel {
  /* transform + opacity animate on the compositor: no layout, no paint per frame. */
  transition: transform 200ms ease, opacity 200ms ease;
}
.panel.is-open {
  transform: translateX(0);
  opacity: 1;
}
/* Promote only while an interaction is imminent; the JS removes it after. */
.panel:hover { will-change: transform; }

/* Skip layout/paint for off-screen sections until they approach the viewport. */
.long-section { content-visibility: auto; contain-intrinsic-size: 0 800px; }
```

**Bad Example** — layout-triggering animation, global promotion

```css
.panel {
  /* Animating left/width recomputes LAYOUT every frame → dropped frames. */
  transition: left 200ms ease, width 200ms ease;
}
.panel.is-open { left: 0; width: 320px; }

/* will-change on everything forces a layer per element → memory blowout,
   often SLOWER than not using it at all. */
* { will-change: transform; }
```

## Common Mistakes

- Animating `width`, `height`, `top`, `left`, `margin`, or `box-shadow` and expecting
  smoothness — each forces layout or paint per frame.
- Slapping `will-change` on many elements (or `*`), exhausting memory and hurting the
  very performance it was meant to help.
- Shipping one giant render-blocking stylesheet for the whole app instead of critical +
  deferred CSS.
- Leaving an unpurged utility/CSS framework in production, shipping tens of KB of unused
  rules.
- Using deep, expensive selectors under the belief they are the main cost, while the
  real problem is layout thrash or stylesheet size.
- Ignoring `content-visibility` on long pages, paying layout cost for content nobody has
  scrolled to.

## Production Tips

- Profile with DevTools Performance panel: look for purple "Layout" and green "Paint"
  bars during animation — compositor-only animations show neither.
- Measure real Core Web Vitals (LCP, CLS, INP) from field data, not just lab runs; CSS
  regressions surface first on slow devices and networks.
- Watch CLS: reserve space for images/ads/fonts with `aspect-ratio` and sizing so late-
  loading content does not shift layout.

## AI Review Checklist

- Are animations limited to `transform` and `opacity` (compositor-only)?
- Is `will-change` applied narrowly and removed after the animation, never globally?
- Is critical CSS small/inlined and the rest deferred, so first paint is not blocked?
- Is unused CSS purged and the bundle split by route rather than shipped whole?
- Is `content-visibility`/`contain` used to isolate long or independent sections?
- Is layout stability protected (reserved space via `aspect-ratio`) to avoid CLS?

## Related

- `knowledge/css/16-animations.md`
- `knowledge/css/14-transforms.md`
- `knowledge/css/15-transitions.md`
- `knowledge/css/21-architecture.md`
- `knowledge/css/26-browser-compatibility.md`
