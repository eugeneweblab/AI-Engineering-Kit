---
id: performance/06-rendering
topic: performance
slug: rendering
title: "Performance Rendering"
type: doc
order: 6
status: ready
tags: [performance, rendering, opacity, transform, will-change, writes, translateY]
related: [performance/07-loading, performance/09-lazy-loading, performance/11-images, performance/18-web-vitals, performance/03-cpu]
when_to_use: "Read before building or reviewing any UI that renders lists, animations, or frequently-updating state on the client."
---
# Performance Rendering

## Purpose

This document defines how to turn application state into pixels without stalling the
main thread or dropping frames. It covers the browser rendering pipeline, layout and
paint cost, and how UI frameworks re-render. It is written so an agent can build or
review a view that stays responsive under real data volumes.

Rendering is where *work you already computed* becomes *work the browser must do*.
The goal is not "render fast" but "render only what changed, only when it changed,
and never block the thread doing it."

## Why It Matters

The browser gets ~16.7 ms to produce each frame at 60 Hz. Everything — script,
style recalculation, layout, paint, composite — must fit in that budget. A single
synchronous layout of a large list, or a re-render that touches the whole tree,
blows the budget and the user sees jank: stutter on scroll, lag on typing, frozen
animations. Unlike a slow API call, rendering jank happens on every interaction and
is felt directly. It is also the most common cause of a poor Interaction to Next
Paint ([web-vitals](18-web-vitals.md)) score.

## Core Principles

- **Minimize the work, don't just speed it up.** The fastest render is the one you
  skip. Render only the components whose inputs actually changed.
- **Never block the main thread.** Long synchronous work — parsing, sorting, layout
  of thousands of nodes — freezes input. Break it up, defer it, or move it off-thread.
- **Batch reads and writes to the DOM.** Interleaving a read (`offsetHeight`) with a
  write forces synchronous layout ("layout thrashing"). Group all reads, then writes.
- **Prefer compositor-only changes.** Animate `transform` and `opacity`; they skip
  layout and paint. Animating `top`, `width`, or `box-shadow` forces relayout/repaint.
- **Bound what you render.** A view's cost must not grow linearly with data. Virtualize
  long lists so DOM size stays constant regardless of item count.

## Best Practices

- Virtualize any list that can exceed ~100 rows: render only the visible window plus a
  small overscan. DOM node count is the dominant cost, so keeping it constant keeps
  scroll smooth at any data size.
- Give list items stable, data-derived keys (not array index). Index keys make the
  framework re-render and re-mount rows on insert/reorder, discarding DOM state.
- Memoize expensive derived values and pure components so they recompute only when
  inputs change. Measure first — memoization has its own cost and is not free.
- Debounce or throttle high-frequency handlers (`scroll`, `resize`, `mousemove`,
  input) so they run at most once per frame via `requestAnimationFrame`.
- Move heavy pure computation (parsing, sorting large arrays, image processing) to a
  Web Worker so the main thread stays free for input and painting.
- Keep animations on `transform`/`opacity` and promote animated layers with
  `will-change` sparingly — every promoted layer costs GPU memory.
- Avoid deep component trees that re-render from the root; colocate state so an update
  touches the smallest possible subtree.

## Examples

**Good Example** — batched DOM access, no layout thrash

```js
// Read ALL layout values first, then write. One layout, one paint.
const heights = rows.map((row) => row.offsetHeight); // reads (forces layout once)
rows.forEach((row, i) => {
  row.style.transform = `translateY(${heights[i]}px)`; // writes (compositor-only)
});
// transform avoids relayout; batching avoids read→write→read thrashing.
```

**Bad Example** — layout thrashing in a loop

```js
// Each iteration writes, then the next read forces a synchronous relayout.
rows.forEach((row) => {
  const h = row.offsetHeight;        // read forces layout...
  row.style.height = `${h + 10}px`;  // ...write invalidates it...
  row.style.top = `${row.offsetTop}px`; // ...read forces layout AGAIN. O(n) reflows.
});
// Also animates `height`/`top`, which relayout every frame instead of compositing.
```

## Common Mistakes

- Rendering an entire list of thousands of rows into the DOM instead of virtualizing.
- Using array index as a list key, causing full re-mounts on insert or reorder.
- Interleaving DOM reads and writes in a loop, forcing repeated synchronous layout.
- Animating layout-triggering properties (`width`, `top`, `margin`) instead of
  `transform`/`opacity`.
- Doing heavy computation (sorting, filtering huge arrays) synchronously in a render
  path or an unthrottled scroll handler.
- Sprinkling `will-change` everywhere, exhausting GPU memory and slowing composition.
- Over-memoizing trivial components so the equality checks cost more than the render.

## Production Tips

- Profile with the browser Performance panel: look for long tasks (>50 ms), forced
  reflows (flagged in the timeline), and dropped frames during interaction.
- Track Interaction to Next Paint in the field, not just the lab — jank shows up under
  real data and real devices. See [monitoring](17-monitoring.md).
- Test rendering on a mid-tier mobile CPU with throttling, not your dev laptop; the
  main-thread budget there is 4-6x tighter.

## AI Review Checklist

- Are long or unbounded lists virtualized so DOM size stays constant?
- Do list items use stable, data-derived keys rather than array index?
- Are animations limited to `transform`/`opacity` (compositor-only) properties?
- Are DOM reads and writes batched to avoid synchronous layout thrashing?
- Is heavy synchronous computation debounced, deferred, or moved to a Web Worker?
- Is memoization applied where measured to help, not reflexively everywhere?
- Was rendering profiled on a throttled/mobile CPU, not just the dev machine?

## Related

- `knowledge/performance/07-loading.md`
- `knowledge/performance/09-lazy-loading.md`
- `knowledge/performance/11-images.md`
- `knowledge/performance/18-web-vitals.md`
- `knowledge/performance/03-cpu.md`
