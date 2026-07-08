---
id: html/21-best-practices
topic: html
slug: best-practices
title: "Best Practices"
type: doc
order: 21
status: ready
tags: [html, best-practices]
related: [html/02-semantic-html, html/11-accessibility, html/22-validation, html/19-security, html/18-performance]
when_to_use: "Read before authoring or reviewing any HTML document, as a baseline of non-negotiable conventions."
---
# Best Practices

## Purpose

This document is the baseline of HTML conventions that every page should follow,
regardless of framework or purpose. It consolidates the highest-value rules from
across this topic — semantics, accessibility, validity, and structure — into one
checklist an agent can apply to any document.

Where other docs go deep on one concern, this one is the breadth pass: the set of
habits that keep markup correct, accessible, and maintainable by default.

## Why It Matters

HTML is forgiving to write and unforgiving in aggregate. A page renders even when the
markup is a wall of `<div>`s, but that page is unreadable to screen readers, invisible
to search engines, brittle to style, and painful to change. Because browsers silently
recover from bad markup, mistakes never announce themselves — they accumulate as
technical debt that surfaces months later as an accessibility lawsuit, an SEO gap, or a
layout that breaks the moment content changes. Getting the fundamentals right up front
costs nothing extra and prevents all of it.

## Core Principles

- **Semantics first.** Choose the element that describes the content's meaning, not its
  appearance. `<button>`, `<nav>`, `<article>` carry behavior and accessibility for free
  that a styled `<div>` does not. See [semantic HTML](02-semantic-html.md).
- **Valid, well-formed documents.** A correct `<!doctype html>`, `lang`, `charset`, and
  properly nested/closed tags keep rendering predictable. See [validation](22-validation.md).
- **Accessible by default.** Every image has meaningful `alt`, every input has a `<label>`,
  and structure uses one logical heading order. See [accessibility](11-accessibility.md).
- **Separation of concerns.** HTML is content and structure; CSS is presentation; JS is
  behavior. Keep styling out of the markup and behavior out of inline handlers.
- **Progressive by construction.** The core content and actions work as plain HTML before
  any script enhances them. See [progressive enhancement](23-progressive-enhancement.md).

## Best Practices

- Start every document with `<!doctype html>`, `<html lang="…">`, `<meta charset="utf-8">`,
  and a responsive `<meta name="viewport">`. Omitting `lang` or `charset` breaks screen
  readers and character decoding respectively.
- Use one `<h1>` per page and never skip heading levels; headings are the document outline
  that assistive tech and search engines navigate by.
- Prefer native elements over ARIA re-implementations: a real `<button>` beats
  `<div role="button">` because it is focusable, keyboard-operable, and announced for free.
  ARIA is a patch, not a first choice.
- Associate every form control with a `<label for>` (or wrap it); placeholder text is not
  a label and disappears on input. See [forms](08-forms.md).
- Give every meaningful `<img>` descriptive `alt`; use `alt=""` for purely decorative
  images so screen readers skip them.
- Keep presentation in CSS: no inline `style` or layout-only wrapper `<div>`s where a
  semantic element or CSS grid would do.
- Write lowercase tags/attributes and quote all attribute values for consistency and
  diff-friendliness.

## Examples

**Good Example** — semantic, labeled, accessible

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Account settings</title>
  </head>
  <body>
    <main>
      <h1>Account settings</h1>
      <form action="/settings" method="post">
        <!-- Explicit label: clicking the text focuses the input, announced by AT -->
        <label for="email">Email</label>
        <input id="email" name="email" type="email" required />
        <!-- Native button: focusable and keyboard-operable with no extra code -->
        <button type="submit">Save</button>
      </form>
    </main>
  </body>
</html>
```

**Bad Example** — div soup, no semantics, no labels

```html
<!-- No doctype/lang/charset; div-based structure has no meaning -->
<div class="page">
  <div class="title">Account settings</div> <!-- not a heading → no outline -->
  <div class="form">
    <!-- Placeholder is not a label; vanishes on input, unreadable to AT -->
    <input placeholder="Email" />
    <!-- role/tabindex re-invents a button badly; still no Enter/Space handling -->
    <div class="btn" role="button" tabindex="0" onclick="save()">Save</div>
  </div>
</div>
```

## Common Mistakes

- Missing `<!doctype html>`, `lang`, or `charset`, causing quirks mode or garbled text.
- `<div>`/`<span>` used where `<button>`, `<nav>`, `<main>`, or `<article>` belongs.
- Multiple or skipped headings, destroying the document outline.
- Inputs without labels, or placeholder text standing in for a label.
- Inline styles and event handlers mixing presentation/behavior into markup.
- ARIA roles bolted onto generic elements instead of using the native equivalent.

## Production Tips

- Run an HTML linter and an accessibility checker (axe, Lighthouse) in CI so violations
  fail the build rather than reaching users.
- Add a `.editorconfig`/formatter (Prettier) so casing, quoting, and indentation stay
  consistent across contributors without review nitpicks.
- Periodically test with a real screen reader and keyboard-only navigation; automated
  tools catch structure, not usability.

## AI Review Checklist

- Does the document declare `<!doctype html>`, `lang`, `charset`, and a viewport meta?
- Is there exactly one `<h1>` and a heading order with no skipped levels?
- Are semantic elements used instead of generic `<div>`/`<span>` where meaning exists?
- Does every form control have an associated `<label>`, and every image an `alt`?
- Are native elements preferred over ARIA-patched generics?
- Is presentation kept in CSS and behavior out of inline handlers?

## Related

- `knowledge/html/02-semantic-html.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/22-validation.md`
- `knowledge/html/19-security.md`
- `knowledge/html/18-performance.md`
