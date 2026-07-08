---
id: html/03-text-elements
topic: html
slug: text-elements
title: "Text Elements"
type: doc
order: 3
status: ready
tags: [html, text-elements]
related: [html/02-semantic-html, html/04-links, html/06-lists, html/11-accessibility]
when_to_use: "Read before marking up paragraphs, headings, emphasis, quotes, or inline text content."
---
# Text Elements

## Purpose

This document defines how to mark up prose: headings, paragraphs, emphasis, quotations,
code, abbreviations, and other inline and block text elements. It is written so an agent
picks the element that carries the correct *meaning* — because for text, the element name
is the semantics, and screen readers change their delivery based on it.

This builds on [semantic HTML](02-semantic-html.md): the same "meaning over appearance"
rule, applied to the elements that hold words.

## Why It Matters

Text elements are where the "just use CSS" temptation is strongest and most damaging.
Bolding a word with `<b>` versus `<strong>` looks identical, but only `<strong>` tells a
screen reader to add vocal stress. `<i>` and `<em>` render the same slant; only `<em>`
signals emphasis. A `<blockquote>` is exposed as a quotation landmark; a styled `<div>` is
just text. These distinctions are invisible on screen and decisive for anyone not looking
at the screen — and for search engines weighing which words matter. Choosing the meaningful
element costs nothing and is impossible to retrofit reliably later.

## Core Principles

- **Semantic vs. presentational pairs are not interchangeable.** `<strong>` (importance) and
  `<em>` (emphasis) carry meaning; `<b>` and `<i>` are stylistic with no emphasis. Default to
  the semantic member.
- **Headings rank content, they do not size it.** `<h1>`–`<h6>` express hierarchy; use CSS
  for size. Never pick a heading level for its default font.
- **Paragraphs hold flow text.** Wrap prose in `<p>`; never use `<br>` to fake paragraph
  gaps or `<div>` for a line of text.
- **Mark the meaning of special text.** `<code>`, `<time>`, `<abbr>`, `<mark>`, `<q>`,
  `<blockquote>`, `<cite>`, `<kbd>`, `<sub>`/`<sup>` each say something specific — use them.
- **Never carry meaning in whitespace or line breaks alone.** HTML collapses whitespace;
  structure must come from elements.

## Best Practices

- Use `<strong>` for content that is important/urgent, `<em>` for stress emphasis. Reserve
  `<b>` (keywords, product names) and `<i>` (foreign phrases, technical terms) for the rare
  stylistic-only case where no emphasis is meant.
- Use `<blockquote>` for block quotations and `<q>` for inline ones (the browser adds
  quotation marks); attribute the source with `<cite>`.
- Wrap machine-readable dates and times in `<time datetime="…">` so tooling can parse them.
- Wrap code in `<code>`; for multi-line code use `<pre><code>` to preserve whitespace.
- Use `<abbr title="…">` for abbreviations whose expansion aids understanding, and `<kbd>`
  for keyboard input.
- Use `<br>` only for line breaks that are part of the content itself (addresses, poems),
  never for spacing — that is CSS `margin`.

## Examples

**Good Example** — meaning encoded in the elements

```html
<h2>Release notes</h2>
<p>
  This build is <strong>a required security update</strong>.  <!-- importance, vocalized -->
  Install it before <time datetime="2026-07-14">July 14</time>. <!-- machine-readable date -->
</p>
<blockquote cite="https://example.com/advisory">
  <p>Affected versions must be patched immediately.</p>
</blockquote>
<p>Run <kbd>npm audit fix</kbd>, then restart with <code>npm start</code>.</p>
```

**Bad Example** — presentation standing in for meaning

```html
<div class="h2">Release notes</div>          <!-- not a heading: absent from outline -->
<div class="p">
  This build is <b>a required security update</b>. <!-- <b> = no emphasis conveyed -->
  Install it before Jul 14.<br><br>            <!-- <br><br> faking a paragraph gap -->
</div>
<div class="quote">
  "Affected versions must be patched immediately."  <!-- not exposed as a quotation -->
</div>
<div>Run <span class="mono">npm audit fix</span>.</div> <!-- not marked as code -->
```

## Common Mistakes

- Using `<b>`/`<i>` where `<strong>`/`<em>` are meant, dropping emphasis for screen readers.
- Building headings out of styled `<div>`s, so they never appear in the document outline.
- Using `<br><br>` or empty `<p>` for vertical spacing instead of CSS margins.
- Wrapping code in a styled `<span>` instead of `<code>`, losing the semantic and monospace default.
- Writing human-only dates with no `<time datetime>`, so they cannot be parsed or localized.
- Relying on collapsed whitespace or indentation to imply structure.

## Production Tips

- For long-form content, keep the heading hierarchy shallow and logical; an editor or CMS
  that lets authors pick heading *sizes* will produce broken outlines — constrain it to
  levels.
- Prefer real typographic characters or CSS for quotation marks over hardcoding `"`; `<q>`
  and `<blockquote>` let the browser localize them by `lang`.

## AI Review Checklist

- Are `<strong>`/`<em>` used for meaning, with `<b>`/`<i>` limited to non-emphatic styling?
- Do headings use `<h1>`–`<h6>` by rank, never chosen for font size?
- Is all flow text in `<p>`, with no `<br>` used for spacing?
- Are dates/times wrapped in `<time datetime>` and code in `<code>`/`<pre>`?
- Are quotations marked with `<blockquote>`/`<q>` and attributed with `<cite>`?

## Related

- `knowledge/html/02-semantic-html.md`
- `knowledge/html/04-links.md`
- `knowledge/html/06-lists.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/12-seo.md`
