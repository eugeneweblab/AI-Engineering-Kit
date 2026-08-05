---
id: tailwind/26-best-practices
topic: tailwind
slug: best-practices
title: "Tailwind CSS Best Practices"
type: doc
order: 26
status: ready
tags: [tailwind, best-practices, tokens, gap-6, eslint-plugin-tailwindcss]
related: [tailwind/03-utility-first, tailwind/21-design-system, tailwind/17-components, tailwind/28-patterns, tailwind/100-common-antipatterns]
when_to_use: "Read before writing or reviewing Tailwind markup to keep it consistent, themeable, and maintainable."
---
# Tailwind CSS Best Practices

## Purpose

This document defines the day-to-day habits that keep a Tailwind codebase
readable, consistent, and cheap to change: when to use tokens versus arbitrary
values, when to extract a component, how to keep class lists ordered, and how to
stay inside the design system. It is written so an agent can produce markup that a
team would accept in review without rework.

Tailwind's whole value is that the constraints (a fixed spacing/color/type scale)
prevent drift. Best practice is mostly about honoring those constraints instead of
escaping them one arbitrary value at a time.

## Why It Matters

Tailwind gives you thousands of one-off escape hatches — arbitrary values, inline
overrides, `!important`. Used freely, they reproduce exactly the unmaintainable,
inconsistent CSS Tailwind was meant to prevent, except now it is spread across
JSX. The discipline is not writing utilities; it is refusing the easy escape hatch
so the design stays on-scale and theme changes remain a one-file edit. A codebase
that respects the token system can be re-themed centrally; one full of
`bg-[#3b7cff]` and `mt-[13px]` cannot.

## Core Principles

- **Use theme tokens, not arbitrary values.** `p-4`, `text-gray-700`, `gap-6` pull
  from the scale; `p-[17px]`, `text-[#334]` bypass it and break re-theming.
- **Utilities first, abstraction later.** Keep styles in the markup; extract a
  component only when the same class list repeats and needs to stay in sync.
- **One source of truth for design decisions.** Colors, spacing, radii, and
  breakpoints live in the theme, referenced everywhere, defined once.
- **Deterministic class order.** Let the Prettier plugin sort classes so diffs are
  minimal and humans stop arguing about order.
- **Semantic HTML underneath the utilities.** Tailwind styles appearance; the tag,
  roles, and states still carry the meaning and accessibility.

## Best Practices

- Reach for an arbitrary value only for a genuinely one-off, non-reusable number;
  if it appears twice, add it to the theme instead.
- Extract to a React component (not `@apply`) when a class list repeats three or
  more times — it keeps the utilities visible and the variants typed.
- Prefer `@apply` only for third-party/unstyleable markup (e.g. prose, injected
  widgets) where you cannot add classes to the element directly.
- Order utilities by concern with the Prettier plugin: layout → box → typography →
  visual → state; never hand-sort.
- Use `gap-*` on fl/grid containers instead of margins between children — it avoids
  margin-collapse surprises and the first/last child special-casing.
- Style state with variants (`hover:`, `focus-visible:`, `disabled:`,
  `aria-*`, `data-*`), not JavaScript class toggling.
- Keep responsive design mobile-first: unprefixed = smallest screen, then layer
  `sm:`/`md:`/`lg:` upward. Do not write `max-*` variants to undo a desktop default.
- Centralize brand and semantic colors as named tokens (`--color-brand`,
  `--color-danger`) so intent survives a palette change.

## Examples

**Good Example** — tokens, semantic state, mobile-first

```tsx
// Scale tokens (p-4, gap-3, text-gray-700) keep this on the design system.
// focus-visible + disabled are declarative; gap avoids margin math.
<button
  className="flex items-center gap-3 rounded-lg bg-brand px-4 py-2
             text-sm font-medium text-white
             hover:bg-brand/90 focus-visible:ring-2 focus-visible:ring-brand
             disabled:cursor-not-allowed disabled:opacity-50
             md:text-base"
>
  Save
</button>
```

**Bad Example** — arbitrary values, hardcoded color, JS-toggled state

```tsx
// mt-[13px] and #3b7cff bypass the scale, so a re-theme misses this element.
// max-md: undoes a desktop default — anti-mobile-first and hard to reason about.
// isHover class toggling reimplements :hover in JS for no reason.
<button
  className={
    "mt-[13px] rounded-[7px] bg-[#3b7cff] px-[17px] py-[9px] text-[15px] " +
    "max-md:px-[10px] " +
    (isHover ? "bg-[#2f6ae0]" : "")
  }
  onMouseEnter={() => setHover(true)}
  onMouseLeave={() => setHover(false)}
>
  Save
</button>
```

## Common Mistakes

- Peppering markup with arbitrary values instead of extending the theme, so the
  design silently drifts off-scale and cannot be re-themed.
- Extracting components or `@apply`-ing on first use, hiding the utilities and the
  intent before any repetition exists.
- Hardcoding hex colors instead of semantic tokens, so brand changes require a
  find-and-replace across the codebase.
- Hand-ordering classes and bikeshedding order in review instead of enabling the
  Prettier plugin.
- Using margins between flex/grid children where `gap-*` is cleaner and avoids
  collapse.
- Writing `max-*` desktop-down overrides instead of building up mobile-first.

## Production Tips

- Enforce order and forbid a raw-hex denylist in CI (`eslint-plugin-tailwindcss` or
  a lint rule) so drift is caught mechanically, not by reviewer memory.
- Track the shipped CSS size over time; a sudden jump usually means arbitrary-value
  sprawl or an accidental safelist.
- Document the semantic token names in the design-system doc so contributors reach
  for `bg-danger`, not `bg-red-600`.

## AI Review Checklist

- Do spacing, color, and radius come from theme tokens rather than arbitrary
  values?
- Is component extraction / `@apply` justified by real repetition, not premature?
- Are brand and status colors referenced as semantic tokens, not raw hex?
- Is the class order handled by the Prettier plugin (consistent, not hand-sorted)?
- Is layout mobile-first (`sm:`/`md:` upward), not desktop-down `max-*` overrides?
- Is interactive state expressed with variants rather than JS class toggling?

## Related

- `knowledge/tailwind/03-utility-first.md`
- `knowledge/tailwind/21-design-system.md`
- `knowledge/tailwind/17-components.md`
- `knowledge/tailwind/28-patterns.md`
- `knowledge/tailwind/100-common-antipatterns.md`
