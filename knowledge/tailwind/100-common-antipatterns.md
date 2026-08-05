---
id: tailwind/100-common-antipatterns
topic: tailwind
slug: common-antipatterns
title: "Tailwind CSS Common Antipatterns"
type: doc
order: 100
status: ready
tags: [tailwind, common-antipatterns]
related: [tailwind/03-utility-first, tailwind/26-best-practices, tailwind/30-engineering-principles, tailwind/19-performance, tailwind/22-accessibility]
when_to_use: "Read when writing or reviewing Tailwind markup to recognize and avoid the recurring failure patterns below."
---
# Tailwind CSS Common Antipatterns

## Purpose

A catalog of the Tailwind CSS (v4) patterns that look reasonable but reliably cause pain:
inconsistency, bloated bundles, broken accessibility, and unmaintainable markup. Each
entry states the pattern, why it is wrong, and the concrete fix. Use it as a lookup when a
diff "renders fine" but feels off.

## Why It Matters

Tailwind's failure modes are quiet. Nothing errors when you type `p-[7px]`, remove a focus
ring, or paste a button for the ninth time — the page still looks correct in the browser.
The cost shows up later as a design system nobody can restyle, a CSS bundle that grew for
no reason, or a keyboard user who can't tell where they are. Recognizing these patterns
early is cheaper than the refactor that follows.

## Anti-Patterns

### 1. Arbitrary values instead of theme tokens

Writing `text-[#3b82f6]`, `p-[7px]`, `rounded-[11px]` throughout the markup.

- **Why it is wrong:** Each one is an unauditable magic number. Rebranding or adjusting the
  spacing scale becomes a find-and-replace across the whole codebase, and values drift
  (`#3b82f6` here, `#3b70f4` there).
- **The fix:** Define the value once as a theme token and reference it. `bg-brand`,
  `p-2`, `rounded-card`. Reserve arbitrary values for genuinely unique, one-time cases.

### 2. Recreating global CSS with `@apply`

Collapsing utilities into `.btn { @apply px-4 py-2 rounded bg-brand; }` "to clean up the
HTML."

- **Why it is wrong:** It reintroduces exactly the problems Tailwind removes — a growing
  global stylesheet, specificity conflicts, and indirection between markup and style. The
  class name now hides its own definition.
- **The fix:** Extract a **component** (`<Button>`) that owns the utility string. Reserve
  `@apply` for third-party markup you don't control.

### 3. Ignoring `tailwind-merge` in reusable components

```tsx
// Bad: both padding classes ship; which wins depends on CSS source order.
<button className={`px-4 py-2 ${className}`} />
```

- **Why it is wrong:** A caller passing `px-6` doesn't override `px-4`; both land in the
  DOM and the result is non-deterministic across builds.
- **The fix:** Merge with `tailwind-merge` (usually via a `cn()` helper) so the later,
  caller-supplied utility replaces the earlier one: `className={cn("px-4 py-2", className)}`.

### 4. Desktop-first overrides

Writing base styles for desktop and using `sm:`/`max-*` to walk them back down for phones.

- **Why it is wrong:** Tailwind's variants are min-width and mobile-first by design.
  Desktop-first fights the framework, produces more classes, and breaks the natural
  cascade.
- **The fix:** Style the mobile layout unprefixed, then add complexity upward:
  `grid grid-cols-1 md:grid-cols-3`.

### 5. Removing focus outlines without replacing them

`focus:outline-none` (or a global `outline-none`) with nothing added back.

- **Why it is wrong:** Keyboard users lose all indication of where they are — a serious,
  common accessibility failure.
- **The fix:** Pair removal with a visible replacement and use `focus-visible:`:
  `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand`.

### 6. Shipping Tailwind from the CDN in production

`<script src="https://cdn.tailwindcss.com">` on a real site.

- **Why it is wrong:** The CDN build ships the entire framework and compiles in the
  browser — a large, slow, uncacheable payload the build step exists to avoid.
- **The fix:** Use a real build (Vite/PostCSS/CLI) so only used utilities are emitted,
  minified, and hashed. Keep the CDN for prototypes only.

### 7. Color-only status signals

Communicating success/error purely with `text-red-500` / `text-green-500`.

- **Why it is wrong:** Color-blind users and low-contrast environments can't distinguish
  the states; it fails WCAG.
- **The fix:** Add a non-color cue — an icon, label, or shape — alongside the color.

### 8. Dark mode as a blind inversion

Adding `dark:` variants mechanically without checking the result.

- **Why it is wrong:** Inverting a mid-tone often produces low-contrast, unreadable text
  or muddy surfaces; the page technically has a dark theme but is unusable.
- **The fix:** Choose dark tokens deliberately and verify contrast for each
  surface/text/border pair. Cover *every* element — a missing `dark:` leaves a white flash.

### 9. Typo'd class names that silently do nothing

`flexx`, `justfy-center`, `bg-blu-500`.

- **Why it is wrong:** Tailwind generates nothing for unknown classes and raises no error,
  so the style is silently missing and easy to miss in review.
- **The fix:** Run `eslint-plugin-tailwindcss` (or the editor IntelliSense) to flag
  unknown class names before merge.

### 10. Copy-pasted markup instead of components

The same card/button markup duplicated across pages.

- **Why it is wrong:** Every copy drifts independently; a design change means editing N
  places and missing some.
- **The fix:** Extract shared UI into one component and reuse it. The utility string lives
  in exactly one place.

## AI Review Checklist

- Are arbitrary values replaced by theme tokens wherever the value repeats?
- Is `@apply` limited to third-party markup, with components used otherwise?
- Do reusable components merge `className` with `tailwind-merge`?
- Are styles mobile-first rather than desktop-first with walk-backs?
- Is every removed focus outline replaced with a visible `focus-visible:` state?
- Is production CSS built (not CDN), and are class names free of silent typos?

## Related

- `knowledge/tailwind/03-utility-first.md`
- `knowledge/tailwind/26-best-practices.md`
- `knowledge/tailwind/30-engineering-principles.md`
- `knowledge/tailwind/19-performance.md`
- `knowledge/tailwind/22-accessibility.md`
