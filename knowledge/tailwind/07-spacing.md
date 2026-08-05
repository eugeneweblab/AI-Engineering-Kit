---
id: tailwind/07-spacing
topic: tailwind
slug: spacing
title: "Tailwind CSS Spacing"
type: doc
order: 7
status: ready
tags: [tailwind, spacing, gap-6, gap-4, mx-auto]
related: [tailwind/08-sizing, tailwind/06-grid, tailwind/05-flexbox, tailwind/04-layout, tailwind/16-theme]
when_to_use: "Read before adding padding, margins, or gaps — any time you space elements apart or pad content inside a box."
---
# Tailwind CSS Spacing

## Purpose

This document defines how to control the space around and inside elements with Tailwind's
`p-*` (padding), `m-*` (margin), `gap-*`, and `space-x-*` / `space-y-*` utilities. It is
written so an agent produces consistent, scale-based spacing instead of arbitrary one-off
values that drift out of rhythm.

Spacing utilities all draw from a single numeric scale (`p-4` = `1rem`, `p-8` = `2rem`).
Padding pushes content inward from the box edge; margin pushes the box away from its
neighbors; `gap` spaces children of a Flex or Grid container. Choosing the right one is
what keeps a layout aligned.

## Why It Matters

Spacing is the visual rhythm of an interface. When every gap comes from the same scale, a
page feels intentional and stays easy to change globally. When gaps are hand-picked
(`mt-[13px]` here, `mt-[15px]` there), the design looks subtly broken and every adjustment
becomes a scavenger hunt. Margins in particular cause layout bugs that are invisible until
a component is reused: collapsing margins, doubled gutters, and space that belongs to the
wrong owner. Getting spacing right is cheap up front and expensive to retrofit.

## Core Principles

- **Stay on the spacing scale.** Use `p-4`, `gap-6`, `mt-2` — not arbitrary `p-[17px]`.
  The scale is the design system; arbitrary values opt out of it and break consistency.
- **Prefer `gap-*` for spacing between siblings.** In Flex and Grid containers, `gap`
  spaces children without adding outer margins you then have to remove. It never collapses
  and never doubles.
- **Let the parent own the gap, not the child.** A component should not carry its own outer
  margin; the container decides the space between items. This keeps components reusable in
  any context.
- **Padding for inside, margin for outside.** Padding is space within a box (background
  extends through it); margin is space between boxes (transparent). Confusing them yields
  backgrounds that stop too early or clickable areas that are too small.
- **Space asymmetrically only with intent.** `px-*` / `py-*` and `mx-*` / `my-*` exist so
  you set only the axis you mean; setting all four sides when you need two is noise.

## Best Practices

- Use `gap-*` on Flex/Grid containers as the default way to separate children.
- When a container is not Flex/Grid, use `space-y-*` / `space-x-*` to insert gaps between
  direct children — but know it applies margins to all but the first child, so it interacts
  badly with conditional rendering and `flex-wrap`.
- Center a fixed-width block horizontally with `mx-auto`; do not simulate it with equal
  `ml-*` / `mr-*`.
- Reach for logical padding on interactive elements (`px-4 py-2` on a button) so the hit
  area matches the visual size.
- If a design genuinely needs a value off the scale, extend the scale in the theme
  (`--spacing-*`) rather than sprinkling `[13px]` arbitrary values across files.
- Use negative margins (`-mt-4`) sparingly and only for deliberate overlap; they are a
  frequent source of clipped content.

## Examples

**Good Example** — scale values, container-owned gap, axis-specific padding

```html
<!-- The parent owns the spacing between children via gap; children stay context-free -->
<div class="flex flex-col gap-4">
  <!-- px/py set only the axes that matter; values come from the scale -->
  <button class="px-4 py-2 rounded bg-blue-600 text-white">Save</button>
  <button class="px-4 py-2 rounded border">Cancel</button>
</div>
```

**Bad Example** — arbitrary values, child-owned margins, all-four-sides padding

```html
<div class="flex flex-col">
  <!-- Every button carries its own outer margin: breaks the moment it's reused,
       and space-collapsing makes the real gap unpredictable -->
  <button class="p-[9px_17px] mb-[13px] rounded bg-blue-600 text-white">Save</button>
  <!-- Off-scale values that no other component shares → visual drift -->
  <button class="p-[9px_17px] rounded border">Cancel</button>
</div>
```

## Common Mistakes

- Arbitrary spacing (`mt-[13px]`, `p-[17px]`) instead of scale steps — the design loses its
  rhythm and becomes impossible to adjust globally.
- Giving components outer margins so they can't be reused without stripping the margin first.
- Using `space-y-*` inside a Flex container where `gap-*` is cleaner and wrap-safe.
- Doubling gutters by combining `gap-*` with per-child margins.
- Confusing padding and margin, producing backgrounds or borders that don't reach the edge.
- Overusing negative margins to patch spacing, which clips content and hides the real bug.

## Production Tips

- Tailwind's spacing scale is generated from a single `--spacing` base, so `p-4` and `gap-4`
  always agree. Keep custom spacing in the theme so tooling and autocomplete know about it.
- For consistent vertical rhythm in article/body content, prefer a single `gap-*` on a Flex
  column over stacked `mt-*` values on each child — one place to tune, no collapsing margins.
- Audit for arbitrary spacing with a quick grep for `-[` on `p`/`m`/`gap` classes; a spike of
  them is a sign the scale needs extending, not bypassing.

## AI Review Checklist

- Do all spacing values come from the scale (or an extended theme token), with no stray
  `[13px]`-style arbitrary values?
- Is spacing between siblings done with `gap-*` on the container where possible?
- Do components avoid carrying their own outer margins so they stay reusable?
- Is padding used for inside space and margin for outside space, not interchanged?
- Are `px`/`py` / `mx`/`my` used to set only the intended axis instead of all four sides?
- Are negative margins limited to deliberate overlap, not spacing patches?

## Related

- `knowledge/tailwind/08-sizing.md`
- `knowledge/tailwind/06-grid.md`
- `knowledge/tailwind/05-flexbox.md`
- `knowledge/tailwind/04-layout.md`
- `knowledge/tailwind/16-theme.md`
