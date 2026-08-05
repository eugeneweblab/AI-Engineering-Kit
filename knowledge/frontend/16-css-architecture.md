---
id: frontend/16-css-architecture
topic: frontend
slug: css-architecture
title: "Frontend CSS Architecture"
type: doc
order: 16
status: ready
tags: [frontend, css-architecture, "@layer", stylelint, Button.tsx]
related: [css/21-architecture, frontend/15-styling, frontend/03-design-systems, frontend/02-component-driven-development, frontend/25-folder-structure, frontend/08-performance]
defers_to: css/21-architecture
when_to_use: "Read before establishing how CSS is organized, layered, and scaled across a codebase."
---
# Frontend CSS Architecture

## Purpose

This document defines how CSS is organized at the scale of a whole application: layering,
naming, ownership, and how the cascade is kept predictable as the codebase and team grow.
Where [styling](15-styling.md) covers how a single component gets its look, CSS
architecture covers the *system* that keeps thousands of rules from colliding.

The goal is a codebase where any developer can predict which rule wins, add a style
without fear of breaking a distant page, and delete CSS with confidence that nothing else
depended on it.

## Why It Matters

CSS has a global namespace and a cascade that resolves conflicts by specificity and source
order. Without an architecture, those two facts turn every stylesheet into a shared mutable
global. Teams respond by escalating specificity and adding `!important`, which makes the
next override even harder — a one-way ratchet toward unmaintainability. The most expensive
symptom is fear: nobody deletes CSS because they cannot prove it is unused, so stylesheets
only grow, bundles bloat, and paint slows. A deliberate architecture — explicit layers,
scoped ownership, flat specificity — is what lets CSS stay changeable and shrinkable at
scale.

## Core Principles

- **Layer intent explicitly.** Organize styles into ordered layers — reset/base, design
  tokens, layout, components, utilities — so precedence is decided by layer, not by
  specificity accidents. Native `@layer` makes this explicit.
- **Every style has one owner.** A component owns its styles; nothing outside reaches in.
  Scoping (CSS Modules, scoped SFCs, hashed classes) enforces ownership mechanically.
- **Keep specificity flat and uniform.** A codebase where almost every selector is one
  class is one where source/layer order — which you control — decides the winner.
- **Name for meaning, and name consistently.** Whether BEM, utilities, or module locals,
  one naming convention across the codebase makes styles searchable and predictable.
- **Make dead code detectable.** Co-locate styles with components and scope them so an
  unused component's styles are unambiguously removable.

## Best Practices

- Use CSS Cascade Layers (`@layer reset, tokens, base, layout, components, utilities;`) to
  fix precedence order once, so later files cannot accidentally out-specify earlier intent.
- Scope component styles with **CSS Modules** or an equivalent so class names are locally
  unique; reserve global selectors for a small, reviewed base/reset layer.
- Keep the design-token layer separate and dependency-free; layout, components, and
  utilities all consume tokens but tokens consume nothing.
- Pick one naming methodology (BEM for hand-written CSS, or a utility system like Tailwind)
  and apply it everywhere. Do not mix per-component styles, BEM, and utilities ad hoc.
- Co-locate a component's styles with its code (`Button.tsx` + `Button.module.css`) so
  ownership and deletion are obvious; avoid one giant global stylesheet.
- Budget and monitor CSS bundle size; remove unused rules with tooling and treat a growing
  stylesheet-that-never-shrinks as an architecture smell.
- Forbid `!important` outside a documented utility escape hatch; a rule you cannot override
  without it signals a layering problem, not a missing modifier.

## Examples

**Good Example** — explicit layers, scoped modules, flat specificity

```css
/* app.css — declare precedence ONCE; order here beats specificity */
@layer reset, tokens, base, layout, components, utilities;

@layer components {
  /* Card.module.css — single class, hashed & scoped, owned by the Card */
  .card {
    background: var(--color-surface);
    padding: var(--space-4);
  }
}

@layer utilities {
  /* utilities always win over components thanks to layer order, no !important */
  .u-hidden { display: none; }
}
```

```tsx
import styles from "./Card.module.css"; // local class names cannot collide globally
export const Card = ({ children }) => <div className={styles.card}>{children}</div>;
```

**Bad Example** — global soup, specificity ladder, unremovable

```css
/* one shared global.css imported everywhere */
.card { padding: 16px; }
/* someone needed an override, so they climbed specificity */
.page .content .card { padding: 24px; }
/* someone needed to beat THAT */
body .page .content .card.card--wide { padding: 32px !important; }
/* now nobody can tell which .card rules are still used → nothing is ever deleted */
```

## Common Mistakes

- One large global stylesheet where every rule can affect every page.
- Escalating specificity (long descendant chains) and `!important` to force overrides.
- Mixing multiple styling methodologies with no rule for which one owns what.
- No token layer, so colors and spacing are redefined and drift across features.
- Styles not co-located with components, making dead CSS impossible to identify and delete.
- Relying on source-import order (fragile) instead of explicit `@layer` for precedence.
- Letting the CSS bundle grow monotonically with no size budget or unused-rule pruning.

## Production Tips

- Enforce naming and specificity ceilings in CI with `stylelint` (e.g. max specificity,
  no `!important`, BEM pattern) so drift is caught at review time, not months later.
- Track CSS bundle size as a budgeted metric; a jump signals duplicated or unpruned styles.
- When adopting `@layer` incrementally, wrap legacy global CSS in a low-priority layer so
  new scoped styles can override it without a specificity fight.

## AI Review Checklist

- Is precedence controlled by explicit cascade layers rather than specificity accidents?
- Are component styles scoped/owned, with global selectors limited to a reviewed base layer?
- Is specificity flat (mostly single-class selectors) with `!important` effectively absent?
- Is there a single, consistently applied naming/utility methodology?
- Is there a dependency-free token layer that everything else consumes?
- Are styles co-located with components so unused CSS is detectable and deletable?
- Is CSS bundle size budgeted and monitored?

## Related

- `knowledge/css/21-architecture.md`
- `knowledge/frontend/15-styling.md`
- `knowledge/frontend/03-design-systems.md`
- `knowledge/frontend/02-component-driven-development.md`
- `knowledge/frontend/25-folder-structure.md`
- `knowledge/frontend/08-performance.md`
