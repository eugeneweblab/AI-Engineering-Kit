---
id: css/03-specificity
topic: css
slug: specificity
title: "Specificity"
type: doc
order: 3
status: ready
tags: [css, specificity]
related: [css/02-selectors, css/01-css-fundamentals, css/21-architecture, css/29-css-methodologies, css/28-best-practices]
when_to_use: "Read before writing a selector that overrides another, or when a rule isn't applying and you don't know why."
---
# Specificity

## Purpose

This document defines **specificity**: the algorithm the cascade uses to pick a winner when
two rules set the same property on the same element. It is the single most common source of
"my CSS won't apply" and of stylesheets that decay into `!important` wars. An agent that can
compute specificity — and, more importantly, keep it low and flat — writes CSS that stays
overridable.

Specificity is one step in the cascade (see [css-fundamentals](01-css-fundamentals.md));
it is consulted only after origin/importance and only before source order.

## Why It Matters

Specificity is a ratchet. Every time an author writes a stronger selector to beat an
existing rule, they raise the bar for everyone after them, who must write something stronger
still. Left unmanaged, this ends in a stylesheet where the only way to change anything is
`!important`, and then `!important` on top of that. There is no error and no warning — just
a codebase that becomes progressively harder to edit. Keeping specificity deliberately low
is what keeps CSS changeable over its lifetime.

## Core Principles

- **Specificity is a three-part tuple `(A, B, C)`, compared left to right.** `A` = ID
  selectors, `B` = classes, attributes, and pseudo-classes, `C` = element/type selectors
  and pseudo-elements. A higher `A` beats any amount of `B`; a higher `B` beats any amount
  of `C`. The universal selector `*` and combinators add nothing.
- **Ties break on source order — last wins.** Equal specificity is resolved by which rule
  appears later. This is why a later, equally-specific rule can quietly override an earlier
  one; it is a feature, not a bug.
- **Inline styles and `!important` sit outside the normal tuple.** Inline `style=""` beats
  selectors; `!important` beats everything except another `!important` later in the cascade.
  Both are escape hatches that break the model — avoid them.
- **`:where()` contributes zero specificity; `:is()`/`:not()` take their most specific
  argument.** Use these deliberately to control how strong a selector becomes.

## Best Practices

- Keep almost every selector at a **single class** — `(0,1,0)`. A flat stylesheet is one
  where source order alone predicts the winner, which is easy to reason about.
- Never use IDs for styling. One ID jumps you to `(1,0,0)`, which no reasonable class-based
  rule can override, forcing escalation.
- Wrap design-system base styles in `:where()` so consumers can override them with a plain
  class without a specificity fight.
- If you feel the urge to use `!important`, treat it as a signal that a selector upstream is
  too strong. Fix the source, don't stack overrides. The one acceptable use is a tightly
  scoped utility class whose whole job is to win (e.g. `.hidden { display: none !important }`).
- Layer intentionally with `@layer` (cascade layers): rules in a later layer beat earlier
  layers **regardless of specificity**, which lets you separate resets, framework, and app
  styles without specificity arithmetic.

## Examples

**Good Example** — flat specificity, order-predictable, layer-scoped

```css
@layer base, components, utilities; /* later layers win regardless of specificity */

@layer base {
  /* zero specificity: any component class can override with no fight */
  :where(button) { font: inherit; }
}

@layer components {
  .btn { background: var(--brand); }          /* (0,1,0) */
  .btn--danger { background: var(--danger); } /* (0,1,0), later → wins, no !important */
}
```

**Bad Example** — escalating specificity into a dead end

```css
#app .toolbar button.btn { background: gray; }  /* (1,2,1): hard to beat */
.btn--danger { background: red; }               /* (0,1,0): loses, silently */

/* "Fix" that makes it worse for everyone after */
.btn--danger { background: red !important; }    /* now the next override must also shout */
```

## Common Mistakes

- Using an ID selector for styling, then discovering nothing can override it cleanly.
- "Winning" a conflict with `!important`, which only defers and worsens the problem.
- Not realizing a later rule of equal specificity is the reason an earlier one "stopped
  working" — the culprit is source order, not the selector.
- Assuming `:is(.a, #b)` has class-level specificity; the `#b` argument makes it `(1,0,0)`.
- Adding a parent selector (`.page .btn`) just to "make it apply," raising specificity when
  the real fix was source order or a layer.

## Production Tips

- Enforce `selector-max-specificity` and `selector-max-id` in Stylelint to prevent creep.
- Adopt `@layer` early; retrofitting cascade layers into a mature `!important`-laden
  stylesheet is far harder than starting with them.
- When debugging, use the browser's Styles panel — it strikes through overridden
  declarations and shows the winning rule's specificity.

## AI Review Checklist

- Is every styling selector a single class (or lower) unless there is a documented reason?
- Are IDs kept out of selectors used for styling?
- Is the stylesheet free of `!important` except for intentional, scoped utilities?
- Where used, are `:is()`/`:not()` specificity implications understood (most-specific arg)?
- Are resets, framework, and app styles separated with `@layer` rather than specificity hacks?

## Related

- `knowledge/css/02-selectors.md`
- `knowledge/css/01-css-fundamentals.md`
- `knowledge/css/21-architecture.md`
- `knowledge/css/29-css-methodologies.md`
- `knowledge/css/28-best-practices.md`
