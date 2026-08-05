---
id: css/30-engineering-principles
topic: css
slug: engineering-principles
title: "CSS Engineering Principles"
type: doc
order: 30
status: ready
tags: [css, engineering-principles, box-shadow, border-radius, min-width, max-width, rgba]
related: [css/21-architecture, css/29-css-methodologies, css/20-css-variables, css/22-performance, css/23-accessibility]
when_to_use: "Read before writing or reviewing any non-trivial stylesheet, design system, or component styling strategy."
---
# CSS Engineering Principles

## Purpose

This document defines the durable principles that keep CSS maintainable as a codebase
and a team grow. It is written so an agent can make styling decisions — where a rule
lives, how specific it is, how it scales — without creating the slow decay that turns a
stylesheet into a pile of `!important` overrides.

CSS has no compiler to catch a bad architecture. Nothing fails loudly when a selector
is too specific or a value is hard-coded in forty places. The cost shows up months
later as fragility. These principles exist to prevent that.

## Why It Matters

CSS is global by default and append-only in practice. Every rule you add can affect
elements you did not intend, and removing an old rule is risky because you cannot easily
prove nothing depends on it. The result is that teams stop deleting CSS and only add to
it, so stylesheets grow without bound. Good principles counter this: they make styles
local in effect, predictable in specificity, and safe to change. The payoff is that a
new contributor can add a component without breaking three others.

## Core Principles

- **Keep specificity low and flat.** Style with a single class wherever possible.
  Low, uniform specificity means the cascade is decided by source order, which is
  predictable. High specificity forces the next author to escalate, and the war ends in
  `!important`. See [specificity](03-specificity.md).
- **Scope styles to components, not pages.** A style should describe *what a thing is*
  (`.card`), not *where it sits* (`.homepage .sidebar div`). Component-scoped styles are
  portable and deletable; location-scoped styles rot when the layout changes.
- **Tokenize decisions once.** Every color, spacing step, font size, and breakpoint is a
  design decision. Encode it once as a [custom property](20-css-variables.md) and
  reference it everywhere. A magic number repeated is a bug waiting to diverge.
- **Prefer composition over override.** Build from small, single-purpose classes or
  utilities rather than overriding a heavy base rule. Overrides are debt; composition is
  additive and reversible.
- **Design for deletion.** You should be able to remove a component's CSS by removing its
  file. If styles leak across module boundaries, nothing is ever safe to delete.
- **Let the platform do the work.** Reach for Flexbox, Grid, `clamp()`, container queries,
  and logical properties before JavaScript or brittle fixed dimensions. Native layout is
  more robust than any hand-tuned pixel math.

## Best Practices

- Adopt one naming convention (BEM, utility-first, or CSS Modules) per codebase and apply
  it consistently — see [methodologies](29-css-methodologies.md). The convention matters
  less than the consistency.
- Express spacing, color, and type as tokens with `:root` custom properties; never repeat
  a raw `#3b82f6` or `16px` across files.
- Keep the maximum selector specificity in a component at `0,1,0` (one class). Escalate
  only with a documented reason.
- Use logical properties (`margin-inline`, `padding-block`, `inset`) so layouts adapt to
  RTL and vertical writing modes for free.
- Build mobile-first: write the base rules for small screens, then add complexity with
  `min-width` [media queries](18-media-queries.md) and [container queries](19-container-queries.md).
- Co-locate styles with their component and load only what a page needs; unused CSS is a
  [performance](22-performance.md) cost the user pays on every visit.
- Respect user preferences (`prefers-reduced-motion`, `prefers-color-scheme`, `forced-colors`)
  as a baseline, not a nice-to-have — see [accessibility](23-accessibility.md).

## Examples

**Good Example** — one class, tokens, composition

```css
/* Decisions defined once, reused everywhere. */
:root {
  --space-4: 1rem;
  --radius: 8px;
  --color-surface: #ffffff;
}

/* Component-scoped, specificity 0,1,0 — easy to override in source order. */
.card {
  padding: var(--space-4);
  border-radius: var(--radius);
  background: var(--color-surface);
}

/* A modifier composes onto the base; it does not fight it. */
.card--raised {
  box-shadow: 0 2px 8px rgb(0 0 0 / 0.1);
}
```

**Bad Example** — location-scoped, magic numbers, escalating specificity

```css
/* Tied to page structure — breaks the moment the markup moves. */
.homepage .content .sidebar div.card {
  padding: 16px;                 /* magic number, repeated elsewhere */
  border-radius: 8px;            /* another magic number */
  background: #ffffff;
}

/* The only way to beat the selector above is to escalate further. */
.card.card--raised {
  box-shadow: 0 2px 8px rgba(0,0,0,.1) !important; /* the specificity war has begun */
}
```

## Common Mistakes

- Styling by descendant chains (`.page .list li a`) instead of a single component class,
  making every rule fragile to markup changes.
- Hard-coding the same color or spacing value in many places instead of a token, so a
  redesign becomes a find-and-replace hunt that misses cases.
- Reaching for `!important` to win a cascade fight that low specificity would have avoided.
- Writing desktop-first and then unwinding it with `max-width` overrides, which produces
  more code and more edge cases than mobile-first.
- Treating CSS as untouchable and only appending, so the bundle grows forever and dead
  rules accumulate.
- Solving layout in JavaScript (measuring, positioning) when Grid or `clamp()` would do it
  declaratively and survive reflow.

## Production Tips

- Enforce the conventions with tooling: Stylelint for specificity limits and property
  order, and a bundle-size budget in CI so regressions are caught before merge.
- Track dead CSS with coverage tooling (Chrome DevTools coverage, or a build-time purge)
  and delete what pages no longer use.
- Keep design tokens in one source of truth and generate the CSS variables from it, so
  design and code cannot drift.

## AI Review Checklist

- Is the maximum specificity in each component a single class, with any escalation justified?
- Are colors, spacing, type, and breakpoints referenced from tokens rather than hard-coded?
- Are styles scoped to the component (portable, deletable) rather than to page location?
- Is the CSS mobile-first, extending with `min-width` queries instead of `max-width` overrides?
- Are user preferences (reduced motion, color scheme, forced colors) handled?
- Could this component's styles be deleted by removing its file, with no cross-module leakage?

## Related

- `knowledge/css/21-architecture.md`
- `knowledge/css/29-css-methodologies.md`
- `knowledge/css/20-css-variables.md`
- `knowledge/css/22-performance.md`
- `knowledge/css/23-accessibility.md`
