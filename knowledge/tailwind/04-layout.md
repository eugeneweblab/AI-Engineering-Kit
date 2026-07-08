---
id: tailwind/04-layout
topic: tailwind
slug: layout
title: "Layout"
type: doc
order: 4
status: ready
tags: [tailwind, layout]
related: [tailwind/05-flexbox, tailwind/06-grid, tailwind/07-spacing, tailwind/11-responsive-design, tailwind/02-core-concepts]
when_to_use: "Read before structuring page or component layout with display, position, and container utilities."
---
# Layout

## Purpose

This document covers the layout primitives in Tailwind: the `display` utilities that pick a
layout engine (`flex`, `grid`, `block`, `hidden`), the `position` utilities (`relative`,
`absolute`, `sticky`, `fixed`) with their inset controls, and container/overflow behavior.
It sets the decision rules for choosing among them so structure is correct before you tune
spacing.

## Why It Matters

Most visual bugs — overlapping elements, content that will not center, sticky headers that
do not stick, scrollbars in the wrong place — are layout-mode mistakes, not spacing
mistakes. Choosing the wrong `display` or `position` value produces markup that looks close
but breaks at a different viewport or content length. Getting the layout engine right first
makes every later spacing utility behave predictably.

## Core Principles

- **Display picks the engine; everything else follows.** `flex` and `grid` change how
  children lay out. Choose the engine deliberately: one-dimensional flow → flex
  ([05-flexbox](05-flexbox.md)); two-dimensional → grid ([06-grid](06-grid.md)).
- **`position: absolute` needs a positioned ancestor.** `absolute` is placed relative to
  the nearest ancestor with `relative`/`absolute`/`fixed`, not the page. Set `relative`
  on the intended container.
- **`sticky` needs a scroll container and an offset.** `sticky` does nothing without a
  `top-*`/`bottom-*` inset and an ancestor tall enough to scroll within.
- **`hidden` removes from layout; use responsive variants to toggle.** `hidden md:block`
  hides on mobile and shows from `md` up — the standard responsive show/hide idiom.

## Best Practices

- Reach for `flex` or `grid` for structural layout; avoid `float`/`inline-block` hacks —
  Tailwind supports them but they are rarely the right tool.
- Establish a positioning context explicitly: put `relative` on the parent whenever a child
  uses `absolute`, so placement does not silently escape to a distant ancestor.
- Center with the engine, not margins-and-guesswork: `flex items-center justify-center`
  for a single item; `grid place-items-center` for grid.
- Constrain page width with `max-w-*` plus `mx-auto` (or the `container` utility) rather
  than fixed widths, so layout is fluid and responsive by default.
- Control overflow intentionally with `overflow-x-auto`/`overflow-hidden`; wide content
  (tables, code) should scroll inside its own box, never the page body.

## Examples

**Good Example** — explicit positioning context and responsive show/hide

```html
<!-- `relative` on the card makes the badge's `absolute` position resolve to the card,
     not to some distant ancestor. The nav is hidden on mobile, shown from md up. -->
<div class="relative max-w-sm mx-auto rounded-lg border p-4">
  <span class="absolute top-2 right-2 rounded-full bg-red-500 px-2 text-xs text-white">
    New
  </span>
  <h3 class="text-lg font-semibold">Plan</h3>
  <nav class="hidden md:block mt-4">…</nav>
</div>
```

**Bad Example** — absolute with no positioning context, fixed width

```html
<!-- No ancestor is `relative`, so the badge positions against the viewport and drifts.
     A hardcoded width breaks on small screens and ignores the responsive system. -->
<div class="w-[380px] rounded-lg border p-4">
  <span class="absolute top-2 right-2 bg-red-500 text-white">New</span>
  <h3>Plan</h3>
</div>
```

## Common Mistakes

- Using `absolute` without a `relative` ancestor, so elements position against the wrong
  box and shift when the page scrolls or resizes.
- Expecting `sticky` to work without an inset (`top-0`) or inside a non-scrolling parent.
- Using `hidden` alone and forgetting the responsive variant to bring content back
  (`hidden md:flex`).
- Fixed pixel widths (`w-[380px]`) instead of `max-w-*` + `mx-auto`, breaking fluidity.
- Letting wide content overflow the page instead of scoping it with `overflow-x-auto`.

## Production Tips

- Test layouts at the narrowest supported width first; mobile-first layout exposes
  overflow and wrapping bugs that a desktop-only pass hides.
- For overlay/portal content (modals, tooltips), prefer `fixed` positioning plus a stacking
  context you control, and manage z-index on the design scale rather than ad-hoc large numbers.

## AI Review Checklist

- Is the `display` engine (flex/grid) chosen to match the layout's dimensionality?
- Does every `absolute` child have a `relative` (or other positioned) ancestor?
- Do `sticky` elements have both an inset and a scrollable ancestor?
- Are show/hide toggles done with responsive variants (`hidden md:block`)?
- Is width constrained with `max-w-*`/`mx-auto` rather than fixed pixels?
- Is wide content scoped with `overflow-*` so the page body never scrolls sideways?

## Related

- `knowledge/tailwind/05-flexbox.md`
- `knowledge/tailwind/06-grid.md`
- `knowledge/tailwind/07-spacing.md`
- `knowledge/tailwind/11-responsive-design.md`
- `knowledge/tailwind/02-core-concepts.md`
