---
id: html/00-overview
topic: html
slug: overview
title: "HTML Overview"
type: doc
order: 0
status: ready
tags: [html, overview, lang]
related: [html/01-document-structure, html/02-semantic-html, html/11-accessibility, html/21-best-practices, html/99-ai-review-checklist]
when_to_use: "Read first when writing or reviewing any HTML, to orient yourself in this topic and find the right detail doc."
---
# HTML Overview

## Purpose

This document is the map for the `html` topic. It explains what HTML is responsible
for, the principles that run through every doc here, and where to go for each concern.
Read it first, then jump to the specific doc for the element or problem in front of you.

HTML defines the *structure and meaning* of a document — what each piece of content
*is*, not how it looks (that is CSS) or how it behaves (that is JavaScript). Getting
this layer right is what makes a page accessible, indexable, resilient, and cheap to
maintain. Getting it wrong is invisible in a browser but breaks screen readers, search
crawlers, and every tool that reads the DOM as data.

## Why It Matters

HTML is the one layer that every other layer depends on. CSS selects it, JavaScript
queries it, screen readers announce it, search engines parse it, and browsers repair it
when it is malformed. A `<div>` that should have been a `<button>` looks identical on
screen but is unreachable by keyboard, silent to assistive technology, and invisible to
the accessibility tree. These defects pass visual QA and ship. Because HTML failures are
silent and affect users you cannot see, correct semantics are not a nicety — they are the
baseline for a working product.

## Core Principles

- **Meaning over appearance.** Choose an element for what the content *is*, then style it.
  Never reach for `<div>`/`<span>` when a semantic element exists — see [semantic HTML](02-semantic-html.md).
- **The browser will fix nothing for you.** Invalid or misnested markup is silently
  repaired into a DOM you did not intend. Write valid HTML and [validate it](22-validation.md).
- **Accessibility is not optional.** Native elements come with keyboard, focus, and
  screen-reader behavior for free. Preserve it; do not reimplement it. See [accessibility](11-accessibility.md).
- **Structure is data.** Search engines, social previews, and AI agents read your markup
  as a structured document. Correct headings, landmarks, and [metadata](10-metadata.md) make it legible.
- **Degrade gracefully.** Content and links must work before CSS or JavaScript load — see
  [progressive enhancement](23-progressive-enhancement.md).

## How These Docs Fit Together

- **Foundations** — start here: [document structure](01-document-structure.md) (the skeleton
  and `<head>`), [semantic HTML](02-semantic-html.md) (choosing the right element),
  [metadata](10-metadata.md) (charset, viewport, `<meta>`).
- **Content elements** — [text](03-text-elements.md), [links](04-links.md),
  [images](05-images.md), [lists](06-lists.md), [tables](07-tables.md),
  [forms](08-forms.md), [media](09-media.md).
- **Quality and reach** — [accessibility](11-accessibility.md), [SEO](12-seo.md),
  [structured data](13-structured-data.md), [performance](18-performance.md),
  [security](19-security.md).
- **Advanced** — [SVG](16-svg.md), [canvas](17-canvas.md), [web components](25-web-components.md),
  [iframes](15-iframes.md), [custom data attributes](14-custom-data-attributes.md).
- **Discipline** — [best practices](21-best-practices.md), [validation](22-validation.md),
  [debugging](29-debugging.md), [engineering principles](30-engineering-principles.md),
  [production checklist](98-production-checklist.md), [AI review checklist](99-ai-review-checklist.md),
  [common anti-patterns](100-common-antipatterns.md).

## Best Practices

- Begin every document with `<!DOCTYPE html>` and a declared `lang` — see [document structure](01-document-structure.md).
- Pick the element with the closest *meaning* before falling back to `<div>`/`<span>`.
- Keep one logical `<h1>` per page and never skip heading levels.
- Treat the [AI review checklist](99-ai-review-checklist.md) as the definition of done for
  any HTML change.

## Examples

**Good Example** — semantic skeleton a reader and a crawler both understand

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Quarterly Report</title>
  </head>
  <body>
    <header><nav><!-- site nav --></nav></header>
    <main>
      <h1>Quarterly Report</h1>   <!-- one topic-defining heading -->
      <article><!-- primary content --></article>
    </main>
    <footer><!-- contact, legal --></footer>
  </body>
</html>
```

**Bad Example** — visually identical, structurally meaningless

```html
<!-- No doctype, no lang, no landmarks: works on screen, fails everywhere else -->
<div class="page">
  <div class="header"><div class="nav"></div></div>
  <div class="title">Quarterly Report</div> <!-- not a heading; invisible to a11y/SEO -->
  <div class="content"></div>
</div>
```

## Common Mistakes

- Treating HTML as "just markup for CSS to style" and defaulting everything to `<div>`.
- Skipping the doctype or `lang`, forcing quirks mode and breaking language tooling.
- Copying markup from a design tool without checking that it is semantic and valid.
- Assuming the browser rendering the page means the HTML is correct.

## AI Review Checklist

- Does the document start with `<!DOCTYPE html>` and declare `lang`?
- Is every element chosen for meaning, with `<div>`/`<span>` only for styling hooks?
- Is there exactly one `<h1>` and an unbroken heading hierarchy?
- Are landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`) present and used once each?
- Does the markup validate, and does it work with CSS and JS disabled?

## Related

- `knowledge/html/01-document-structure.md`
- `knowledge/html/02-semantic-html.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/21-best-practices.md`
- `knowledge/html/99-ai-review-checklist.md`
