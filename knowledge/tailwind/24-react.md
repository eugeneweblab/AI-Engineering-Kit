---
id: tailwind/24-react
topic: tailwind
slug: react
title: "React"
type: doc
order: 24
status: ready
tags: [tailwind, react, twMerge, className, Button, clsx, VariantProps, peer]
related: [tailwind/17-components, tailwind/23-nextjs, tailwind/13-state-variants, tailwind/28-patterns, tailwind/26-best-practices]
when_to_use: "Read before styling a React component with Tailwind or building a reusable, prop-driven component API."
---
# React

## Purpose

This document defines how to use Tailwind CSS inside React components: how to
compose class strings, drive styles from props, merge conflicting utilities, and
build a reusable component API without losing the utility-first model. It is
written so an agent can style a component correctly and keep it maintainable as it
grows variants.

React and Tailwind meet at the `className` string. Everything hard about the
combination — conditional classes, variant props, list-based class generation —
is a string-construction problem, and the failure modes come from getting that
string wrong at build time or runtime.

## Why It Matters

Tailwind generates CSS only for class names it can find as complete, static
strings in your source. React tempts you to build class names dynamically
(`` `text-${color}-500` ``), which the scanner cannot see, so the class silently
never ships and the style is missing in production while working in dev with a CDN.
Separately, React re-renders make conflicting utilities (`px-2` and `px-4` on the
same element) resolve by CSS source order, not by which one you passed last — so
a variant override "randomly" wins or loses. Both bugs are invisible in code
review and only surface as visual defects, so the discipline has to be structural.

## Core Principles

- **Class names must be complete static strings.** The scanner does regex, not
  evaluation. Never interpolate a fragment of a class name.
- **Merge, don't concatenate, when overriding.** Two utilities from the same group
  conflict; the loser is decided by CSS order unless you use `tailwind-merge`.
- **Push variants into a typed API.** Encode visual states as props (`variant`,
  `size`), map them to classes in one place, not scattered ternaries at call sites.
- **Keep the utilities in the markup by default.** Reach for a component wrapper
  when a pattern repeats, not on the first use — utilities in JSX are the point.
- **Style is a pure function of props and state.** No imperative `element.style`,
  no toggling classes via refs; render the right className instead.

## Best Practices

- Define one `cn()` helper — `clsx` for conditionals plus `twMerge` to resolve
  conflicts — and route every dynamic className through it.
- Drive multi-variant components with `class-variance-authority` (CVA): it gives a
  typed `variants`/`defaultVariants` map and returns a single merged string.
- Map prop values to whole classes with a lookup object, never string
  interpolation: `const colors = { red: "bg-red-500", blue: "bg-blue-500" }`.
- Always accept and merge an incoming `className` prop (`cn(base, className)`) so
  parents can override — put the incoming class last so `twMerge` lets it win.
- Forward `ref` and spread `...rest` onto the styled element so the component stays
  composable as a real DOM primitive.
- Use `group`/`peer` and `data-*` variants for interaction state instead of
  tracking hover/open in React state and swapping classes manually.
- Only extract a component (or use `@apply`) when the exact class list repeats in
  three or more places; premature extraction hides the utilities.

## Examples

**Good Example** — static classes, typed variants, merged override

```tsx
import { cva, type VariantProps } from "class-variance-authority";
import { twMerge } from "tailwind-merge";
import clsx from "clsx";

export const cn = (...i: clsx.ClassValue[]) => twMerge(clsx(i));

const button = cva("rounded font-medium transition disabled:opacity-50", {
  variants: {
    variant: { primary: "bg-blue-600 text-white", ghost: "bg-transparent text-blue-600" },
    size: { sm: "px-2 py-1 text-sm", md: "px-4 py-2 text-base" },
  },
  defaultVariants: { variant: "primary", size: "md" },
});

type Props = React.ComponentProps<"button"> & VariantProps<typeof button>;

export function Button({ variant, size, className, ...rest }: Props) {
  // cn() merges base + variant + caller override; a later px-* wins cleanly.
  return <button className={cn(button({ variant, size }), className)} {...rest} />;
}
```

**Bad Example** — interpolated class, naive concat, unmergeable override

```tsx
function Button({ color, className, ...rest }: any) {
  // `bg-${color}-500` is never emitted: the scanner sees no complete class,
  // so in production the background is missing entirely.
  const base = `bg-${color}-500 px-4 py-2 rounded`;

  // String concat: if className is "px-2", BOTH px-4 and px-2 render and CSS
  // source order — not intent — decides the padding. Result is nondeterministic.
  return <button className={base + " " + (className ?? "")} {...rest} />;
}
```

## Common Mistakes

- Building class names with template literals from props or loop variables, so the
  class is purged and the style vanishes in the production build.
- Concatenating className strings so conflicting utilities both survive and order
  decides the winner; forgetting `tailwind-merge`.
- Not accepting a `className` prop, forcing callers to wrap in an extra div or use
  `!important`.
- Scattering `variant === "x" ? "..." : "..."` ternaries across JSX instead of one
  CVA/lookup map — variants drift out of sync.
- Toggling classes imperatively via refs or `useEffect` instead of rendering the
  correct className from state.
- Reaching for `@apply` or a wrapper component on first use, burying the utilities
  and the design intent.

## Production Tips

- Add the safelist only for the genuinely dynamic classes you cannot make static
  (e.g. a color from a CMS); everything else should be a real string in source.
- Enable the Tailwind Prettier plugin so class order is deterministic across the
  team and diffs stay small.
- Memoize CVA calls only if profiling shows it matters — the string build is cheap
  and premature `useMemo` adds noise.

## AI Review Checklist

- Is every class name a complete static string (no `` `x-${var}` `` interpolation)?
- Do all dynamic classNames go through a `cn()`/`twMerge` helper that resolves
  conflicts?
- Does the component accept and merge an incoming `className`, with the override
  applied last?
- Are variants defined once (CVA or a lookup map), not as scattered ternaries?
- Are `ref` and `...rest` forwarded so the component stays composable?
- Is interaction state driven by `group`/`peer`/`data-*` variants rather than
  imperative class toggling?

## Related

- `knowledge/tailwind/17-components.md`
- `knowledge/tailwind/23-nextjs.md`
- `knowledge/tailwind/13-state-variants.md`
- `knowledge/tailwind/28-patterns.md`
- `knowledge/tailwind/26-best-practices.md`
