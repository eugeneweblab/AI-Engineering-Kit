---
id: html/02-semantic-html
topic: html
slug: semantic-html
title: "Semantic HTML"
type: doc
order: 2
status: ready
tags: [html, semantic-html]
related: [html/01-document-structure, html/03-text-elements, html/11-accessibility, html/12-seo, html/04-links]
when_to_use: "Read before choosing which element to wrap content in, or when reviewing div/span-heavy markup."
---
# Semantic HTML

## Purpose

This document defines how to choose HTML elements by *meaning* rather than appearance. It
covers the landmark, sectioning, and content elements that give a document structure a
machine can understand, and it establishes the rule for when the generic `<div>`/`<span>`
are — and are not — acceptable.

Semantics are the difference between a page that a browser can render and a document that a
screen reader, search crawler, or AI agent can *understand*. This is the single highest-
leverage skill in HTML.

## Why It Matters

Every consumer of your page except the human eye reads the elements, not the pixels. A
`<button>` is focusable, keyboard-activatable, and announced as "button"; a `<div onclick>`
styled to look identical is none of those things — it is invisible to keyboard users and
silent to assistive tech. `<nav>`, `<main>`, and `<h2>` build the landmark and heading maps
that let a screen-reader user jump around a page the way a sighted user scans it. Remove the
semantics and those users are left reading the whole page top to bottom, or unable to
interact at all. Because the page still *looks* right, these failures ship constantly. Using
the correct element is the cheapest accessibility and SEO win available.

## Core Principles

- **Element = meaning, class = styling.** Pick the element for what the content *is*; use
  classes and CSS for how it looks. Never pick `<div>` because it is "unstyled".
- **`<div>`/`<span>` are the last resort.** They carry zero meaning. Use them only when no
  semantic element fits and you purely need a styling or scripting hook.
- **Prefer native interactive elements.** `<button>`, `<a>`, `<input>`, `<select>`,
  `<details>` bring keyboard, focus, and ARIA behavior for free. Recreating them with
  `<div>` + JS + ARIA is error-prone and almost always worse.
- **Headings define the outline.** `<h1>`–`<h6>` are the table of contents. Rank by
  document logic, never by font size.
- **One landmark per role, per page.** One `<main>`; one primary `<header>`/`<footer>`; name
  multiple `<nav>`s with `aria-label`.

## Best Practices

- Use `<main>` for the unique page content, `<header>`/`<footer>` for banner and contentinfo,
  `<nav>` for major navigation blocks, and `<aside>` for tangential content.
- Use `<article>` for a self-contained, independently distributable unit (a post, a card, a
  comment); use `<section>` for a thematic grouping that has a heading.
- Do not skip heading levels (no `<h1>` straight to `<h3>`); the jump implies a missing
  level to anyone navigating by headings.
- Reach for `<button>` for in-page actions and `<a href>` for navigation — the distinction
  matters, see [links](04-links.md).
- Only add ARIA roles when no native element expresses the meaning. "No ARIA is better than
  bad ARIA" — a wrong role actively misleads assistive tech.
- Give `<section>` and `<article>` an accessible name via a contained heading so they appear
  meaningfully in the landmark list.

## Examples

**Good Example** — meaning-first, native interactivity

```html
<article>                              <!-- self-contained, syndicatable unit -->
  <header>
    <h2>Shipping delays this week</h2> <!-- ranked heading, not styled div -->
    <p>Posted <time datetime="2026-07-07">Jul 7</time></p>
  </header>
  <p>We are seeing longer transit times…</p>
  <footer>
    <button type="button" data-action="subscribe">Notify me</button>
    <!-- native <button>: focusable + keyboard-activatable + announced as "button" -->
  </footer>
</article>
```

**Bad Example** — div soup, faked button

```html
<div class="article">
  <div class="title-lg">Shipping delays this week</div>  <!-- looks like a heading; isn't one -->
  <div class="meta">Posted Jul 7</div>
  <div class="body">We are seeing longer transit times…</div>
  <div class="btn" onclick="subscribe()">Notify me</div>
  <!-- not focusable, no keyboard/Enter support, screen reader says nothing useful -->
</div>
```

## Common Mistakes

- Wrapping everything in `<div>` and conveying meaning only through class names.
- Faking buttons and links with `<div onclick>`, losing keyboard access and focus.
- Choosing heading levels by visual size instead of document hierarchy.
- Adding ARIA roles to elements that already have the semantics (e.g. `role="button"` on a
  `<button>`), or using ARIA to paper over the wrong element.
- Multiple `<main>` elements, or `<nav>` blocks with no `aria-label` to tell them apart.
- Using `<section>` as a generic wrapper when it has no heading — it should be a `<div>`.

## Production Tips

- Inspect the accessibility tree (Chrome DevTools → Accessibility pane) to confirm the page
  exposes the roles and names you intended, not just the visuals.
- Enable a linter rule set such as eslint-plugin-jsx-a11y or axe in CI to catch non-semantic
  interactive elements automatically — see [accessibility](11-accessibility.md).

## AI Review Checklist

- Is each element chosen for meaning, with `<div>`/`<span>` used only as styling hooks?
- Are interactive controls native `<button>`/`<a>`/`<input>` rather than `<div onclick>`?
- Do headings form an unbroken hierarchy with no skipped levels?
- Are landmarks (`<main>`, `<nav>`, `<header>`, `<footer>`) present, unique, and labeled?
- Is ARIA absent where a native element already conveys the role?
- Does every `<section>`/`<article>` have an accessible name from a heading?

## Related


- `knowledge/html/01-document-structure.md`
- `knowledge/html/03-text-elements.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/12-seo.md`
- `knowledge/html/04-links.md`
