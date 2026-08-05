---
id: tailwind/20-optimization
topic: tailwind
slug: optimization
title: "Optimization"
type: doc
order: 20
status: ready
tags: [tailwind, optimization, tailwindcss, Button, twMerge, clsx, px-2, prettier-plugin-tailwindcss]
related: [tailwind/19-performance, tailwind/27-production, tailwind/17-components, tailwind/03-utility-first, tailwind/26-best-practices]
when_to_use: "Read before shrinking CSS output, deduplicating class recipes, or resolving class conflicts."
---
# Optimization

## Purpose

This document defines the concrete techniques for producing lean, conflict-free
Tailwind CSS v4 output: how classes are deduplicated, how to resolve conflicting
utilities predictably, how to keep class order deterministic, and how to compress
the final asset. Where [19-performance](19-performance.md) explains *why* size and
build speed matter, this doc is the *how* — the specific tools and patterns.

Optimization here is not a separate build step you bolt on. Most of it is achieved
by writing classes the engine can dedupe, resolving conflicts at the source, and
letting the production pipeline minify and compress. The mistakes are subtle:
duplicate or conflicting utilities that render the wrong style rather than error.

## Why It Matters

Two Tailwind classes that set the same CSS property (`px-2 px-4`) do not merge — the
one later in the *generated stylesheet* wins, not the one later in your `class`
attribute. This makes conditional styling ("override the default padding when active")
silently produce the wrong result. Meanwhile, non-deterministic class order creates
noisy diffs and merge conflicts, and skipping compression leaves an easily halved
asset on the wire. Each is a small, avoidable loss that compounds across a codebase.

## Core Principles

- **Conflicting utilities do not cascade by attribute order.** `class="px-4 px-2"`
  does not reliably yield `px-2`; source order in the class string is not the tiebreaker.
  Resolve conflicts by not emitting both — merge intelligently instead.
- **Merge, do not concatenate, conditional classes.** Use a merge helper
  (`tailwind-merge`) so the last-intended utility wins for a given property.
- **Deterministic class order is a maintainability optimization.** Sort classes with
  the official Prettier plugin so every author and diff agrees.
- **The engine already dedupes identical utilities.** Repeating `flex` across components
  emits `.flex{}` once; do not chase "duplicate class" removal in markup.
- **Compression is a two-layer win.** Minify the CSS (whitespace, shorthand) and serve
  it with Brotli/gzip; the two stack.

## Best Practices

- Use `clsx`/`cn` to build conditional class lists and wrap with `twMerge` so overrides
  resolve correctly: `cn("px-4", isTight && "px-2")` yields `px-2`, not both.
- Add `prettier-plugin-tailwindcss` so class order is canonical and reviewable; it also
  sorts custom utilities registered via `@utility`.
- Extract repeated recipes into a component or a `cn()` helper, not `@apply`; `@apply`
  can hide conflicts and duplicate declarations across files (see [17-components](17-components.md)).
- Prefer the design scale so equal values collapse to one rule; arbitrary values with
  near-identical numbers each emit a unique rule that cannot dedupe.
- Let the production build minify and hash the CSS, and enable Brotli at the CDN/server.
- Keep one Tailwind entry stylesheet; multiple imports of `tailwindcss` duplicate base
  layers and inflate output.

## Examples

**Good Example** — conflict-safe merge, deterministic order

```tsx
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// cn() merges so the LAST utility for a property wins, regardless of order.
export const cn = (...inputs: any[]) => twMerge(clsx(inputs));

function Button({ compact }: { compact?: boolean }) {
  // Default px-4; when compact, px-2 actually overrides it (both never ship).
  return <button className={cn("rounded px-4 py-2", compact && "px-2")}>Go</button>;
}
```

```jsonc
// .prettierrc — canonical class order, stable diffs, no bikeshedding
{ "plugins": ["prettier-plugin-tailwindcss"] }
```

**Bad Example** — concatenated conflicts and arbitrary-value sprawl

```tsx
function Button({ compact }: { compact?: boolean }) {
  // BUG: both px-4 and px-2 ship; which wins depends on generated-CSS order,
  // not this string → the compact override is unreliable.
  return (
    <button className={`rounded px-4 py-2 ${compact ? "px-2" : ""}`}>Go</button>
  );
}
```

```html
<!-- BUG: three near-identical arbitrary widths → three unique rules that cannot
     dedupe. Use the scale (w-40, w-44, w-48) so equal values collapse. -->
<div class="w-[161px]"></div>
<div class="w-[162px]"></div>
<div class="w-[163px]"></div>
```

## Common Mistakes

- Concatenating conditional classes without a merge helper and expecting the later
  string to win; property conflicts resolve by stylesheet order, not attribute order.
- Reaching for `@apply` to "optimize" markup, which can duplicate declarations and hide
  conflicts across files.
- Importing `tailwindcss` in more than one stylesheet, duplicating base and utility layers.
- Manually deleting "duplicate" utilities from markup that the engine already dedupes.
- Skipping Brotli/gzip and shipping unminified CSS, doubling the transferred size.
- Filling markup with unique arbitrary values that defeat rule reuse.

## Production Tips

- Verify the response is compressed: check `content-encoding: br` (or `gzip`) on the CSS.
- Cache-bust with content hashes so an updated stylesheet is not served stale.
- Track emitted CSS size over time; a spike signals a conflict pattern or arbitrary sprawl.
- Run the Prettier plugin in CI so unsorted class order fails the check, keeping diffs clean.

## AI Review Checklist

- Are conditional/override classes merged with `tailwind-merge` (via `cn`), not concatenated?
- Is class order enforced by `prettier-plugin-tailwindcss`?
- Is `tailwindcss` imported exactly once across the stylesheets?
- Are repeated recipes extracted into components rather than `@apply`?
- Is production CSS minified, content-hashed, and served with Brotli/gzip?
- Are design-scale values preferred so identical rules dedupe?

## Related

- `knowledge/tailwind/19-performance.md`
- `knowledge/tailwind/27-production.md`
- `knowledge/tailwind/17-components.md`
- `knowledge/tailwind/03-utility-first.md`
- `knowledge/tailwind/26-best-practices.md`
