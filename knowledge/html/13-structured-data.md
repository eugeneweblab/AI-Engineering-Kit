---
id: html/13-structured-data
topic: html
slug: structured-data
title: "Structured Data"
type: doc
order: 13
status: ready
tags: [html, structured-data]
related: [html/12-seo, html/26-microdata, html/10-metadata, html/02-semantic-html]
when_to_use: "Read before adding Schema.org / JSON-LD markup to make a page eligible for rich results."
---
# Structured Data

## Purpose

This document defines how to add machine-readable meaning to a page using
[Schema.org](https://schema.org) vocabulary — so search engines can render rich
results (star ratings, breadcrumbs, FAQs, events, products) and other agents can
extract facts reliably. It focuses on **JSON-LD**, the format Google recommends and
the one an agent should emit by default.

Structured data is a parallel description of what the page *is*: this is an Article by
this author, published on this date; this is a Product priced at this amount. It is
distinct from [SEO](12-seo.md) titles and from inline [microdata](26-microdata.md),
which annotates existing HTML rather than adding a separate JSON block.

## Why It Matters

Rich results earn more clicks and take more space in the results page, but they are
*earned*, not requested — the engine grants them only when the markup is valid and
matches the visible page. Structured data fails in two silent ways: markup that is
syntactically broken is ignored entirely, and markup that describes content the user
cannot see is a guidelines violation that can trigger a manual penalty. Both look fine
in the browser. Because the reward is conditional and the failure is invisible, the
markup must be exact and honest.

## Core Principles

- **Prefer JSON-LD.** A single `<script type="application/ld+json">` block keeps the
  data separate from presentation, is easy to generate server-side, and is Google's
  recommended format. Microdata/RDFa are valid but couple data to markup.
- **Mark up only what is visible.** Structured data must describe content actually on
  the page. Marking up hidden or fabricated data violates the guidelines.
- **Use the right type and required properties.** Each rich-result type has required
  and recommended fields. Missing a required field makes the page ineligible.
- **Keep data and page in sync.** A price, rating, or date in the JSON-LD must match
  what the user sees; drift causes the rich result to be dropped.
- **Validate before shipping.** Structured data has no browser feedback loop — a typo
  fails silently, so validation is mandatory, not optional.

## Best Practices

- Emit JSON-LD in a `<script type="application/ld+json">` tag, ideally in `<head>` or
  at the end of `<body>`. Serialize it server-side from the same data the page renders.
- Always include `@context` (`https://schema.org`) and a specific `@type`
  (`Article`, `Product`, `FAQPage`, `BreadcrumbList`, `Organization`, `Event`).
- Provide every *required* property for the target rich result; add recommended ones
  where you have honest data. Check the type's requirements before shipping.
- Use absolute URLs for `url`, `image`, and `@id`. Relative URLs are unreliable for
  crawlers processing the JSON out of page context.
- Reference entities with `@id` so an `Article` can point to its `author`
  `Organization` without duplicating it.
- Escape correctly: the JSON-LD block is JSON, so any user-supplied string must be JSON-
  encoded to avoid breaking the script or injecting markup.
- Validate every template against the [Schema.org validator](https://validator.schema.org)
  and Google's Rich Results Test before merging.

## Examples

**Good Example** — valid Article JSON-LD matching the visible page

```html
<article>
  <h1>Argon2 vs bcrypt</h1>
  <p>By Jane Doe · Published 2026-05-01</p>
</article>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Argon2 vs bcrypt",          // matches the visible <h1>
  "datePublished": "2026-05-01",           // matches the visible date, ISO 8601
  "author": {
    "@type": "Person",
    "name": "Jane Doe"                      // matches the visible byline
  },
  "image": "https://example.com/img/cover.png",  // absolute URL
  "publisher": {
    "@type": "Organization",
    "name": "Example",
    "logo": { "@type": "ImageObject", "url": "https://example.com/logo.png" }
  }
}
</script>
```

**Bad Example** — invalid, dishonest, and unsafe

```html
<script type="application/ld+json">
{
  "@type": "Product",                       // missing @context → ignored entirely
  "name": "Widget",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "5.0", "reviewCount": "999"  // no reviews shown → guidelines violation
  },
  "description": "Great <b>widget</b> " + userInput  // unescaped input can break/inject
}
</script>
<!-- datePublished, image and required fields absent → not eligible for rich result -->
```

## Common Mistakes

- Omitting `@context` or using a vague `@type`, so the block is silently ignored.
- Marking up ratings, prices, or FAQs that do not appear on the page (a violation).
- Leaving out a required property, quietly disqualifying the page from rich results.
- Using relative URLs for `image`/`url`, which crawlers may fail to resolve.
- Injecting unescaped user content into the JSON block, breaking parsing or the page.
- Letting JSON-LD data drift out of sync with the rendered price/date/rating.
- Shipping without running a validator, so a single typo kills the whole block.

## Production Tips

- Generate JSON-LD from the same server-side model that renders the HTML, so the two
  cannot diverge. Never hand-maintain a second copy of the data.
- Add a CI check that runs the Rich Results Test (or a schema validator) against key
  templates and fails the build on errors.
- Monitor the "Enhancements" reports in Search Console for structured-data errors after
  deploys — they surface issues the browser never shows.

## AI Review Checklist

- Is the markup JSON-LD in a `<script type="application/ld+json">` block?
- Does it include `@context: https://schema.org` and a specific `@type`?
- Are all *required* properties for the target rich-result type present?
- Does every marked-up value match content actually visible on the page?
- Are `url`/`image`/`@id` absolute URLs?
- Is all user-supplied data JSON-encoded so it cannot break or inject into the block?
- Has the markup passed a schema validator / Rich Results Test?

## Related

- `knowledge/html/12-seo.md`
- `knowledge/html/26-microdata.md`
- `knowledge/html/10-metadata.md`
- `knowledge/html/02-semantic-html.md`
