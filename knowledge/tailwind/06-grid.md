---
id: tailwind/06-grid
topic: tailwind
slug: grid
title: "Tailwind CSS Grid"
type: doc
order: 6
status: ready
tags: [tailwind, grid, auto-fit, auto-fill, minmax, subgrid]
related: [tailwind/05-flexbox, tailwind/04-layout, tailwind/07-spacing, tailwind/11-responsive-design, tailwind/08-sizing]
when_to_use: "Read before building any two-dimensional layout — dashboards, card galleries, form grids, or page shells that align in both rows and columns."
---
# Tailwind CSS Grid

## Purpose

This document defines how to build layouts with CSS Grid using Tailwind utilities:
`grid`, `grid-cols-*`, `grid-rows-*`, `col-span-*`, `gap-*`, and the auto-placement and
`subgrid` helpers. It is written so an agent can choose Grid over Flexbox correctly and
produce a layout that stays aligned in two dimensions as content and viewport change.

Grid controls placement on **two axes at once** (rows and columns). It is distinct from
[Flexbox](05-flexbox.md), which distributes items along **one axis**. Reach for Grid when
you need cells to line up both horizontally and vertically; reach for Flexbox for a single
row or column of content.

## Why It Matters

Grid choices are structural: they decide how a layout reflows on every screen size and how
it survives content you did not anticipate — a long title, a missing image, a translated
string twice as wide. A layout built with the wrong tool (nested Flexbox faking a grid, or
absolute positioning) works in the demo and collapses in production the moment real data
arrives. Because Tailwind makes the wrong approach as easy to type as the right one, the
decision has to be deliberate.

## Core Principles

- **Use Grid for two-dimensional alignment; use Flexbox for one dimension.** If cells must
  align across both rows and columns, Grid is the correct tool. Nesting Flex rows to fake a
  grid loses column alignment the instant one cell is taller.
- **Define tracks on the container, place items in cells.** `grid-cols-*` and `grid-rows-*`
  belong on the parent; `col-span-*` / `row-span-*` on children. Keep the two responsibilities
  separate so the layout is readable.
- **Prefer `gap-*` over margins for spacing between cells.** `gap` spaces items without adding
  edge margins you then have to strip; margins on grid children create uneven, hard-to-debug
  gutters.
- **Let the grid be responsive by default.** Start with one column on mobile and add columns
  at breakpoints. A fixed multi-column grid overflows small screens.
- **Reach for `auto-fit` / `minmax` when the column count should follow available width**, not
  a hard-coded number — the browser then decides how many cards fit.

## Best Practices

- Set an explicit track count with `grid-cols-3` when the design has a fixed structure (a
  form, a stat row). Use `grid-cols-[repeat(auto-fit,minmax(16rem,1fr))]` when the count
  should adapt to width (a responsive card wall).
- Space cells with `gap-*` (or `gap-x-*` / `gap-y-*` for asymmetric gutters), never per-child
  margins.
- Span cells with `col-span-2`, `row-span-2`, or `col-span-full`; place precisely with
  `col-start-*` / `col-end-*` only when a span is not enough.
- Use `grid-cols-subgrid` on a child grid so its tracks inherit the parent's — this keeps
  nested content aligned to the outer columns instead of guessing widths.
- Control flow of auto-placed items with `grid-flow-row` (default), `grid-flow-col`, or
  `grid-flow-dense` to backfill gaps.
- Make the grid responsive mobile-first: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`.

## Examples

**Good Example** — container defines tracks, children span, gap handles spacing, responsive

```html
<!-- Tracks + gap on the parent; the grid is one column on mobile, three on desktop -->
<ul class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
  <li class="rounded-lg border p-4">Card</li>
  <li class="rounded-lg border p-4">Card</li>
  <!-- Feature cell spans two columns at lg; falls back to full width below it -->
  <li class="rounded-lg border p-4 lg:col-span-2">Wide card</li>
</ul>
```

**Bad Example** — nested Flex faking a grid, margins for gutters, fixed columns

```html
<!-- Flex rows can't align columns: a tall card in row 1 desyncs row 2 -->
<div class="flex flex-wrap">
  <!-- margins create uneven edge gutters and double-spacing between rows -->
  <div class="m-3 w-1/3 border p-4">Card</div>
  <div class="m-3 w-1/3 border p-4">Card</div>
  <!-- w-1/3 is fixed: three cards overflow a phone instead of stacking -->
  <div class="m-3 w-1/3 border p-4">Card</div>
</div>
```

## Common Mistakes

- Faking a grid with nested Flexbox — columns stop aligning as soon as one cell is taller.
- Using margins between cells instead of `gap-*`, producing uneven or doubled gutters.
- Hard-coding `grid-cols-4` with no mobile fallback, so the grid overflows small screens.
- Putting `col-span-*` on the container or `grid-cols-*` on a child — the utilities do nothing
  there.
- Reaching for arbitrary `col-start` / `col-end` positioning when a simple `col-span-*` would do,
  making the layout brittle to reorder.
- Forgetting that `grid` items ignore `space-x-*` / `space-y-*`; those are Flex/inline helpers —
  use `gap-*`.

## Production Tips

- For card walls where the item count is unknown, `grid-cols-[repeat(auto-fill,minmax(...,1fr))]`
  keeps rows full without media-query churn — pick `auto-fit` to stretch the last row, `auto-fill`
  to keep card width constant.
- Use `grid-cols-subgrid` for line-item tables and definition lists so labels and values align to
  the page grid instead of each row inventing its own widths.
- When mixing a sidebar and content, name the shape with `grid-cols-[16rem_1fr]` rather than two
  fractional columns — the sidebar then holds a fixed width and the content takes the rest.

## AI Review Checklist

- Is Grid used for genuine two-axis alignment, not a single row that Flexbox handles better?
- Are `grid-cols-*` / `grid-rows-*` on the container and `col-span-*` / `row-span-*` on children?
- Is spacing done with `gap-*` rather than per-child margins?
- Does the grid start single-column on mobile and add columns at breakpoints?
- Where the column count should follow width, is `auto-fit`/`auto-fill` + `minmax` used instead
  of a hard-coded count?
- Are precise `col-start`/`col-end` placements justified, or could a `col-span-*` replace them?

## Related

- `knowledge/tailwind/05-flexbox.md`
- `knowledge/tailwind/04-layout.md`
- `knowledge/tailwind/07-spacing.md`
- `knowledge/tailwind/08-sizing.md`
- `knowledge/tailwind/11-responsive-design.md`
