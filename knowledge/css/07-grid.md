---
id: css/07-grid
topic: css
slug: grid
title: "Grid"
type: doc
order: 7
status: ready
tags: [css, grid]
related: [css/06-flexbox, css/08-sizing, css/09-spacing, css/17-responsive-design, css/19-container-queries]
when_to_use: "Read before building any two-dimensional layout, page shell, or responsive card gallery."
---
# Grid

## Purpose

This document defines how to lay out elements in two dimensions — rows and columns at
once — using `display: grid`. It covers track definition, the `fr` unit, `repeat()`,
`minmax()`, `auto-fit`/`auto-fill`, named areas, and `gap`, so an agent can build a page
shell or card gallery that reflows without media queries.

Grid is for *structure*: page layouts, dashboards, galleries, any design where children
align in both axes. For a single row or column driven by content, use
[Flexbox](06-flexbox.md).

## Why It Matters

Before Grid, two-dimensional layout meant nested floats, clearfix hacks, and precise
pixel math that shattered at every breakpoint. Grid replaces all of it with an explicit
model where the parent owns the layout and children slot into it. The intrinsic-sizing
primitives (`fr`, `minmax`, `auto-fit`) let a layout respond to available space directly,
so a well-built grid often needs *zero* media queries. Getting this right eliminates the
most tedious and bug-prone category of CSS.

## Core Principles

- **The grid container defines the tracks; children place into them.**
  `grid-template-columns`, `grid-template-rows`, and `gap` live on the container.
  Placement (`grid-column`, `grid-row`, `grid-area`) lives on children.
- **`fr` distributes leftover space; it is not a fixed unit.** `1fr 1fr` splits free
  space in two *after* fixed tracks and `gap` are subtracted — so `fr` columns never
  overflow the container the way `50%` can.
- **Prefer intrinsic responsiveness over breakpoints.** `repeat(auto-fit, minmax(min, 1fr))`
  fits as many columns as space allows and reflows automatically, replacing a stack of
  media queries.
- **Name what is structural.** For page shells, `grid-template-areas` makes the layout
  readable and lets you rearrange regions at a breakpoint by rewriting one string map.

## Best Practices

- Build responsive galleries with `repeat(auto-fit, minmax(16rem, 1fr))`: columns are at
  least `16rem`, share extra space equally, and wrap when they no longer fit — no media
  queries needed.
- Use `minmax(0, 1fr)` instead of `1fr` when grid children hold text that must truncate;
  a bare `1fr` resolves to `minmax(auto, 1fr)` and refuses to shrink below content,
  causing overflow (the grid analogue of Flexbox's `min-width: auto`).
- Use `gap` for gutters; never simulate them with margins on grid children.
- Use `grid-template-areas` for page shells (header / sidebar / main / footer) — the ASCII
  map documents intent and reorders trivially at breakpoints.
- Choose `auto-fill` vs `auto-fit` deliberately: `auto-fill` keeps empty tracks (items
  stay their min size); `auto-fit` collapses empty tracks so items stretch to fill.
- Place items with line-based `grid-column: 1 / 3` or `span 2` rather than sizing them
  by hand; the grid keeps them aligned.

## Examples

**Good Example** — gallery that reflows with no media queries

```css
.gallery {
  display: grid;
  /* Fit as many >=16rem columns as fit; share extra space; wrap automatically. */
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: 1rem;
}

.page {
  display: grid;
  grid-template-columns: 16rem 1fr;              /* sidebar + fluid main */
  grid-template-areas:
    "header  header"
    "sidebar main"
    "footer  footer";
  gap: 1rem;
}
.page > header { grid-area: header; }
.page > nav    { grid-area: sidebar; }
.page > main   { grid-area: main; min-width: 0; } /* allow content to shrink */
.page > footer { grid-area: footer; }
```

**Bad Example** — fixed columns and percentage math that overflow

```css
.gallery {
  display: grid;
  grid-template-columns: 250px 250px 250px; /* fixed count: overflows narrow screens */
  gap: 1rem; /* gap is added ON TOP of 750px, so total exceeds container */
}
.page {
  display: grid;
  grid-template-columns: 20% 80%; /* percentages ignore the gap → horizontal scroll */
}
/* No auto-fit, so this needs a media query for every breakpoint. */
```

## Common Mistakes

- Using fixed pixel column counts (`200px 200px 200px`) instead of
  `repeat(auto-fit, minmax(...))`, forcing a media query per breakpoint.
- Using `1fr` for text-bearing tracks and getting overflow because it means
  `minmax(auto, 1fr)`; use `minmax(0, 1fr)`.
- Mixing `%` tracks with `gap`, which overflows because `%` is of the container but `gap`
  is added after.
- Reaching for Grid on a simple one-axis toolbar where [Flexbox](06-flexbox.md) is simpler.
- Forgetting that `grid-template-areas` requires every cell named or `.` — an unnamed
  hole is a parse error.

## Production Tips

- Grid aligns children *across* rows and columns automatically — use it (not Flexbox)
  whenever cards in different rows must line up on a shared grid.
- Combine Grid for the page and Flexbox inside each cell: Grid for structure, Flex for
  the content flow within a component. They compose cleanly.
- Pair Grid with [container queries](19-container-queries.md) so a component's column
  count responds to *its own* width, not the viewport.

## AI Review Checklist

- Is this layout genuinely 2-D? If one-axis, should it be [Flexbox](06-flexbox.md)?
- Are responsive galleries built with `repeat(auto-fit/auto-fill, minmax(...))` rather
  than fixed column counts plus media queries?
- Do text-bearing tracks use `minmax(0, 1fr)` to allow truncation?
- Are gutters done with `gap`, not child margins?
- Do `%`-based tracks avoid overflowing when combined with `gap`?
- For page shells, are regions named via `grid-template-areas` for readability?

## Related

- `knowledge/css/06-flexbox.md`
- `knowledge/css/08-sizing.md`
- `knowledge/css/09-spacing.md`
- `knowledge/css/17-responsive-design.md`
- `knowledge/css/19-container-queries.md`
