---
id: tailwind/08-sizing
topic: tailwind
slug: sizing
title: "Tailwind CSS Sizing"
type: doc
order: 8
status: ready
tags: [tailwind, sizing, min-w-0, w-full, max-w-prose, w-64, flex-1, truncate]
related: [tailwind/07-spacing, tailwind/06-grid, tailwind/05-flexbox, tailwind/11-responsive-design, tailwind/04-layout]
when_to_use: "Read before setting widths, heights, or constraints — especially when content length is unknown or the element must stay responsive."
---
# Tailwind CSS Sizing

## Purpose

This document defines how to size elements with Tailwind's `w-*`, `h-*`, `size-*`,
`min-w-*` / `max-w-*`, `min-h-*` / `max-h-*` utilities, and the fractional, viewport, and
content-based keywords. It is written so an agent picks sizes that flex with content and
viewport instead of pinning fixed pixels that overflow or truncate.

Width and height set a target size; the `min-*` and `max-*` utilities set the boundaries the
element may not cross. The most robust layouts use constraints (`max-w-*`, `min-h-*`) far
more than fixed sizes, letting content and the browser decide the rest.

## Why It Matters

Fixed sizes are the single most common cause of broken responsive layouts. A `w-[400px]`
card looks perfect on the designer's monitor and overflows a phone; an `h-[200px]` box
clips its text the moment the copy is longer than the mock. Because the element still
renders, these bugs pass casual review and surface only with real content or a narrow
screen. Sizing with constraints instead of fixed values is what makes a component survive
contexts you never tested.

## Core Principles

- **Constrain, don't fix.** Prefer `max-w-*` and `min-h-*` over `w-*` and `h-*`. A max-width
  lets a block shrink on small screens; a min-height lets it grow with content. Fixed sizes
  do neither.
- **Avoid fixed heights on anything holding text.** Text length is variable and localized;
  `min-h-*` reserves space without clipping, a fixed `h-*` truncates or overflows.
- **Use `size-*` for square elements.** `size-10` sets width and height together — cleaner
  and less error-prone than `w-10 h-10` for icons, avatars, and buttons.
- **Cap line length for readability.** Long-form text should sit inside `max-w-prose` (or a
  `max-w-*` around 60–75ch). Full-width paragraphs are hard to read.
- **Let flex/grid children size themselves.** `w-full`, `flex-1`, and `min-w-0` cooperate
  with the container; a hard pixel width fights it and causes overflow.

## Best Practices

- Constrain page and content width with `max-w-*` (`max-w-screen-lg`, `max-w-3xl`) plus
  `mx-auto` to center, rather than a fixed `w-*`.
- Use fractional widths (`w-1/2`, `w-1/3`) or `w-full` inside Flex/Grid; reserve fixed
  widths for genuinely fixed chrome like a `w-64` sidebar.
- Add `min-w-0` to a flex child that holds text you want to truncate — without it, the
  child refuses to shrink and overflows the row.
- Prefer `min-h-screen` (or the dynamic `min-h-dvh`) over `h-screen` for full-height page
  shells so content taller than the viewport can still scroll into view.
- Use `size-*` for square controls; use `aspect-*` (e.g. `aspect-video`) to size media by
  ratio instead of pinning both dimensions.
- Reach for arbitrary sizes (`w-[420px]`) only for fixed design constants, and prefer theme
  tokens when the value repeats.

## Examples

**Good Example** — capped width, min-height, truncation-safe flex child

```html
<!-- max-w caps line length and shrinks on mobile; mx-auto centers; content sets height -->
<article class="mx-auto max-w-prose px-4">
  <div class="flex items-center gap-3">
    <img class="size-10 rounded-full" src="/avatar.jpg" alt="" />
    <!-- min-w-0 lets this child shrink so truncate can work inside the flex row -->
    <p class="min-w-0 truncate font-medium">A potentially very long author name</p>
  </div>
  <p class="mt-4">Body copy that grows to any length without clipping…</p>
</article>
```

**Bad Example** — fixed width and height that overflow and clip

```html
<!-- w-[600px] overflows any viewport narrower than 600px -->
<article class="w-[600px] mx-auto">
  <div class="flex items-center gap-3">
    <img class="w-10 h-10 rounded-full" src="/avatar.jpg" alt="" />
    <!-- no min-w-0: the name pushes the row wider instead of truncating -->
    <p class="truncate font-medium">A potentially very long author name</p>
  </div>
  <!-- h-[120px] clips any body copy longer than 120px tall -->
  <p class="h-[120px] overflow-hidden mt-4">Body copy that gets cut off…</p>
</article>
```

## Common Mistakes

- Fixed pixel widths (`w-[600px]`) that overflow on small screens — use `max-w-*` + responsive
  variants instead.
- Fixed heights on text containers, which clip or overflow with real content — use `min-h-*`.
- Writing `w-10 h-10` where `size-10` says the same thing more safely.
- Forgetting `min-w-0` on a flex child, so `truncate` never triggers and the row overflows.
- Using `h-screen` for page shells, cutting off content taller than the viewport instead of
  `min-h-screen` / `min-h-dvh`.
- Letting long-form text run edge to edge with no `max-w-*`, hurting readability.

## Production Tips

- Prefer the dynamic viewport units (`min-h-dvh`, `h-dvh`) over `vh` for full-height mobile
  layouts — they account for the collapsing browser toolbar that `100vh` ignores.
- Combine `max-w-*` with a responsive step (`max-w-md md:max-w-2xl`) to widen containers on
  large screens without ever exceeding the viewport on small ones.
- For image and video, set `aspect-*` plus `w-full` and let height follow — this reserves
  layout space before the asset loads and prevents cumulative layout shift.

## AI Review Checklist

- Are constraints (`max-w-*`, `min-h-*`) used in place of fixed `w-*` / `h-*` wherever content
  is variable?
- Is every text container free of fixed heights that would clip content?
- Are square elements sized with `size-*` rather than matching `w-*`/`h-*`?
- Do truncating flex children include `min-w-0`?
- Do full-height shells use `min-h-screen` / `min-h-dvh` instead of `h-screen`?
- Is long-form text capped with `max-w-prose` or a comparable `max-w-*`?

## Related

- `knowledge/tailwind/07-spacing.md`
- `knowledge/tailwind/06-grid.md`
- `knowledge/tailwind/05-flexbox.md`
- `knowledge/tailwind/11-responsive-design.md`
- `knowledge/tailwind/04-layout.md`
