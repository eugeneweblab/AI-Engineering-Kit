---
id: divi/10-performance
topic: divi
slug: performance
title: "Divi Performance"
type: doc
order: 10
status: ready
tags: [divi, performance, JavaScript, weight, vitals, launching]
related: [divi/09-custom-css, divi/06-global-elements, divi/11-responsive-design, divi/13-seo, divi/25-production]
when_to_use: "Read before launching a Divi site or when Core Web Vitals / page weight are unacceptable."
---
# Divi Performance

## Purpose

This document defines how to make a Divi site fast: enabling Divi's performance engine,
controlling CSS/JS payload, optimizing images, and avoiding the module-level habits that bloat
pages. It is written so an agent can build or audit a Divi site against Core Web Vitals (LCP,
CLS, INP) rather than shipping the megabyte-heavy default that gives Divi its bad reputation.

Divi *can* be fast — the current builder ships critical-CSS inlining, deferred/dynamic CSS and
JS, and dynamic module framework loading — but these are opt-in and undone by undisciplined use.

## Why It Matters

Page weight is a direct business and ranking cost: LCP and INP are Google ranking signals, and
every 100 KB of blocking CSS/JS delays first paint on real mobile devices. Divi's failure mode is
death by a thousand cuts — a hundred lightly-configured modules, per-module custom CSS, unlazy
full-resolution images, and three page-builder plugins stacked together — none fatal alone, all
fatal together. Because the bloat is diffuse, it is far cheaper to prevent than to diagnose after
launch. Performance is a build-time discipline, not a post-launch plugin you bolt on.

## Core Principles

- **Turn on Divi's performance features first.** Enable Dynamic CSS, Dynamic Module Framework,
  Critical CSS, and deferred/dynamic JavaScript in Theme Options → Performance. They are off or
  partial on some setups; verify. The cost of leaving them off is a much larger baseline payload.
- **Fewer, well-configured modules beat many.** Every unique module configuration adds CSS. Reuse
  (globals, presets) collapses variants into one. See [global-elements](06-global-elements.md).
- **Images are usually the LCP.** Serve correctly-sized, next-gen (WebP/AVIF) images, lazy-load
  below the fold, and set explicit dimensions to avoid layout shift (CLS).
- **CSS lives in the right layer.** Per-module CSS multiplies payload; shared classes in the child
  theme do not. See [custom-css](09-custom-css.md).
- **Measure on mobile, not your laptop.** Optimize against throttled mobile Lighthouse/CrUX field
  data; desktop numbers hide the problems users actually hit.
- **Don't stack builders/plugins.** Divi plus a second page builder plus a heavyweight slider
  plugin loads three frameworks for one page. Pick one.

## Best Practices

- In Theme Options → Performance, enable Dynamic CSS, Critical CSS, Dynamic Module Framework, and
  deferred/dynamic JS. Confirm with a network trace that dynamic CSS is actually splitting.
- Compress and resize images before upload; serve WebP/AVIF; let Divi/WordPress lazy-load offscreen
  images but **eagerly** load the LCP (hero) image so it is not deferred.
- Set explicit width/height (or aspect-ratio) on images and reserve space for embeds to keep CLS
  near zero.
- Preload the hero image and the primary web font; self-host fonts and subset them rather than
  pulling full families from a third party.
- Add a caching layer (page cache + object cache) and a CDN. Verify dynamic content still varies
  per post under cache. See [production](25-production.md).
- Audit module count per page; consolidate duplicated modules into presets/globals so Divi emits
  one CSS variant instead of many.
- Remove unused Divi modules/features you do not use via the performance toggles rather than loading
  the full framework.

## Examples

**Good Example** — performance features on, hero optimized, CLS controlled

```text
Theme Options → Performance
  ✓ Dynamic CSS            ✓ Critical CSS
  ✓ Dynamic Module Framework  ✓ Dynamic/Deferred JavaScript

Hero Image module
  source: hero.avif (1600px, ~90 KB)   // sized to the container, next-gen format
  loading: eager + <link rel=preload>  // LCP image not deferred
  width/height set                     // reserves space → CLS ≈ 0
Below-fold images: lazy-loaded
Fonts: self-hosted, subset, preloaded
```

Why: the framework ships minimal CSS/JS, the LCP image is small and prioritized, and reserved
dimensions keep layout stable — good LCP, low CLS, small payload.

**Bad Example** — defaults left on, heavy unlazy hero, per-module CSS everywhere

```text
Performance features: default/off        // full CSS + JS framework loads
Hero: hero.png 4000×2600, 3.4 MB, lazy   // huge AND deferred → terrible LCP
60 modules, each with a Custom CSS tweak  // 60 CSS variants instead of a few presets
Google Fonts loaded from CDN, 6 weights   // render-blocking third-party request
Second slider plugin also enqueued        // a whole extra JS framework
```

Why this is wrong: an oversized, lazy-loaded LCP image, no critical-CSS split, per-module CSS
sprawl, blocking third-party fonts, and a redundant plugin — each adds weight; together they tank
every Core Web Vital.

## Common Mistakes

- Shipping with performance features off, so the full framework loads on every page.
- Lazy-loading the hero/LCP image (deferring the one image that should load first).
- Full-resolution, non-optimized images left at upload size.
- Per-module custom CSS instead of shared presets/classes, multiplying CSS variants.
- Missing image dimensions, causing layout shift (CLS).
- Loading fonts and a second page builder from third parties, blocking render.
- Measuring only on a fast desktop and declaring the site fast.

## Production Tips

- Gate launch on a throttled mobile Lighthouse run and, after launch, watch CrUX/field CWV — lab
  and field can diverge.
- Keep a page-weight budget (e.g. < 1 MB, < 50 requests above the fold) and check exports against it.
- Re-audit after content editors add pages; performance regresses as non-developers add modules.

## AI Review Checklist

- Are Dynamic CSS, Critical CSS, Dynamic Module Framework, and deferred JS enabled and verified?
- Is the LCP image next-gen, correctly sized, eagerly loaded, and preloaded?
- Do all images have explicit dimensions so CLS stays low?
- Is CSS shared via presets/child theme rather than duplicated per module?
- Are fonts self-hosted/subset and is there only one page builder loading?
- Was performance measured on throttled mobile, not just desktop?

## Related

- `knowledge/divi/09-custom-css.md`
- `knowledge/divi/06-global-elements.md`
- `knowledge/divi/11-responsive-design.md`
- `knowledge/divi/13-seo.md`
- `knowledge/divi/25-production.md`
