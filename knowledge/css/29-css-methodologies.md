---
id: css/29-css-methodologies
topic: css
slug: css-methodologies
title: "CSS Methodologies"
type: doc
order: 29
status: ready
tags: [css, css-methodologies]
related: [css/21-architecture, css/28-best-practices, css/03-specificity, css/20-css-variables]
when_to_use: "Read before choosing how a project will name, organize, and scope its CSS, or when joining a codebase with an unfamiliar convention."
---
# CSS Methodologies

## Purpose

This document explains the established CSS methodologies — BEM, utility-first, ITCSS,
CUBE, and scoped/CSS-Modules — what problem each solves, and how to choose. A methodology
is a shared set of conventions for naming, organizing, and scoping styles so a team writes
CSS the same way. The point is not which one is "best" but that the project picks one and
applies it consistently.

## Why It Matters

CSS gives you no module system, no naming rules, and one global scope. Left unmanaged, ten
developers produce ten incompatible styles of CSS in the same file, and specificity and
naming collisions follow. A methodology supplies the boundaries the language lacks: it makes
names predictable, keeps specificity flat, and tells you where a style lives and how to
override it. The specific choice matters far less than consistency — a mediocre convention
applied uniformly beats a great one applied half the time. Inconsistency is the actual cost.

## Core Principles

- **Consistency over ideology.** Any coherent methodology, applied everywhere, produces
  maintainable CSS; mixing conventions produces chaos. Decide once, document it, enforce it.
- **Flat, predictable specificity.** Every serious methodology exists partly to keep
  selectors at a single low weight so overrides stay possible. See [specificity](03-specificity.md).
- **Explicit scope.** Whether by naming convention (BEM), tooling (CSS Modules), or single-purpose
  classes (utilities), the goal is that a style's reach is obvious and bounded.
- **Match the methodology to the team and build.** Utility-first needs a build step and buys
  in to markup-heavy classes; BEM needs discipline but no tooling. Choose for your constraints.
- **Layered organization.** Order matters — reset, base, components, utilities — so late,
  intentional rules win. Cascade layers (`@layer`) make this explicit. See [architecture](21-architecture.md).

## Best Practices

- **BEM** (`block__element--modifier`): name by component structure. `.card`, `.card__title`,
  `.card--featured`. Keeps specificity flat (all single classes) and names self-documenting.
  Best when you write hand-authored component CSS and want zero build dependency.
- **Utility-first** (Tailwind-style): compose from single-purpose classes
  (`flex gap-4 p-3 text-sm`). Eliminates naming and dead CSS, colocates styling with markup,
  but requires a build/purge step and moves complexity into HTML. Best for product teams
  shipping many small variations fast.
- **CSS Modules / scoped styles**: the build hashes class names per file, guaranteeing local
  scope. Best inside component frameworks (React, Vue, Svelte) where colocation is natural.
- **ITCSS**: an *organizing* layer that orders CSS by increasing specificity (settings →
  tools → generic → elements → objects → components → utilities). Pairs with BEM; today its
  ordering is often expressed directly with `@layer`.
- **CUBE CSS**: composition + utilities + block + exception — a pragmatic blend that leans on
  the cascade instead of fighting it. Good middle ground between BEM and pure utilities.
- Whatever you choose, **write it down** (a `STYLE_GUIDE.md`) and **lint it** (stylelint rules
  for naming pattern and specificity ceiling) so the convention is enforced, not aspirational.

## Examples

**Good Example** — consistent BEM, flat specificity

```html
<article class="card card--featured">
  <h2 class="card__title">Title</h2>
  <p class="card__body">…</p>
</article>
```

```css
/* Every selector is a single class → specificity 0,1,0, trivially overridable.
   The name encodes structure and state, so it reads without opening the HTML. */
.card { /* block */ }
.card__title { /* element belongs to card */ }
.card--featured { /* modifier: a variant, not a new component */ }
```

**Bad Example** — mixed conventions, escalating specificity

```html
<!-- BEM, utility, and appearance names mixed in one component: no convention at all. -->
<article class="card featured mt-20 blue-card" id="card-3">
  <h2 class="cardTitle">Title</h2>
</article>
```

```css
#card-3 .cardTitle { }        /* ID + camelCase: high specificity, off-convention */
.card.featured.blue-card { }  /* three names describing one variant, one of them a color */
.mt-20 { margin-top: 20px !important; } /* utility forced to win with !important */
```

## Common Mistakes

- Mixing methodologies in one codebase (BEM here, utilities there, ad-hoc names elsewhere)
  so no reader can predict a class name or its scope.
- Choosing utility-first without the required purge/build step, shipping a huge stylesheet.
- Treating a methodology as optional — following it "mostly" — which reintroduces the exact
  collisions it prevents.
- Using BEM but sneaking in nested/ID selectors, defeating its flat-specificity guarantee.
- Adopting a heavy organizing system (ITCSS) on a tiny project where a single `@layer`
  ordering would do.
- Not documenting the choice, so new contributors and agents guess and drift.

## Production Tips

- Encode the methodology in **stylelint** (e.g. `selector-class-pattern` for BEM, a
  `max-specificity` rule) and in code review, so drift is caught mechanically.
- When migrating an old codebase, wrap legacy styles in a low-priority `@layer legacy` and
  write new code in the chosen methodology's layer, rather than rewriting everything at once.
- For agents: detect the existing convention from the codebase before adding CSS, and match
  it — introducing a second methodology is a regression even if it is "better".

## AI Review Checklist

- Does the project use one methodology consistently, documented somewhere?
- Do new classes follow the established naming and scope convention?
- Is specificity kept flat (single classes, no IDs, no `!important` to win)?
- If utility-first, is a purge/build step configured so unused classes are stripped?
- Is cascade order handled deliberately (`@layer`/ITCSS ordering) rather than by file order?
- Was the existing convention detected and matched before adding new styles?

## Related

- `knowledge/css/21-architecture.md`
- `knowledge/css/28-best-practices.md`
- `knowledge/css/03-specificity.md`
- `knowledge/css/20-css-variables.md`
