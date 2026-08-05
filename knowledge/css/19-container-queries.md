---
id: css/19-container-queries
topic: css
slug: container-queries
title: "Container Queries"
type: doc
order: 19
status: ready
tags: [css, container-queries, container-type, "@container", card, container]
related: [css/18-media-queries, css/17-responsive-design, css/21-architecture, css/20-css-variables, css/22-performance]
when_to_use: "Read before building any reusable component that must adapt to the width of its parent, not the viewport — cards, sidebars, widgets placed in varying layouts."
---
# Container Queries

## Purpose

This document defines how to make a component respond to the size of *its own
container* using `@container`. It covers declaring a query container, the `cqw`/`cqi`
length units, `container-type` gotchas, and when to reach for this instead of a media
query.

Container queries answer "how much space does this component actually have?" — which
is what you need for a truly reusable component that might sit in a wide main column
on one page and a narrow sidebar on another. For the whole-page environment, use
[media queries](18-media-queries.md).

## Why It Matters

Media queries couple a component's layout to the viewport, but the same component is
often dropped into containers of wildly different widths. A product card that looks
right full-width breaks in a 300px sidebar, even though the *screen* is huge. Before
container queries the only fixes were duplicated modifier classes (`.card--compact`)
or JavaScript width observers — both fragile and both leaking layout knowledge into
markup. Container queries let a component own its responsive behavior once and stay
correct wherever it is reused, which is the foundation of a real component library.

## Core Principles

- **The queried element must be inside a declared container.** `@container` looks up
  the nearest ancestor with `container-type` set. An element cannot query itself.
- **`container-type: inline-size` is almost always what you want.** It lets the browser
  size the container along the block axis normally while making the inline (width) axis
  queryable. Plain `size` requires an explicit height and will collapse content that
  relies on intrinsic height.
- **Query the container, size with container units.** `cqi` (1% of the container's
  inline size) and `cqw`/`cqb` let type and spacing scale continuously with the
  container, not just at breakpoints.
- **Name containers when nesting.** `container-name` disambiguates which ancestor a
  query targets when containers are nested, preventing a query from binding to the
  wrong one.
- **A container establishes containment.** Setting `container-type` also creates layout
  and style containment, which is why the element can no longer be sized by its
  descendants' height under `size`.

## Best Practices

- Declare the container on the *wrapper*, and put the query on the *child*. An element
  with `container-type` cannot be styled by its own `@container` rule.
- Use the shorthand `container: card / inline-size` to set name and type together.
- Prefer `inline-size` unless you genuinely need to react to height; `size` demands a
  determinate height and breaks content-driven components.
- Combine with [CSS variables](20-css-variables.md): flip a `--layout` custom property
  inside `@container` and let the rest of the component read it.
- Keep container query breakpoints, like media breakpoints, driven by where the
  component's layout actually breaks — not arbitrary numbers.
- Treat container queries as an enhancement layer: write a sensible base layout so a
  component in an undeclared container still renders acceptably.

## Examples

**Good Example** — component adapts to its parent, reusable anywhere

```css
/* Wrapper declares the query container. Child styles react to it. */
.card-wrap { container: card / inline-size; }

/* Base: stacked, works in any width including undeclared containers. */
.card { display: grid; gap: 0.5rem; }

/* When the card's OWN container is at least 30em wide, go side-by-side.
   Independent of viewport — correct in a sidebar or a full-width row. */
@container card (width >= 30em) {
  .card { grid-template-columns: 8rem 1fr; }
  /* Type scales with the container, not the screen. */
  .card__title { font-size: clamp(1rem, 4cqi, 1.5rem); }
}
```

**Bad Example** — viewport-based, so the same card breaks per placement

```css
/* Uses the screen width. On a huge monitor this is always "wide", even when
   the card sits in a 280px sidebar → text and image overflow. */
@media (width >= 30em) {
  .card { grid-template-columns: 8rem 1fr; }
}

/* Trying to query without a container-type: this @container matches nothing. */
@container (width >= 30em) {
  .card { gap: 1rem; } /* silently never applies — no ancestor is a container */
}
```

## Common Mistakes

- Writing `@container` rules with no ancestor that has `container-type` set — the rules
  silently never match.
- Putting `container-type` on the same element you then try to style via its `@container`
  query; the element cannot query itself.
- Using `container-type: size` on content-driven components, collapsing them because no
  explicit height is set.
- Reaching for a media query for component-level adaptation, coupling the component to
  the viewport and forcing duplicate modifier classes.
- Forgetting `container-name` in nested containers, so a query binds to the wrong
  ancestor.

## Production Tips

- Container queries are Baseline (widely available since 2023). For older engines,
  the base (unqueried) layout is the fallback, so keep it usable — a `@supports
  (container-type: inline-size)` guard is rarely needed if the base is sound.
- Container query units (`cqi`) make excellent fluid-typography inputs inside a
  component; pair them with `clamp()` for a floor and ceiling.
- When debugging "my query does nothing", check the ancestor chain for `container-type`
  first — it is the number-one cause.

## AI Review Checklist

- Does every `@container` rule have an ancestor with `container-type` declared?
- Is the query on a *descendant* of the container, never the container element itself?
- Is `inline-size` used unless height reactivity is genuinely required?
- Is component-level adaptation done with `@container`, not a viewport media query?
- Are nested containers named to avoid binding a query to the wrong ancestor?
- Does the base layout render acceptably when no container is declared?

## Related

- `knowledge/css/18-media-queries.md`
- `knowledge/css/17-responsive-design.md`
- `knowledge/css/20-css-variables.md`
- `knowledge/css/21-architecture.md`
- `knowledge/css/22-performance.md`
