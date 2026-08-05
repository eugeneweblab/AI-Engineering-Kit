---
id: accessibility/10-color-and-contrast
topic: accessibility
slug: color-and-contrast
title: "Color and Contrast"
type: doc
order: 10
status: ready
tags: [accessibility, color-and-contrast]
related: [accessibility/11-typography, accessibility/02-pour-principles, accessibility/08-forms, accessibility/09-images, accessibility/23-wcag]
when_to_use: "Read before choosing colors, defining themes, or building any UI where color conveys meaning or state."
---
# Color and Contrast

## Purpose

This document defines how to use color so that text is readable and meaning is not lost to
users with low vision or color blindness. It gives the concrete contrast ratios to hit and
the rule that color must never be the *only* way information is conveyed. It is written so an
agent can pick and review colors against verifiable thresholds, not taste.

Contrast and color-independence are two of the most objectively testable accessibility
requirements: they reduce to numbers and to a simple "would this still make sense in
grayscale?" check.

## Why It Matters

Roughly one in twelve men and one in two hundred women have a color vision deficiency, and
far more people have reduced contrast sensitivity from age, low-quality screens, or bright
sunlight. Low-contrast text is unreadable for them regardless of font size, and status shown
by color alone (red = error, green = success) is invisible. These are among the most common
failures found in automated audits and the easiest to fix — which also means shipping them
signals carelessness that legal reviewers notice.

## Core Principles

- **Meet the WCAG contrast minimums.** Normal text needs **4.5:1** against its background;
  large text (≥24px, or ≥18.66px bold) needs **3:1**. UI components and meaningful graphics
  need **3:1** (WCAG 2.2 SC 1.4.3 / 1.4.11).
- **Never use color as the only signal.** Pair every color-coded meaning with text, an icon,
  a pattern, or a shape. This is WCAG SC 1.4.1 "Use of Color".
- **Contrast is a ratio of luminance, not "darkness".** Two vivid colors can look distinct
  yet fail; always compute the ratio rather than eyeballing it.
- **State must be perceivable without hue.** Focus, error, selected, and disabled states need
  a non-color cue (outline, underline, label, icon).
- **Respect user and system preferences.** Support dark mode and forced-colors/high-contrast
  modes; do not hard-code colors that these modes cannot override.

## Best Practices

- Verify every text/background pair against 4.5:1 (or 3:1 for large text) with a contrast
  checker or a token linter in CI — do not approve colors by eye.
- Give focus indicators their own visible style meeting 3:1 against adjacent colors; see
  [typography](11-typography.md) and focus states, and never remove the outline without a
  replacement.
- Encode status redundantly: an error field gets a red border *and* an icon *and* a text
  message, not red alone; see [forms](08-forms.md).
- In charts, distinguish series by pattern, label, or direct annotation, not color alone;
  test the design in grayscale.
- Define colors as design tokens with contrast baked into the pairing rules, so components
  cannot combine a foreground and background that fail.
- For `forced-colors` (Windows High Contrast), use system color keywords and `currentColor`,
  and test that borders and focus rings survive.
- Do not lower contrast for "aesthetic" gray-on-gray placeholder or helper text — it is a
  frequent, avoidable failure.

## Examples

**Good Example** — redundant status cue and a passing ratio

```html
<!-- Meaning is carried by icon + text, not color alone; the red merely reinforces.
     #b3261e on #ffffff = 5.9:1, above the 4.5:1 minimum for body text. -->
<p class="status status--error" style="color:#b3261e">
  <svg aria-hidden="true"><!-- alert icon --></svg>
  Payment failed — check your card number.
</p>
```

```css
/* Focus is shown by an outline (a shape), independent of color, at ≥3:1. */
:focus-visible { outline: 3px solid #1a73e8; outline-offset: 2px; }
```

**Bad Example** — color-only meaning and failing contrast

```html
<!-- The ONLY difference between valid and invalid is the text color: invisible to
     color-blind users and to grayscale. No icon, no message, no border. -->
<input class="invalid" style="color:#e57373" />

<!-- #9e9e9e placeholder on #ffffff = 2.8:1 — below 4.5:1, unreadable for low vision. -->
<style>::placeholder { color:#9e9e9e; }</style>
```

## Common Mistakes

- Conveying required/error/success/selected purely through color.
- Low-contrast gray text (placeholders, captions, disabled-looking-but-active controls).
- Assuming large headings pass — they still need 3:1, and thin weights often fail.
- Forgetting UI-component contrast: input borders, toggle tracks, and icon buttons need 3:1.
- Removing focus outlines for looks, leaving keyboard users with no visible state.
- Hard-coding colors that break dark mode or forced-colors, or setting a background without a
  matching foreground.
- Judging contrast by how "bright" a color looks instead of computing the ratio.

## Production Tips

- Add a contrast check to CI (e.g. an axe/lint rule over rendered components or over token
  pairings) so a failing combination cannot merge.
- Keep a grayscale screenshot in design review — if a state disappears, it violates
  use-of-color.
- Test the real product in dark mode and Windows High Contrast, not just the default theme;
  many token systems only cover one.

## AI Review Checklist

- Does all text meet 4.5:1 (normal) or 3:1 (large), verified by a tool?
- Do UI components, borders, and meaningful icons meet 3:1?
- Is every color-coded meaning also conveyed by text, icon, or shape?
- Do focus, error, and selected states have a non-color indicator?
- Are colors defined as tokens that respect dark mode and forced-colors?
- Would the interface still be understandable in grayscale?

## Related

- `knowledge/accessibility/11-typography.md`
- `knowledge/accessibility/02-pour-principles.md`
- `knowledge/accessibility/08-forms.md`
- `knowledge/accessibility/09-images.md`
- `knowledge/accessibility/23-wcag.md`
