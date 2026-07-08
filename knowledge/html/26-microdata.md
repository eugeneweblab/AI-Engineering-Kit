---
id: html/26-microdata
topic: html
slug: microdata
title: "Microdata"
type: doc
order: 26
status: ready
tags: [html, microdata]
related: [html/13-structured-data, html/12-seo, html/14-custom-data-attributes, html/02-semantic-html]
when_to_use: "Read before annotating page content with inline schema.org markup for search engines."
---
# Microdata

## Purpose

This document defines how to embed machine-readable meaning directly in HTML using the
Microdata attributes `itemscope`, `itemtype`, `itemprop`, and `itemref`. Microdata lets
you attach [schema.org](https://schema.org) types (Product, Article, Event, Recipe) to
the same DOM nodes a human reads, so search engines can build rich results without a
separate data feed. This complements — and is often superseded by — JSON-LD, covered in
[structured data](13-structured-data.md).

## Why It Matters

Structured data is how a page earns rich results: star ratings, prices, FAQ accordions,
and event dates in search listings. Microdata's distinction is that the annotations live
*on the visible content itself*, so the markup and the data cannot drift apart — the
price Google reads is the price the user sees. That property matters because Google
penalizes structured data that misrepresents on-page content. Get the vocabulary and
nesting right and you gain visibility; get it wrong and you emit invalid data that is
silently ignored or flagged.

## Core Principles

- **`itemscope` creates an item; `itemtype` names its type.** Put both on the element
  that wraps the thing you are describing, with a full schema.org URL as the type.
- **`itemprop` binds a property to its value.** The value comes from the element's text,
  or from a type-specific attribute (`href` on `<a>`, `src` on `<img>`,
  `content` on `<meta>`, `datetime` on `<time>`).
- **Nest scopes to nest objects.** A property whose value is itself an item gets its own
  `itemscope`/`itemtype`, producing a tree that mirrors the schema.
- **Annotate what is on the page, not a parallel truth.** Markup must describe visible
  content; hidden or contradictory data violates search-engine policy.
- **Match required properties for the target rich result.** Each rich-result type has a
  required-property list; missing ones mean no enhancement.

## Best Practices

- Use the canonical `https://schema.org/Type` URL for `itemtype` and the exact
  property names from that type's page — casing and spelling are significant.
- Carry non-visible-but-necessary values (ISO dates, currency codes, ratings) on
  `<meta itemprop="..." content="...">` or `<time datetime>` rather than inventing text.
- Reuse elements you already have: put `itemprop="name"` on the existing `<h1>`, not a
  duplicate hidden node.
- Use `itemref` to include properties that live outside the item's DOM subtree when your
  layout can't wrap them together.
- Validate with Google's Rich Results Test and the Schema Markup Validator before
  shipping; treat warnings as bugs.
- Prefer JSON-LD (see structured data) for complex or duplicated graphs; reach for
  Microdata when the data maps cleanly onto existing visible elements.

## Examples

**Good Example** — Product with nested Offer, values bound to real content

```html
<!-- itemscope opens the item; itemtype names it with a full schema.org URL -->
<div itemscope itemtype="https://schema.org/Product">
  <!-- itemprop reuses the visible heading as the product name -->
  <h1 itemprop="name">Trail Runner 3</h1>
  <img itemprop="image" src="/shoe.jpg" alt="Trail Runner 3">

  <!-- a nested itemscope: the offer is its own object -->
  <div itemprop="offers" itemscope itemtype="https://schema.org/Offer">
    <!-- <meta> carries the machine value; the visible text stays human ($129.00) -->
    <meta itemprop="priceCurrency" content="USD">
    <span itemprop="price" content="129.00">$129.00</span>
    <link itemprop="availability" href="https://schema.org/InStock">In stock
  </div>
</div>
```

**Bad Example** — wrong types, hidden mismatched data, string where a scope is needed

```html
<!-- "product" is not a valid type; the URL must be canonical schema.org casing -->
<div itemscope itemtype="http://schema.org/product">
  <h1 itemprop="title">Trail Runner 3</h1> <!-- "title" is not a Product property -->

  <!-- hidden price that contradicts the visible one: a policy violation -->
  <span itemprop="price">129.00</span>
  <p>Now only $89!</p>

  <!-- offers must be a nested item, not a bare string -->
  <span itemprop="offers">available</span>
</div>
```

## Common Mistakes

- Misspelling the type or property, or using non-canonical `itemtype` URLs — the item is
  discarded as invalid.
- Putting a value string where a nested `itemscope` (an object) is required, or vice versa.
- Marking up data that is hidden or differs from the visible page, risking a penalty.
- Omitting required properties for the rich-result type, so no enhancement appears.
- Using `content`/`datetime` attributes with the wrong element (e.g. `content` on a
  `<span>` that has no such native attribute — use `<meta>`).
- Duplicating the same entity in both Microdata and conflicting JSON-LD.

## Production Tips

- Wire the Rich Results Test into a pre-deploy check for templates that render structured
  data; catching a broken template stops thousands of bad pages.
- Keep the schema mapping close to the template so a content change updates the markup and
  the data together.
- Monitor Google Search Console's structured-data reports for errors after launch — rich
  results can be revoked when validation regresses.

## AI Review Checklist

- Do `itemscope` elements carry a canonical `https://schema.org/Type` `itemtype`?
- Are `itemprop` names the exact properties defined by that type?
- Are nested objects expressed as nested `itemscope`s, not strings?
- Do machine values use `<meta content>`/`<time datetime>`/`href` appropriately?
- Does the marked-up data match the visible on-page content (no hidden mismatch)?
- Are the required properties for the intended rich result all present?
- Has the page passed the Rich Results Test / Schema Markup Validator?

## Related

- `knowledge/html/13-structured-data.md`
- `knowledge/html/12-seo.md`
- `knowledge/html/14-custom-data-attributes.md`
- `knowledge/html/02-semantic-html.md`
