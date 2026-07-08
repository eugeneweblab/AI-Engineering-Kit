---
id: css/05-positioning
topic: css
slug: positioning
title: "Positioning"
type: doc
order: 5
status: ready
tags: [css, positioning]
related: [css/04-box-model, css/06-flexbox, css/07-grid, css/14-transforms, css/23-accessibility]
when_to_use: "Read before using position, z-index, or overlays like modals, tooltips, and sticky headers."
---
# Positioning

## Purpose

This document defines the `position` property — `static`, `relative`, `absolute`, `fixed`,
`sticky` — how each removes an element from or keeps it in normal flow, and how **stacking
contexts** and `z-index` decide what renders on top. Positioning powers overlays, tooltips,
sticky headers, and badges, and it is where "why is this element behind that one?" and "why
did my layout jump?" bugs come from. An agent that understands containing blocks and
stacking contexts places elements deterministically instead of nudging with magic offsets.

## Why It Matters

Positioning quietly changes the rules an element plays by. `absolute` and `fixed` pull an
element *out of normal flow*, so its siblings collapse as if it were gone — a common cause of
overlapping content. `z-index` only works within a **stacking context**, so a `z-index: 9999`
tooltip can still render *behind* a sibling if a parent created a new context. These are not
random: they follow precise rules about containing blocks and stacking. Learn the rules and
overlays become predictable; ignore them and you get an arms race of ever-larger `z-index`
values that still don't work.

## Core Principles

- **`position` sets the containing block and flow participation.** `static` (default) and
  `relative` stay in flow; `absolute` and `fixed` leave flow; `sticky` toggles between the two
  at a scroll threshold. Offsets (`top`/`right`/`bottom`/`left`) do nothing on `static`.
- **`absolute` positions against the nearest *positioned* ancestor.** That means the nearest
  ancestor with `position` other than `static`. If you want to anchor a child, set
  `position: relative` on the parent — this is the fundamental containment pattern.
- **`z-index` is scoped to a stacking context.** An element only stacks against siblings in
  the same context. Many properties silently create a new context — `transform`, `opacity < 1`,
  `filter`, `will-change`, `position: fixed/sticky`, and `isolation: isolate`. A high
  `z-index` cannot escape its context.
- **`sticky` is relative until it crosses a threshold, then pins within its scroll container.**
  It stops at the edge of its *parent*, and it silently does nothing if an ancestor has
  `overflow: hidden/auto/scroll`.

## Best Practices

- To anchor an `absolute` child, always give the intended parent `position: relative`.
  Relying on a distant ancestor is how elements escape to the wrong container.
- Manage `z-index` with a small, documented scale (e.g. tokens: dropdown 100, sticky 200,
  modal 300, toast 400) instead of ad-hoc `9999`. Escalating numbers is a symptom of not
  understanding stacking contexts.
- Use `isolation: isolate` to deliberately create a stacking context and contain a
  component's `z-index` so it cannot interfere with, or be trapped by, the rest of the page.
- Prefer **flexbox/grid** for layout and reserve `absolute`/`fixed` for true overlays
  (tooltips, badges, modals). Positioning is not a layout system; using it as one produces
  brittle, overlap-prone pages.
- For modern overlays, prefer the top-layer primitives — `<dialog>` with `showModal()` and
  the Popover API / CSS anchor positioning — which escape `overflow: hidden` and stacking
  traps entirely, instead of a hand-rolled `position: fixed` overlay.
- Keep `position: fixed` overlays accessible: trap focus, restore it on close, and respect
  scroll (see [accessibility](23-accessibility.md)).

## Examples

**Good Example** — explicit containing block, tokenized stacking, robust sticky

```css
.badge-wrap { position: relative; }        /* the anchor for the absolute child */
.badge {
  position: absolute;
  top: 0; right: 0;                         /* offsets resolve against .badge-wrap */
  transform: translate(50%, -50%);
}

.site-header {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky, 200);            /* documented scale, not a magic 9999 */
}
/* No ancestor of .site-header sets overflow:hidden, so sticky actually pins. */
```

**Bad Example** — no anchor, magic z-index, trapped stacking

```css
.badge {
  position: absolute;
  top: 0; right: 0;
  /* No positioned ancestor → anchors to the viewport/page, floats to the wrong place. */
}

.tooltip { z-index: 999999; }               /* still hidden: a parent with transform */
.card    { transform: translateZ(0);        /* created a stacking context that traps it */ }
```

## Common Mistakes

- Using `position: absolute` without a `position: relative` ancestor, so the element anchors
  somewhere unexpected.
- Escalating `z-index` to huge numbers when the real issue is a stacking context created by a
  parent's `transform`, `opacity`, or `filter`.
- `position: sticky` "not working" because an ancestor has `overflow: hidden` or no scrollable
  threshold, or because `top`/`bottom` was never set.
- Building layout with absolute positioning, then fighting overlaps whenever content changes.
- Removing an element from flow with `absolute`/`fixed` and being surprised its siblings reflow
  into the space it left.

## Production Tips

- When `z-index` "doesn't work," inspect ancestors for stacking-context-creating properties
  before touching the number; browser devtools flag stacking contexts.
- Prefer the platform's top layer (`<dialog>`, Popover API, anchor positioning) for menus and
  modals — it sidesteps clipping and z-index conflicts by design.

## AI Review Checklist

- Does every `position: absolute` element have an intended `position: relative` ancestor?
- Are `z-index` values drawn from a documented scale rather than arbitrary large numbers?
- Have you checked for parent-created stacking contexts (`transform`, `opacity`, `filter`) before raising `z-index`?
- Does `position: sticky` have a threshold set and no clipping `overflow` ancestor?
- Is layout done with flex/grid, with positioning reserved for genuine overlays?

## Related

- `knowledge/css/04-box-model.md`
- `knowledge/css/06-flexbox.md`
- `knowledge/css/07-grid.md`
- `knowledge/css/14-transforms.md`
- `knowledge/css/23-accessibility.md`
