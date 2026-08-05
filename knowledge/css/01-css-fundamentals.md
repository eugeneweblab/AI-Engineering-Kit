---
id: css/01-css-fundamentals
topic: css
slug: css-fundamentals
title: "CSS Fundamentals"
type: doc
order: 1
status: ready
tags: [css, css-fundamentals, border, background, color, line-height, color-scheme, unset]
related: [css/02-selectors, css/03-specificity, css/04-box-model, css/20-css-variables, css/28-best-practices]
when_to_use: "Read before writing any CSS, to ground yourself in the cascade, inheritance, and value model."
---
# CSS Fundamentals

## Purpose

This document defines the mechanics every other CSS decision rests on: the anatomy of a
rule, how the **cascade** picks a winner, how **inheritance** flows values down the tree,
and how the **value model** (units, computed values, custom properties) resolves what an
element actually renders. An agent that understands these can predict what a stylesheet
does instead of guessing and re-running the browser.

CSS is declarative: you describe the desired result, and the engine resolves conflicts
using fixed rules. Those rules are the subject here.

## Why It Matters

CSS has no runtime error for "this rule did nothing." A misplaced property, a value the
element cannot inherit, or a rule beaten by the cascade all fail silently — the page keeps
rendering, just wrong. Debugging therefore means reasoning about *why* a value won, not
reading a stack trace. The engineers who ship reliable CSS are the ones who can state, for
any rendered pixel, which rule set it and why. The rest reach for `!important` and hope.

## Core Principles

- **The cascade resolves conflicts in a fixed order.** For competing declarations the
  engine compares, in order: origin and importance, then **specificity**, then **source
  order** (last wins). Learn this sequence — it explains every "why didn't my style apply?".
- **Inheritance is opt-in per property.** Text-related properties (`color`, `font`,
  `line-height`) inherit; box properties (`margin`, `border`, `background`) do not. Know
  which before assuming a child "should" pick up a value.
- **Every property has a computed value.** Percentages, `em`, and `var()` all resolve
  against something concrete. When a value surprises you, check what it computed against.
- **Custom properties are dynamic and inherited.** `--x` participates in the cascade and
  inheritance like any property, and `var()` is resolved at use time — this is what makes
  theming and runtime overrides possible without a build step.

## Best Practices

- Start every project with a reset or normalize layer and `box-sizing: border-box`
  (see [box-model](04-box-model.md)) so measurements are predictable.
- Prefer relative units (`rem`, `em`, `%`, `ch`, viewport units) over hard-coded `px`
  for anything that should scale with text or the viewport; reserve `px` for hairlines
  and details that must not scale.
- Use `inherit`, `initial`, `unset`, and `revert` deliberately to control the cascade
  rather than re-declaring values by hand.
- Centralize design decisions in **custom properties** (see [css-variables](20-css-variables.md))
  so one edit propagates; do not scatter the same magic number across files.
- Avoid `!important`. It escapes the cascade and forces the next author to escalate too.
  If you need it to win, your selectors are the problem — fix specificity instead.

## Examples

**Good Example** — tokens, inheritance, and predictable units

```css
:root {
  --brand: #2563eb;
  --space: 1rem;
  color-scheme: light dark; /* opt into native light/dark form controls */
}

.card {
  box-sizing: border-box;   /* padding + border stay inside the width */
  padding: var(--space);    /* one token, reused everywhere */
  color: inherit;           /* explicitly flow text color from context */
}

.card a {
  color: var(--brand);      /* themeable in one place, not per-link */
}
```

**Bad Example** — magic numbers, fighting the cascade

```css
.card {
  padding: 16px;               /* duplicated in 40 files; no single source of truth */
}
.card a {
  color: #2563eb !important;   /* wins by force, so every future override must also shout */
  font-size: 14px;             /* fixed px ignores the user's font-size preference */
}
```

## Common Mistakes

- Assuming a property inherits when it does not (e.g. expecting `border` or `background`
  to reach children).
- Reaching for `!important` to resolve a conflict instead of understanding which rule won
  and why.
- Hard-coding `px` for typography and spacing, breaking user zoom and accessibility.
- Repeating the same literal value everywhere instead of a custom property, so a design
  change means a find-and-replace across the codebase.
- Forgetting that source order breaks specificity ties — a later, equally-specific rule
  quietly overrides an earlier one.

## Production Tips

- Lint with Stylelint and enforce a property/order convention so diffs stay readable.
- Use the browser's Computed panel to see the *winning* value and its origin; do not guess.
- Keep a small, documented set of design tokens at `:root`; treat them as an API other
  files depend on.

## AI Review Checklist

- Can you name, for each conflicting rule, why the winner won (importance, specificity, order)?
- Are shared values expressed as custom properties rather than repeated literals?
- Is `box-sizing: border-box` set so widths include padding and border?
- Are typography and spacing in relative units unless a fixed `px` is genuinely required?
- Is the stylesheet free of `!important` except for deliberate, documented utility overrides?

## Related

- `knowledge/css/02-selectors.md`
- `knowledge/css/03-specificity.md`
- `knowledge/css/04-box-model.md`
- `knowledge/css/20-css-variables.md`
- `knowledge/css/28-best-practices.md`
