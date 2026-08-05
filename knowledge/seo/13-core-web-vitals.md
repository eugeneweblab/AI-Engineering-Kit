---
id: seo/13-core-web-vitals
topic: seo
slug: core-web-vitals
title: "Core Web Vitals"
type: doc
order: 13
status: ready
tags: [seo, core-web-vitals, web-vitals, setTimeout, shift, aspect-ratio, append, Promise]
related: [seo/12-performance, seo/16-images, seo/04-rendering, seo/24-monitoring, seo/22-search-console]
when_to_use: "Read before touching layout, above-the-fold rendering, or interactivity, or when diagnosing a failing LCP/INP/CLS metric."
---
# Core Web Vitals

## Purpose

This document defines the three Core Web Vitals (CWV) — the user-centric metrics Google
uses as a ranking signal — their 2026 thresholds, and the concrete engineering causes of
each. It exists so an agent can build pages that pass CWV by construction and can trace a
failing metric to the code that causes it.

Where [Performance](12-performance.md) covers the general engineering of a fast page,
this doc is about the *specific measured metrics* and how each one is scored, diagnosed,
and fixed.

## Why It Matters

Core Web Vitals are a confirmed Google ranking factor, and — unlike most ranking signals
— they are measured from *real users* (the Chrome UX Report field data), not from your
lab. That means you cannot pass by optimizing a single fast test run; you pass only when
the 75th-percentile experience across your actual mobile traffic is good. A page can look
instant on your machine and still fail in the field. The metrics also map directly to
things users feel — slow content, jank, unresponsive taps — so passing them improves
conversion as well as ranking. They are assessed per URL and grouped by page type, so one
bad template drags a whole section down.

## Core Principles

- **Three metrics, one bar each, measured at p75 on mobile.** A URL passes only when all
  three are in the "good" band for 75% of real visits.
  - **LCP (Largest Contentful Paint)** — loading: time until the largest above-the-fold
    element renders. Good ≤ **2.5s**, poor > 4.0s.
  - **INP (Interaction to Next Paint)** — responsiveness: worst input latency across the
    visit. Good ≤ **200ms**, poor > 500ms. (INP replaced FID in 2024; FID is gone.)
  - **CLS (Cumulative Layout Shift)** — visual stability: how much visible content moves
    unexpectedly. Good ≤ **0.1**, poor > 0.25 (unitless).
- **Field data ranks; lab data diagnoses.** CrUX field data decides your assessment;
  Lighthouse/DevTools reproduces causes. Never conflate the two.
- **Each metric has distinct causes.** LCP is a loading problem, INP a main-thread
  problem, CLS a layout problem. Diagnose them separately.
- **Reserve space, defer work, prioritize the hero.** Most CWV fixes reduce to these
  three moves — one per metric.

## Best Practices

- **LCP:** identify the LCP element (usually the hero image or heading). Preload it,
  serve it in a modern format at the right size, set `fetchpriority="high"`, and never
  lazy-load it. Cut TTFB and render-blocking resources upstream of it.
- **INP:** break up long JavaScript tasks (yield to the main thread, use `scheduler`
  APIs or `setTimeout` chunking). Debounce expensive handlers. Move heavy work off the
  main thread with a Web Worker. Ship less JS so hydration does not block early taps.
- **CLS:** set explicit `width`/`height` (or `aspect-ratio`) on every image, video, and
  ad slot so the browser reserves space before the asset loads. Reserve space for
  injected banners and embeds. Use `font-display: swap` with size-matched fallbacks to
  avoid text reflow. Never insert content above existing content after load.
- Measure with a RUM library (for example, the `web-vitals` npm package) and send the
  attribution data so you know *which element* caused each bad score.
- Track CWV per template in [Search Console](22-search-console.md)'s Core Web Vitals
  report; fixing the template fixes every URL that uses it.

## Examples

**Good Example** — reserved space, prioritized hero, chunked work

```html
<!-- width/height reserve the box before load → no layout shift (CLS) -->
<img src="/hero.avif" width="1200" height="630" fetchpriority="high" alt="…" />
```

```js
// INP: split a long list render so the main thread stays responsive to taps.
async function renderRows(rows) {
  for (let i = 0; i < rows.length; i++) {
    append(rows[i]);
    if (i % 50 === 0) await new Promise((r) => setTimeout(r)); // yield to the browser
  }
}
```

**Bad Example** — shifting layout, unresponsive main thread

```html
<!-- No dimensions: image pops in after load and shoves content down → CLS spike -->
<img src="/hero.jpg" alt="…" />
```

```js
// INP killer: one synchronous 400ms task blocks every tap until it finishes.
button.addEventListener("click", () => {
  const result = sortAndScoreEverything(hugeArray); // no yielding, no worker
  render(result);
});
```

## Common Mistakes

- Chasing a green Lighthouse score while field CLS/INP stay red — lab ≠ field.
- Lazy-loading or deferring the LCP image, delaying the exact element being measured.
- Omitting image/video/ad dimensions, the number-one cause of CLS.
- Still optimizing FID: it was removed in 2024. Optimize INP, which is stricter and
  covers the whole visit, not just the first input.
- Blaming the framework for INP when the real cause is a single unchunked handler or an
  oversized hydration bundle.
- Averaging metrics instead of reading p75; a good average hides a failing tail.

## Production Tips

- Report `web-vitals` with attribution to your analytics so each bad LCP/INP/CLS names
  the responsible element or script. See [Monitoring](24-monitoring.md).
- Alert when p75 mobile LCP crosses 2.5s or INP crosses 200ms on any key template.
- CrUX field data is a 28-day rolling window: fixes take weeks to fully reflect in the
  ranking signal, so ship early and verify with lab data in the meantime.

## AI Review Checklist

- Do all images, videos, and ad/embed slots have explicit dimensions or `aspect-ratio`?
- Is the LCP element preloaded, prioritized, and never lazy-loaded?
- Are long-running handlers chunked/yielded or moved to a Web Worker to protect INP?
- Is CWV measured from real users at p75 on mobile, not just Lighthouse?
- Are fonts loaded with `font-display: swap` and size-matched fallbacks to avoid reflow?
- Is the team optimizing INP (not the removed FID)?

## Related

- `knowledge/seo/12-performance.md`
- `knowledge/seo/16-images.md`
- `knowledge/seo/04-rendering.md`
- `knowledge/seo/24-monitoring.md`
- `knowledge/seo/22-search-console.md`
