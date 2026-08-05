---
id: performance/18-web-vitals
topic: performance
slug: web-vitals
title: "Web Vitals"
type: doc
order: 18
status: ready
tags: [performance, web-vitals, web-vitals, shift, onLCP, onINP, onCLS, sendBeacon]
related: [performance/02-metrics, performance/06-rendering, performance/07-loading, performance/11-images, performance/23-performance-budget]
when_to_use: "Read before measuring or optimizing the perceived loading and responsiveness of a web page."
---
# Web Vitals

## Purpose

This document defines the Core Web Vitals — **LCP**, **INP**, and **CLS** — the
user-centered metrics Google standardized to measure how a page *feels* to load and
respond. It exists so an agent optimizes the numbers users actually experience, not a
synthetic score on a fast laptop.

Web Vitals are the frontend specialization of [metrics](02-metrics.md): the same
percentile discipline, applied to loading, responsiveness, and visual stability. If you
are instrumenting a page, this is the target set.

## Why It Matters

Users abandon slow pages before they ever see your content, and the abandonment shows up
in revenue, not just dashboards. The Core Web Vitals are also a Google ranking signal, so
a regression costs traffic as well as conversions. Crucially, these metrics are measured
on *real user hardware and networks* (field data), which is usually far worse than the
machine an engineer tests on. A page that scores 100 in a local lab run can still fail in
the field. Optimizing Web Vitals means optimizing for the p75 of your actual users.

## Core Principles

- **Three metrics, three axes.** LCP measures *loading*, INP measures *responsiveness*,
  CLS measures *visual stability*. They are independent; fixing one does not move another.
- **Field data is the truth; lab data is the tool.** Google ranks on field (RUM, 28-day
  p75). Lab tools (Lighthouse) are reproducible for debugging but do not reflect real
  users. Optimize with lab, verify with field.
- **The threshold is the p75, not the average.** A metric is "good" only when 75% of
  visits meet the bar. The slow quarter is the point.
- **INP replaced FID in March 2024.** FID measured only the first interaction's delay;
  INP measures the full latency of *all* interactions. Do not target the deprecated FID.
- **Vitals reflect architecture, not tweaks.** Poor LCP usually means a slow server or a
  render-blocking chain — a structural fix, not a one-line change.

## The Three Core Web Vitals

- **LCP — Largest Contentful Paint** (loading): time until the largest visible element
  (hero image, headline) renders. **Good: ≤ 2.5s.** Driven by [TTFB](14-api-performance.md),
  render-blocking resources, and [image](11-images.md) load time.
- **INP — Interaction to Next Paint** (responsiveness): the worst-case latency from a
  user input to the next frame, across the whole visit. **Good: ≤ 200ms.** Driven by long
  main-thread tasks blocking event handlers.
- **CLS — Cumulative Layout Shift** (stability): how much visible content jumps during
  load. **Good: ≤ 0.1.** Driven by images/ads/embeds without reserved space.
- Supporting diagnostics: **TTFB** (server response) and **FCP** (first paint) explain
  *why* LCP is slow but are not themselves Core Web Vitals.

## Best Practices

- Reserve space for every image, ad, and embed with explicit `width`/`height` or
  `aspect-ratio` so late-loading content cannot shift layout (fixes CLS).
- Preload the LCP element (hero image or font) and never lazy-load it — lazy-loading the
  largest element directly delays LCP.
- Break long JavaScript tasks (> 50ms) into chunks and defer non-critical work; a single
  long task blocking an input handler is the usual INP culprit.
- Serve fonts with `font-display: swap` and preload them, so text is not invisible while
  the font loads (a hidden LCP and CLS cause). See [fonts](12-fonts.md).
- Measure in the field with the `web-vitals` library and report p75; use Lighthouse only
  to reproduce and debug.
- Set Web Vitals thresholds in a [performance budget](23-performance-budget.md) and gate
  CI on the lab numbers.

## Examples

**Good Example** — reserve space, capture field data at p75

```html
<!-- Explicit dimensions reserve the box before the image loads → no layout shift (CLS). -->
<img src="/hero.avif" width="1200" height="630" fetchpriority="high" alt="…" />
```

```js
import { onLCP, onINP, onCLS } from "web-vitals";

// Report REAL user metrics; the backend aggregates to p75 (the ranking threshold).
function send(metric) {
  navigator.sendBeacon("/rum", JSON.stringify({ name: metric.name, value: metric.value }));
}
onLCP(send); onINP(send); onCLS(send); // all three axes, from real devices
```

**Bad Example** — lazy hero, no dimensions, lab-only

```html
<!-- Lazy-loading the LARGEST element delays the very metric it defines (LCP). -->
<img src="/hero.jpg" loading="lazy" />
<!-- No width/height: the image pushes content down when it arrives → CLS spike. -->

<!-- "It scores 98 in Lighthouse on my laptop" is not field data; real users on 4G
     phones may be at LCP 6s. Never ship on a lab number alone. -->
```

## Common Mistakes

- Optimizing to a Lighthouse lab score and ignoring field p75, where real users live.
- Lazy-loading or deferring the LCP element, delaying the metric it defines.
- Shipping images/ads/embeds without reserved dimensions, causing CLS.
- Still targeting FID; it was removed in 2024 and replaced by INP.
- One giant JavaScript bundle that monopolizes the main thread and wrecks INP.
- Reporting the average vital instead of the p75 threshold that actually counts.

## Production Tips

- Collect Web Vitals via RUM continuously; a deploy can regress LCP without any lab
  signal. Alert on p75 crossing the "good" boundary.
- Segment field data by device class and connection — the failing cohort is almost always
  low-end mobile, and the aggregate hides it.
- Attribute regressions: the `web-vitals` attribution build names the specific element or
  script responsible, turning a number into a fix.

## AI Review Checklist

- Are LCP, INP, and CLS all measured (not just a single Lighthouse score)?
- Is the target the field p75, not an average or a lab run?
- Does the LCP element load eagerly and with high priority (never lazy)?
- Do all images, ads, and embeds reserve space to prevent CLS?
- Are long main-thread tasks broken up so input handlers stay responsive (INP)?
- Is the code using INP, not the deprecated FID?

## Related

- `knowledge/performance/02-metrics.md`
- `knowledge/performance/06-rendering.md`
- `knowledge/performance/07-loading.md`
- `knowledge/performance/11-images.md`
- `knowledge/performance/23-performance-budget.md`
