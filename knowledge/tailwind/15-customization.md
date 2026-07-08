---
id: tailwind/15-customization
topic: tailwind
slug: customization
title: "Customization"
type: doc
order: 15
status: ready
tags: [tailwind, customization]
related: [tailwind/16-theme, tailwind/21-design-system, tailwind/10-colors, tailwind/18-plugins, tailwind/02-core-concepts]
when_to_use: "Read before extending Tailwind — adding tokens, custom utilities, variants, or arbitrary values."
---
# Customization

## Purpose

This document defines how to customize Tailwind CSS v4: extending the design
system with new tokens, adding first-class utilities with `@utility`, defining
variants with `@custom-variant`, and using arbitrary values as a deliberate
escape hatch. It covers the CSS-first configuration model that replaced
`tailwind.config.js`. Token definition itself is covered in
[16-theme](16-theme.md); this doc covers everything you add *around* the theme.

The guiding decision at every step: extend the system so the value becomes part
of it, or reach outside the system with a one-off. Extending scales; one-offs
accumulate into inconsistency. This doc tells you which to pick and how.

## Why It Matters

Customization is where a Tailwind codebase either stays coherent or rots. Agents
trained on v3 emit `tailwind.config.js` with `theme.extend` and `content` arrays
— all removed or changed in v4 — producing files that no-op or error. Overriding
a namespace instead of extending it silently deletes Tailwind's defaults, so
`bg-red-500` suddenly stops existing. And a codebase peppered with `p-[13px]`,
`text-[#3b7]`, `w-[327px]` has abandoned the design system entirely: nothing is
reusable and nothing is consistent. Correct customization keeps every new value
inside the scale.

## Core Principles

- **Configuration is CSS in v4.** Customize in your CSS via `@theme`, `@utility`,
  `@custom-variant`, and `@layer`. There is no required `tailwind.config.js`; do
  not create one unless a plugin genuinely needs the JS API.
- **Extend, don't clobber.** Adding a key to a theme namespace extends it; the
  defaults remain. Wholesale-replacing a namespace removes Tailwind's built-ins —
  do that only when you intend to.
- **Arbitrary values are an escape hatch, not a habit.** `w-[327px]` is fine for a
  genuine one-off (a third-party embed size). If a value repeats, promote it to a
  token instead.
- **Add real utilities with `@utility`, not `@layer utilities`.** `@utility`
  registers a first-class utility that participates in variants (`hover:`, `md:`);
  a hand-rolled class in `@layer` does not.
- **Custom CSS lives in `@layer`.** Put base/element styles in `@layer base` and
  component classes in `@layer components` so cascade order and override behavior
  are predictable.

## Best Practices

- Add design tokens in `@theme` (colors, spacing, fonts, breakpoints); they
  become both utilities and CSS variables — see [16-theme](16-theme.md).
- Create custom utilities with `@utility name { … }`; use the `--value()` /
  `--modifier()` functions for utilities that take a scale value or modifier.
- Define reusable variants with `@custom-variant`, e.g.
  `@custom-variant hocus (&:hover, &:focus-visible);` or the dark-mode class
  variant. Prefer this over repeating raw selectors.
- Reserve arbitrary values for true one-offs and prefer arbitrary *properties*
  (`[mask-type:luminance]`) only when no utility exists.
- Keep custom CSS minimal and layered; if you find yourself writing lots of it,
  reconsider whether a utility or token fits better.
- When you must interoperate with a JS-config plugin, use `@config
  "path.js";`—but treat it as legacy, not the default.

## Examples

**Good Example** — v4 CSS-first: extend tokens, real utility, named variant

```css
@import "tailwindcss";

/* Extends the color + spacing scales — Tailwind defaults are preserved */
@theme {
  --color-brand-500: oklch(0.62 0.19 255);
  --spacing-18: 4.5rem; /* fills a gap in the scale, now usable as p-18, gap-18 */
}

/* First-class utility: works with variants → hover:content-auto, md:content-auto */
@utility content-auto {
  content-visibility: auto;
}

/* Reusable variant instead of repeating &:hover, &:focus-visible everywhere */
@custom-variant hocus (&:hover, &:focus-visible);
```

```html
<button class="bg-brand-500 p-18 hocus:brightness-110 content-auto">Go</button>
```

**Bad Example** — v3 config, clobbered namespace, arbitrary sprawl

```js
// BUG: v4 does not use this file for theme; `content` is auto-detected now.
// BUG: setting `colors` (not extend) REPLACES the palette → bg-slate-* gone.
module.exports = {
  content: ["./src/**/*.{html,js}"],
  theme: { colors: { brand: "#3b82f6" } },
};
```

```html
<!-- BUG: arbitrary values everywhere → no reuse, no consistency, no scale -->
<div class="p-[13px] mt-[7px] text-[#3b82f6] w-[327px] rounded-[9px]">…</div>
```

## Common Mistakes

- Creating a `tailwind.config.js` on a v4 project out of habit when CSS-first
  config is the idiom.
- Replacing a whole theme namespace (`--color-*`) instead of adding to it, wiping
  Tailwind's defaults.
- Using `@layer utilities` for custom classes that should be `@utility` — they
  won't respond to `hover:`/`md:` variants.
- Sprinkling arbitrary values (`p-[13px]`) for values that repeat; they should be
  tokens.
- Copying v3 plugin/config snippets that reference the JS `theme.extend` object.
- Writing large custom stylesheets that duplicate utilities already available.

## Production Tips

- Grep the codebase for `\[.*px\]` and `\[#[0-9a-f]` to find arbitrary-value
  sprawl that should be tokens.
- Keep customizations in one CSS entry file so the design system has a single
  source of truth reviewers can scan.
- When adding a utility, confirm no existing utility or plugin already covers it
  before writing CSS.

## AI Review Checklist

- Is customization done in CSS (`@theme`/`@utility`/`@custom-variant`) rather than
  a v3-style `tailwind.config.js`?
- Do theme changes *extend* namespaces, preserving Tailwind's defaults?
- Are custom utilities defined with `@utility` so they support variants?
- Are arbitrary values limited to genuine one-offs, with repeated values promoted
  to tokens?
- Are reusable selectors expressed as `@custom-variant` rather than duplicated?
- Is custom CSS placed in the correct `@layer`?

## Related

- `knowledge/tailwind/16-theme.md`
- `knowledge/tailwind/21-design-system.md`
- `knowledge/tailwind/10-colors.md`
- `knowledge/tailwind/18-plugins.md`
- `knowledge/tailwind/02-core-concepts.md`
