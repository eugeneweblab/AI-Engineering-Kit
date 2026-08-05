---
id: seo/15-local-seo
topic: seo
slug: local-seo
title: "Local SEO"
type: doc
order: 15
status: ready
tags: [seo, local-seo, "@type", LocalBusiness, "@context"]
related: [seo/09-structured-data, seo/14-international-seo, seo/05-metadata, seo/25-content-quality, seo/07-sitemaps]
when_to_use: "Read before building store locators, location pages, or any site whose customers search 'near me' with local intent."
---
# Local SEO

## Purpose

This document defines the technical work that makes a business rank for local, intent-rich
queries ("plumber near me", "coffee shop open now") and appear in the map pack. It covers
`LocalBusiness` structured data, NAP consistency, location-page architecture, and the
signals that tie a URL to a physical place. It is the engineer's half of local SEO — the
markup and site structure — not the marketing half (reviews, listings management).

Local SEO leans heavily on [Structured Data](09-structured-data.md): the machine-readable
facts about where a business is, when it is open, and what it offers are what feed the map
pack and rich results.

## Why It Matters

Local searches convert: a large share of "near me" searches lead to a visit or call the
same day, and the map pack sits above the classic organic results. But local ranking runs
on data an engineer must emit correctly — a business's name, address, and phone (NAP),
hours, and coordinates. If your site's NAP disagrees with your Google Business Profile or
lists the wrong hours, the engine loses confidence and drops you from the pack, silently.
Multi-location businesses fail differently: one shared page for fifty stores gives the
engine no distinct URL to rank per city. These are structural bugs — wrong markup, thin
pages, inconsistent data — that cost foot traffic without any error in the logs.

## Core Principles

- **NAP must be identical everywhere.** Name, address, and phone must match exactly —
  character for character — across the site, structured data, and external listings.
  "St." vs "Street" or a formatted vs unformatted phone number reads as two businesses.
- **One indexable page per location.** Each physical location gets its own crawlable URL
  with unique, substantive content (address, hours, services, local context) — not one
  page with a store-picker dropdown.
- **Mark it up with `LocalBusiness` schema.** Emit valid JSON-LD with the correct
  subtype (`Restaurant`, `Dentist`, …), `address`, `geo`, `openingHoursSpecification`,
  and `telephone`. This is what powers rich results and reinforces the map pack.
- **The site supports, the profile ranks.** The Google Business Profile is the primary
  local ranking entity; your site's job is to corroborate it with consistent, structured,
  crawlable data.
- **Local pages are still pages.** They must satisfy [Content Quality](25-content-quality.md)
  — thin, templated, near-duplicate location pages get filtered, not ranked.

## Best Practices

- Give each location a stable URL under a clear path (`/locations/austin-tx/`), listed in
  the [sitemap](07-sitemaps.md) and linked from a crawlable locations index.
- Put NAP in the page as real HTML text (not baked into an image) and mirror it exactly
  in `LocalBusiness` JSON-LD.
- Use `openingHoursSpecification` for regular hours and mark special/holiday hours; stale
  hours are a top cause of lost trust and bad reviews.
- Include `geo` coordinates and a valid `PostalAddress`; embed a map, but do not rely on
  the embed alone for the address data.
- Localize each page's [metadata](05-metadata.md): title and description should name the
  city/neighborhood the page targets.
- Write genuinely location-specific content per page (parking, neighborhood, local
  services). Reusing one paragraph across every city is thin content.
- For businesses serving an area without a storefront, use `areaServed` and set the
  service area rather than a fake street address.

## Examples

**Good Example** — valid LocalBusiness JSON-LD, consistent NAP

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Restaurant",
  "name": "Blue Fig Cafe",                       // EXACTLY matches on-page + GBP
  "telephone": "+1-512-555-0142",                // same format everywhere
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "412 W 6th Street",
    "addressLocality": "Austin",
    "addressRegion": "TX",
    "postalCode": "78701",
    "addressCountry": "US"
  },
  "geo": { "@type": "GeoCoordinates", "latitude": 30.2685, "longitude": -97.7469 },
  "openingHoursSpecification": [{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "opens": "07:00", "closes": "18:00"
  }],
  "url": "https://example.com/locations/austin-tx/"
}
</script>
```

**Bad Example** — one page for all stores, inconsistent NAP

```html
<!-- Single URL for 50 locations: engine has nothing distinct to rank per city -->
<h1>Our Locations</h1>
<select id="store-picker"><option>Austin</option><option>Dallas</option></select>

<!-- Phone here disagrees with the JSON-LD below → read as two businesses -->
<p>Call us: (512) 555 0142</p>
<script type="application/ld+json">
{ "@type": "Restaurant", "name": "Blue Fig Cafe LLC",   // name mismatch vs on-page
  "telephone": "512.555.0142" }                          // format mismatch
</script>
```

## Common Mistakes

- Inconsistent NAP across the page, the JSON-LD, and the Business Profile.
- One store-locator page with a dropdown instead of one indexable URL per location.
- Thin, templated location pages that differ only by the city name.
- Address as an image or map embed, invisible to the crawler as text.
- Missing or stale `openingHoursSpecification`, including holiday hours.
- Fabricating a street address for a service-area business instead of using `areaServed`.

## Production Tips

- Validate `LocalBusiness` markup with the Rich Results Test and monitor the merchant/
  local reports in [Search Console](22-search-console.md).
- Generate location pages and their JSON-LD from one canonical data source (the same
  record that feeds the Business Profile), so NAP cannot drift between them.
- Audit NAP consistency across major directories periodically; external mismatches erode
  the local ranking signal even when your site is correct.

## AI Review Checklist

- Is NAP byte-for-byte identical across on-page HTML, JSON-LD, and the Business Profile?
- Does each physical location have its own indexable, crawlable, unique-content URL?
- Is valid `LocalBusiness` JSON-LD present with `address`, `geo`, hours, and `telephone`?
- Is the address real HTML text, not only an image or map embed?
- Are opening hours (including special hours) present and current?
- Do location pages clear the thin-content bar in [Content Quality](25-content-quality.md)?

## Related

- `knowledge/seo/09-structured-data.md`
- `knowledge/seo/14-international-seo.md`
- `knowledge/seo/05-metadata.md`
- `knowledge/seo/25-content-quality.md`
- `knowledge/seo/07-sitemaps.md`
