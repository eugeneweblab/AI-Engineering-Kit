---
id: tailwind/22-accessibility
topic: tailwind
slug: accessibility
title: "Tailwind CSS Accessibility"
type: doc
order: 22
status: ready
tags: [tailwind, accessibility]
related: [tailwind/13-state-variants, tailwind/14-pseudo-classes, tailwind/12-dark-mode, tailwind/10-colors, tailwind/21-design-system]
when_to_use: "Read before shipping interactive UI: focus states, contrast, motion, and screen-reader support."
---
# Tailwind CSS Accessibility

## Purpose

This document defines how to keep Tailwind CSS v4 UI accessible: preserving visible
focus, meeting contrast, respecting reduced-motion, and exposing content to screen
readers. It is written so an agent can style with utilities without stripping the
affordances assistive technology and keyboard users depend on.

Tailwind styles appearance; it does not make an element accessible. Accessibility
comes from correct semantics (a real `<button>`, not a styled `<div>`), a visible
focus indicator, sufficient contrast, and motion that honors user preference — all
of which Tailwind can express, and all of which are easy to accidentally remove.

## Why It Matters

The most common accessibility regression in a utility-first codebase is silent:
someone adds `outline-none` to make a button "look cleaner" and removes the only
signal a keyboard user has about where they are. Focus disappears, and the UI becomes
unusable without a mouse — while looking perfect in a screenshot. Contrast failures,
motion that triggers vestibular disorders, and `div`-as-button patterns fail the same
way: invisible to sighted mouse users, blocking to everyone else. These are legal and
ethical requirements (WCAG), not polish.

## Core Principles

- **Never remove focus without replacing it.** `outline-none` is only acceptable when
  paired with a visible `focus-visible:` style. A keyboard user must always see focus.
- **Semantics first, utilities second.** Use the correct element (`<button>`, `<a>`,
  `<nav>`); style it with utilities. A styled `<div>` gets no keyboard or role behavior.
- **Contrast is a hard requirement, per theme.** Text must meet WCAG AA (4.5:1 normal,
  3:1 large). A pair that passes in light can fail in dark — verify both.
- **Respect `prefers-reduced-motion`.** Gate animations behind `motion-safe:`; provide a
  static fallback for `motion-reduce:`.
- **Hidden-but-available is a distinct state.** `sr-only` exposes text to screen readers
  while hiding it visually; `hidden` removes it from everyone.

## Best Practices

- Use `focus-visible:` (not `focus:`) for keyboard focus rings so mouse clicks do not
  show a ring but keyboard navigation does: `focus-visible:outline-2 focus-visible:outline-offset-2`.
- If you set `outline-none`, add a visible `focus-visible:ring-2 focus-visible:ring-primary`
  in the same class list — never alone.
- Label icon-only controls: give an `aria-label` and, where useful, an `sr-only` text node.
  Never rely on the icon glyph alone.
- Gate motion: `motion-safe:animate-spin` or `motion-safe:transition`; ensure the
  no-motion state is still usable.
- Ensure interactive targets are at least 24×24 CSS px (WCAG 2.2); use padding (`p-2`) to
  reach it rather than shrinking hit area.
- Support `forced-colors` (Windows High Contrast): avoid conveying state by color alone,
  and use `forced-colors:` overrides where a border/outline is needed.
- Verify contrast per theme with an automated checker and fix at the token level (see
  [21-design-system](21-design-system.md)).

## Examples

**Good Example** — semantic element, visible focus, reduced-motion aware

```html
<!-- Real <button>: keyboard, role, and Enter/Space come for free. -->
<button
  type="button"
  class="rounded bg-primary px-4 py-2 text-white
         outline-none focus-visible:ring-2 focus-visible:ring-offset-2
         focus-visible:ring-primary
         motion-safe:transition-colors hover:bg-primary/90"
>
  <!-- outline-none is safe ONLY because focus-visible:ring replaces it. -->
  Save
</button>

<!-- Icon-only control: labeled for screen readers. -->
<button type="button" aria-label="Close dialog" class="p-2">
  <svg aria-hidden="true" class="size-5"><!-- … --></svg>
</button>
```

**Bad Example** — div button, focus stripped, color-only state

```html
<!-- BUG: a <div> is not focusable, not announced as a button, and Enter/Space
     do nothing → unusable by keyboard and screen-reader users. -->
<div class="cursor-pointer rounded bg-primary px-4 py-2 text-white outline-none">
  <!-- BUG: outline-none with no focus-visible replacement → no focus indicator. -->
  Save
</div>

<!-- BUG: state signalled by color alone → invisible to colorblind users and in
     forced-colors mode. Also always animates, ignoring reduced-motion. -->
<span class="animate-pulse text-green-500">Active</span>
```

## Common Mistakes

- Adding `outline-none` (or `focus:outline-none`) with no `focus-visible:` replacement,
  erasing the keyboard focus indicator.
- Building interactive controls from `<div>`/`<span>` instead of `<button>`/`<a>`, losing
  keyboard, role, and default behavior.
- Icon-only buttons with no `aria-label`, leaving screen-reader users with no name.
- Using `focus:` for rings, so every mouse click flashes a ring and teams then remove it.
- Animating unconditionally, ignoring `prefers-reduced-motion`.
- Conveying status by color alone, failing colorblind and forced-colors users.
- Checking contrast only in light mode when the app also ships dark mode.

## Production Tips

- Run axe or Lighthouse in CI on key pages, once per theme, and fail the build on
  serious violations.
- Add a keyboard-only pass to manual QA: Tab through every interactive element and confirm
  a visible focus indicator on each.
- Provide a "reduce motion" experience by default under `motion-reduce:` and verify it in
  the OS setting, not just the DevTools emulation.

## AI Review Checklist

- Is every interactive control a semantic element (`<button>`, `<a>`), not a styled `<div>`?
- Does every focusable element show a visible `focus-visible:` indicator (no bare `outline-none`)?
- Do text/background pairs meet WCAG AA contrast in both light and dark themes?
- Are animations gated behind `motion-safe:` with a usable reduced-motion fallback?
- Do icon-only controls have an `aria-label` (and `aria-hidden` on the icon)?
- Is state conveyed by more than color, and do interactive targets meet the 24px minimum?

## Related

- `knowledge/tailwind/13-state-variants.md`
- `knowledge/tailwind/14-pseudo-classes.md`
- `knowledge/tailwind/12-dark-mode.md`
- `knowledge/tailwind/10-colors.md`
- `knowledge/tailwind/21-design-system.md`
