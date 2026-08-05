---
id: css/21-architecture
topic: css
slug: architecture
title: "CSS Architecture"
type: doc
order: 21
status: ready
tags: [css, architecture]
related: [css/29-css-methodologies, css/03-specificity, css/20-css-variables, css/02-selectors, css/22-performance]
when_to_use: "Read before structuring the CSS of a non-trivial project, choosing a methodology, or refactoring a stylesheet that has become an unmaintainable specificity war."
---
# CSS Architecture

## Purpose

This document defines how to *organize* CSS at scale: file structure, naming
conventions, specificity control, scoping strategy, and the layering that keeps a
growing stylesheet predictable. It is written so an agent can add or refactor styles
without triggering the classic decay into `!important` and copy-pasted overrides.

CSS has no module system by default — every rule is global and the cascade decides
winners by specificity and source order. Architecture is the discipline that imposes
structure on that global namespace so changes stay local and intent stays legible.

## Why It Matters

Unarchitected CSS rots faster than almost any other code. Because every selector is
global, a rule written for one page silently restyles another; developers respond by
raising specificity, which forces the next developer to raise it further, ending in
`!important` wars and stylesheets nobody dares delete from. The symptoms — fear of
changing anything, ballooning file size, visual regressions from unrelated edits — are
expensive and self-reinforcing. A clear architecture (predictable naming, flat
specificity, explicit layers) makes CSS behave like modular code: you can find the rule
that owns a thing, change it, and know exactly what you affected.

## Core Principles

- **Keep specificity flat and low.** Style with single classes. Deep descendant chains
  and IDs create rules that can only be beaten by even-worse rules. Flat specificity
  means source order and layers, not selector weight, decides the winner.
- **Name for reuse and clarity, not location.** A convention like BEM
  (`block__element--modifier`) makes a class self-documenting and collision-resistant
  without tying it to where it appears.
- **Separate concerns into layers.** Split reset, design tokens, base elements, layout,
  components, and utilities. Each layer has one job and a known override order.
- **Scope by construction, not by fighting the cascade.** Prefer BEM naming, CSS
  Modules, or `@scope`/Shadow DOM to keep a component's styles from leaking, instead of
  out-specifying leaks after the fact.
- **Make override order explicit with `@layer`.** Cascade layers let you declare that
  utilities always beat components regardless of selector specificity — removing the
  main reason people reach for `!important`.

## Best Practices

- Pick one methodology (BEM, or utility-first, or CSS Modules) and apply it
  consistently; the specific choice matters less than not mixing three. See
  [CSS methodologies](29-css-methodologies.md).
- Organize files by concern (e.g. ITCSS-style: settings, tools, generic, elements,
  objects, components, utilities), most-generic to most-specific, so import order
  matches override order.
- Define design tokens as [custom properties](20-css-variables.md) in one place and
  consume them everywhere; never hardcode a color or spacing value in a component.
- Use `@layer` to fix precedence between reset, framework, components, and utilities
  once, so you never need `!important` to make a utility win.
- Reserve `!important` for utility classes that are *intended* to be final, and document
  that intent. Never use it to patch a specificity accident.
- Keep components self-contained: a component's styles should not reach outside its own
  block, and layout (margins, grid placement) should be owned by the parent, not baked
  into the child.

## Examples

**Good Example** — flat specificity, BEM naming, explicit layers

```css
/* Precedence declared once: utilities always beat components, no !important needed. */
@layer reset, tokens, components, utilities;

@layer components {
  /* Single-class, self-documenting, collision-resistant BEM names. */
  .card { padding: var(--space-4); }
  .card__title { font-weight: 600; }
  .card--featured { border: 2px solid var(--color-accent); }
}

@layer utilities {
  .mt-0 { margin-top: 0; } /* wins over .card by LAYER order, not specificity */
}
```

**Bad Example** — deep selectors, escalating specificity, `!important` patch

```css
/* Specificity 0-1-3: only beatable by something even worse. Leaks into any
   .container with these nested tags. */
#main .container .card > div p { font-weight: 600; }

/* The next developer cannot override the above with a class, so: */
.card-title { font-weight: 400 !important; } /* specificity war escalates */

.card { padding: 16px; } /* hardcoded value, no shared token */
```

## Common Mistakes

- Styling with descendant chains and IDs, so specificity ratchets upward over time.
- Using `!important` to fix an override that a flat-specificity or `@layer` design would
  make unnecessary.
- Mixing multiple methodologies (BEM here, utilities there, ad-hoc elsewhere) with no
  stated convention.
- Letting components style elements outside their own block, so edits ripple unexpectedly.
- Baking layout margins into components instead of letting the parent position them.
- Hardcoding colors/spacing per file instead of consuming shared tokens.
- No file-organization scheme, so nobody can find or safely delete a rule.

## Production Tips

- Adopt `@layer` early; retrofitting layers into a mature `!important`-laden codebase is
  painful because you must untangle existing precedence assumptions.
- Add stylelint with a specificity ceiling and a `no-important` rule (with a utilities
  exception) to enforce the architecture in CI rather than in review.
- When refactoring a legacy stylesheet, wrap the old CSS in a low-priority `@layer
  legacy {}` and write new code in higher layers — new code wins without touching old.

## AI Review Checklist

- Are rules styled with single, low-specificity classes rather than ID/descendant chains?
- Is there one consistent naming methodology across the codebase?
- Is override precedence controlled by `@layer` (or source order), not `!important`?
- Are `!important` uses limited to deliberately-final utilities and documented?
- Are colors and spacing consumed from shared tokens, not hardcoded per component?
- Do components avoid styling outside their own block, with layout owned by parents?
- Does the file structure order concerns generic-to-specific to match override order?

## Related

- `knowledge/css/29-css-methodologies.md`
- `knowledge/css/03-specificity.md`
- `knowledge/css/02-selectors.md`
- `knowledge/css/20-css-variables.md`
- `knowledge/css/22-performance.md`
