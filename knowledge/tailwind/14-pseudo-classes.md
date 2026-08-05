---
id: tailwind/14-pseudo-classes
topic: tailwind
slug: pseudo-classes
title: "Pseudo Classes"
type: doc
order: 14
status: ready
tags: [tailwind, pseudo-classes, "before:", "after:", inline-block, peer, content, "hover:"]
related: [tailwind/13-state-variants, tailwind/09-typography, tailwind/22-accessibility, tailwind/02-core-concepts, tailwind/11-responsive-design]
when_to_use: "Read before styling structural or form pseudo-classes (first/last, odd/even, required/checked, placeholder, before/after)."
---
# Pseudo Classes

## Purpose

This document defines how to use structural and form pseudo-class variants and
pseudo-element variants in Tailwind CSS v4: `first:`, `last:`, `odd:`, `even:`,
`empty:`, `required:`, `checked:`, `invalid:`, `placeholder:`, `placeholder-shown:`,
`autofill:`, and the `before:`/`after:` pseudo-elements. It complements
[13-state-variants](13-state-variants.md), which covers interaction states; this
doc covers position, structure, and form-validity states.

The distinction matters: interaction states (`hover:`) come and go with the user;
pseudo-class states here are mostly properties of the *document* — an element's
position among siblings, a form field's validity, whether an input is empty. You
style them declaratively so the browser, not JS, keeps them in sync.

## Why It Matters

These variants replace fragile JavaScript. Without `first:`/`last:` you compute
"is this the first row?" in a loop and pass a prop; with them, the browser
decides and CSS reacts — no off-by-one when the list reorders. Without
`required:`/`invalid:` you re-implement HTML's own validity tracking. And
pseudo-elements (`before:`/`after:`) let you add decorative content — separators,
required-field asterisks, counters — without polluting markup or the
accessibility tree. Using the platform's own state removes a whole category of
"the UI didn't update" bugs.

## Core Principles

- **Let structure drive style.** `first:`, `last:`, `odd:`, `even:`,
  `first-of-type:` react to DOM position. Prefer them over index-prop logic; they
  stay correct when the list changes.
- **Use `empty:` to handle the no-data case in CSS.** `empty:hidden` collapses a
  container with no children without a JS length check.
- **Style form validity with `required:`/`invalid:`/`valid:`, but gate on
  interaction.** Raw `invalid:` fires before the user types; combine with
  `user-invalid:` (or `peer-[&:not(:placeholder-shown)]`) so errors show after
  input, not on load.
- **`placeholder:` styles the placeholder; `placeholder-shown:` styles the input
  while empty.** They are different things — do not confuse them.
- **Pseudo-elements are decorative and need `content`.** `before:`/`after:`
  require a `content-*` utility (even `content-['']`) to render, and must not
  carry meaning a screen reader needs.

## Best Practices

- Remove edge borders/margins with position variants:
  `divide-y` plus `last:border-0`, or `first:pt-0 last:pb-0`, instead of
  conditionally rendering.
- Zebra-stripe with `odd:bg-slate-50 even:bg-white` rather than computing parity
  per row.
- Add a required-field asterisk decoratively:
  `after:content-['*'] after:text-red-500` on the label, with the real semantics
  carried by the input's `required` attribute and `aria-required`.
- Show validation only after interaction: prefer `user-invalid:` over `invalid:`,
  or drive the message off a `peer` input's `peer-[&:user-invalid]:` state.
- Style autofilled inputs with `autofill:` to override the browser's yellow
  background, which otherwise ignores your theme.
- Always pair `before:`/`after:` with `content-[...]`; give them layout
  (`inline-block`, size) since they default to inline with empty content.

## Examples

**Good Example** — structure- and validity-driven, decorative pseudo-element

```html
<!-- Border between rows only; first/last edges stay clean, order-safe -->
<ul class="divide-y divide-slate-200">
  <li class="py-3 first:pt-0 last:pb-0">Item</li>
  <li class="py-3 first:pt-0 last:pb-0">Item</li>
</ul>

<!-- Asterisk is decorative (after:content); `required` carries the real meaning -->
<label class="after:ml-0.5 after:text-red-500 after:content-['*']">Email</label>
<input
  type="email" required aria-required="true"
  class="border placeholder-shown:italic
         user-invalid:border-red-500 autofill:bg-white"
/>
```

**Bad Example** — index math, error-on-load, empty pseudo-element

```jsx
{rows.map((r, i) => (
  // BUG: manual first/last via index breaks when the list reorders/filters
  <li className={i === rows.length - 1 ? "py-3" : "py-3 border-b"}>{r}</li>
))}

<input
  type="email" required
  // BUG: `invalid:` fires before the user types → red error on first paint
  // BUG: before:text-red-500 with no content-[] → nothing renders
  className="invalid:border-red-500 before:text-red-500"
/>
```

## Common Mistakes

- Reimplementing `first:`/`last:`/`odd:`/`even:` with array-index logic that
  breaks on reorder or filter.
- Using `invalid:` alone, so validation errors appear before the user has typed;
  use `user-invalid:` or gate on `placeholder-shown`.
- Confusing `placeholder:` (styles the placeholder text) with `placeholder-shown:`
  (styles the input while empty).
- Writing `before:`/`after:` without a `content-*` utility — the pseudo-element
  never renders.
- Putting meaningful text in `before:`/`after:` content that assistive tech and
  copy-paste cannot reliably reach.
- Leaving autofilled fields with the browser's default background, breaking the
  theme.

## AI Review Checklist

- Are edge and parity styles done with `first:`/`last:`/`odd:`/`even:` instead of
  index math?
- Does form validation use `user-invalid:` (or an interaction gate) rather than
  bare `invalid:` firing on load?
- Is `placeholder:` vs `placeholder-shown:` used for the intended target?
- Does every `before:`/`after:` include a `content-*` utility and layout?
- Is pseudo-element content purely decorative, with real semantics in the markup?
- Are autofilled inputs styled so they match the theme?

## Related

- `knowledge/tailwind/13-state-variants.md`
- `knowledge/tailwind/09-typography.md`
- `knowledge/tailwind/22-accessibility.md`
- `knowledge/tailwind/02-core-concepts.md`
- `knowledge/tailwind/11-responsive-design.md`
