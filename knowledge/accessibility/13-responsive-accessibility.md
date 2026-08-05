---
id: accessibility/13-responsive-accessibility
topic: accessibility
slug: responsive-accessibility
title: "Responsive Accessibility"
type: doc
order: 13
status: ready
tags: [accessibility, responsive-accessibility, repeat, grid-template-columns, minmax, min-width]
related: [accessibility/12-layout, accessibility/11-typography, accessibility/14-motion-and-animation, accessibility/10-color-and-contrast, accessibility/04-keyboard-navigation]
when_to_use: "Read before setting viewport meta, breakpoints, units, or any zoom/reflow behavior."
---
# Responsive Accessibility

## Purpose

This document defines how a layout must adapt so that it remains usable when the user
changes the one thing designers do not control: the rendering conditions. Users zoom,
enlarge text, rotate their device, and browse at 320 CSS px. Responsive accessibility
is the guarantee that **no content and no functionality is lost** under any of these
conditions.

It maps directly to WCAG success criteria — **1.4.4 Resize Text**, **1.4.10 Reflow**,
**1.4.12 Text Spacing**, and **1.3.4 Orientation** — and is written so an agent can set
up units, breakpoints, and the viewport tag without silently violating them.

## Why It Matters

Zoom and text enlargement are the single most common assistive technique — far more
common than screen readers. Low-vision users routinely browse at 200%–400%. If the
layout was built in fixed pixels, that zoom either does nothing, produces a horizontal
scrollbar, or clips content behind the fold. The user cannot read what they came for.

The classic regression is a `<meta viewport>` tag with `user-scalable=no` or
`maximum-scale=1` copied from a template. It disables pinch-zoom entirely on mobile —
locking out exactly the users who need it most — and it is trivially easy to ship
because nothing looks broken on the developer's large screen.

## Core Principles

- **Never disable zoom.** The viewport tag must allow scaling. Blocking it is a direct
  WCAG 1.4.4 failure and helps no one.
- **Reflow, do not scroll sideways.** At 320 CSS px width (equivalent to 400% zoom on a
  1280px screen), content must reflow to one column with no two-dimensional scrolling —
  except for parts that inherently need it, like data tables or maps.
- **Size text in relative units.** `rem`/`em` scale with the user's font preference;
  fixed `px` on text ignores it.
- **Support both orientations.** Do not lock to portrait or landscape unless the content
  essentially requires one (e.g., a piano app). WCAG 1.3.4.
- **Nothing is lost on adaptation.** Every link, control, and block of copy available at
  desktop width must remain reachable at mobile width — hidden is not the same as
  removed only if it is still operable another way.

## Best Practices

- Use this viewport tag and nothing that blocks scaling:
  `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- Size fonts and spacing in `rem`; reserve `px` for hairline borders and similar
  non-scaling details. Base your `<html>` font on the user default (do not hard-set it
  to a fixed pixel size that overrides their browser preference).
- Design breakpoints around content, not devices. Use `min-width` media queries and let
  the layout collapse to a single column by 320px.
- Verify the **text-spacing** override does not clip content: line-height 1.5, paragraph
  spacing 2em, letter-spacing 0.12em, word-spacing 0.16em (WCAG 1.4.12).
- Prefer `dvh`/`svh`/`lvh` over `vh` for full-height sections so mobile browser chrome
  does not clip content.
- Keep touch targets at least 24x24 CSS px (44px is a comfortable target) with spacing,
  since fingers are less precise than a cursor.
- Test the real conditions: 320px width, 200% and 400% zoom, and both orientations.

## Examples

**Good Example** — scalable viewport, relative units, content-based reflow

```html
<!-- Allows pinch-zoom and honors the user's default text size. -->
<meta name="viewport" content="width=device-width, initial-scale=1">
```

```css
.card-grid {
  display: grid;
  /* Columns are defined by content width, not device count. The grid
     naturally collapses to one column as the viewport narrows, so it
     reflows at 320px with no horizontal scroll and no lost cards. */
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: 1rem;
}
h1 { font-size: 2rem; } /* rem → scales with the user's font setting */
```

**Bad Example** — zoom disabled, fixed pixels, fixed columns

```html
<!-- user-scalable=no blocks pinch-zoom: a direct WCAG 1.4.4 failure
     that locks out every low-vision user on mobile. -->
<meta name="viewport" content="width=device-width, user-scalable=no, maximum-scale=1">
```

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 400px); /* fixed → overflows narrow screens */
}
h1 { font-size: 32px; } /* px → ignores the user's text-size preference */
```

## Common Mistakes

- `user-scalable=no` or `maximum-scale=1` in the viewport tag, disabling pinch-zoom.
- Fixed-pixel font sizes that do not respond to the browser's text-size setting.
- Fixed-width columns or containers that force horizontal scrolling below ~768px.
- Locking orientation to portrait "for design reasons".
- Hiding, rather than reflowing, navigation and controls at small widths so features
  become unreachable.
- `100vh` sections whose bottom is clipped by mobile browser toolbars.

## Production Tips

- Add a CI check (or an axe/Lighthouse rule) that fails the build if the viewport tag
  contains `user-scalable=no` or `maximum-scale` below 2.
- In visual-regression tests, capture 320px width and 200% zoom snapshots, not just the
  desktop breakpoint.

## AI Review Checklist

- Does the viewport tag allow zoom (no `user-scalable=no`, no `maximum-scale` under 2)?
- Are text and spacing sized in `rem`/`em`, honoring the user's default font size?
- Does content reflow to a single column at 320px width with no horizontal scroll?
- Does the layout survive 200% and 400% zoom without clipping or loss of function?
- Are both orientations supported unless the content genuinely requires one?
- Does applying the WCAG 1.4.12 text-spacing overrides not clip or overlap content?

## Related

- `knowledge/accessibility/12-layout.md`
- `knowledge/accessibility/11-typography.md`
- `knowledge/accessibility/14-motion-and-animation.md`
- `knowledge/accessibility/10-color-and-contrast.md`
- `knowledge/accessibility/04-keyboard-navigation.md`
