---
id: html/30-engineering-principles
topic: html
slug: engineering-principles
title: "HTML Engineering Principles"
type: doc
order: 30
status: ready
tags: [html, engineering-principles, html-validate, charset, eslint-plugin-jsx-a11y, autocomplete]
related: [html/02-semantic-html, html/11-accessibility, html/23-progressive-enhancement, html/21-best-practices, html/19-security]
when_to_use: "Read before authoring or reviewing any HTML, to ground decisions in durable principles rather than styling habits."
---
# HTML Engineering Principles

## Purpose

This document defines the foundational principles for writing HTML that is correct,
accessible, and durable. It is not a tag reference; it is the reasoning an agent should
apply *before* choosing an element or attribute, so that markup expresses meaning rather
than appearance.

HTML is the load-bearing layer of every web page. CSS and JavaScript can fail, be
disabled, or arrive late; the HTML is what remains. Treat it as the contract between
your content and every consumer of it — browsers, assistive technology, crawlers, and
future maintainers.

## Why It Matters

Bad HTML fails quietly. A `<div>` used as a button still looks clickable, so nobody
notices that keyboard and screen-reader users cannot operate it — until an accessibility
audit or a lawsuit. Non-semantic markup passes every visual review and still locks out a
measurable fraction of users, tanks SEO, and forces JavaScript to re-implement behavior
the browser gives for free. Because the failure is invisible to a sighted mouse user,
HTML must be held to a higher bar than "it renders." Correctness here is verifiable
against a specification, not against a screenshot.

## Core Principles

- **Semantics first, styling second.** Choose an element for what the content *is*, not
  how it should look. A heading is `<h1>`–`<h6>` because it is a heading; make it look
  right with CSS afterward.
- **The document must stand alone.** It should convey structure and be operable with no
  CSS and no JavaScript. Everything else is enhancement layered on that foundation.
- **Use the platform.** Native elements (`<button>`, `<a>`, `<details>`, `<dialog>`,
  form controls) ship with focus, keyboard, and ARIA semantics built in. Reimplementing
  them in `<div>`s means reimplementing accessibility, and you will get it wrong.
- **Accessibility is not optional.** Every interactive element must be reachable and
  operable by keyboard, and every non-text element must expose a text alternative.
- **Valid, well-formed markup.** Nest elements per the spec, close what must be closed,
  and keep `id` values unique. Browsers repair invalid HTML unpredictably; do not rely
  on the repair.
- **Separation of concerns.** Structure in HTML, presentation in CSS, behavior in JS.
  Inline styles and inline event handlers couple the three and rot fast.

## Best Practices

- Declare `<!DOCTYPE html>`, set `<html lang="…">`, and specify
  `<meta charset="utf-8">` first inside `<head>`. These are cheap and prevent whole
  classes of rendering and encoding bugs.
- Reach for a semantic element before a generic one: `<nav>`, `<main>`, `<article>`,
  `<section>`, `<header>`, `<footer>`, `<aside>` over `<div>`.
- Use exactly one `<main>` per page and a logical, non-skipping heading order.
- Give every `<img>` an `alt` attribute — descriptive for meaningful images, empty
  (`alt=""`) for decorative ones so screen readers skip them.
- Associate every form control with a `<label>` via `for`/`id`, and use the right
  `type` and `autocomplete` so browsers can assist.
- Prefer `<a href>` for navigation and `<button>` for actions. Never swap them: a link
  is not a button, and a `<div onclick>` is neither.
- Keep the DOM shallow and meaningful. Wrapper `<div>` soup slows rendering and hides
  structure.

## Examples

**Good Example** — semantic, self-describing, works without JS

```html
<!-- Element choice communicates intent: nav for navigation, button for an action. -->
<nav aria-label="Primary">
  <a href="/pricing">Pricing</a>
</nav>
<main>
  <article>
    <h1>Report</h1>
    <!-- Native <button> is keyboard-operable and announced as a button for free. -->
    <button type="button" onclick="exportReport()">Export</button>
  </article>
</main>
```

**Bad Example** — divs faking semantics, inaccessible, style-driven

```html
<!-- Looks identical on screen, but exposes none of the meaning or behavior. -->
<div class="nav">
  <div class="link" onclick="location='/pricing'">Pricing</div> <!-- not focusable, not a link -->
</div>
<div class="title-big">Report</div>          <!-- not a heading; breaks outline & SEO -->
<div class="btn" onclick="exportReport()">    <!-- no keyboard, no role, no focus -->
  Export
</div>
```

## Common Mistakes

- Choosing an element for its default appearance instead of its meaning, then fighting
  CSS to make a `<div>` behave like a control.
- Using `<div>`/`<span>` with click handlers instead of `<button>` or `<a>`, dropping
  keyboard and screen-reader support.
- Skipping heading levels (`<h1>` straight to `<h4>`) and breaking the document outline.
- Omitting `alt`, `lang`, `<label>`, or `charset` because the page "looks fine."
- Duplicate `id` values, which break label association, anchors, and scripts.
- Relying on CSS or JavaScript to supply structure the HTML should carry itself.

## Production Tips

- Wire an HTML validator (W3C Nu or `html-validate`) and an accessibility linter
  (`axe`, `eslint-plugin-jsx-a11y`) into CI so regressions fail the build, not the user.
- Test each page with CSS and JavaScript disabled; the core content and navigation must
  still work.
- Audit the tab order with the keyboard alone before shipping any interactive component.

## AI Review Checklist

- Is every element chosen for its meaning rather than its default appearance?
- Does the page have `<!DOCTYPE html>`, `<html lang>`, and `<meta charset>`?
- Are all interactive controls native elements (`<a>`, `<button>`, form controls) or
  properly role-and-keyboard-enabled?
- Does every image have an appropriate `alt`, and every form control a `<label>`?
- Is the heading order logical and non-skipping, with exactly one `<main>`?
- Does the document convey its structure with CSS and JavaScript disabled?

## Related

- `knowledge/html/02-semantic-html.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/23-progressive-enhancement.md`
- `knowledge/html/21-best-practices.md`
- `knowledge/html/19-security.md`
