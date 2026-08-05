---
id: css/09-spacing
topic: css
slug: spacing
title: "CSS Spacing"
type: doc
order: 9
status: ready
tags: [css, spacing]
related: [css/04-box-model, css/08-sizing, css/06-flexbox, css/07-grid, css/20-css-variables]
when_to_use: "Read before choosing margin, padding, or gap to separate elements."
---
# CSS Spacing

## Purpose

This document defines how to create space between and inside elements: `margin` vs
`padding` vs `gap`, margin collapsing, logical properties, and spacing scales. It is
written so an agent produces consistent, predictable spacing instead of scattered
one-off pixel values that drift and collide.

Spacing is part of the [box model](04-box-model.md); this doc focuses on *choosing the
right spacing tool* and keeping values systematic.

## Why It Matters

Inconsistent spacing is what makes an interface look amateur even when nothing is
"broken": gaps of 13px here, 17px there, a double margin where two collapsed ones were
expected. Two root problems cause it — using the wrong property (margin where gap belongs)
and using arbitrary values instead of a scale. Fixing both makes layouts predictable,
easier to review, and immune to the "why is there extra space here?" debugging that
margin collapsing famously produces.

## Core Principles

- **`padding` is space *inside* the border; `margin` is space *outside* it.** Use padding
  to give content breathing room within a box; use margin to separate a box from siblings.
- **Prefer `gap` for spacing between siblings in flex/grid.** `gap` applies only between
  items, cannot collapse, and needs no `:last-child` cleanup — it is strictly better than
  per-child margins where it applies.
- **Vertical margins collapse; know it or be surprised.** Adjacent top/bottom margins
  merge into the larger of the two, and a parent's margin can collapse with its first/last
  child's. `gap`, padding, and flex/grid contexts do not collapse.
- **Space in one direction.** Applying margin on a single side (e.g. `margin-top` on every
  item, or the "owl" `* + *`) avoids double-spacing and collapsing ambiguity.
- **Use a scale, not arbitrary numbers.** Derive all spacing from a small token set
  (e.g. multiples of `0.25rem`); this is what makes spacing look intentional.

## Best Practices

- Define a spacing scale as [custom properties](20-css-variables.md)
  (`--space-1: 0.25rem` … `--space-6: 2rem`) and reference tokens, never raw pixels, so
  spacing stays consistent and themeable.
- Use `gap` in every flex and grid container instead of margins between children; it
  removes trailing-margin cleanup entirely.
- Use logical properties — `margin-block`, `margin-inline`, `padding-inline` — so spacing
  flips correctly in right-to-left languages without extra rules.
- For flow content outside flex/grid, use a single-direction rule
  (`.flow > * + * { margin-block-start: var(--space-4); }`) so only *between* elements get
  space and margins never collapse unexpectedly.
- Put page-edge spacing as `padding` on the container, not `margin` on children, so the
  gutter is owned in one place.
- Never use `margin` to nudge an element into position that [Flexbox](06-flexbox.md) or
  [Grid](07-grid.md) alignment should handle; alignment survives content changes, nudges
  do not.

## Examples

**Good Example** — token scale, gap, single-direction flow

```css
:root {
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-6: 2rem;
}

.toolbar {
  display: flex;
  gap: var(--space-2);   /* space only between items, no trailing margin */
  padding: var(--space-4); /* inner breathing room, owned by the container */
}

/* Flow content: space only BETWEEN siblings, so no collapsing surprises */
.article > * + * { margin-block-start: var(--space-6); }
```

**Bad Example** — arbitrary values, margins, collapsing surprises

```css
.toolbar { display: flex; }
.toolbar > button {
  margin-right: 9px;  /* arbitrary; last button has a stray trailing margin */
}
.article > p {
  margin-top: 32px;
  margin-bottom: 32px; /* adjacent margins collapse to 32, not 64 — confusing */
}
.card { margin-top: 40px; } /* collapses with parent margin, space "disappears" */
```

## Common Mistakes

- Spacing flex/grid children with per-item `margin` and then stripping the last one with
  `:last-child`, where `gap` would need none of that.
- Setting both `margin-top` and `margin-bottom` and expecting them to add between
  elements — they collapse to the larger value.
- Using arbitrary pixel values (`13px`, `17px`) instead of a scale, producing subtly
  uneven, unmaintainable spacing.
- Using physical `margin-left`/`right` in RTL-supporting UIs where `margin-inline` is
  needed.
- Confusing padding and margin — e.g. padding on a clickable card that should be margin,
  making the whole gap clickable (or vice versa).

## Production Tips

- Adopt one spacing scale for the whole codebase and lint against raw pixel spacing; it is
  the cheapest way to keep a UI looking coherent across many contributors.
- When space appears where you did not add it, suspect margin collapsing first — switch
  the parent to `display: flex`/`grid` or add `padding` to establish a block formatting
  context and the collapse stops.
- `gap` works in Flexbox in all current browsers; there is no remaining reason to prefer
  margin-based gutters.

## AI Review Checklist

- Are flex/grid gutters done with `gap` rather than per-child margins?
- Do all spacing values come from a defined scale/tokens, not arbitrary pixels?
- Is spacing applied in a single direction to avoid margin collapsing?
- Are logical properties (`*-inline`, `*-block`) used for RTL-safe spacing?
- Is padding used for inner space and margin for outer separation, not swapped?
- Is unexpected whitespace explained by margin collapsing rather than hacked away?

## Related

- `knowledge/css/04-box-model.md`
- `knowledge/css/08-sizing.md`
- `knowledge/css/06-flexbox.md`
- `knowledge/css/07-grid.md`
- `knowledge/css/20-css-variables.md`
