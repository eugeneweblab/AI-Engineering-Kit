---
id: css/23-accessibility
topic: css
slug: accessibility
title: "CSS Accessibility"
type: doc
order: 23
status: ready
tags: [css, accessibility]
related: [css/18-media-queries, css/11-colors, css/10-typography, css/16-animations, css/22-performance]
when_to_use: "Read before styling focus, color, motion, text sizing, or anything that hides or reorders content — i.e. before shipping almost any CSS."
---
# CSS Accessibility

## Purpose

This document defines how CSS affects accessibility: visible focus, color contrast,
honoring motion and contrast preferences, accessible hiding, text scaling, and the
danger of using CSS to reorder content away from the DOM. It is written so an agent's
styling does not exclude users with disabilities or fail WCAG.

CSS controls what users *perceive and operate*, so it is squarely an accessibility
surface. Many of the most common WCAG failures are pure CSS mistakes: removed focus
outlines, low-contrast text, motion that cannot be turned off, and content hidden in a
way that also hides it from assistive tech.

## Why It Matters

Roughly one in six people has a disability, and CSS decisions routinely lock them out:
an invisible focus ring makes a keyboard user unable to see where they are; 3:1 body
text is unreadable for low-vision users; unstoppable parallax can cause nausea or
seizures. These are not edge cases — they are WCAG conformance requirements and, in many
jurisdictions, legal obligations. They are also cheap to get right in CSS and expensive
to retrofit after launch, because they touch focus, color, and motion decisions made
throughout the stylesheet.

## Core Principles

- **Never remove focus without replacing it.** `outline: none` with no substitute makes
  the interface unusable by keyboard. If the default outline is ugly, style a better one
  with `:focus-visible`, do not delete it.
- **Meet contrast minimums.** WCAG AA requires 4.5:1 for normal text, 3:1 for large text
  and for UI components/graphical objects. Verify with a contrast tool, not by eye.
- **Honor user preferences.** `prefers-reduced-motion`, `prefers-contrast`, and
  `prefers-color-scheme` are direct statements of user need; treat them as requirements.
- **Do not convey meaning by color alone.** Color-blind users miss a red/green
  distinction; pair color with text, icon, or shape.
- **CSS order is not DOM order.** Flexbox/grid `order` and positioning change the visual
  sequence but not the tab/reading order, which follows the DOM. Divergence disorients
  keyboard and screen-reader users — keep them aligned.

## Best Practices

- Style focus with `:focus-visible` so keyboard users get a clear ring while mouse
  clicks stay clean; ensure the indicator itself meets 3:1 contrast against its
  surroundings (WCAG 2.2 focus-appearance).
- Size text in relative units (`rem`/`em`) so browser font-size and zoom scale it; never
  disable zoom via `user-scalable=no`.
- Gate animation behind `@media (prefers-reduced-motion: no-preference)` and provide a
  static equivalent; reserve full stops for the "reduce" branch.
- Hide content accessibly on purpose: use a `.visually-hidden` clip pattern to expose
  content to screen readers while hiding it visually, and `display: none` /
  `[hidden]` to hide from *everyone*. Do not confuse the two.
- Ensure interactive targets are at least 24x24 CSS px (WCAG 2.2) via padding/min-size,
  so they are operable by users with motor impairments.
- Keep DOM order equal to reading order; use `order`/absolute positioning only for
  presentation that does not change meaning.

## Examples

**Good Example** — visible focus, accessible hiding, honored motion

```css
/* Keyboard users get a high-contrast ring; mouse users are not distracted. */
:focus-visible { outline: 3px solid #1a56db; outline-offset: 2px; }

/* Visually hidden but still announced by screen readers (e.g. "Search" label). */
.visually-hidden {
  position: absolute; width: 1px; height: 1px;
  clip-path: inset(50%); overflow: hidden; white-space: nowrap;
}

/* Motion only for users who have not requested reduced motion. */
@media (prefers-reduced-motion: no-preference) {
  .modal { transition: transform 200ms ease; }
}
```

**Bad Example** — focus removed, color-only meaning, forced motion

```css
*:focus { outline: none; } /* keyboard users can no longer see where they are */

.error { color: #e11; }   /* meaning by color alone → invisible to color-blind users;
                             also needs an icon or text like "Error:" */

.hidden { display: none; } /* used for a label meant for screen readers → hidden from
                              THEM too; should be .visually-hidden instead */

.modal { transition: transform 200ms ease; } /* ignores prefers-reduced-motion */
```

## Common Mistakes

- `outline: none` with no `:focus-visible` replacement, stranding keyboard users.
- Body text below 4.5:1 contrast, or UI/borders below 3:1, judged by eye instead of a tool.
- Conveying state (error, success, required) with color only, no text or icon.
- Using `display: none` for content that should be screen-reader-only (use the
  `.visually-hidden` clip pattern) — or vice versa.
- Reordering content with flex/grid `order` so tab order no longer matches the visuals.
- Fixed `px` font sizes and `user-scalable=no`, breaking zoom for low-vision users.
- Animating without a `prefers-reduced-motion` guard.

## Production Tips

- Run automated checks (axe, Lighthouse) in CI to catch contrast and focus regressions,
  but pair them with a keyboard-only pass — automation misses focus-order problems.
- Test the whole flow with Tab/Shift-Tab and a screen reader; verify the focus ring is
  always visible and the reading order matches the layout.
- Support `prefers-contrast: more` by strengthening borders and text where your default
  theme is subtle; low-contrast "aesthetic" UI is a frequent complaint.

## AI Review Checklist

- Is focus always visible, styled via `:focus-visible`, and is `outline: none` never
  left without a replacement?
- Does text meet 4.5:1 and do UI components/large text meet 3:1 contrast?
- Is meaning conveyed by more than color (text, icon, or shape as well)?
- Is `prefers-reduced-motion` honored for every non-essential animation?
- Is screen-reader-only content hidden with the clip pattern, not `display: none`?
- Does DOM/reading order match the visual order (no meaning-changing `order` reflow)?
- Are text sizes relative and zoom left enabled, with 24px+ interactive targets?

## Related

- `knowledge/css/18-media-queries.md`
- `knowledge/css/11-colors.md`
- `knowledge/css/10-typography.md`
- `knowledge/css/16-animations.md`
- `knowledge/css/22-performance.md`
