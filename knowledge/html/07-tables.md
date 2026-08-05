---
id: html/07-tables
topic: html
slug: tables
title: "HTML Tables"
type: doc
order: 7
status: ready
tags: [html, tables, rowspan, colspan, scope, region, aria-label]
related: [html/11-accessibility, html/02-semantic-html, html/08-forms, html/06-lists]
when_to_use: "Read before rendering any tabular data grid or reviewing a data table's markup."
---
# HTML Tables

## Purpose

This document defines how to mark up **two-dimensional data** — rows and columns whose
cells relate along both axes — with `<table>`. Tables are for data, not layout. Done
right, a table lets a screen-reader user query "what column am I in?" and hear the
header for the current cell; done wrong, it is an unnavigable maze of numbers.

## Why It Matters

A sighted user reads a table by glancing up to the column header and left to the row
header. Assistive technology cannot glance — it relies entirely on the markup to know
which `<th>` governs each `<td>`. If headers are not declared with `<th>` and scopes,
every data cell is announced without context: the user hears "1,240" with no idea it is
Q3 revenue for the EU region. Correct table structure is the difference between usable
data and noise. Layout tables, meanwhile, inject fake rows/columns that confuse readers.

## Core Principles

- **Tables are for tabular data only.** Never use `<table>` for page layout — use CSS
  Grid or Flexbox. Layout tables create phantom structure for screen readers.
- **Every data table needs a `<caption>`.** It is the table's accessible name and
  first thing a screen reader announces; it orients the user before the data.
- **Headers are `<th>`, data is `<td>`.** Declare direction with `scope="col"` or
  `scope="row"` so each data cell maps to its header(s).
- **Group rows semantically** with `<thead>`, `<tbody>`, and `<tfoot>`. This lets the
  header row repeat when printing or scrolling and clarifies structure.
- **Keep one logical grid.** Avoid merged cells (`colspan`/`rowspan`) unless the data
  genuinely spans; complex spans need explicit header association.

## Best Practices

- Place `<caption>` as the first child of `<table>`; it can be visually styled but must
  stay in the DOM.
- Use `scope` on simple tables. For complex tables with multi-level headers, give each
  `<th>` an `id` and reference them from cells with `headers="id1 id2"`.
- Put column headers in `<thead>`, the footer totals in `<tfoot>`, and the body rows in
  `<tbody>`. `<tfoot>` may appear before `<tbody>` in source; browsers render it last.
- For wide tables, wrap in a scroll container (`<div style="overflow-x:auto">`) with
  `role="region"`, `aria-label`, and `tabindex="0"` so keyboard users can scroll it.
- Right-align and use `tabular-nums` for numeric columns via CSS; do not pad with
  spaces in the markup.
- Do not use `<table>` inside email-agnostic app UIs for cards or forms.

## Examples

**Good Example** — captioned, scoped headers, grouped sections

```html
<table>
  <caption>Quarterly revenue by region (USD, thousands)</caption>
  <thead>
    <tr>
      <th scope="col">Region</th> <!-- scope=col: governs its column -->
      <th scope="col">Q1</th>
      <th scope="col">Q2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">EU</th> <!-- scope=row: governs its row -->
      <td>1,240</td>
      <td>1,380</td>
    </tr>
  </tbody>
</table>
```

**Bad Example** — layout table, no headers, no caption

```html
<!-- Table used for layout: screen readers announce a bogus 1x2 grid.
     No <th>/scope means data cells have no header context; no <caption>
     means the table has no accessible name. Use CSS Grid for layout. -->
<table>
  <tr>
    <td><img src="/logo.png" alt="Acme"></td>
    <td><nav>...</nav></td>
  </tr>
</table>
```

## Common Mistakes

- Using `<table>` to position unrelated content instead of CSS layout.
- Marking header cells as `<td>` (styled bold) instead of `<th>` with `scope`.
- Omitting `<caption>`, leaving the table without an accessible name.
- Overusing `colspan`/`rowspan` without `headers`/`id` associations, so merged cells
  lose their header mapping.
- Wrapping a wide table without a focusable, scrollable container — keyboard users
  cannot reach off-screen columns.
- Faking rows with `<br>` or stacked `<div>`s that lose row/column relationships.

## AI Review Checklist

- Is `<table>` used only for genuinely tabular data, never for layout?
- Does every data table have a `<caption>` as its first child?
- Are header cells `<th>` with correct `scope` (or `id`/`headers` for complex tables)?
- Are rows grouped with `<thead>`/`<tbody>`/`<tfoot>`?
- Do merged cells (`colspan`/`rowspan`) retain explicit header association?
- Is a wide table wrapped in a keyboard-scrollable, labelled region?
- Are numeric cells aligned via CSS rather than whitespace in the markup?

## Related

- `knowledge/html/02-semantic-html.md`
- `knowledge/html/06-lists.md`
- `knowledge/html/08-forms.md`
- `knowledge/html/11-accessibility.md`
