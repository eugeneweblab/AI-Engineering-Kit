---
id: seo/09-structured-data
topic: seo
slug: structured-data
title: "SEO Structured Data"
type: doc
order: 9
status: ready
tags: [seo, structured-data, "@type", "@context", InStock, Organization, LocalBusiness, Article]
related: [seo/05-metadata, seo/10-open-graph, seo/03-indexing, seo/25-content-quality]
when_to_use: "Read before adding schema.org / JSON-LD markup for rich results (products, articles, FAQs, breadcrumbs, reviews)."
---
# SEO Structured Data

## Purpose

This document defines how to add structured data — machine-readable descriptions of a
page's content using the schema.org vocabulary — so search engines can understand entities
and render rich results. It is written so an agent can emit valid, eligible markup without
triggering a manual spam penalty.

Structured data answers "what *is* this page, in a machine's terms?": this is a Product
with this price and rating; this is a Recipe with these steps; this is an Article by this
author. Correct markup can earn rich results (stars, prices, FAQ dropdowns) that raise
click-through — but only when the markup faithfully mirrors what a user sees.

## Why It Matters

Search results are increasingly composed of rich elements, not just blue links. Structured
data is how you become eligible for them. It also feeds knowledge panels, voice answers,
and AI overviews that read entities rather than prose. But eligibility is conditional and
strictly policed: markup that describes content not visible on the page, or that inflates
ratings, is treated as spam and can trigger a manual action that removes *all* rich results
for the site. So the payoff is real but the downside — a sitewide penalty — is severe.

## Core Principles

- **Use JSON-LD.** Google recommends it; it lives in a single `<script>` block, decoupled
  from your HTML, so it is easy to generate, test, and keep correct. Prefer it over
  Microdata/RDFa.
- **Markup must match visible content.** Never mark up prices, reviews, or text the user
  cannot see on the page. This is the single most-enforced structured-data rule.
- **Follow Google's required/recommended properties, not just schema.org.** schema.org
  permits far more than Google uses. Rich-result *eligibility* has its own required fields;
  omit a required one and you get nothing.
- **One accurate type beats many speculative ones.** Mark up the page's real primary
  entity. Stacking unrelated types to "cover bases" invites errors and distrust.
- **Structured data is not a ranking boost by itself.** It earns presentation features and
  understanding; it does not directly move rankings. Do not add it expecting position gains.

## Best Practices

- Emit JSON-LD in `<head>` or `<body>` as `<script type="application/ld+json">`. Generate
  it from the same data that renders the page so the two cannot diverge.
- Populate every property Google marks **required** for the target rich result; add
  recommended ones for better coverage. Check the type's reference page, not just
  schema.org.
- Set `@id` and cross-reference entities (an `Article` whose `author` `@id` resolves to a
  `Person`) to build a connected graph the engine can trust.
- Escape user content and validate types (numbers as numbers, ISO 8601 dates) — malformed
  JSON-LD is silently dropped.
- Only mark up review/rating data that a real user left and can see on the page; never
  self-serving `aggregateRating` on your own organization.
- Validate with the Rich Results Test and Schema Markup Validator on every template change,
  and monitor the Search Console "Enhancements" reports for errors in production.

## Examples

**Good Example** — one accurate type, required fields, mirrors the page

```html
<!-- Product page: price, availability, and rating all match what the user sees. -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Trail Runner 3",
  "image": "https://example.com/img/trail-runner-3.jpg",
  "description": "Lightweight trail shoe with a 6mm drop.",
  "sku": "TR3-42",
  "offers": {
    "@type": "Offer",
    "price": "129.00",          // string per Google's Offer spec
    "priceCurrency": "USD",     // required for the price rich result
    "availability": "https://schema.org/InStock"
  },
  "aggregateRating": {          // ONLY because real reviews render on this page
    "@type": "AggregateRating",
    "ratingValue": "4.6",
    "reviewCount": "212"
  }
}
</script>
```

**Bad Example** — invented ratings, wrong types, content not on the page

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Trail Runner 3",
  "offers": {
    "@type": "Offer",
    "price": 129,               // number, not string, and no priceCurrency → dropped
    "availability": "InStock"   // bare value, not a schema.org URL → invalid
  },
  "aggregateRating": {
    "ratingValue": "5.0",       // no reviews exist on the page → spam / manual action
    "reviewCount": "9999"
  }
}
</script>
```

## Common Mistakes

- Marking up ratings, prices, or FAQ text that does not appear in the visible page — the
  top cause of manual actions.
- Self-serving `aggregateRating` or `review` on your own `Organization`/`LocalBusiness`,
  which is disallowed.
- Meeting schema.org's loose rules but missing a Google **required** property, so no rich
  result appears at all.
- Wrong value types (unquoted numbers where strings are required, non-ISO dates), causing
  silent drops.
- Duplicating or contradicting the same entity across multiple blocks on one page.
- Adding markup and assuming it lifts rankings; it only affects eligibility and
  understanding.

## Production Tips

- Centralize JSON-LD generation in a typed helper per template so required fields cannot be
  forgotten and values stay in sync with the rendered page.
- Watch the Search Console Enhancements reports; a spike in "invalid" items after a deploy
  usually means a template changed a field's type.
- Rich-result eligibility rules change; re-validate templates against the current Rich
  Results Test periodically rather than trusting old markup.

## AI Review Checklist

- Is the markup JSON-LD, generated from the same data that renders the page?
- Does every marked-up value (price, rating, text, dates) appear in the visible content?
- Are all of Google's *required* properties present for the target rich result?
- Are value types correct (strings/numbers/ISO dates) and enum values full schema.org URLs?
- Is there no self-serving or fabricated review/rating data?
- Was the template validated with the Rich Results Test before shipping?

## Related

- `knowledge/seo/05-metadata.md`
- `knowledge/seo/10-open-graph.md`
- `knowledge/seo/03-indexing.md`
- `knowledge/seo/25-content-quality.md`
