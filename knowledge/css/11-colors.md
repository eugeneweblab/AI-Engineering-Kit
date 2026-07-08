---
id: css/11-colors
topic: css
slug: colors
title: "Colors"
type: doc
order: 11
status: ready
tags: [css, colors]
related: [css/10-typography, css/23-accessibility, css/20-css-variables, css/12-backgrounds, css/25-modern-css]
when_to_use: "Read before choosing color values, defining a palette, or building dark mode."
---
# Colors

## Purpose

This document defines how to work with color in CSS: color notations
(`hex`/`rgb`/`hsl`/`oklch`), contrast requirements, using custom properties for a
themeable palette, dark mode, and not encoding meaning in color alone. It is written so
an agent produces color that is accessible, consistent, and easy to theme.

Color decisions are tightly bound to [accessibility](23-accessibility.md) (contrast) and
[custom properties](20-css-variables.md) (theming); this doc focuses on choosing and
applying color correctly.

## Why It Matters

Color is where accessibility most often silently fails: low-contrast text passes visual
review by a sighted designer on a good monitor but is unreadable for many users, and
color-only status indicators (red = error) are invisible to color-blind users. Color is
also where inconsistency creeps in fastest — dozens of near-duplicate hex values scattered
through a codebase. Centralizing color into tokens and enforcing contrast fixes both the
accessibility and the maintainability problem at once.

## Core Principles

- **Never encode meaning in color alone.** Pair color with text, an icon, or a pattern.
  ~8% of men have some color-vision deficiency; a red/green-only signal excludes them
  (also a WCAG 1.4.1 requirement).
- **Meet contrast minimums.** WCAG AA requires ≥4.5:1 for normal text and ≥3:1 for large
  text and UI component boundaries. This is verifiable, not a matter of taste.
- **Define color once as tokens.** Put every color in a [custom property](20-css-variables.md)
  and reference the token everywhere; this makes theming and dark mode a matter of
  swapping variable values, not a global find-and-replace.
- **Prefer perceptually uniform color for palettes.** `oklch()` (widely supported since
  2023) keeps lightness consistent as you vary hue, so generated scales and states look
  even — unlike `hsl()`, where equal lightness values look unequal across hues.
- **Let the platform theme.** Respect `prefers-color-scheme` and use `color-scheme` so
  form controls and scrollbars match the theme.

## Best Practices

- Store semantic tokens (`--color-text`, `--color-surface`, `--color-danger`), not just
  raw palette values, so components reference *intent*; retheme by reassigning tokens.
- Verify every text/background pair against WCAG AA (4.5:1 body, 3:1 large) before
  shipping; treat failing contrast as a bug, not a style preference.
- Implement dark mode by overriding the same tokens inside
  `@media (prefers-color-scheme: dark)` (and/or a `[data-theme]` override for a manual
  toggle) — the components never change.
- Declare `color-scheme: light dark` so native UI (inputs, scrollbars) adapts and default
  text/background respond to the OS theme.
- Use `oklch()` for building palettes and adjusting states (hover/active) by nudging
  lightness/chroma; it keeps steps perceptually even and avoids muddy midpoints.
- Convey status with icon + label + color together (a red X with "Error"), never color
  alone.
- Never hardcode a hex value inside a component rule; reference a token so it stays
  consistent and themeable.

## Examples

**Good Example** — tokens, semantic naming, accessible dark mode

```css
:root {
  color-scheme: light dark;         /* native controls follow the theme */
  --color-surface: oklch(99% 0 0);  /* near-white */
  --color-text:    oklch(25% 0 0);  /* ~13:1 on surface — passes AA easily */
  --color-danger:  oklch(55% 0.18 25);
}
@media (prefers-color-scheme: dark) {
  :root {
    --color-surface: oklch(20% 0 0);
    --color-text:    oklch(92% 0 0); /* re-verified for contrast on dark */
  }
}
.alert--danger {
  color: var(--color-danger);
}
/* Status is not color-only: icon + text carry the meaning too */
.alert--danger::before { content: "⚠ Error: "; }
```

**Bad Example** — hardcoded, low-contrast, color-only meaning

```css
.note {
  color: #999;          /* #999 on white ≈ 2.8:1 — fails WCAG AA */
  background: #fff;      /* hardcoded; no dark-mode path */
}
.status-ok    { color: green; }  /* meaning conveyed by color ALONE */
.status-error { color: red; }    /* invisible distinction for color-blind users */
/* No tokens: these hex/keywords are duplicated across dozens of files. */
```

## Common Mistakes

- Low-contrast text (light gray on white) that fails the 4.5:1 AA threshold.
- Signaling state with color only (red/green) with no icon or label.
- Hardcoding hex values in components instead of referencing tokens, causing drift and
  making dark mode a rewrite.
- Building dark mode by duplicating whole stylesheets instead of overriding tokens.
- Forgetting `color-scheme`, leaving native form controls stuck in light mode on a dark UI.
- Using `hsl()` for a palette and getting uneven perceived lightness across hues.

## Production Tips

- Add an automated contrast check (axe, Lighthouse, or a linter) to CI so failing pairs
  are caught before merge, not in an audit later.
- Keep a two-layer token system: a primitive palette (`--blue-500`) and semantic aliases
  (`--color-link: var(--blue-500)`); components use only semantic tokens.
- `color-mix(in oklch, ...)` generates hover/disabled variants from a base token at
  runtime, avoiding a hand-maintained shade for every state.
- Test the UI in both light and dark and with a color-blindness simulator before shipping.

## AI Review Checklist

- Does every text/background pair meet WCAG AA (4.5:1 body, 3:1 large / UI)?
- Is status/meaning conveyed by more than color (icon or label too)?
- Are colors defined as tokens/custom properties rather than hardcoded per component?
- Is dark mode implemented by overriding tokens under `prefers-color-scheme`, not by
  duplication?
- Is `color-scheme` declared so native controls match the theme?
- Are semantic tokens (`--color-text`) used by components rather than raw palette values?

## Related

- `knowledge/css/10-typography.md`
- `knowledge/css/23-accessibility.md`
- `knowledge/css/20-css-variables.md`
- `knowledge/css/12-backgrounds.md`
- `knowledge/css/25-modern-css.md`
