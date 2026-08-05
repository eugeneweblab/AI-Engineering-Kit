---
id: seo/98-production-checklist
topic: seo
slug: production-checklist
title: "SEO Production Checklist"
type: checklist
order: 98
status: ready
tags: [seo, production-checklist, noindex, robots.txt, "og:url", onclick, "og:title", "og:description"]
related: [seo/00-overview, seo/27-production-checks, seo/07-sitemaps, seo/08-robots-txt, seo/13-core-web-vitals]
when_to_use: "Read before launching a new site or a routing/rendering change, to verify search engines can crawl, render, and index it."
---
# SEO Production Checklist

## Purpose

A pre-launch and pre-deploy gate for technical SEO. Every item is a concrete, verifiable
yes/no check an engineer or agent can confirm against the running site — not the source.
If any box is unchecked, the change is not production-ready. Verify against the deployed
environment (or a production-parity preview), because edge logic, CDNs, and build steps
can change the final output.

## Indexation Control

**Rules:** [Indexing](03-indexing.md) · [Robots Txt](08-robots-txt.md)

- [ ] Production returns `index,follow` for every URL that should rank, and no page
  carries an accidental `noindex`.
- [ ] Staging, preview, and non-production hosts return `noindex` (or are blocked at the
  edge / behind auth) and cannot be crawled.
- [ ] `robots.txt` exists, returns `200`, and contains no stray `Disallow: /` on
  production.
- [ ] No URL is simultaneously `Disallow`ed in `robots.txt` and relied on for a
  `noindex` tag (a disallowed URL is never fetched, so its `noindex` is never seen).
- [ ] `X-Robots-Tag` headers (if used) agree with the `robots` meta on the same URL.

## URLs, Status Codes, and Redirects

**Rules:** [Links](17-links.md) · [Crawling](02-crawling.md)

- [ ] Every indexable URL returns `200`; no indexable content sits behind a `3xx`,
  `4xx`, or `5xx`.
- [ ] Old URLs from any prior structure `301`-redirect to their new equivalents (no
  redirect chains longer than one hop, no redirect loops).
- [ ] Redirects point to the final destination directly, not to another redirect.
- [ ] A single canonical host and protocol is enforced (e.g. `https://www.` →
  chosen form) via `301`.
- [ ] Trailing-slash and letter-casing rules are consistent and enforced by redirect.
- [ ] Soft 404s are eliminated: missing pages return a real `404`/`410`, not a `200`
  with an "empty" body.

## Canonicalization and Duplicates

**Rules:** [Canonicalization](06-canonicalization.md)

- [ ] Every indexable page emits exactly one `<link rel="canonical">` with an absolute
  URL.
- [ ] Canonical URLs are self-referential on canonical pages and point to the canonical
  on duplicate/parameter variants.
- [ ] Faceted, sorted, and tracking-parameter URLs do not create indexable duplicates.
- [ ] Paginated sequences expose each page's content and canonicalize correctly
  (see [Pagination](18-pagination.md)).

## Rendering

**Rules:** [Rendering](04-rendering.md) · [JavaScript SEO](19-javascript-seo.md)

- [ ] Indexable content is present in the server response (SSR/SSG) or reliably
  prerendered — not dependent on client-side hydration to exist.
- [ ] The rendered HTML seen by Search Console URL Inspection matches the intended
  content, title, and canonical.
- [ ] No critical content or links are hidden behind interactions the crawler will not
  perform (click, scroll, tab).

## Metadata and Social

**Rules:** [Metadata](05-metadata.md) · [Open Graph](10-open-graph.md)

- [ ] Every indexable page has a unique, non-empty `<title>` and meta description.
- [ ] `<html lang>` is set correctly; `hreflang` tags are present, reciprocal, and use
  valid language/region codes where the site is multilingual.
- [ ] Open Graph (`og:title`, `og:description`, `og:image`, `og:url`) and Twitter Card
  tags are present and resolve to reachable, correctly sized images.
- [ ] Structured data (JSON-LD) validates and reflects the actual on-page content.

## Discoverability

**Rules:** [Sitemaps](07-sitemaps.md) · [Crawling](02-crawling.md)

- [ ] An XML sitemap exists, lists only canonical, indexable, `200` URLs, and is
  referenced from `robots.txt`.
- [ ] The sitemap contains no `noindex`, redirected, or blocked URLs.
- [ ] Primary navigation and internal links are real `<a href>` anchors the crawler can
  follow (not `onclick` handlers or buttons).
- [ ] The property is verified in Search Console and the sitemap is submitted.

## Performance and Core Web Vitals

**Rules:** [Core Web Vitals](13-core-web-vitals.md) · [Performance](12-performance.md)

- [ ] Largest Contentful Paint, Interaction to Next Paint, and Cumulative Layout Shift
  meet "good" thresholds on mobile for key templates (see
  [Core Web Vitals](13-core-web-vitals.md)).
- [ ] Images are responsive, correctly sized, lazy-loaded below the fold, and declare
  width/height to prevent layout shift.
- [ ] The page is usable and readable on mobile without horizontal scroll or blocked
  content.

## Monitoring

**Rules:** [Monitoring](24-monitoring.md) · [Search Console](22-search-console.md)

- [ ] Search Console coverage and Core Web Vitals reports are watched and alert on
  regressions.
- [ ] Analytics tracks organic landing pages so a traffic drop is detected in days.
- [ ] A CI check asserts key SEO invariants (status, single canonical, robots, title) on
  representative routes.

## Related

- `knowledge/seo/00-overview.md`
- `knowledge/seo/27-production-checks.md`
- `knowledge/seo/07-sitemaps.md`
- `knowledge/seo/08-robots-txt.md`
- `knowledge/seo/13-core-web-vitals.md`
