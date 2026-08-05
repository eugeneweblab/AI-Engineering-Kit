---
id: accessibility/11-typography
topic: accessibility
slug: typography
title: "Accessibility Typography"
type: doc
order: 11
status: ready
tags: [accessibility, typography, line-height, min-height, font-size, max-width, height]
related: [accessibility/10-color-and-contrast, accessibility/12-layout, accessibility/13-responsive-accessibility, accessibility/02-pour-principles, accessibility/23-wcag]
when_to_use: "Read before setting font sizes, line spacing, or building any text-heavy layout or theme."
---
# Accessibility Typography

## Purpose

This document defines how to set type so text stays readable and *resizable* for users with
low vision, dyslexia, or reduced motor precision. It covers sizing units, spacing minimums,
and the reflow behavior your layout must survive when a user zooms. It is written so an agent
can pick font values that meet WCAG requirements rather than fixed pixel guesses.

The core idea: text belongs to the user, not the designer. Users must be able to enlarge and
re-space it, and your layout must adapt without clipping, overlap, or horizontal scrolling.

## Why It Matters

Low vision is far more common than total blindness, and these users rely on browser zoom and
enlarged system fonts every day. A layout that hard-codes pixel sizes and fixed-height boxes
breaks the moment text grows — content is cut off or scrolls sideways, and the page becomes
unusable. Because these failures only appear when text is scaled (which developers rarely
test), they ship silently. Meeting a few concrete WCAG criteria for resize, reflow, and
spacing prevents an entire category of low-vision exclusion.

## Core Principles

- **Size text in relative units.** Use `rem`/`em` (or unitless line-height) so text scales
  with the user's browser and system settings. Fixed `px` on body text ignores their choice.
- **Support 200% zoom without loss (WCAG 1.4.4).** Text must be resizable to 200% with no
  loss of content or function — no clipping, no overlap.
- **Reflow at 320px (WCAG 1.4.10).** Content must reflow to a 320px-wide viewport (≈400% zoom
  on desktop) with no two-dimensional scrolling, except for things that inherently need it
  (data tables, maps).
- **Respect user-set text spacing (WCAG 1.4.12).** The page must not break when users override
  line-height to 1.5×, paragraph spacing to 2×, letter-spacing to 0.12em, word-spacing 0.16em.
- **Readability is measurable.** Adequate size, line length, and spacing are requirements,
  not stylistic preferences.

## Best Practices

- Set body text to at least 16px equivalent (`1rem` with a normal root), and never disable
  zoom (`user-scalable=no` / `maximum-scale=1` in the viewport meta is prohibited).
- Use `line-height` of at least ~1.5 for body copy and keep line length around 45–80
  characters (`max-width: 70ch`) for scannability.
- Avoid fixed heights on text containers; let them grow with content. Use `min-height`, not
  `height`, when a minimum is needed.
- Prefer left-aligned (start-aligned) body text over justified — justification creates uneven
  "rivers" of space that hinder dyslexic readers.
- Do not convey meaning by typography alone (weight, italics) without a text or semantic
  equivalent; pair with color-independent cues per [color and contrast](10-color-and-contrast.md).
- Keep sufficient contrast at every weight — thin fonts often fail contrast even when the
  color value is dark; see [color and contrast](10-color-and-contrast.md).
- Test with browser zoom to 200% and 400%, and with a text-spacing bookmarklet, on real
  pages; see [responsive accessibility](13-responsive-accessibility.md).

## Examples

**Good Example** — relative, resizable, reflow-friendly type

```css
:root { font-size: 100%; }          /* honors the user's browser font size */
body {
  font-size: 1rem;                  /* scales with user setting, not locked to px */
  line-height: 1.5;                 /* meets text-spacing expectations */
}
.article {
  max-width: 70ch;                  /* readable line length, shrinks on zoom */
  /* no fixed height: container grows when text is enlarged or re-spaced */
}
```

```html
<!-- Zoom is allowed: no maximum-scale / user-scalable lock. -->
<meta name="viewport" content="width=device-width, initial-scale=1" />
```

**Bad Example** — pixel-locked, zoom-blocked, clipping layout

```html
<!-- Disables pinch-zoom, blocking the primary low-vision magnification tool. -->
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
```

```css
body   { font-size: 13px; line-height: 16px; } /* fixed px ignores user zoom/settings */
.card  { height: 120px; overflow: hidden; }    /* enlarged text is clipped and lost */
```

## Common Mistakes

- Setting body font size in `px`, so browser and OS font preferences are ignored.
- Disabling zoom via `maximum-scale=1` or `user-scalable=no` in the viewport meta.
- Fixed-height text boxes with `overflow: hidden`, clipping content when text grows.
- Line-height packed too tight (< 1.5) or lines too long (> 80 chars) for comfortable reading.
- Justified body text, producing uneven spacing that harms readers with dyslexia.
- Layouts that force horizontal scrolling at 320px / 400% zoom.
- Conveying emphasis by italics or weight alone with no semantic or textual backup.

## Production Tips

- Add a manual QA step (or a Playwright script) that loads key pages at 200% and 400% zoom
  and asserts no horizontal scrollbar and no clipped content.
- Ship a text-spacing test to CI or QA: inject the WCAG 1.4.12 overrides and check nothing
  overlaps or disappears.
- When embedding a design system, verify its type scale uses `rem`; many older systems hard-
  code `px` and silently fail resize criteria.

## AI Review Checklist

- Is body text sized in `rem`/`em`, not fixed `px`?
- Is zoom allowed (no `user-scalable=no` / `maximum-scale=1` in the viewport meta)?
- Does the layout survive 200% zoom and reflow at 320px with no 2-D scrolling?
- Do text containers avoid fixed heights that clip enlarged or re-spaced text?
- Is line-height ≥ ~1.5 and line length in a readable range?
- Does the page tolerate user-overridden line, letter, word, and paragraph spacing?

## Related

- `knowledge/accessibility/10-color-and-contrast.md`
- `knowledge/accessibility/12-layout.md`
- `knowledge/accessibility/13-responsive-accessibility.md`
- `knowledge/accessibility/02-pour-principles.md`
- `knowledge/accessibility/23-wcag.md`
