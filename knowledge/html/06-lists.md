---
id: html/06-lists
topic: html
slug: lists
title: "Lists"
type: doc
order: 6
status: ready
tags: [html, lists]
related: [html/02-semantic-html, html/03-text-elements, html/11-accessibility, html/04-links]
when_to_use: "Read before marking up any sequence, menu, navigation set, or key-value pairs."
---
# Lists

## Purpose

This document defines how to mark up groups of related items using `<ul>`, `<ol>`,
and `<dl>`. A list is the correct element whenever content is a *set of items* —
navigation links, steps, tags, definitions — not just visually stacked text. Picking
the right list type gives assistive technology an accurate count and structure for free.

## Why It Matters

Screen readers announce lists explicitly: *"list, 5 items"*. That count lets a blind
user decide whether to dive in or skip. Faking a list with `<div>`s and bullet
characters destroys that affordance — the user hears an undifferentiated wall of text.
Lists also carry semantics search engines and reader modes rely on. The wrong element
is not a cosmetic issue; it is missing information for every non-visual consumer.

## Core Principles

- **Ordered vs unordered is about meaning, not styling.** Use `<ol>` when sequence
  matters (steps, rankings, legal clauses); use `<ul>` when order is irrelevant (tags,
  features). Do not choose based on whether you want numbers — style with CSS.
- **List children must be `<li>` only.** A `<ul>`/`<ol>` may contain only `<li>`
  (plus script-supporting elements). Any other direct child is invalid and breaks the
  accessibility tree.
- **Definition lists pair terms with descriptions.** `<dl>` is for name/value groups:
  glossaries, metadata, key-value displays — not for generic two-column layout.
- **Nest lists inside the parent `<li>`,** never between `<li>` elements. The sublist
  belongs to the item it elaborates.
- **Navigation is a list of links.** Wrap nav links in a `<ul>` inside `<nav>`; the
  count and structure help keyboard and screen-reader users.

## Best Practices

- Use `<ol>` attributes instead of faking them: `start` to begin at a number,
  `reversed` for countdowns, and `value` on an `<li>` to override a single number.
- Style bullets and numbers with CSS (`list-style`, `::marker`) rather than typing
  literal `•` or `1.` into the text — literal markers get read aloud and misalign.
- In a `<dl>`, group one or more `<dt>` (term) with one or more `<dd>` (description).
  Multiple `<dd>` per `<dt>` is valid when a term has several values.
- Keep `list-style: none` intentional: removing markers on Safari can strip list
  semantics from VoiceOver — add `role="list"` back when you zero out the style.
- Reserve `<menu>` for toolbars/command lists; for ordinary content prefer `<ul>`.

## Examples

**Good Example** — semantic list, CSS-driven markers, correct nesting

```html
<!-- Order matters, so <ol>; the sublist lives inside its parent <li> -->
<ol>
  <li>Preheat the oven to 220 C.</li>
  <li>
    Prepare the base:
    <ul> <!-- unordered: these sub-steps have no required order -->
      <li>Knead the dough</li>
      <li>Rest for 20 minutes</li>
    </ul>
  </li>
  <li>Bake for 12 minutes.</li>
</ol>

<!-- Name/value pairs belong in a definition list -->
<dl>
  <dt>HTTP</dt>
  <dd>Hypertext Transfer Protocol</dd>
</dl>
```

**Bad Example** — fake list loses count and structure

```html
<!-- Divs with literal bullets: screen readers hear no list, no item count.
     The "•" is read aloud as "bullet" and cannot be restyled per locale. -->
<div class="list">
  <div>• Knead the dough</div>
  <div>• Rest for 20 minutes</div>
</div>

<!-- Invalid: text and <span> are not allowed as direct children of <ul> -->
<ul>
  Ingredients:
  <span>Flour</span>
  <li>Water</li>
</ul>
```

## Common Mistakes

- Using `<ul>` for numbered steps (or `<ol>` for an unordered tag set) because of how
  it *looks* rather than what it *means*.
- Putting non-`<li>` elements as direct children of `<ul>`/`<ol>`, breaking validation
  and the a11y tree.
- Typing literal `•`, `-`, or `1.` characters instead of using real list elements.
- Removing markers with `list-style: none` and unintentionally stripping list
  semantics in some screen readers.
- Abusing `<dl>` as a generic grid layout instead of true term/description pairs.
- Nesting a sublist between `<li>` siblings instead of inside the owning `<li>`.

## AI Review Checklist

- Is every visually-listed group a real `<ul>`, `<ol>`, or `<dl>`?
- Does `<ol>` vs `<ul>` reflect whether sequence carries meaning?
- Are all direct children of a list `<li>` (or `<dt>`/`<dd>` for `<dl>`)?
- Are markers produced by CSS, not literal characters in the text?
- Are nested lists placed inside the parent `<li>`?
- Where `list-style: none` is used, is list semantics preserved (e.g. `role="list"`)?
- Are navigation links wrapped in a list inside `<nav>`?

## Related

- `knowledge/html/02-semantic-html.md`
- `knowledge/html/03-text-elements.md`
- `knowledge/html/04-links.md`
- `knowledge/html/11-accessibility.md`
