---
id: figma/07-figma-to-html
topic: figma
slug: figma-to-html
title: "Figma to Semantic HTML"
type: doc
order: 7
status: ready
tags: [figma, figma-to-html, addToBasket, button]
related: [figma/02-layout-analysis, figma/03-design-token-extraction, html/02-semantic-html, css/17-responsive-design]
when_to_use: "Read before converting a Figma design into clean, accessible, semantic HTML markup."
---
# Figma to Semantic HTML

## Purpose

This document defines the standard process for converting a Figma design into semantic HTML.

The objective is to build clean, accessible, maintainable markup that represents the meaning of the content rather than the visual structure of the Figma layers.

Figma is a design tool.

HTML is a document structure.

They should never have a one-to-one relationship.

---

## Core Principle

Translate intent, not layers.

Every HTML element should have semantic meaning.

Never reproduce the Figma layer hierarchy directly.

---

## AI Mindset

Before writing HTML, ask:

- What is this section?
- What is the main content?
- Is this navigation?
- Is this a list?
- Is this an article?
- Is this interactive?
- Does HTML already provide a semantic element?

Choose semantics before choosing styling.

---

## HTML Planning Workflow

Every page should follow this workflow:

```
Identify Page Purpose
        ↓
Identify Landmarks
        ↓
Identify Sections
        ↓
Identify Content Hierarchy
        ↓
Identify Interactive Elements
        ↓
Choose Semantic HTML
        ↓
Apply CSS Layout
```

HTML structure should exist independently of CSS.

---

## Step 1 — Identify Page Landmarks

Every page should define its major landmarks.

Common examples:

```
<header>

<nav>

<main>

<section>

<article>

<aside>

<footer>
```

Landmarks improve accessibility and document structure.

---

## Step 2 — Build the Content Hierarchy

Content should follow a logical hierarchy.

Example:

```
main

    Hero Section

    Features Section

    Testimonials Section

    Pricing Section

    FAQ Section

    Footer
```

Do not create wrappers unless they have a clear responsibility.

---

## Step 3 — Use Semantic Elements

Prefer semantic HTML whenever possible.

Examples:

Navigation

```
<nav>
```

Page content

```
<main>
```

Standalone content

```
<article>
```

Logical grouping

```
<section>
```

Supporting content

```
<aside>
```

Footer

```
<footer>
```

Avoid replacing semantic elements with generic `<div>` elements.

---

## Step 4 — Choose the Correct Element

Examples:

Heading

```
<h1> ... <h6>
```

Paragraph

```
<p>
```

List

```
<ul>

<ol>

<li>
```

Button

```
<button>
```

Link

```
<a>
```

Image

```
<img>

<picture>
```

Form

```
<form>
```

Input

```
<input>
```

Textarea

```
<textarea>
```

Table

```
<table>
```

Use the element that best represents the content.

---

## Step 5 — Minimize Wrapper Elements

Every wrapper should have a purpose.

Valid reasons include:

- layout container;
- spacing container;
- positioning context;
- reusable component.

Avoid wrappers created only because they existed in Figma.

---

## Step 6 — Group Related Content

Example:

```
Pricing Card

    Heading

    Price

    Features

    Button
```

This should become:

```
<article>

    <h3>

    <p>

    <ul>

    <button>

</article>
```

Semantic grouping improves readability.

---

## Step 7 — Respect Heading Hierarchy

Example:

```
h1

    h2

        h3

            h4
```

Never skip heading levels without a valid reason.

Headings describe document structure rather than appearance.

---

## Step 8 — Separate Structure from Presentation

HTML defines structure.

CSS defines presentation.

Avoid writing HTML that exists only to simplify CSS.

---

## Step 9 — Accessibility

Review:

- headings;
- landmarks;
- button labels;
- form labels;
- alt text;
- keyboard navigation;
- focus order.

Semantic HTML is the foundation of accessibility.

