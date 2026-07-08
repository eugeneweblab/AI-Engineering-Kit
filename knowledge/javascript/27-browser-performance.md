---
id: javascript/27-browser-performance
topic: javascript
slug: browser-performance
title: "Browser Performance"
type: doc
order: 27
status: ready
tags: [javascript, browser-performance]
related: [javascript/12-dom, javascript/11-browser-api, javascript/25-performance, javascript/10-event-loop, javascript/13-fetch-api]
when_to_use: "Read before optimizing page load, rendering, scrolling, or interaction responsiveness in the browser."
---
# Browser Performance

## Purpose

This document defines how to keep a web page fast for real users: minimizing main-thread
work, avoiding layout thrashing, shrinking and deferring JavaScript, and hitting the Core
Web Vitals. It covers the *browser rendering and delivery* side of performance; algorithmic
and Node-side cost lives in [performance](25-performance.md). It is written so an agent
optimizes the metrics users actually feel — how fast the page loads and how quickly it
responds to input.

## Why It Matters

The browser has one main thread, and it runs your JavaScript, computes layout, paints, and
handles input on that same thread. Every millisecond of script is a millisecond the page
cannot respond to a tap or a scroll. Users perceive jank instantly and abandon slow pages;
performance directly moves conversion and search ranking. The failure mode is subtle: the
page "works" in a fast dev environment on a wired connection, then falls apart on a mid-tier
phone over cellular — which is where most users actually are.

## Core Principles

- **The main thread is the scarcest resource.** Long tasks (>50ms) block input. Break work
  into chunks, defer it, or move it to a Web Worker. The cost of a monolithic task is a
  frozen UI.
- **Optimize for Core Web Vitals.** LCP (loads fast), INP (responds fast), CLS (doesn't
  shift). These are what users feel and search engines measure — tune them, not synthetic
  microbenchmarks.
- **Ship less JavaScript.** Every KB is parse, compile, and execute time on the main thread.
  Code-split and lazy-load; the fastest script is the one you never send.
- **Batch DOM reads and writes.** Interleaving reads and writes forces synchronous
  reflow ("layout thrashing"). Read all, then write all.
- **Measure on real hardware.** Profile on a throttled mid-tier device, not your laptop.

## Best Practices

- **Code-split** with dynamic `import()` and load non-critical code on interaction or when
  visible. Defer third-party scripts (`async`/`defer`).
- Use **`IntersectionObserver`** for lazy-loading images and infinite scroll instead of
  scroll-event polling. Add `loading="lazy"` to below-the-fold images.
- **Debounce/throttle** high-frequency handlers (scroll, resize, input); do visual updates
  inside `requestAnimationFrame`, never directly in a scroll handler.
- **Batch layout**: read geometry (`offsetWidth`, `getBoundingClientRect`) once, then apply
  all writes. Avoid reading a layout property right after a write.
- Reserve space for images/ads (`width`/`height` or `aspect-ratio`) to prevent CLS.
- Virtualize long lists so the DOM holds only visible rows.
- Move heavy computation (parsing, image processing) to a **Web Worker** to keep input
  responsive (protects INP).
- Mark passive scroll/touch listeners `{ passive: true }` so the browser can scroll without
  waiting on your handler.

## Examples

**Good Example** — batched layout, rAF-driven, observer-based lazy load

```js
// Read every geometry value first, then write. No read→write→read interleaving,
// so the browser reflows once instead of once per element.
const tops = items.map((el) => el.getBoundingClientRect().top); // all reads
items.forEach((el, i) => { el.style.transform = `translateY(${tops[i]}px)`; }); // all writes

// Lazy-load images only as they approach the viewport — no scroll polling.
const io = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) {
    e.target.src = e.target.dataset.src;
    io.unobserve(e.target);
  }
});
document.querySelectorAll("img[data-src]").forEach((img) => io.observe(img));
```

**Bad Example** — layout thrash, unthrottled scroll, sync work on main thread

```js
items.forEach((el) => {
  const top = el.getBoundingClientRect().top; // read forces layout...
  el.style.height = top + "px";               // ...then write invalidates it → reflow every iteration
});

window.addEventListener("scroll", () => {
  render(computeExpensiveLayout()); // runs on every scroll tick, blocks the main thread → jank
});
```

## Common Mistakes

- Reading and writing DOM layout properties in a loop, causing forced synchronous reflow.
- Doing visual work directly in `scroll`/`resize`/`mousemove` without throttle or rAF.
- Shipping one giant bundle instead of code-splitting critical vs. deferred code.
- Images without dimensions, causing layout shift (CLS) as they load.
- Rendering thousands of DOM nodes instead of virtualizing the list.
- Running heavy parsing/computation on the main thread, spiking INP.
- Profiling only on a fast machine, missing the mid-tier-phone reality.

## Production Tips

- Collect **field** Core Web Vitals from real users (`web-vitals` library / RUM), not just
  lab scores — lab and field diverge sharply.
- Set performance budgets in CI (bundle size, Lighthouse thresholds) and fail the build on
  regression.
- Use `content-visibility: auto` to skip rendering off-screen content cheaply.
- Preload the LCP image and critical fonts; lazy-load everything else.

## AI Review Checklist

- Are DOM reads batched before writes to avoid forced reflow?
- Are high-frequency handlers throttled/debounced and visual updates inside `requestAnimationFrame`?
- Is non-critical JavaScript code-split and lazy-loaded rather than shipped upfront?
- Do images and embeds reserve space to keep CLS near zero?
- Is heavy computation moved off the main thread to a Web Worker?
- Are long lists virtualized instead of fully rendered?
- Are Core Web Vitals (LCP, INP, CLS) measured on real devices, not just a fast laptop?

## Related

- `knowledge/javascript/12-dom.md`
- `knowledge/javascript/11-browser-api.md`
- `knowledge/javascript/25-performance.md`
- `knowledge/javascript/10-event-loop.md`
- `knowledge/javascript/13-fetch-api.md`
