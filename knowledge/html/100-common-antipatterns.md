---
id: html/100-common-antipatterns
topic: html
slug: common-antipatterns
title: "HTML Common Antipatterns"
type: antipatterns
order: 100
status: ready
tags: [html, common-antipatterns, deleteItem, window.opener, placeholder, save, getElementById]
related: [html/30-engineering-principles, html/02-semantic-html, html/11-accessibility, html/08-forms, html/99-ai-review-checklist]
when_to_use: "Read when writing or reviewing HTML, to recognize and reject the recurring mistakes that pass visual review but break real users."
---
# HTML Common Antipatterns

## Purpose

This document catalogs the HTML mistakes that appear most often in generated and
hand-written markup. Each entry names the antipattern, explains *why it is wrong* in
concrete terms, and gives *the fix*. Use it as a rejection list: if you see one of these,
change it.

## Why It Matters

These antipatterns share one trait — they render correctly for a sighted mouse user, so
they survive casual review and reach production. There they exclude keyboard and
screen-reader users, break search and social previews, and force fragile JavaScript to
patch what the browser would have done natively. Naming them makes them catchable.

## Antipatterns

### 1. Div-as-button

```html
<div class="btn" onclick="save()">Save</div>   <!-- not focusable, no role, no Enter/Space -->
```

- **Why it is wrong:** A `<div>` is not focusable, exposes no button role to assistive
  technology, and does not respond to Enter/Space. Keyboard users cannot activate it.
- **The fix:** Use `<button type="button" onclick="save()">Save</button>`. It ships with
  focus, keyboard handling, and the correct role.

### 2. Headings chosen for size

```html
<h3>Page Title</h3>   <!-- used because h3 "looks the right size" -->
```

- **Why it is wrong:** Heading level defines the document outline that screen readers and
  crawlers navigate by. Picking a level for its font size corrupts that structure.
- **The fix:** Choose the level by hierarchy (`<h1>` for the page title, then descend
  without skipping) and set the visual size in CSS.

### 3. Missing or misused `alt`

```html
<img src="chart.png">                     <!-- no alt: unusable to screen readers -->
<img src="divider.png" alt="divider.png"> <!-- filename is noise, not information -->
```

- **Why it is wrong:** Without `alt`, screen readers announce a filename or nothing.
  Meaningless `alt` on decorative images adds noise.
- **The fix:** Give informative images a description of their meaning; give purely
  decorative images `alt=""` so they are skipped.

### 4. Unlabeled form controls

```html
<input type="text" placeholder="Email">   <!-- placeholder is not a label -->
```

- **Why it is wrong:** A `placeholder` disappears on input and is not reliably announced
  as a name. Users lose the field's identity and screen readers may skip it.
- **The fix:** Add `<label for="email">Email</label>` bound to the input's `id`. Keep the
  placeholder only as an example, if at all.

### 5. Links and buttons swapped

```html
<a href="#" onclick="deleteItem()">Delete</a>   <!-- action dressed as navigation -->
```

- **Why it is wrong:** `<a href="#">` implies navigation, adds a bogus history entry, and
  breaks on middle-click/open-in-new-tab. Actions belong to buttons.
- **The fix:** Use `<button type="button" onclick="deleteItem()">Delete</button>`.
  Reserve `<a href>` for real destinations.

### 6. Div soup / non-semantic layout

```html
<div class="header"><div class="nav">…</div></div>
<div class="content">…</div>
```

- **Why it is wrong:** Generic wrappers carry no meaning, so assistive tech and crawlers
  see no landmarks, and the DOM grows deep and slow.
- **The fix:** Use `<header>`, `<nav>`, `<main>`, `<article>`, `<footer>`. Reserve
  `<div>` for grouping that has no semantic name.

### 7. Deprecated presentational markup

```html
<center><font color="red" size="5">Sale</font></center>   <!-- obsolete elements -->
```

- **Why it is wrong:** These elements are obsolete, mix presentation into structure, and
  are not guaranteed to work. They signal legacy, unmaintainable markup.
- **The fix:** Use semantic elements plus CSS: `<p class="promo">Sale</p>` styled in a
  stylesheet.

### 8. Duplicate `id` values

```html
<label for="name">…</label>
<input id="name"><input id="name">   <!-- two elements, same id -->
```

- **Why it is wrong:** `id` must be unique. Duplicates break label association, in-page
  anchors, and `getElementById`, which returns only the first match.
- **The fix:** Give each element a unique `id`; use `class` for shared styling hooks.

### 9. Unsafe `target="_blank"`

```html
<a href="https://x.com" target="_blank">Open</a>   <!-- new tab can control opener -->
```

- **Why it is wrong:** Without `rel="noopener"`, the opened page can access `window.opener`
  and redirect the original tab (reverse tabnabbing).
- **The fix:** Add `rel="noopener"` (or `noopener noreferrer`) to every cross-origin
  `target="_blank"` link.

### 10. Structure supplied by JavaScript

```html
<div id="app"></div>   <!-- empty; all content injected client-side -->
```

- **Why it is wrong:** If the script fails, is blocked, or is slow, the page is empty for
  users and crawlers. Accessibility and SEO depend on JS execution.
- **The fix:** Render meaningful HTML on the server (or as static markup) and use
  JavaScript to *enhance* it, not to create it from nothing.

## AI Review Checklist

- [ ] Are all clickable elements native `<button>`/`<a>` rather than `<div>`/`<span>`?
- [ ] Are headings, landmarks, and `alt` text chosen for meaning, not appearance?
- [ ] Does every form control have a real `<label>`?
- [ ] Are there no deprecated elements, duplicate `id`s, or unsafe `target="_blank"`?
- [ ] Does meaningful content exist in the HTML without JavaScript?

## Related

- `knowledge/html/30-engineering-principles.md`
- `knowledge/html/02-semantic-html.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/08-forms.md`
- `knowledge/html/99-ai-review-checklist.md`
