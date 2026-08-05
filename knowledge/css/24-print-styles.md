---
id: css/24-print-styles
topic: css
slug: print-styles
title: "Print Styles"
type: doc
order: 24
status: ready
tags: [css, print-styles, "@media", font-size, prefers-color-scheme]
related: [css/18-media-queries, css/17-responsive-design, css/23-accessibility, css/12-backgrounds]
when_to_use: "Read before building an invoice, report, article, receipt, or any page a user is expected to print or save as PDF."
---
# Print Styles

## Purpose

This document defines how to make a page render correctly on paper and in "Save as PDF".
Print is a distinct medium with its own constraints: fixed page width, hard page breaks,
no scrolling, no interactivity, and (usually) no color. A page that looks perfect on
screen is often unreadable when printed. Print styles fix that with a dedicated
`@media print` block, not a second document.

## Why It Matters

Print output is invisible during normal development — nobody prints while coding — so
these bugs ship silently and surface only when a user prints an invoice with the nav bar
covering the total, or a report where a table splits a row across two pages. For many
business documents (invoices, receipts, tickets, contracts) the printed artifact is the
*product*. Ink and paper also cost money: a dark hero background printed edge to edge
wastes a cartridge. Getting print right is cheap if you plan for it and expensive to
retrofit.

## Core Principles

- **Print is a media type, not a theme.** Scope all print rules inside `@media print`
  so they never affect the screen and screen rules never leak onto paper.
- **Remove, don't rearrange.** On paper there is no interaction: hide navigation,
  buttons, search boxes, cookie banners, and sidebars rather than restyling them.
- **Reflow to a single readable column.** The page is a fixed A4/Letter width; multi-column
  screen layouts and fixed positioning break. Reset them to normal flow.
- **Control page breaks explicitly.** The browser will otherwise split headings, table
  rows, and figures across pages. Tell it where breaks may and may not happen.
- **Make ink optional.** Assume black text on white paper; never rely on background color
  to convey meaning, because browsers strip backgrounds when printing by default.

## Best Practices

- Put print rules in `@media print`. Use `@page { margin: 1.5cm; }` to set paper margins
  in physical units (`cm`, `mm`, `pt`), not `px`.
- Hide non-content chrome with a utility: `.no-print { display: none !important; }` plus
  `nav, footer, aside, .cookie-banner { display: none; }`. `!important` is acceptable here
  because print utilities must win.
- Reset layout: set fixed/sticky elements to `position: static`, collapse grids and
  flex containers to a single column, and set `width: 100%`.
- Prevent orphaned headings and split rows with `break-inside: avoid` on `tr`, figures,
  and cards, and `break-after: avoid` on headings so a heading never ends a page alone.
- Force a fresh page between major sections with `break-before: page`.
- Reveal link targets: `a[href]::after { content: " (" attr(href) ")"; }` so a printed
  page keeps the URLs a click would have followed.
- Use `print-color-adjust: exact` (with `-webkit-print-color-adjust`) **only** when a
  background is load-bearing (e.g. a status badge), and warn the user it needs "background
  graphics" enabled.
- Test with the browser's print preview and "Save as PDF" — that is the real render path.

## Examples

**Good Example** — scoped, reflowed, break-aware

```css
@media print {
  @page { margin: 1.5cm; }               /* physical margin the printer honors */

  nav, aside, .toolbar, .no-print {
    display: none !important;            /* remove chrome; nothing to interact with */
  }

  body { color: #000; background: #fff; font-size: 12pt; } /* pt is the print unit */

  .layout { display: block; }            /* collapse the multi-column grid to one flow */

  h2, h3 { break-after: avoid; }         /* heading never stranded at page bottom */
  table, figure, tr { break-inside: avoid; } /* keep a row/figure on one page */

  a[href^="http"]::after {
    content: " (" attr(href) ")";        /* printed link keeps its destination */
    font-size: 0.85em;
  }
}
```

**Bad Example** — screen layout leaks onto paper

```css
/* No @media print block at all. On paper this fixed header overlaps the content,
   the dark background wastes ink (or is silently dropped, hiding white text),
   and long tables split rows mid-cell with no way to control it. */
.header { position: fixed; top: 0; background: #1a1a2e; color: #fff; }
.report { display: grid; grid-template-columns: 250px 1fr; } /* sidebar wastes page width */
a { color: #4a90d9; }  /* on paper the URL is lost — "click here" points nowhere */
```

## Common Mistakes

- Shipping no `@media print` block, so the screen layout (fixed headers, sidebars,
  dark backgrounds) prints verbatim.
- Using `px` and `vh`/`vw` units for print — physical output wants `cm`/`mm`/`pt`; viewport
  units are meaningless on paper.
- Relying on `display: none` for the deprecated goal of hiding, then forgetting `print`
  utilities need `!important` to override component styles.
- Letting tables and cards break across pages because no `break-inside: avoid` was set.
- Hiding link URLs, so a printed article's references are unrecoverable.
- Assuming background colors print — they are stripped by default, so white-on-color text
  vanishes into white-on-white.

## Production Tips

- Offer an explicit "Print" or "Download PDF" button that calls `window.print()`, and
  test the output for every document template (invoice, receipt, report) in CI or a visual
  snapshot suite — print regressions are otherwise never caught.
- Use `prefers-color-scheme` for screen but always reset to light in `@media print`; a
  dark-mode user must not get a black-rectangle printout.
- For server-generated PDFs (headless Chromium/Puppeteer), the same `@media print` rules
  apply — keep one stylesheet, not a separate PDF template.

## AI Review Checklist

- Are all print rules scoped inside `@media print`?
- Is page chrome (nav, sidebars, buttons, banners) hidden for print?
- Are `@page` margins set in physical units, not `px`?
- Are `break-inside: avoid` / `break-after: avoid` applied to tables, figures, and headings?
- Is text forced to a printable color (dark on white), not dependent on background color?
- Are link URLs exposed via `attr(href)` for important links?
- Was the output verified in real print preview / Save-as-PDF, not just assumed?

## Related

- `knowledge/css/18-media-queries.md`
- `knowledge/css/17-responsive-design.md`
- `knowledge/css/23-accessibility.md`
- `knowledge/css/12-backgrounds.md`
