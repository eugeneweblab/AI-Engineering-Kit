---
id: accessibility/03-semantic-html
topic: accessibility
slug: semantic-html
title: "Accessibility Semantic HTML"
type: doc
order: 3
status: ready
tags: [accessibility, semantic-html]
related: [accessibility/07-aria, accessibility/04-keyboard-navigation, accessibility/06-screen-readers, accessibility/08-forms, accessibility/02-pour-principles]
when_to_use: "Read before writing any markup or building a component, to choose the element that carries the right role and behavior."
---
# Accessibility Semantic HTML

## Purpose

This document explains how to choose HTML elements for their *meaning* so the browser
builds a correct accessibility tree. Semantic markup is the single highest-leverage
accessibility practice: it gives you roles, names, states, keyboard behavior, and focus
for free. Getting element choice right eliminates most of the ARIA and keyboard work the
other docs would otherwise require.

## Why It Matters

The browser maps HTML elements to accessibility roles. A `<button>` is announced as a
button, is focusable, and fires on both Enter and Space; a `<div>` styled to look like a
button is announced as nothing and does none of that. When you use the wrong element you
inherit *no* behavior and must rebuild all of it by hand with ARIA and JavaScript — code
that is easy to get subtly wrong and that assistive tech may still misread. The
[Robust pillar](02-pour-principles.md) of WCAG is largely satisfied or violated right
here, at element choice.

## Core Principles

- **Choose elements by meaning, not appearance.** Style is CSS's job; semantics is HTML's.
  A heading is `<h2>` even if you want it small; a button is `<button>` even if you want it
  to look like a link.
- **Native controls carry a full contract for free.** `<button>`, `<a href>`, `<input>`,
  `<select>`, `<textarea>`, `<details>` come with role, name, state, focusability, and
  keyboard behavior. Reproducing that with `<div>` + ARIA + JS is error-prone and rarely
  complete. See [ARIA](07-aria.md) for when native isn't enough.
- **Use landmarks to structure the page.** `<header>`, `<nav>`, `<main>`, `<aside>`,
  `<footer>` let screen-reader users jump between regions. Every page needs exactly one
  `<main>`.
- **Headings form the document outline.** One `<h1>` per page; nest `<h2>`–`<h6>` without
  skipping levels. Screen-reader users navigate by headings more than any other way.
- **`<a>` navigates; `<button>` acts.** A link changes location (has an `href`); a button
  triggers an action in place. Swapping them breaks expected keyboard and context-menu
  behavior.

## Best Practices

- Wrap form fields in `<label>` (or use `for`/`id`) so the control has an accessible name
  and a larger click target. See [forms](08-forms.md).
- Use `<ul>`/`<ol>`/`<li>` for lists, `<table>` with `<th scope>` for tabular data, and
  `<fieldset>`/`<legend>` for grouped inputs — assistive tech announces counts and
  relationships from these.
- Use `<button type="button">` for in-page actions to avoid an accidental form submit;
  use `type="submit"` deliberately.
- Prefer `<details>`/`<summary>` for simple disclosure widgets — native, keyboard-ready,
  no JavaScript.
- Don't nest interactive elements (a `<button>` inside an `<a>`); the accessibility tree
  and keyboard behavior become undefined.

## Examples

**Good Example** — meaning-first markup, zero ARIA needed

```html
<main>
  <h1>Invoices</h1>
  <nav aria-label="Invoice filters">
    <!-- a real button: focusable, Enter/Space work, announced "Download, button" -->
    <button type="button" onclick="downloadCsv()">Download CSV</button>
  </nav>
  <!-- a real link: right-click "open in new tab" works, announced as a link -->
  <a href="/invoices/2026">View 2026 invoices</a>
</main>
```

**Bad Example** — div soup that reimplements nothing

```html
<div class="main">
  <div class="title">Invoices</div>          <!-- not a heading: no outline entry -->
  <div class="button" onclick="downloadCsv()">Download CSV</div>
  <!-- not focusable, no Enter/Space, announced as plain text; keyboard users are stuck -->
  <div class="link" onclick="location='/invoices/2026'">View 2026 invoices</div>
  <!-- not a link: no href, no middle-click, no context menu, no "link" role -->
</div>
```

## Common Mistakes

- Using `<div>`/`<span>` with click handlers instead of `<button>`/`<a>`, then bolting on
  `role`, `tabindex`, and key handlers to fake it — usually incompletely.
- Skipping heading levels (`<h1>` then `<h4>`) or using headings purely for visual size.
- Multiple `<h1>`s or no `<main>`, so landmark and outline navigation break.
- Using `<a href="#">` or `<a>` with no href as a button — it isn't focusable/actionable
  the way authors expect.
- Tables built from `<div>`s, losing row/column relationships screen readers rely on.

## Production Tips

- Run an accessibility-tree inspector (Chrome/Firefox DevTools) on new components and
  confirm the role and name match intent before shipping.
- Lint for it: `eslint-plugin-jsx-a11y` (React) flags click handlers on non-interactive
  elements and other semantic slips at build time.

## AI Review Checklist

- Is each interactive element the correct native control (`<button>` for actions, `<a href>`
  for navigation), not a `<div>`/`<span>`?
- Is there exactly one `<h1>` and one `<main>`, with headings nested without skipping?
- Are landmarks (`<nav>`, `<main>`, `<header>`, `<footer>`) used to structure the page?
- Do form controls have real `<label>`s, and grouped inputs a `<fieldset>`/`<legend>`?
- Is ARIA absent wherever a native element would have done the job?

## Related

- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/04-keyboard-navigation.md`
- `knowledge/accessibility/06-screen-readers.md`
- `knowledge/accessibility/08-forms.md`
- `knowledge/accessibility/02-pour-principles.md`
