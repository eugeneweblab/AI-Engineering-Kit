---
id: css/02-selectors
topic: css
slug: selectors
title: "Selectors"
type: doc
order: 2
status: ready
tags: [css, selectors]
related: [css/01-css-fundamentals, css/03-specificity, css/21-architecture, css/29-css-methodologies, css/22-performance]
when_to_use: "Read before writing or reviewing any selector, to target elements portably without over-coupling to the DOM."
---
# Selectors

## Purpose

This document defines how to target elements: the selector types, combinators, and the
modern functional pseudo-classes (`:is()`, `:where()`, `:has()`). A selector is a contract
with the DOM — it says "these rules apply to elements shaped like this." Good selectors
express *intent* (a component's role) and survive refactors; bad ones encode *structure*
(where an element happens to sit) and shatter when the markup moves.

Selectors are inseparable from [specificity](03-specificity.md): every selector you write
also decides how hard it will be to override. Read them together.

## Why It Matters

The selector is where CSS couples to HTML. Over-couple — deep descendant chains, tag names,
`nth-child` positional matches — and a harmless markup change (wrapping a `div`, reordering
items) silently breaks styling with no error. Under-target — a bare tag selector — and rules
leak onto elements you never intended. Because CSS is global, a sloppy selector is not a
local bug; it is a rule that can reach the whole page. Precise, intent-revealing selectors
are the difference between a stylesheet you can refactor and one you can only append to.

## Core Principles

- **Match intent, not location.** Prefer a class that names a role (`.card__title`) over a
  path that describes position (`.sidebar > div > h3`). Roles are stable; positions are not.
- **Keep selectors shallow.** Every combinator adds coupling to the DOM shape. One class is
  usually enough; two levels is a lot; four is a code smell.
- **Specificity is a cost, not a feature.** The strongest selector that works is the wrong
  one — it forces every future override to be stronger still. Reach for the weakest.
- **Use `:where()` to add matching without adding specificity.** It lets you group or scope
  selectors while contributing zero specificity, keeping the cascade flat.

## Best Practices

- Style with **classes** by default. Avoid IDs for styling (they are hard to override) and
  avoid bare tag selectors except in resets and base typography.
- Group related selectors with `:is()` / `:where()` instead of repeating declarations:
  `:is(h1, h2, h3)` is clearer and shorter than three rules.
- Use `:where()` for opinionated defaults you *want* users to override easily (design-system
  base styles); use `:is()` when the grouping should keep normal specificity.
- Reserve **attribute selectors** for state (`[aria-expanded="true"]`, `[disabled]`) — this
  ties styling to accessibility state, which is exactly where it belongs.
- Use `:has()` (the "parent"/relational selector, baseline across modern browsers since
  2023) to style a container based on its contents — e.g. a form field that has an invalid
  input — instead of adding JavaScript to toggle a class.
- Avoid the universal selector `*` in hot paths and deep descendant selectors; both are
  broad and can matter for [performance](22-performance.md) on large DOMs.

## Examples

**Good Example** — intent-revealing, shallow, state-driven

```css
/* Role-based class: survives markup reshuffles */
.menu__item { padding-block: 0.5rem; }

/* Group without specificity cost, so overrides stay easy */
:where(.prose h1, .prose h2, .prose h3) { line-height: 1.2; }

/* Style the container from its state — no JS needed */
.field:has(input:invalid) { border-color: var(--danger); }

/* State via ARIA attribute keeps CSS and a11y in sync */
.accordion[aria-expanded="true"] .accordion__panel { display: block; }
```

**Bad Example** — positional, deep, brittle

```css
/* Breaks the moment a wrapper is added or items reorder */
.sidebar > div > ul li:nth-child(2) a { color: red; }

/* ID selector: near-impossible to override later without escalation */
#main .content h3 { font-weight: bold; }

/* Bare tag selector leaks onto every span on the page */
span { color: gray; }
```

## Common Mistakes

- Encoding DOM position (`nth-child`, `>` chains) for styling that is really about a
  component role — the rule breaks on the next markup edit.
- Using IDs to style, then being forced into `!important` or longer selectors to override.
- Long descendant chains that couple CSS tightly to one specific HTML structure.
- Duplicating declarations across selectors instead of grouping with `:is()`/`:where()`.
- Forgetting that `:is()` takes the specificity of its *most specific* argument — a single
  `#id` inside `:is()` spikes the whole selector's specificity.

## Production Tips

- Adopt a naming methodology (BEM or utilities — see [css-methodologies](29-css-methodologies.md))
  so class intent is legible and collisions are rare.
- Lint against qualified IDs and overly deep selectors with Stylelint's
  `selector-max-specificity` and `selector-max-id`.

## AI Review Checklist

- Does each selector target a role/class rather than a DOM position?
- Are selectors as shallow as possible (prefer one class over a descendant chain)?
- Is styling done via classes, with IDs avoided for styling?
- Where grouping or scoping is used, is `:where()` chosen to keep specificity flat?
- Is component state expressed through ARIA/attribute selectors, keeping a11y and CSS aligned?

## Related

- `knowledge/css/01-css-fundamentals.md`
- `knowledge/css/03-specificity.md`
- `knowledge/css/21-architecture.md`
- `knowledge/css/29-css-methodologies.md`
- `knowledge/css/22-performance.md`
