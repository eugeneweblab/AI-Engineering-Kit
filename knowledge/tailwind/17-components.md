---
id: tailwind/17-components
topic: tailwind
slug: components
title: "Tailwind CSS Components"
type: doc
order: 17
status: ready
tags: [tailwind, components, className, tailwind-merge, "@apply", twMerge, color, VariantProps]
related: [tailwind/03-utility-first, tailwind/24-react, tailwind/15-customization, tailwind/28-patterns, tailwind/21-design-system]
when_to_use: "Read before extracting repeated utility markup into a reusable component or class."
---
# Tailwind CSS Components

## Purpose

This document defines how to turn repeated Tailwind utility markup into reusable
components without losing the benefits of utility-first CSS. It covers the three
extraction mechanisms — framework/template components, `@apply` classes, and
variant helpers like CVA / tailwind-variants — and, crucially, *when* to use each.
It extends [03-utility-first](03-utility-first.md), which argues for utilities in
markup; this doc covers what to do when that markup repeats.

The core question is: what is the right unit of reuse? Tailwind's answer is
"reuse the *template*, not the *class string*." A button component that renders
utility classes gives you one place to change styling and behavior together. An
`@apply`-based `.btn` class gives you a shared class string but throws away
Tailwind's main advantage.

## Why It Matters

Extraction done wrong recreates the exact problem Tailwind solves. `@apply` is the
usual trap: it looks like clean CSS, but it invents a naming layer (`.btn`,
`.btn-primary`, `.card-header`), scatters styling back into stylesheets, and grows
its own specificity and dead-code problems — the CSS-architecture mess utilities
were meant to end. Meanwhile, premature extraction (a `<Button>` created after two
uses that are only superficially similar) produces a rigid component with a dozen
boolean props. Knowing when to extract, and into what, is what keeps the codebase
both DRY and flexible.

## Core Principles

- **Extract the template, not the classes.** Prefer a component (React, Vue,
  Blade, a partial) that owns the markup and its utilities over an `@apply` CSS
  class. One source of truth for structure *and* style.
- **`@apply` is a last resort.** Use it only where you can't make a component:
  styling third-party HTML you don't control, base element styles, or content you
  don't render (Markdown/CMS output). Never as the default way to "clean up" JSX.
- **Wait for the rule of three.** Extract when a pattern genuinely repeats and has
  stabilized — not on the second, superficially-similar occurrence. Premature
  components ossify the wrong abstraction.
- **Model variants as data, not class soup.** For components with states/sizes,
  use a variant helper (CVA, tailwind-variants) so variants are typed and
  conflicts are resolved — don't hand-concatenate class strings.
- **Merge classes safely.** When a component accepts an incoming `className`, merge
  with `tailwind-merge` so overrides win predictably instead of leaving two
  conflicting utilities in the string.

## Best Practices

- Build reusable UI as framework components that render utilities and forward a
  `className` prop (merged with `twMerge`) plus `...rest` for accessibility
  attributes.
- Use CVA / `tailwind-variants` for multi-variant components; define `variants`,
  `defaultVariants`, and `compoundVariants` instead of ternary class strings.
- Keep utilities in markup for one-off layouts; extraction has a cost (indirection)
  that only pays off on real repetition.
- Restrict `@apply` to `@layer base`/`components` for element defaults and
  un-ownable HTML; keep those blocks small and reviewable.
- Expose semantic props (`variant="primary"`, `size="sm"`), not styling props
  (`padding`, `color`), so the design system stays the source of truth.
- Co-locate the component with its variants; a reviewer should see structure,
  styles, and state in one file.

## Examples

**Good Example** — component owns markup, typed variants, safe merge

```tsx
import { cva, type VariantProps } from "class-variance-authority";
import { twMerge } from "tailwind-merge";

const button = cva(
  "inline-flex items-center rounded font-medium focus-visible:ring-2",
  {
    variants: {
      variant: { primary: "bg-blue-600 text-white hover:bg-blue-700",
                 ghost:   "bg-transparent text-blue-600 hover:bg-blue-50" },
      size:    { sm: "px-3 py-1.5 text-sm", md: "px-4 py-2" },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

type Props = React.ComponentProps<"button"> & VariantProps<typeof button>;

// One source of truth for structure + style; className merges without conflicts;
// ...rest forwards type, aria-*, disabled, etc.
export function Button({ variant, size, className, ...rest }: Props) {
  return <button className={twMerge(button({ variant, size }), className)} {...rest} />;
}
```

**Bad Example** — `@apply` naming layer, conflicting overrides

```css
/* BUG: reinvents CSS naming + specificity that utilities exist to avoid.
   Every new state needs another hand-maintained class. */
.btn { @apply inline-flex items-center rounded px-4 py-2 font-medium; }
.btn-primary { @apply bg-blue-600 text-white hover:bg-blue-700; }
```

```html
<!-- BUG: to override padding you now fight specificity; both px-* survive in
     the class list and the winner depends on CSS source order, not intent -->
<button class="btn btn-primary px-2">Save</button>
```

## Common Mistakes

- Using `@apply` as the default cleanup for repeated JSX instead of a component,
  recreating a CSS-naming/specificity layer.
- Extracting a component on the second occurrence, freezing an abstraction that
  doesn't fit the third case.
- Concatenating variant class strings with ternaries, which is untyped and lets
  conflicting utilities coexist.
- Accepting a `className` prop but not merging with `tailwind-merge`, so caller
  overrides silently lose to the base classes.
- Exposing low-level styling props (`color`, `padding`) that leak the design
  system and let call sites drift.
- Wrapping a single-use bit of markup in a component "for consistency," adding
  indirection with no payoff.

## Production Tips

- Add `tailwind-merge` and a variant helper (CVA or tailwind-variants) as first-class
  dependencies for any component library; document the pattern once.
- Configure the Tailwind IntelliSense `classRegex` (or the CVA/tv plugin) so class
  strings inside variant helpers still get autocomplete and linting.
- Review new `@apply` usages in code review as exceptions requiring justification,
  not routine.

## AI Review Checklist

- Is repeated markup extracted into a *component* rather than an `@apply` class?
- Is `@apply` limited to base styles or un-ownable/third-party HTML?
- Did extraction wait for genuine, stabilized repetition (rule of three)?
- Are multi-state components using a typed variant helper, not concatenated
  strings?
- Is an incoming `className` merged with `tailwind-merge` so overrides win?
- Do components expose semantic variant props rather than raw styling props?

## Related

- `knowledge/tailwind/03-utility-first.md`
- `knowledge/tailwind/24-react.md`
- `knowledge/tailwind/15-customization.md`
- `knowledge/tailwind/28-patterns.md`
- `knowledge/tailwind/21-design-system.md`
