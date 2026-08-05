---
id: tailwind/02-core-concepts
topic: tailwind
slug: core-concepts
title: "Core Concepts"
type: doc
order: 2
status: ready
tags: [tailwind, core-concepts, "hover:", variants, w-64, text-sm]
related: [tailwind/03-utility-first, tailwind/11-responsive-design, tailwind/13-state-variants, tailwind/16-theme, tailwind/04-layout]
when_to_use: "Read before writing Tailwind markup to understand utilities, variants, and the design token model."
---
# Core Concepts

## Purpose

This document defines the mental model behind every Tailwind class: what a **utility** is,
how **variants** modify it, how the **design token scale** constrains values, and how
**arbitrary values** provide a controlled escape hatch. Once these four ideas click, the
thousands of class names become predictable rather than memorized.

## Why It Matters

Agents that treat Tailwind classes as opaque strings copy patterns without understanding
them, producing markup that is inconsistent, non-responsive, or that hardcodes values the
design system already provides. Understanding that `md:hover:bg-blue-500` is
`variant:variant:utility` — and that `bg-blue-500` reads a theme token — lets you generate
correct classes for cases you have never seen, and reject wrong ones in review.

## Core Principles

- **A utility sets one thing.** `pt-4` sets `padding-top`; `flex` sets `display: flex`.
  Utilities compose; they do not overlap in intent.
- **Variants are prefixes that add a condition.** `hover:`, `md:`, `dark:`, `focus:`,
  `disabled:` gate when a utility applies. They stack left-to-right and read outer-to-inner.
- **Values come from a finite scale.** `p-4` is `1rem` because `4` maps to a spacing token,
  not because `4` means pixels. The scale is the design system (see [16-theme](16-theme.md)).
- **Mobile-first is the default.** An unprefixed utility applies at all widths; `md:` and up
  override it at larger breakpoints. There is no `sm:`-and-below.
- **Arbitrary values are explicit exceptions.** `top-[117px]` works but announces "this is
  off-system" — use it rarely and deliberately.

## Best Practices

- Read a class name as `[responsive]:[state]:[property][value]`. `lg:hover:text-white`
  = "on large screens, on hover, set text color to white."
- Reach for the scale first (`gap-2`, `text-sm`, `w-64`). Use arbitrary values only when
  no token fits and the value is genuinely one-off.
- Layer utilities in a stable, readable order (layout → box model → typography → color →
  state) so diffs are easy to review; a formatter like `prettier-plugin-tailwindcss` can
  enforce this automatically.
- Use `theme()` or CSS variables exposed by `@theme` (e.g. `var(--color-brand)`) when you
  need a token value inside custom CSS, rather than duplicating the literal.

## Examples

**Good Example** — variants and scale used as intended

```html
<!-- One element: mobile-first base, responsive override, and a state variant.
     Every value comes from the design scale, so it stays consistent site-wide. -->
<button
  class="px-4 py-2 text-sm font-medium
         bg-blue-600 text-white rounded-md
         hover:bg-blue-700 focus-visible:outline-2
         md:px-6 md:text-base"
>
  Save
</button>
```

**Bad Example** — fighting the system with arbitrary values and inline overrides

```html
<!-- Hardcoded pixel values bypass the scale, so this button never matches the
     others. Inline style defeats variants (no hover/focus/responsive possible). -->
<button
  class="pt-[9px] pb-[9px] pl-[17px] pr-[17px] text-[13px] rounded-[5px]"
  style="background:#2563eb;color:#fff"
>
  Save
</button>
```

## Common Mistakes

- Writing `sm:` expecting it to mean "small screens only." `sm:` means "≥ 640px and up";
  put the small-screen style in the unprefixed base.
- Ordering stacked variants wrong or assuming order does not matter for pseudo-elements
  like `before:`/`after:` where the element target changes.
- Reaching for `[arbitrary]` values for spacing/colors that a token already covers,
  eroding consistency.
- Putting responsive or state logic in `style={{}}`, which cannot express `hover:` or `md:`.
- Assuming a class exists because it "should"; Tailwind only generates classes it detects
  in source — a dynamically concatenated class name (`` `text-${color}-500` ``) is not seen.

## Production Tips

- Never build class names by string concatenation of dynamic fragments; the compiler
  cannot detect them and they get purged. Map to complete static class strings instead.
- Expose brand tokens through `@theme` so utilities like `bg-brand` exist, keeping the
  markup on-system instead of scattering arbitrary hex values.

## AI Review Checklist

- Is each class a single-purpose utility rather than an overloaded custom class?
- Are values drawn from the design scale, with arbitrary values used only as deliberate
  exceptions?
- Is the styling mobile-first (base unprefixed, larger breakpoints override)?
- Are responsive and state conditions expressed as variants, not inline styles?
- Are all class names statically present in source (no dynamic string concatenation)?

## Related

- `knowledge/tailwind/03-utility-first.md`
- `knowledge/tailwind/11-responsive-design.md`
- `knowledge/tailwind/13-state-variants.md`
- `knowledge/tailwind/16-theme.md`
- `knowledge/tailwind/04-layout.md`
