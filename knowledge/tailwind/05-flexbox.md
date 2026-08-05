---
id: tailwind/05-flexbox
topic: tailwind
slug: flexbox
title: "Tailwind CSS Flexbox"
type: doc
order: 5
status: ready
tags: [tailwind, flexbox, flex-wrap, flex-1, min-w-0, truncate, overflow-hidden]
related: [tailwind/04-layout, tailwind/06-grid, tailwind/07-spacing, tailwind/11-responsive-design, tailwind/02-core-concepts]
when_to_use: "Read before laying out a one-dimensional row or column of items with flex utilities."
---
# Tailwind CSS Flexbox

## Purpose

This document covers Tailwind's flexbox utilities: turning on flex (`flex`), setting
direction (`flex-row`/`flex-col`), aligning along the main axis (`justify-*`) and cross
axis (`items-*`), wrapping (`flex-wrap`), growing/shrinking children (`flex-1`, `grow`,
`shrink`), and spacing them with `gap-*`. It sets the rules for building rows, columns, and
toolbars that behave under real content.

## Why It Matters

Flexbox is the workhorse for component-level layout — navbars, button rows, card footers,
form fields. Its two-axis alignment model is the single most common source of confusion:
mixing up `justify-*` (main axis) and `items-*` (cross axis) produces layouts that center on
the wrong axis and refuse to fix with more tweaks. And using margins instead of `gap` for
spacing creates brittle edge-item bugs. Precise flex usage removes a whole category of
"why won't this align" churn.

## Core Principles

- **`justify-*` follows the main axis; `items-*` follows the cross axis.** In `flex-row`
  the main axis is horizontal, so `justify-center` centers horizontally and `items-center`
  centers vertically. In `flex-col` the axes swap.
- **Space with `gap-*`, not child margins.** `gap` spaces only *between* items, with no
  leading/trailing margin to strip, and it works identically in row and column.
- **Growth is opt-in.** Children keep their content size until you add `flex-1`/`grow`.
  Use `flex-1` to fill remaining space, `shrink-0` to protect an item from being squeezed.
- **Wrapping is off by default.** A row overflows rather than wraps unless you add
  `flex-wrap`; decide explicitly which behavior you want.

## Best Practices

- Center a single element with `flex items-center justify-center` — the canonical,
  content-agnostic centering idiom (no fixed heights or margins).
- Use `justify-between` for "edges pushed apart" layouts (logo left, actions right) instead
  of pushing one side with `ml-auto` guesses; reserve `ml-auto`/`mr-auto` for one-off nudges.
- Protect fixed elements (icons, avatars) with `shrink-0` so long neighboring text does not
  crush them.
- Add `min-w-0` to a flex child that contains truncatable text; without it, `truncate` /
  `overflow-hidden` will not take effect because the child refuses to shrink below content.
- Set `gap-*` from the spacing scale so item spacing matches the rest of the design system.

## Examples

**Good Example** — correct axes, gap spacing, shrink protection

```html
<!-- Row: justify-between splits the two groups; items-center aligns them vertically.
     gap spaces the right-side buttons. shrink-0 keeps the avatar from being squeezed. -->
<header class="flex items-center justify-between gap-4 p-4">
  <div class="flex items-center gap-2 min-w-0">
    <img src="/a.png" class="size-8 shrink-0 rounded-full" alt="" />
    <span class="truncate">A very long user name that should ellipsize</span>
  </div>
  <div class="flex gap-2">
    <button class="px-3 py-1">Edit</button>
    <button class="px-3 py-1">Save</button>
  </div>
</header>
```

**Bad Example** — wrong axis and margin-based spacing

```html
<!-- items-center is the cross axis; on a default row it does NOT center horizontally,
     so this won't do what the author expects. Right margins leave a stray trailing gap
     after the last button, and the avatar can be crushed by long text (no shrink-0). -->
<header class="flex items-center p-4">
  <img src="/a.png" class="size-8 rounded-full mr-4" alt="" />
  <span class="truncate">A very long user name</span>
  <button class="mr-2">Edit</button>
  <button class="mr-2">Save</button>
</header>
```

## Common Mistakes

- Swapping `justify-*` and `items-*`, then adding more utilities to compensate instead of
  fixing the axis.
- Spacing flex children with `mr-*`/`mb-*`, leaving a trailing margin on the last item and
  breaking when items wrap.
- Forgetting `min-w-0` on a flex child, so `truncate` silently does nothing.
- Omitting `shrink-0` on fixed-size items, letting them collapse under long siblings.
- Expecting a row to wrap without `flex-wrap`, causing horizontal overflow.
- Using `flex-col` but still reasoning about `justify-*` as horizontal (it is vertical in a
  column).

## Production Tips

- For responsive layouts, switch direction with a variant — `flex-col md:flex-row` — to
  stack on mobile and align in a row on wider screens, rather than duplicating markup.
- Prefer `gap` over `space-x-*`/`space-y-*` for new code; `gap` is simpler and avoids the
  first-child selector edge cases that `space-*` introduces when items wrap or reorder.

## AI Review Checklist

- Are `justify-*` (main axis) and `items-*` (cross axis) used correctly for the direction?
- Is spacing done with `gap-*` rather than per-child margins?
- Do text-containing flex children have `min-w-0` when they must truncate?
- Are fixed-size items protected with `shrink-0`?
- Is `flex-wrap` present wherever wrapping is intended (and absent where it is not)?
- Are responsive direction changes done with variants (`flex-col md:flex-row`)?

## Related

- `knowledge/tailwind/04-layout.md`
- `knowledge/tailwind/06-grid.md`
- `knowledge/tailwind/07-spacing.md`
- `knowledge/tailwind/11-responsive-design.md`
- `knowledge/tailwind/02-core-concepts.md`
