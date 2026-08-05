---
id: tailwind/28-patterns
topic: tailwind
slug: patterns
title: "Tailwind CSS Patterns"
type: doc
order: 28
status: ready
tags: [tailwind, patterns]
related: [tailwind/17-components, tailwind/24-react, tailwind/13-state-variants, tailwind/26-best-practices, tailwind/21-design-system]
when_to_use: "Read when you need a proven Tailwind pattern for variants, state-driven styling, or reusable component structure."
---
# Tailwind CSS Patterns

## Purpose

This document catalogs the recurring, proven patterns for structuring Tailwind
code: the `cn()` merge helper, variant components with CVA, `group`/`peer`
state propagation, `data-*` and `aria-*` driven styling, and container-query
layouts. It is written so an agent can pick the established pattern for a problem
instead of inventing a one-off that the team then has to learn.

These are not novel techniques — they are the conventions that keep utility-first
code from degenerating into unmaintainable class soup as components gain states
and variants.

## Why It Matters

Without shared patterns, every developer solves "a button with three variants" or
"style a child when the parent is hovered" differently, and the codebase becomes a
collection of incompatible micro-conventions. Patterns matter because they make
styling predictable: a reviewer knows where variants live, a new contributor knows
how state is expressed, and refactors are mechanical. The specific patterns below
also sidestep Tailwind's real hazards — merge conflicts, purged dynamic classes,
and JS-driven state that should have been CSS.

## Core Principles

- **Encode variants declaratively, in one place.** A `variants` map (CVA) beats
  ternaries scattered across JSX; the API becomes typed and the classes stay
  co-located.
- **Let CSS carry interaction state.** `group`, `peer`, `data-*`, and `aria-*`
  variants express hover/open/selected without React state.
- **Merge overrides; never concatenate.** Every reusable component composes its
  classes through `cn()` so callers can override predictably.
- **Prefer container queries for component-level responsiveness.** A card should
  respond to its container's width, not the viewport, so it works in any slot.
- **Keep patterns small and composable.** A pattern that needs a paragraph of
  explanation is usually two patterns fighting.

## Best Practices

- Define `cn()` once (`twMerge(clsx(...))`) and use it in every component that
  builds a className, so overrides always resolve deterministically.
- Use CVA for any component with two or more visual axes (variant × size × state);
  expose `VariantProps` as the component's typed API.
- Reflect open/selected/loading as `data-*` attributes on the element and style
  with `data-[state=open]:` variants, so the DOM is the single source of truth.
- Use `group`/`group-hover:`/`group-focus-within:` to style descendants from a
  parent's state; use named groups (`group/item`) when nesting to avoid collisions.
- Use `peer`/`peer-checked:`/`peer-invalid:` to style a sibling from a form
  control's state — this replaces most "controlled input styling" React code.
- Reach for `@container` and `@sm:`/`@md:` container variants for cards, sidebars,
  and any component reused at different widths.
- Build compound components (e.g. `Card`, `Card.Header`) so structure and spacing
  are encapsulated but the utilities stay visible in each part.

## Examples

**Good Example** — CVA variants, merged override, data-state styling

```tsx
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/cn"; // twMerge(clsx(...))

const badge = cva("inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium", {
  variants: {
    tone: { neutral: "bg-gray-100 text-gray-700", danger: "bg-red-100 text-red-700" },
  },
  defaultVariants: { tone: "neutral" },
});

type Props = React.ComponentProps<"span"> & VariantProps<typeof badge> & { open?: boolean };

export function Badge({ tone, open, className, ...rest }: Props) {
  return (
    <span
      // data-state drives the ring via a variant, not JS class toggling.
      data-state={open ? "open" : "closed"}
      className={cn(badge({ tone }), "data-[state=open]:ring-2", className)}
      {...rest}
    />
  );
}
```

**Bad Example** — ternary soup, concat, JS-driven hover

```tsx
function Badge({ tone, isHover, isOpen, className }: any) {
  // Variants as inline ternaries: unreadable, untyped, drifts out of sync.
  // Concatenation lets conflicting classes both survive (order decides winner).
  // isHover reimplements :hover in React for something CSS does for free.
  return (
    <span
      className={
        (tone === "danger" ? "bg-red-100 text-red-700 " : "bg-gray-100 text-gray-700 ") +
        (isHover ? "opacity-90 " : "") +
        (isOpen ? "ring-2 " : "") +
        (className ?? "")
      }
    />
  );
}
```

## Common Mistakes

- Expressing variants as nested ternaries instead of a CVA/lookup map, producing
  untyped, drift-prone class strings.
- Concatenating classes in a reusable component so overrides depend on CSS order.
- Tracking hover/open/focus in React state when `group`/`peer`/`data-*` variants
  do it declaratively.
- Using viewport breakpoints for a component that is reused at multiple widths,
  where a container query is correct.
- Forgetting named groups when nesting `group`, so an inner element reacts to the
  wrong parent's state.
- Building a bespoke variant system per component instead of reusing the shared
  `cn()` + CVA convention.

## Production Tips

- Keep `cn()` and shared CVA recipes in one `lib` module so the whole app uses the
  same merge and variant semantics.
- When a `data-*`/`aria-*` variant styles a component, it also improves
  accessibility — the attribute is real state, not just a style hook.
- Prefer container queries for design-system primitives; they make a component
  portable across layouts without per-slot overrides.

## AI Review Checklist

- Are variants defined once via CVA/lookup with a typed prop API, not scattered
  ternaries?
- Does every reusable component merge classes through the shared `cn()` helper?
- Is interaction state expressed with `group`/`peer`/`data-*`/`aria-*` variants
  rather than React state?
- Are named groups used when `group` is nested, to avoid state collisions?
- Are container queries used for components reused at varying widths?
- Do compound components keep utilities visible while encapsulating structure?

## Related

- `knowledge/tailwind/17-components.md`
- `knowledge/tailwind/24-react.md`
- `knowledge/tailwind/13-state-variants.md`
- `knowledge/tailwind/26-best-practices.md`
- `knowledge/tailwind/21-design-system.md`
