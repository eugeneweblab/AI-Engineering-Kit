---
id: tailwind/11-responsive-design
topic: tailwind
slug: responsive-design
title: "Tailwind CSS Responsive Design"
type: doc
order: 11
status: ready
tags: [tailwind, responsive-design]
related: [tailwind/04-layout, tailwind/06-grid, tailwind/05-flexbox, tailwind/08-sizing, tailwind/13-state-variants]
when_to_use: "Read before making any layout adapt across screen sizes, or when a component must work on both phones and desktops."
---
# Tailwind CSS Responsive Design

## Purpose

This document defines how to build layouts that adapt across screen sizes using Tailwind's
responsive variants (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`), the mobile-first model, the
`max-*` range variants, and container queries (`@container`, `@sm:` …). It is written so an
agent designs from small screens up and produces layouts that work on every viewport, not
just the one it was tested on.

Tailwind's breakpoint prefixes are **min-width** by default: an unprefixed utility applies
everywhere, and `md:` overrides it at 48rem and up. Understanding this mobile-first
direction is the whole game — get it backwards and every layout fights you.

## Why It Matters

Most traffic is mobile, yet layouts are usually authored on a wide desktop, so the small
screen is the one most likely to be broken and least likely to be tested. Responsive bugs —
overflow, unreadable text, tap targets that overlap — degrade the experience for the
majority of users while looking perfect to the developer. Because Tailwind makes it trivial
to add a `lg:` here and forget the base case, discipline about the mobile-first order is
what separates a layout that holds up from one that only demos well.

## Core Principles

- **Design mobile-first.** Write the base (unprefixed) styles for the smallest screen, then
  layer larger-screen overrides with `sm:` / `md:` / `lg:`. This matches how the variants
  cascade and keeps the small case correct by default.
- **Unprefixed means all sizes.** `md:` is "at medium and above," not "only medium." To style
  a range, combine `md:` with `max-lg:` (`md:max-lg:…`) or use the `max-*` variant.
- **Add breakpoints only where the layout actually breaks.** Don't sprinkle a variant at
  every step; change at the width where content stops fitting. Fewer breakpoints are easier
  to reason about.
- **Prefer container queries for reusable components.** A card that must look right in a
  sidebar and a full-width grid should respond to *its container's* width (`@container` +
  `@md:`), not the viewport — viewport breakpoints can't know where the component sits.
- **Test the smallest and largest ends.** The base case (narrow phone) and the widest case
  are where overflow and awkward stretching appear.

## Best Practices

- Start every responsive layout from the base classes, then add larger variants:
  `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`, `flex-col md:flex-row`, `text-2xl md:text-4xl`.
- Use `hidden md:block` / `md:hidden` to swap layouts (e.g. mobile menu vs desktop nav)
  rather than duplicating a component.
- Wrap a component in `@container` and use `@sm:` / `@md:` variants so it adapts to its slot,
  making it reusable in any width without new breakpoints.
- Constrain widths responsively (`max-w-full md:max-w-2xl`) so content never overflows narrow
  screens (see [Sizing](08-sizing.md)).
- Keep interactive targets at least ~44px on touch (`p-*` to pad small icons) so mobile taps
  land reliably.
- Reserve `2xl:` for genuinely large displays; most designs need only `sm`–`lg`.

## Examples

**Good Example** — mobile-first base, overrides layered up, container-aware component

```html
<!-- Base is the phone layout; each variant adds an override for a larger screen -->
<section class="flex flex-col gap-4 md:flex-row md:gap-8">
  <aside class="w-full md:w-64">Sidebar</aside>
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
    <!-- Card responds to its own container, so it works in any slot width -->
    <article class="@container rounded border p-4">
      <div class="flex flex-col @sm:flex-row @sm:items-center gap-3">…</div>
    </article>
  </div>
</section>
```

**Bad Example** — desktop-first, base assumes a wide screen, breaks on mobile

```html
<!-- Base is the DESKTOP layout; the small screen inherits flex-row and overflows -->
<section class="flex flex-row gap-8 sm:flex-col">
  <!-- Fixed sidebar width with no mobile override → overflows a phone -->
  <aside class="w-64">Sidebar</aside>
  <!-- Four columns as the base: unreadable, overflowing cards on mobile -->
  <div class="grid grid-cols-4 gap-4">
    <article class="rounded border p-4">…</article>
  </div>
</section>
```

## Common Mistakes

- Authoring desktop-first — putting the wide layout in the base and trying to "undo" it at
  small sizes, which fights the min-width cascade.
- Reading `md:` as "only medium screens" instead of "medium and up," then wondering why the
  style leaks to large screens.
- Adding a breakpoint at every tier out of habit instead of only where the layout breaks.
- Using viewport breakpoints for a component that lives in variable-width slots, when a
  container query is the correct tool.
- Fixed widths with no responsive `max-w-*`, causing overflow on phones.
- Testing only on a wide monitor and never on a narrow viewport, where the base case lives.

## Production Tips

- Tailwind v4's default breakpoints are `sm` 40rem, `md` 48rem, `lg` 64rem, `xl` 80rem,
  `2xl` 96rem; customize them in the theme rather than hard-coding arbitrary `min-[737px]:`
  variants that no one else shares.
- Container queries need a `@container` ancestor; forgetting it silently disables the `@`
  variants — check that the wrapper is present when a component won't respond.
- Prefer swapping layout with responsive utilities over rendering two component trees; one
  source of truth is easier to keep in sync than a mobile copy and a desktop copy.

## AI Review Checklist

- Are base (unprefixed) styles the mobile layout, with larger screens layered via variants?
- Is `md:` understood as "and up," with ranges handled by `max-*` where needed?
- Are breakpoints added only where the layout actually breaks, not at every tier?
- Do reusable components use container queries (`@container`) instead of viewport breakpoints
  where their width varies by slot?
- Are widths constrained (`max-w-*`) so nothing overflows narrow screens?
- Have both the smallest and largest viewports been considered?

## Related

- `knowledge/tailwind/04-layout.md`
- `knowledge/tailwind/06-grid.md`
- `knowledge/tailwind/05-flexbox.md`
- `knowledge/tailwind/08-sizing.md`
- `knowledge/tailwind/13-state-variants.md`
