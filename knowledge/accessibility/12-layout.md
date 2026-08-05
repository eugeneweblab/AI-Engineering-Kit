---
id: accessibility/12-layout
topic: accessibility
slug: layout
title: "Accessibility Layout"
type: doc
order: 12
status: ready
tags: [accessibility, layout]
related: [accessibility/13-responsive-accessibility, accessibility/04-keyboard-navigation, accessibility/05-focus-management, accessibility/03-semantic-html, accessibility/11-typography]
when_to_use: "Read before building page structure, grids, columns, or any visual arrangement that could diverge from DOM order."
---
# Accessibility Layout

## Purpose

This document defines how to arrange content on a page without breaking the two
orders a page actually has: the **DOM order** (what assistive technology and keyboard
users traverse) and the **visual order** (what sighted users see). Layout is
accessible when those two orders agree, when content reflows without loss, and when
structure is expressed with meaning rather than only with position.

It is written so an agent can build a grid, a multi-column region, or a landmark
structure without stranding a keyboard user or scrambling the screen-reader reading
order.

## Why It Matters

CSS decouples visual position from source order. That power is also the hazard: a
`flex` `order`, a `grid-template-areas` rearrangement, or an absolutely positioned
overlay can make the screen read top-to-bottom while the DOM reads in a completely
different sequence. A keyboard user then tabs to a control that is visually on the
left but comes last in the DOM, and the focus ring appears to jump randomly. A screen
reader user hears the page in an order that no longer matches the visual logic the
copy was written for.

The failure is invisible in a design review — the page *looks* right. It only surfaces
when someone navigates by keyboard or listens to it, which is exactly the audience
least able to recover from it.

## Core Principles

- **DOM order is the reading order.** Author the HTML in the sequence content should be
  read and focused. Use CSS to position, not to reorder meaning.
- **Structure carries meaning, position does not.** A screen reader ignores where a box
  sits on screen; it reads the DOM and the roles. Express regions with landmarks, not
  with visual placement alone.
- **Content must reflow, not overflow.** Layout must survive zoom and narrow viewports
  without a second scrollbar or clipped content (see
  [responsive accessibility](13-responsive-accessibility.md)).
- **Never trap focus in visual order.** If `order` or `flex-direction` reverses the
  visual sequence, the tab sequence still follows the DOM — verify they still agree.
- **Landmarks are the skeleton.** One `main`, banner `header`, `nav`, and `footer` give
  users a way to jump between regions instead of tabbing through everything.

## Best Practices

- Wrap the page in landmark elements: `<header>`, `<nav>`, `<main>`, `<aside>`,
  `<footer>`. Use exactly one `<main>` and give repeated landmarks (`<nav>`) an
  `aria-label` so they are distinguishable.
- Provide a **skip link** as the first focusable element so keyboard users can bypass
  navigation and jump to `<main>`.
- Use CSS Grid and Flexbox for layout; keep the DOM in reading order and let the layout
  engine place items. Avoid `order`, `row-reverse`, and `column-reverse` unless the
  visual and DOM order still match.
- Never use tables for layout. Tables imply data relationships to a screen reader
  (see [tables](17-tables.md)); use them only for tabular data.
- Keep tap and click targets at least **24x24 CSS px** (WCAG 2.2 SC 2.5.8), with
  adequate spacing, so motor-impaired users can hit them.
- Ensure content is not lost or clipped when the viewport is 320 CSS px wide or when
  text is zoomed to 200%.

## Examples

**Good Example** — DOM in reading order, CSS places columns, skip link first

```html
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header>…</header>
  <div class="page">
    <!-- Main content comes first in the DOM because it is the primary content.
         CSS Grid paints the sidebar to the left without touching source order,
         so keyboard tab order and screen-reader order both stay correct. -->
    <main id="main">…</main>
    <aside>…</aside>
  </div>
</body>
```

```css
.page { display: grid; grid-template-columns: 1fr 16rem; }
main   { grid-column: 1; }
aside  { grid-column: 2; }
.skip-link { position: absolute; left: -9999px; }
.skip-link:focus { left: 0; } /* visible only when focused */
```

**Bad Example** — visual order reversed with `order`, DOM out of sync

```css
/* The DOM is <aside> then <main>, but this flips them visually.
   Keyboard focus still follows the DOM, so tabbing lands in the sidebar
   AFTER the main content that visually precedes it — focus jumps backward
   across the screen and confuses every keyboard user. */
.page   { display: flex; }
main    { order: 2; }
aside   { order: 1; }
```

## Common Mistakes

- Using `flex`/`grid` `order` (or `*-reverse`) so visual order and tab order disagree.
- No skip link, forcing keyboard users to tab through the whole nav on every page.
- Multiple `<main>` elements, or none, so users cannot reliably jump to primary content.
- Layout tables that make a screen reader announce spurious rows, columns, and cells.
- Content that overflows or is clipped at 320px width or 200% zoom.
- Positioning an element visually into a section it does not belong to in the DOM, so
  the screen reader reads it under the wrong heading.

## Production Tips

- Add an automated check that tab order matches visual order for key flows; record the
  focus sequence in an end-to-end test and assert it left-to-right, top-to-bottom.
- Turn off CSS entirely (or read the raw DOM) as a fast sanity check: the page should
  still read in a sensible order.

## AI Review Checklist

- Is the DOM authored in the intended reading and focus order, with CSS doing placement?
- Are `order` / `*-reverse` avoided, or verified to keep visual and tab order aligned?
- Is there exactly one `<main>`, plus labelled `header`, `nav`, and `footer` landmarks?
- Is a skip link the first focusable element and visible on focus?
- Are tables reserved for data, never used for layout?
- Do interactive targets meet the 24x24px minimum with adequate spacing?
- Does content reflow without clipping at 320px width and 200% zoom?

## Related

- `knowledge/accessibility/13-responsive-accessibility.md`
- `knowledge/accessibility/04-keyboard-navigation.md`
- `knowledge/accessibility/05-focus-management.md`
- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/11-typography.md`
