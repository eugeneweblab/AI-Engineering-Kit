---
id: css/00-overview
topic: css
slug: overview
title: "CSS Overview"
type: doc
order: 0
status: ready
tags: [css, overview, position, box-sizing]
related: [css/01-css-fundamentals, css/03-specificity, css/04-box-model, css/21-architecture, css/28-best-practices]
when_to_use: "Read first when starting any CSS work, to orient yourself in this topic and find the right doc."
---
# CSS Overview

## Purpose

This document is the map for the `css` topic. CSS looks forgiving — a wrong value
rarely throws an error, the page just renders slightly off — and that forgiveness is
exactly why it drifts into unmaintainable state. These docs teach an agent to write CSS
that is predictable, debuggable, and cheap to change: rules that win by structure rather
than by brute-force `!important`, layouts that adapt without magic numbers, and selectors
that survive a redesign.

Read this page to understand how the topic is organized, then jump to the specific doc
for the problem in front of you.

## Why It Matters

CSS is global by default. Any rule can, in principle, affect any element on the page,
so a change made to fix one component can silently break another three screens away.
There is no compiler to catch a selector that stopped matching or a specificity war that
`!important` "resolved". The cost of undisciplined CSS is not a crash — it is a stylesheet
that everyone is afraid to touch, where the only safe edit is to append more rules. Getting
the fundamentals right (the cascade, specificity, the box model, modern layout) is what
keeps a codebase's styling editable over years.

## How These Docs Fit Together

- **Foundations — how CSS decides what wins.** Start here before anything else.
  - [css-fundamentals](01-css-fundamentals.md) — syntax, the cascade, inheritance, custom properties.
  - [selectors](02-selectors.md) — how to target elements precisely and portably.
  - [specificity](03-specificity.md) — why one rule beats another, and how to keep the ordering sane.
- **Box & layout — how elements take up space.**
  - [box-model](04-box-model.md) — content, padding, border, margin, and `box-sizing`.
  - [positioning](05-positioning.md) — static, relative, absolute, fixed, sticky, and stacking.
  - [flexbox](06-flexbox.md) and [grid](07-grid.md) — the two modern layout systems.
  - [sizing](08-sizing.md), [spacing](09-spacing.md) — dimensions, min/max, gaps, and rhythm.
- **Visual detail.** [typography](10-typography.md), [colors](11-colors.md),
  [backgrounds](12-backgrounds.md), [borders](13-borders.md),
  [transforms](14-transforms.md), [transitions](15-transitions.md),
  [animations](16-animations.md).
- **Adaptation.** [responsive-design](17-responsive-design.md),
  [media-queries](18-media-queries.md), [container-queries](19-container-queries.md).
- **Scale & quality.** [css-variables](20-css-variables.md),
  [architecture](21-architecture.md), [performance](22-performance.md),
  [accessibility](23-accessibility.md), [css-methodologies](29-css-methodologies.md).
- **Practice.** [modern-css](25-modern-css.md),
  [browser-compatibility](26-browser-compatibility.md), [debugging](27-debugging.md),
  [best-practices](28-best-practices.md), [engineering-principles](30-engineering-principles.md).
- **Guardrails.** [common-antipatterns](100-common-antipatterns.md),
  [production-checklist](98-production-checklist.md),
  [ai-review-checklist](99-ai-review-checklist.md).

## Core Principles

- **The cascade is the model — learn it, don't fight it.** Most CSS pain comes from not
  knowing why a rule won or lost. Understand source order, specificity, and inheritance
  before reaching for overrides.
- **Style by intent, not by position.** Target a component's role (a class), not where it
  happens to sit in the DOM. Position-based rules break on the next refactor.
- **Prefer flow and modern layout to manual math.** Flexbox, grid, and logical properties
  let the browser do the arithmetic; hard-coded pixel offsets do not survive new content.
- **Keep specificity low and flat.** A stylesheet where most rules are single classes is
  one you can override predictably. Escalating specificity is a debt you repay with interest.

## Best Practices

- Read [specificity](03-specificity.md) and [box-model](04-box-model.md) before writing
  layout code — they are the two concepts agents most often get subtly wrong.
- When in doubt about which doc applies, search for the CSS property name; each property
  is documented in its topical doc (e.g. `position` in positioning, `gap` in spacing).
- Treat the [ai-review-checklist](99-ai-review-checklist.md) as the gate before proposing
  CSS in a review.

## AI Review Checklist

- Did you consult the specific doc for the property or behavior you are changing?
- Is the change made by adding intent (a class) rather than raising specificity?
- Have you confirmed the cascade explains why your rule wins, without `!important`?
- Does the change hold up across the breakpoints and containers the component lives in?

## Related

- `knowledge/css/01-css-fundamentals.md`
- `knowledge/css/03-specificity.md`
- `knowledge/css/04-box-model.md`
- `knowledge/css/21-architecture.md`
- `knowledge/css/28-best-practices.md`
