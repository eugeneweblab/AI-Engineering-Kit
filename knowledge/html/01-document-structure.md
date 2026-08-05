---
id: html/01-document-structure
topic: html
slug: document-structure
title: "Document Structure"
type: doc
order: 1
status: ready
tags: [html, document-structure, lang, defer]
related: [html/02-semantic-html, html/10-metadata, html/11-accessibility, html/18-performance, html/22-validation]
when_to_use: "Read before creating a new HTML page or reviewing the top-level skeleton, doctype, or <head>."
---
# Document Structure

## Purpose

This document defines the required skeleton of every HTML page: the doctype, the root
`<html>` element, the `<head>` (metadata the user never sees but tooling depends on), and
the `<body>` (the visible document). It is written so an agent can scaffold a new page
that renders in standards mode, is accessible, and is ready for CSS and JavaScript without
surprises.

Structure is separate from content. This doc covers the *container*; the meaning of what
goes inside `<body>` is [semantic HTML](02-semantic-html.md), and the contents of `<head>`
are [metadata](10-metadata.md).

## Why It Matters

The first bytes of a document decide how the browser parses everything after them. Omit
`<!DOCTYPE html>` and the browser drops into *quirks mode*, silently changing the box model
and CSS behavior in ways that are maddening to debug. Omit `lang` and screen readers guess
the language, mispronouncing the whole page, while translation tools misfire. Put content
outside `<main>` and assistive-technology "skip to content" jumps land nowhere. None of
these show up as an error; the page just renders, subtly broken for the users least able to
work around it. The skeleton is cheap to get right and expensive to retrofit.

## Core Principles

- **Always declare standards mode.** `<!DOCTYPE html>` is the first line, every time. It is
  not versioned and never optional.
- **Declare the language.** `<html lang="…">` is mandatory; it drives pronunciation,
  hyphenation, and translation.
- **`<head>` is for machines, `<body>` is for people.** Metadata, links, and titles belong
  in `<head>`; nothing visible does.
- **One document, one outline.** Exactly one `<main>`, exactly one `<h1>`, one logical
  reading order that matches the source order.
- **Encoding before content.** `<meta charset>` must appear in the first 1024 bytes so the
  browser never re-parses the document under the wrong encoding.

## Best Practices

- Order the first two `<head>` children as `<meta charset="utf-8">` then the viewport meta,
  before any other tag — both must be seen early.
- Give every page a unique, descriptive `<title>`; it is the tab name, the bookmark name,
  and the primary SEO signal — see [SEO](12-seo.md).
- Add `<meta name="viewport" content="width=device-width, initial-scale=1">` so mobile
  browsers stop assuming a 980px desktop viewport.
- Load stylesheets in `<head>`; load scripts with `defer` (or `type="module"`) so parsing
  is not blocked — see [performance](18-performance.md).
- Keep the source order equal to the reading order. CSS may reposition visually, but the DOM
  order is what keyboard and screen-reader users follow.
- Use landmark elements (`<header>`, `<nav>`, `<main>`, `<footer>`) directly inside `<body>`
  so assistive tech can navigate by region.

## Examples

**Good Example** — standards mode, correct head order, one main outline

```html
<!DOCTYPE html>                                  <!-- standards mode, first line -->
<html lang="en">
  <head>
    <meta charset="utf-8" />                     <!-- encoding first, within 1024 bytes -->
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Invoice #4021 — Acme</title>          <!-- unique, descriptive tab title -->
    <link rel="stylesheet" href="/styles.css" /> <!-- CSS in head -->
    <script src="/app.js" defer></script>        <!-- defer: parse-non-blocking -->
  </head>
  <body>
    <header><nav aria-label="Primary"><!-- … --></nav></header>
    <main>
      <h1>Invoice #4021</h1>                      <!-- exactly one h1 -->
    </main>
    <footer><!-- … --></footer>
  </body>
</html>
```

**Bad Example** — quirks mode, guessable language, blocking script

```html
<!-- No doctype → quirks mode; box model and CSS silently change -->
<html>                                <!-- no lang → screen reader guesses language -->
  <head>
    <title>Page</title>               <!-- charset declared too late, after title -->
    <meta charset="utf-8" />
    <script src="/app.js"></script>   <!-- blocks HTML parsing until fetched+run -->
  </head>
  <body>
    <div class="main">                <!-- not <main>: no landmark, skip-link fails -->
      <h1>Invoice</h1>
      <h1>Line Items</h1>             <!-- second h1: breaks the document outline -->
    </div>
  </body>
</html>
```

## Common Mistakes

- Omitting `<!DOCTYPE html>` and then fighting box-model bugs that quirks mode introduced.
- Missing `lang`, so screen readers and translation apply the wrong language.
- Placing `<meta charset>` after other head content, risking an encoding re-parse.
- Multiple `<h1>` or `<main>` elements, destroying the document outline and landmark map.
- Synchronous `<script>` in `<head>` without `defer`, blocking first paint.
- Skipping the viewport meta, so the page renders zoomed-out on phones.

## Production Tips

- Set `lang` from the actual content language of each page, not a hardcoded default; on
  multilingual sites the wrong `lang` is worse than none for pronunciation.
- Add `<link rel="canonical">` and Open Graph tags in `<head>` for pages that are shared or
  indexed — see [metadata](10-metadata.md).
- Run pages through an HTML validator in CI so structural regressions fail the build — see
  [validation](22-validation.md).

## AI Review Checklist

- Is `<!DOCTYPE html>` the literal first line of the document?
- Does `<html>` carry a `lang` attribute matching the content language?
- Are `<meta charset="utf-8">` and the viewport meta the first two head children?
- Is there exactly one `<title>`, unique to the page?
- Is there exactly one `<main>` and one `<h1>`?
- Do scripts use `defer` or `type="module"` instead of blocking the parser?

## Related

- `knowledge/html/02-semantic-html.md`
- `knowledge/html/10-metadata.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/18-performance.md`
- `knowledge/html/22-validation.md`
