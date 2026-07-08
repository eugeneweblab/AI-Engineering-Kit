---
id: tailwind/21-design-system
topic: tailwind
slug: design-system
title: "Design System"
type: doc
order: 21
status: ready
tags: [tailwind, design-system]
related: [tailwind/16-theme, tailwind/15-customization, tailwind/10-colors, tailwind/17-components, tailwind/22-accessibility]
when_to_use: "Read before defining shared design tokens, scales, or a component library on Tailwind."
---
# Design System

## Purpose

This document defines how to build a coherent design system on Tailwind CSS v4:
turning raw utilities into a governed set of **semantic tokens**, respecting the
built-in scales, and constraining the escape hatches so a whole codebase looks
like one product. It is written so an agent extends the system through tokens
rather than scattering one-off values.

Tailwind ships a design system already — a spacing scale, a type scale, a color
palette, all exposed as CSS variables in v4. A design *system* on top of it means
adding **semantic** names (`--color-primary`, `--color-surface`, `--radius-card`)
that encode intent, so the meaning lives in one place and the whole UI moves when
you change it.

## Why It Matters

The value of a design system is that a change propagates. If brand blue is written
as `bg-blue-600` in 300 places, a rebrand is a 300-site find-and-replace with no way
to verify completeness. If it is `bg-primary` backed by one token, it is a one-line
change. Systems also fail the *other* way: too many tokens, or unconstrained arbitrary
values (`p-[13px]`, `text-[#3b82f6]`), and consistency erodes until the UI looks
assembled by different teams. The token layer is where consistency is enforced or lost.

## Core Principles

- **Name tokens by intent, not appearance.** `--color-primary`, `--color-danger`,
  `--color-surface` survive a rebrand; `--color-blue` does not. Semantic names decouple
  meaning from value.
- **Two token tiers: primitives and semantics.** Primitives are the raw palette
  (`--color-blue-600`); semantics map intent to a primitive (`--color-primary: var(--color-blue-600)`).
  Markup consumes semantics; only the token file touches primitives.
- **Respect the scale; the escape hatch is rare.** Spacing, type, and radius come from
  the scale so rhythm stays consistent. Arbitrary values are a deliberate exception,
  reviewed, not a default.
- **Tokens live in `@theme` (v4), in CSS.** Defining them there generates utilities *and*
  CSS variables, so both `bg-primary` and `var(--color-primary)` work.
- **The system is the contract.** Components consume tokens; they do not invent colors
  or spacing locally.

## Best Practices

- Define primitives once, then layer semantics that reference them; theme switches
  (brand, dark mode) reassign semantics without touching primitives (see [16-theme](16-theme.md)).
- Use OKLCH for color tokens so lightness is perceptually uniform and generating accessible
  tints/shades is predictable (see [10-colors](10-colors.md)).
- Keep the scale small and intentional. Do not add a token for every one-off; add one when
  a value recurs with shared *meaning*.
- Constrain arbitrary values in review — an `p-[13px]` should either become a scale step or
  justify why the scale does not fit.
- Encode component-level decisions as tokens too (`--radius-card`, `--shadow-popover`) so
  components stay consistent and themeable.
- Document each semantic token's intent next to its definition so consumers pick the right one.

## Examples

**Good Example** — two-tier semantic tokens in `@theme`

```css
/* theme.css — primitives, then intent-named semantics that reference them */
@import "tailwindcss";

@theme {
  /* Primitives: the raw palette, referenced only here. */
  --color-blue-600: oklch(0.55 0.2 262);
  --color-red-600: oklch(0.58 0.22 27);
  --color-slate-50: oklch(0.98 0.005 250);

  /* Semantics: intent → primitive. Markup uses these. */
  --color-primary: var(--color-blue-600);
  --color-danger: var(--color-red-600);
  --color-surface: var(--color-slate-50);
  --radius-card: 0.75rem; /* one source of truth for card corners */
}
```

```html
<!-- Consumes intent tokens; a rebrand touches only theme.css. -->
<article class="bg-surface rounded-(--radius-card) p-4">
  <button class="bg-primary text-white">Save</button>
  <button class="bg-danger text-white">Delete</button>
</article>
```

**Bad Example** — appearance-named values scattered through markup

```html
<!-- BUG: brand color hardcoded as blue in every call site → a rebrand is a
     risky, unverifiable find-and-replace across the codebase. -->
<button class="bg-blue-600 text-white">Save</button>

<!-- BUG: arbitrary radius and an off-scale hex bypass the system entirely →
     inconsistent corners and a color no token governs. -->
<article class="rounded-[13px] bg-[#f8fafc] p-[13px]">…</article>
```

## Common Mistakes

- Naming tokens by color (`--color-blue`) instead of intent, so a rebrand rewrites token
  names throughout the UI.
- Collapsing primitives and semantics into one tier, so every theme switch edits raw values.
- Letting arbitrary values (`p-[13px]`, `text-[#3b82f6]`) accumulate until the scale is
  meaningless.
- Over-tokenizing — a token per one-off value — which is as inconsistent as none.
- Defining tokens in a JS config on v4, so they never become CSS variables or utilities.
- Hardcoding component radii/shadows locally instead of tokenizing shared decisions.

## Production Tips

- Lint for raw hex colors and off-scale arbitrary values in `class` attributes; route
  violations to a token or the scale.
- Publish the token file as the single import for consuming apps in a monorepo so every
  surface shares one system.
- Snapshot key components in visual-regression tests; a token change should move all
  consumers together, which the snapshots confirm.

## AI Review Checklist

- Are tokens named by intent (`primary`, `danger`, `surface`), not by appearance?
- Is there a primitive tier and a semantic tier, with markup consuming only semantics?
- Are tokens defined in `@theme` so they generate both utilities and CSS variables?
- Are values taken from the scale, with arbitrary values the rare, justified exception?
- Are colors defined in OKLCH for perceptual consistency and accessible derivation?
- Do components consume shared tokens instead of inventing local colors/spacing?

## Related

- `knowledge/tailwind/16-theme.md`
- `knowledge/tailwind/15-customization.md`
- `knowledge/tailwind/10-colors.md`
- `knowledge/tailwind/17-components.md`
- `knowledge/tailwind/22-accessibility.md`
