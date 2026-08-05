---
id: tailwind/10-colors
topic: tailwind
slug: colors
title: "Tailwind CSS Colors"
type: doc
order: 10
status: ready
tags: [tailwind, colors, alone, surface, primary, danger, bg-primary, "dark:"]
related: [tailwind/16-theme, tailwind/12-dark-mode, tailwind/22-accessibility, tailwind/09-typography, tailwind/21-design-system]
when_to_use: "Read before applying any color — backgrounds, text, borders, rings — or defining a palette or brand tokens."
---
# Tailwind CSS Colors

## Purpose

This document defines how to apply color with Tailwind's `bg-*`, `text-*`, `border-*`,
`ring-*`, and `divide-*` utilities, the `/opacity` modifier, and how to name colors by role
in the theme rather than by literal hex. It is written so an agent produces an accessible,
themeable, consistent palette instead of scattering raw color values.

Tailwind ships a numbered palette (`gray-50` … `gray-950`, and the same for every hue) in
the perceptually uniform oklch space. The right approach is to reference these through
semantic theme tokens (`primary`, `surface`, `danger`) so the whole UI can be re-themed —
including dark mode — from one place.

## Why It Matters

Color carries meaning (success, danger, disabled), brand identity, and — critically —
contrast. Low-contrast text fails WCAG and is unreadable for low-vision users, yet it
renders without complaint, so it passes review and reaches production. Hard-coded hex values
scattered across components make re-theming and dark mode nearly impossible and let the
palette drift into dozens of near-duplicate grays. Color decisions are therefore both an
accessibility obligation and an architectural one.

## Core Principles

- **Name colors by role, not by value.** Reference `bg-primary` / `text-danger` mapped in
  the theme, not `bg-[#2563eb]` sprinkled everywhere. Roles can be re-themed; hex cannot.
- **Meet contrast minimums.** Body text needs ≥ 4.5:1 against its background, large text and
  UI components ≥ 3:1 (WCAG AA). Verify it; do not eyeball it.
- **Never encode meaning in color alone.** Pair color with an icon, label, or shape so
  color-blind users get the message (a red border alone is invisible to them).
- **Use the numbered scale for consistent shades.** Pick from `500`/`600` for solid fills,
  `100`/`50` for tints, `700`+ for text on light — don't invent one-off hexes that almost
  match.
- **Adjust opacity with the modifier, not new colors.** `bg-black/50` is one token at half
  alpha; a separate semi-transparent hex is an untracked new color.

## Best Practices

- Define brand and semantic colors in the theme (`--color-primary`, `--color-surface`,
  `--color-danger`) and use them by name everywhere; this is what makes dark mode and
  re-theming a config change, not a find-and-replace.
- Use the `/opacity` modifier for overlays and hover states: `bg-black/60`, `text-white/80`.
- Pair state colors with non-color cues: `text-red-600` plus an error icon and message.
- Choose contrast-checked pairings: dark text (`text-gray-900`) on light surfaces,
  `text-white` on `600`+ fills; verify with a contrast tool for anything borderline.
- Keep the palette small — a primary, a neutral gray ramp, and a few semantic hues. More
  hues means more inconsistency, not more expressiveness.
- Prefer `ring-*` for focus indicators over removing outlines; visible focus is an
  accessibility requirement (see [Accessibility](22-accessibility.md)).

## Examples

**Good Example** — semantic tokens, opacity modifier, contrast-safe, non-color cue

```html
<!-- Semantic tokens map to the theme, so dark mode/rebrand changes one place -->
<button class="bg-primary text-white hover:bg-primary/90 px-4 py-2 rounded">
  Save
</button>

<!-- State uses color AND an icon + text, so it's not color-only -->
<p class="flex items-center gap-2 text-danger">
  <svg class="size-4" aria-hidden="true"><!-- alert icon --></svg>
  Something went wrong.
</p>
```

**Bad Example** — raw hex everywhere, color-only meaning, unverified contrast

```html
<!-- Hard-coded hex can't be re-themed and drifts into near-duplicates -->
<button class="bg-[#2563eb] text-[#ffffff] hover:bg-[#1e50c8] px-4 py-2 rounded">
  Save
</button>

<!-- Meaning carried by color alone (no icon/label) → invisible to color-blind users;
     light gray on white almost certainly fails 4.5:1 contrast -->
<p class="text-[#c0c0c0]">Something went wrong.</p>
```

## Common Mistakes

- Hard-coding hex (`bg-[#2563eb]`) instead of semantic theme tokens, blocking dark mode and
  re-theming.
- Text/background pairs that fail the 4.5:1 (or 3:1 for large/UI) contrast minimum.
- Conveying success/error/disabled state with color only, excluding color-blind users.
- Inventing one-off grays that almost match existing scale steps, fragmenting the palette.
- Creating separate semi-transparent colors instead of using the `/opacity` modifier.
- Removing focus outlines without providing a visible `ring-*` replacement.
- Referencing dark-mode colors with `dark:bg-[#…]` hex instead of tokens that flip
  automatically.

## Production Tips

- Define semantic tokens in `@theme` so both light and dark values live in one file; a
  `dark:` variant then flips them without touching component markup.
- Add a CI or lint check that flags arbitrary color values (`bg-[#`, `text-[#`) in components
  — they're the leading indicator of palette drift.
- When picking new shades, stay within one hue's numbered ramp so tints and shades stay
  perceptually consistent (oklch keeps lightness steps even across hues).

## AI Review Checklist

- Are colors referenced by semantic theme token, not raw hex, in component markup?
- Does text meet ≥ 4.5:1 contrast (≥ 3:1 for large text and UI components)?
- Is every state/meaning conveyed with an icon or label in addition to color?
- Are shades taken from the numbered scale rather than one-off hexes?
- Is transparency applied via the `/opacity` modifier instead of new colors?
- Do focus states have a visible `ring-*` (outline not silently removed)?
- Are dark-mode colors handled by tokens/variants, not hard-coded hex?

## Related

- `knowledge/tailwind/16-theme.md`
- `knowledge/tailwind/12-dark-mode.md`
- `knowledge/tailwind/22-accessibility.md`
- `knowledge/tailwind/09-typography.md`
- `knowledge/tailwind/21-design-system.md`
