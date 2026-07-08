---
id: html/20-browser-rendering
topic: html
slug: browser-rendering
title: "Browser Rendering"
type: doc
order: 20
status: ready
tags: [html, browser-rendering]
related: [html/01-document-structure, html/18-performance, html/10-metadata, html/23-progressive-enhancement, html/17-canvas]
when_to_use: "Read before ordering resources in the head, debugging flashes/reflows, or reasoning about how markup becomes pixels."
---
# Browser Rendering

## Purpose

This document explains how a browser turns your HTML into pixels: parsing, the DOM and
CSSOM, the render tree, layout, paint, and compositing. Understanding this pipeline lets
an agent order resources correctly, avoid render-blocking, and reason about why a page
flashes, reflows, or paints late.

It is the mechanism behind [performance](18-performance.md): performance rules are
recommendations, but the rendering pipeline is *why* they are true.

## Why It Matters

Markup does not become a page in one step — it flows through a pipeline where each stage
depends on the last, and any stage can stall the whole thing. A stylesheet in the head
blocks the first paint because the browser will not paint without the CSSOM. A synchronous
script blocks parsing because it might rewrite the DOM. If you do not know which stages
block, you cannot tell why the screen stays blank, why text flashes unstyled, or why a
tiny DOM change janks an animation. Knowing the pipeline turns rendering bugs from
guesswork into a lookup.

## Core Principles

- **DOM + CSSOM → render tree.** The browser needs both trees before it can build the
  render tree and paint. CSS is therefore render-blocking by default.
- **Parsing is synchronous and interruptible by scripts.** A blocking `<script>` pauses
  the parser because it may call `document.write` or mutate nodes above it.
- **Layout and paint are expensive; compositing is cheap.** Changing geometry (width,
  top) triggers layout (reflow); changing `transform`/`opacity` can skip straight to
  compositing on the GPU.
- **Layout is global-ish.** One element's size change can force recalculation of its
  siblings and ancestors, so late-loading unsized content reflows the page.
- **The preload scanner works ahead of the parser.** It discovers `src`/`href` in the
  raw bytes and starts fetches early — which is why resources hidden in CSS or JS load
  late.

## Best Practices

- Keep render-blocking CSS in the `<head>` and small; inline only the critical CSS needed
  for first paint if you must, and load the rest asynchronously. See
  [document structure](01-document-structure.md).
- Never place a synchronous `<script>` before content you want painted; use `defer`/`async`
  so parsing and painting proceed. See [performance](18-performance.md).
- Give the preload scanner real `<img src>`/`<link href>` in the initial HTML rather than
  injecting them via JavaScript, so it can prefetch during parsing.
- Prevent flash of unstyled/invisible text (FOUT/FOIT) by setting `font-display: swap`
  and preloading critical fonts.
- Animate `transform` and `opacity` — not `width`, `height`, `top`, or `left` — so the
  change composites on the GPU instead of forcing layout every frame.
- Avoid forcing synchronous layout ("layout thrashing") by reading a geometry property
  (`offsetHeight`) immediately after writing one in a loop.

## Examples

**Good Example** — parser and paint proceed, composited animation

```html
<head>
  <link rel="stylesheet" href="/critical.css" />   <!-- small, render-blocking, intentional -->
  <script src="/app.js" defer></script>            <!-- doesn't pause the parser -->
</head>
<style>
  /* transform/opacity animate on the compositor: no layout or paint per frame */
  .card { transition: transform 200ms, opacity 200ms; }
  .card:hover { transform: translateY(-4px); }
  @font-face { font-family: Inter; src: url(/inter.woff2); font-display: swap; }
</style>
```

**Bad Example** — blocked paint, layout-thrashing animation

```html
<head>
  <!-- Blocking script BEFORE content: parser stops, nothing paints until it runs -->
  <script src="/heavy.js"></script>
</head>
<style>
  /* Animating width/left recalculates layout every frame → jank on slow devices */
  .card { transition: width 200ms, left 200ms; }
  .card:hover { width: 320px; left: 40px; }
</style>
```

## Common Mistakes

- Assuming CSS is non-blocking; a large stylesheet delays first paint for everyone.
- Injecting critical images/fonts via JS, hiding them from the preload scanner.
- Animating layout properties (`width`, `top`) and blaming the GPU for the jank.
- Reading layout metrics inside a write loop, forcing synchronous reflows.
- No `font-display`, producing invisible or flashing text while fonts load.
- Treating the DOM as painted the instant `DOMContentLoaded` fires — paint is later.

## Production Tips

- Use the browser's Performance panel to see the parse → layout → paint → composite
  timeline; long "Layout" or "Recalculate Style" bars point straight at the cause.
- Watch for "forced reflow" warnings in DevTools — they mark synchronous layout in a
  hot path.
- Verify the LCP element in the Performance panel; if it is text, fonts are on the
  critical path and should be preloaded.

## AI Review Checklist

- Is render-blocking CSS minimal and in the `<head>`?
- Are scripts `defer`/`async` so they do not stall parsing before paint?
- Are critical images/fonts discoverable by the preload scanner (real `src`/`href`)?
- Do animations use `transform`/`opacity` rather than layout-triggering properties?
- Is `font-display: swap` set to avoid invisible text during font load?
- Is there no read-after-write layout thrashing in scripted DOM updates?

## Related

- `knowledge/html/01-document-structure.md`
- `knowledge/html/18-performance.md`
- `knowledge/html/10-metadata.md`
- `knowledge/html/23-progressive-enhancement.md`
- `knowledge/html/17-canvas.md`
