---
id: html/17-canvas
topic: html
slug: canvas
title: "Canvas"
type: doc
order: 17
status: ready
tags: [html, canvas]
related: [html/16-svg, html/11-accessibility, html/18-performance, html/27-html-apis]
when_to_use: "Read before rendering pixel graphics, charts, or animation with the <canvas> element."
---
# Canvas

## Purpose

This document defines how to use the `<canvas>` element for immediate-mode, pixel-based
rendering: charts, games, image processing, and animation. It covers the accessibility
gap canvas creates, high-DPI scaling, the render loop, and the tainted-canvas security
rule. Canvas draws pixels with no retained DOM, which is why it is fast — and why it is
inaccessible unless you deliberately compensate.

Canvas is the right tool when you draw many primitives per frame or manipulate pixels
directly. For scalable, stylable, few-shapes graphics prefer [SVG](16-svg.md); its
retained DOM is accessible and crisp at any zoom. Choosing canvas means accepting
responsibility for the accessibility and scaling that SVG gives you for free.

## Why It Matters

A `<canvas>` is a black box to everything except your drawing code. Screen readers see
an empty element; keyboard users cannot tab to a rectangle you painted; search engines
index nothing. Teams ship data visualizations and games that are completely unusable to
assistive tech because "it looked fine." On top of that, drawing at CSS pixel size on a
2x display produces blurry output, and drawing a cross-origin image silently *taints* the
canvas so `toDataURL()` throws. These are all invisible until the wrong user or the wrong
device hits them, so they must be designed in from the start.

## Core Principles

- **Canvas has no accessibility by default — you must provide it.** Put real,
  semantic fallback content inside the element and keep it in sync with what you draw.
- **Choose canvas for pixels and volume, SVG for shapes and scale.** Canvas wins on
  thousands of elements or per-pixel work; SVG wins on accessibility and sharpness.
- **Account for device pixel ratio.** The backing store must be sized in device pixels
  (`width = cssWidth * devicePixelRatio`) or output is blurry on HiDPI screens.
- **Animate with `requestAnimationFrame`, never `setInterval`.** rAF syncs to the
  display refresh, pauses in background tabs, and avoids wasted frames.
- **Cross-origin pixels taint the canvas.** Reading back from a canvas that drew an
  image from another origin throws unless that image was served CORS-enabled.

## Best Practices

- Provide fallback content between `<canvas>` tags — a table, description, or
  `<img>` — that conveys the same information to screen readers and no-JS clients.
- Size for HiDPI: set `canvas.width/height` to CSS size × `devicePixelRatio`, keep the
  CSS size fixed, then `ctx.scale(dpr, dpr)` so drawing coordinates stay in CSS pixels.
- Drive animation with `requestAnimationFrame` and compute motion from elapsed time
  (delta), so speed is frame-rate-independent.
- Redraw only what changed where possible; use `clearRect` on dirty regions or layer
  static content on a separate canvas rather than repainting everything each frame.
- For interactive charts, mirror data points as focusable, labeled DOM elements
  overlaid on the canvas so keyboard and screen-reader users can reach them.
- To read pixels or export (`toDataURL`, `getImageData`), load any drawn images with
  `img.crossOrigin = "anonymous"` from a CORS-enabled source to avoid tainting.
- Call `getContext("2d")` once and reuse it; recreating contexts and reallocating the
  canvas each frame thrashes memory.

## Examples

**Good Example** — HiDPI-correct, rAF loop, accessible fallback

```html
<canvas id="chart" width="600" height="300" role="img"
        aria-label="Monthly signups, peaking in June">
  <!-- Fallback: real data for screen readers and no-JS/no-canvas clients -->
  <table><caption>Monthly signups</caption>
    <tr><th>May</th><td>1,200</td></tr><tr><th>Jun</th><td>3,400</td></tr>
  </table>
</canvas>

<script>
  const c = document.getElementById("chart");
  const ctx = c.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  c.width = 600 * dpr; c.height = 300 * dpr;   // backing store in device pixels
  c.style.width = "600px"; c.style.height = "300px";
  ctx.scale(dpr, dpr);                          // draw in CSS pixels → sharp on HiDPI

  function frame(now) {
    ctx.clearRect(0, 0, 600, 300);
    // ...draw using CSS-pixel coordinates...
    requestAnimationFrame(frame);              // syncs to refresh, pauses when hidden
  }
  requestAnimationFrame(frame);
</script>
```

**Bad Example** — blurry, wasteful, invisible to assistive tech

```html
<canvas id="c" width="600" height="300"></canvas>  <!-- no fallback, no label -->
<script>
  const ctx = document.getElementById("c").getContext("2d");
  // No devicePixelRatio handling → blurry on 2x displays
  setInterval(() => {                 // fixed 60fps burn even in background tabs
    ctx.clearRect(0, 0, 600, 300);
    drawEverything();                 // full repaint every tick regardless of change
  }, 16);
  ctx.drawImage(otherOriginImg, 0, 0);
  c.toDataURL();                      // throws: canvas tainted by cross-origin image
</script>
```

## Common Mistakes

- No fallback content or `aria-label`, leaving the canvas invisible to screen readers.
- Ignoring `devicePixelRatio`, producing blurry graphics on HiDPI screens.
- Using `setInterval` instead of `requestAnimationFrame`, wasting CPU/battery in
  background tabs and desyncing from the display.
- Repainting the entire canvas every frame when only a small region changed.
- Drawing a cross-origin image without CORS, then failing on `toDataURL`/`getImageData`.
- Treating canvas as a document — it is not indexable, selectable, or zoomable like DOM.
- Choosing canvas for a handful of static shapes that SVG would render accessibly.

## Production Tips

- Keep the accessible fallback (table/description) generated from the same data source
  as the drawing, so it cannot drift out of sync with the visual.
- Cap the render loop cost: skip frames when the tab is hidden (rAF already pauses) and
  throttle expensive redraws behind a dirty flag.
- Offload heavy pixel work (image processing, large simulations) to `OffscreenCanvas`
  in a Web Worker so the main thread stays responsive.

## AI Review Checklist

- Does the `<canvas>` have fallback content and/or an `aria-label` conveying its meaning?
- Is the backing store scaled by `devicePixelRatio` for sharp HiDPI output?
- Is animation driven by `requestAnimationFrame` with time-based motion?
- Is redraw limited to what changed rather than a full repaint each frame?
- Are drawn cross-origin images CORS-enabled if pixels are read back or exported?
- Would SVG have been the better, more accessible choice for this graphic?

## Related

- `knowledge/html/16-svg.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/18-performance.md`
- `knowledge/html/27-html-apis.md`