---

## Step 10 — Review the Result

Before implementation ask:

- Can unnecessary wrappers be removed?
- Does every element have semantic meaning?
- Is the structure understandable without CSS?
- Would a screen reader understand this page?

If not, improve the markup before styling.

---

## Figma Layer vs HTML

Never map layers directly.

Poor:

```
Frame

    Group

        Rectangle

            Text

                Group

                    Frame
```

Good:

```
<section>

    <div class="container">

        <article>

            <h2>

            <p>

            <button>

        </article>

</section>
```

The HTML represents content, not editor objects.

---

## AI Execution Checklist

## Investigation

☐ Identify page landmarks.

☐ Identify semantic sections.

☐ Identify headings.

☐ Identify interactive elements.

☐ Identify reusable structures.

---

## Planning

☐ Remove unnecessary wrappers.

☐ Build semantic hierarchy.

☐ Preserve accessibility.

☐ Keep structure independent of CSS.

---

## Verification

☐ Every element has semantic meaning.

☐ Heading hierarchy is correct.

☐ Lists use list elements.

☐ Buttons use `<button>`.

☐ Navigation uses `<nav>`.

☐ Main content uses `<main>`.

☐ Wrapper count is minimized.

---

## Common Mistakes

Avoid:

Mapping every Figma Frame to a `<div>`.

Using `<div>` instead of semantic elements.

Using buttons as links.

Using links as buttons.

Skipping heading levels.

Creating unnecessary wrapper elements.

Using HTML purely for styling.

Ignoring accessibility.

---

## Examples

**Good Example** — the visual hierarchy translated into document structure

```html
<article class="product">
	<h2 class="product__title">Ceramic table lamp</h2>

	<img
		class="product__image"
		src="/images/lamp-800.webp"
		srcset="/images/lamp-400.webp 400w, /images/lamp-800.webp 800w"
		sizes="(max-width: 40rem) 100vw, 24rem"
		width="800"
		height="600"
		alt="Ceramic table lamp with a linen shade, lit, on a wooden desk"
	/>

	<p class="product__price">
		<span class="visually-hidden">Price:</span>
		<data value="89.00">£89.00</data>
	</p>

	<button class="button button--primary" type="button">Add to basket</button>
</article>
```

The heading level reflects the page outline, the image carries dimensions so nothing shifts as
it loads, and the control is a `button` — so it is focusable, operable with Enter and Space,
and announced correctly, without a single ARIA attribute.

**Bad Example** — the visual hierarchy translated into nested divs

```html
<div class="product">
	<!-- Styled to look like a heading. It is not one: it does not appear in the
	     document outline and cannot be navigated to by heading. -->
	<div class="text-xl bold">Ceramic table lamp</div>

	<!-- No dimensions: the page reflows when the image loads.
	     No alt: a screen reader announces the file name, or nothing. -->
	<img src="/images/lamp.png" />

	<div class="price">£89.00</div>

	<!-- A div with a click handler: not focusable, not keyboard-operable, and
	     announced as plain text. The role and tabindex bolted on afterwards
	     still do not give it Enter/Space handling. -->
	<div class="button button--primary" onclick="addToBasket()">Add to basket</div>
</div>
```

---

## Completion Criteria

Semantic HTML is complete when:

- the document structure is meaningful;
- landmarks are present;
- headings are correctly organized;
- wrapper elements are minimized;
- accessibility has been considered;
- the markup remains readable without CSS.

---

## Summary

Great frontend development begins with excellent HTML.

Semantic markup creates a solid foundation for accessibility, maintainability, SEO, and responsive layouts.

The best implementations translate the meaning of a design—not its layer structure.

## Related

- `knowledge/figma/02-layout-analysis.md`
- `knowledge/figma/03-design-token-extraction.md`
- `knowledge/html/02-semantic-html.md`
- `knowledge/css/17-responsive-design.md`
