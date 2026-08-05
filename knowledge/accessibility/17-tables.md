---
id: accessibility/17-tables
topic: accessibility
slug: tables
title: "Accessibility Tables"
type: doc
order: 17
status: ready
tags: [accessibility, tables]
related: [accessibility/03-semantic-html, accessibility/12-layout, accessibility/07-aria, accessibility/13-responsive-accessibility, accessibility/06-screen-readers]
when_to_use: "Read before building any data table, grid of tabular data, or when tempted to use a table for layout."
---
# Accessibility Tables

## Purpose

This document defines how to build a data table that a screen reader can navigate cell
by cell while announcing the row and column each value belongs to. A correctly marked
table lets a blind user do what a sighted user does at a glance — read a number and know
what it means. A malformed table turns that same data into an undifferentiated stream of
values with no anchors.

It is written so an agent can associate headers with cells, add a caption, and choose
between a table and other markup, without producing a grid that reads as noise.

## Why It Matters

A sighted user reads a table two-dimensionally: they trace up a column to its header and
left along a row to its label, then land on the intersecting cell. A screen reader has no
spatial view — it reads linearly. The only thing that reconstructs the two-dimensional
meaning is the markup: `<th>` cells, their `scope`, and the header/cell association. Get
that right and the screen reader announces "Revenue, Q3, $1.2M" as the user arrows across
the cell. Get it wrong — headers as bold `<td>`s, no `scope` — and the same cell is
announced as a bare "$1.2M" with no idea which metric or which quarter.

The opposite failure is just as common: using a table purely for visual layout, which
makes a screen reader announce phantom rows and columns for content that has no tabular
relationship at all.

## Core Principles

- **Tables are for data, never for layout.** If the content has no row/column
  relationship, use CSS Grid/Flexbox instead (see [layout](12-layout.md)). A layout
  table pollutes the screen-reader experience with meaningless structure.
- **Every data table has header cells.** Use `<th>` for headers, not styled `<td>`;
  headers are what give data cells their meaning.
- **Declare header direction with `scope`.** `scope="col"` and `scope="row"` tell the
  screen reader which cells a header governs.
- **Give the table a caption.** `<caption>` is the table's accessible name and
  orients the user before they enter it.
- **Preserve structure when responsive.** A table that collapses on mobile must keep its
  header associations (see [responsive accessibility](13-responsive-accessibility.md)).

## Best Practices

- Use real table markup: `<table>`, `<caption>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`,
  `<td>`. Semantics come from the elements, not from ARIA added afterward.
- Put a `<caption>` as the first child of `<table>` describing what the table contains;
  it is announced when the user enters the table.
- Mark column headers `<th scope="col">` and row headers `<th scope="row">`. For simple
  tables `scope` is sufficient and preferred over `headers`/`id`.
- For complex tables with split or multi-level headers, associate cells explicitly with
  `headers` referencing each governing `<th>`'s `id` — but first ask whether the table
  can be simplified instead.
- Do not nest tables, and do not merge cells (`colspan`/`rowspan`) unless the data truly
  requires it; both make navigation harder.
- If a CSS layout (`display: block/flex/grid`) is applied for responsiveness, keep the
  semantics with `role="table"`/`role="row"`/`role="cell"` or restructure so headers are
  still associated. Do not let responsive CSS silently strip table semantics.
- Never use `<table>` to position unrelated content side by side.

## Examples

**Good Example** — caption, scoped headers, real structure

```html
<table>
  <caption>Quarterly revenue by region (USD, millions)</caption>
  <thead>
    <tr>
      <!-- scope="col" ties each header to its whole column so the screen
           reader announces "Region"/"Q1" etc. as it enters each column. -->
      <th scope="col">Region</th>
      <th scope="col">Q1</th>
      <th scope="col">Q2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <!-- scope="row" makes "North" the label for this row, so the cell
           $1.2M is announced as "North, Q1, 1.2". -->
      <th scope="row">North</th>
      <td>1.2</td>
      <td>1.5</td>
    </tr>
  </tbody>
</table>
```

**Bad Example** — layout table, no headers, no caption

```html
<!-- No <th>, no scope, no caption. A screen reader reads a flat stream of
     numbers with no way to know which region or quarter each belongs to.
     Worse if this <table> were only for visual columns of unrelated
     content — it would announce fake rows and cells. -->
<table>
  <tr><td><b>Region</b></td><td><b>Q1</b></td><td><b>Q2</b></td></tr>
  <tr><td>North</td><td>1.2</td><td>1.5</td></tr>
</table>
```

## Common Mistakes

- Using `<table>` for page layout, injecting meaningless structure into the reading order.
- Bold `<td>` cells acting as headers instead of `<th>` with `scope`.
- Omitting `<caption>`, leaving the table without an accessible name.
- Missing `scope` on headers, so cell/header association is guessed or lost.
- Over-using `colspan`/`rowspan` or nested tables, making cell navigation confusing.
- Responsive CSS (`display: block`) that strips the implicit table roles and orphans the
  headers.
- Reaching for ARIA (`role="table"`) on markup that could just be a native `<table>`.

## Production Tips

- Test with a screen reader's table navigation commands (e.g., NVDA `Ctrl+Alt+Arrow`):
  moving cell to cell should announce the row and column headers, not just the value.
- If a table needs sorting, filtering, or editable cells, use the ARIA `grid` pattern
  deliberately — it changes keyboard expectations and is more than a styled table.

## AI Review Checklist

- Is the table used for genuine tabular data, not for layout?
- Does every data table have a `<caption>` describing its contents?
- Are headers `<th>` with correct `scope="col"`/`scope="row"` (or `headers`/`id` when
  complex)?
- Are `colspan`/`rowspan` and nesting avoided unless the data truly requires them?
- Do responsive styles preserve header/cell associations rather than stripping semantics?
- When moving cell to cell, does a screen reader announce the relevant row and column
  headers?

## Related

- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/12-layout.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/13-responsive-accessibility.md`
- `knowledge/accessibility/06-screen-readers.md`
