---
id: seo/03-indexing
topic: seo
slug: indexing
title: "SEO Indexing"
type: doc
order: 3
status: ready
tags: [seo, indexing, noindex, X-Robots-Tag, canonical, Disallow, robots, indexed]
related: [seo/02-crawling, seo/06-canonicalization, seo/04-rendering, seo/08-robots-txt, seo/22-search-console]
when_to_use: "Read before adding noindex, canonical tags, or anything that decides whether a URL enters search results."
---
# SEO Indexing

## Purpose

This document defines how a fetched page **enters or is excluded from** the search index —
the stage after [crawling](02-crawling.md) and before ranking. It covers the `robots` meta
tag, the `X-Robots-Tag` header, canonicalization, and duplicate handling, so an agent can
make exactly the pages it intends appear in search — and no others.

Indexing answers "should this URL be stored and shown in results?". It is controlled by
directives *inside* the fetched response (meta/headers), which is why the page must be
crawlable first: an engine cannot read a `noindex` tag on a page it was blocked from
fetching. Keep this distinction from [robots.txt](08-robots-txt.md), which controls
crawling, sharp — confusing the two is the most common indexing bug.

## Why It Matters

Indexing mistakes are bimodal and both are bad: a stray `noindex` silently removes pages
that should rank (a traffic cliff), while missing controls flood the index with
duplicates, thin pages, and staging URLs that dilute the site and can trigger quality
demotions. Because the directives are small tags buried in a template or a shared layout,
a one-line change can deindex an entire section — and recovery takes weeks as the engine
re-crawls. Indexing changes deserve the same review rigor as auth changes.

## Core Principles

- **`noindex` is the only reliable way to keep a crawlable page out of the index.** Put
  it in a `<meta name="robots">` tag or an `X-Robots-Tag` header. The page must be
  *crawlable* for the engine to see it.
- **Never `Disallow` a page you also want to `noindex`.** If the crawl is blocked, the
  engine never reads the `noindex` and may index the URL anyway from external links.
- **One canonical URL per piece of content.** Use `<link rel="canonical">` to point
  duplicates and variants (tracking params, sort orders) at the single preferred URL
  (see [Canonicalization](06-canonicalization.md)).
- **Signals must agree.** Status code, `robots` directive, canonical, and sitemap entry
  for a URL must be consistent. Contradictions are resolved unpredictably by the engine.
- **Canonical and `noindex` are hints/directives with different force.** `noindex` is
  obeyed; `canonical` is a strong hint the engine may override. Do not combine `noindex`
  with a `canonical` pointing elsewhere — it sends mixed messages.

## Best Practices

- Default important pages to indexable; explicitly `noindex` thin, duplicate, internal,
  or utility pages (search results, filtered views, print pages, staging).
- Set a self-referential `<link rel="canonical">` on every canonical page so the engine
  is not left to guess among parameter variants.
- Use `X-Robots-Tag` for non-HTML resources (PDFs, images) where you cannot add a meta
  tag but still need `noindex`.
- Keep the [sitemap](07-sitemaps.md) limited to canonical, indexable URLs; never list a
  `noindex` or canonicalized-away URL.
- After removing a page, return `404`/`410` (permanent removal) rather than `noindex` on
  a `200` page you keep serving.
- When you truly need urgent removal, use Search Console's Removals tool *and* a
  `noindex`; the tool is temporary, the tag is durable.

## Examples

**Good Example** — crawlable page, explicit directive, self-canonical

```html
<head>
  <!-- Utility page kept out of the index; page is still crawlable so the
       engine can actually read this directive. -->
  <meta name="robots" content="noindex,follow">
</head>
```

```html
<head>
  <!-- Canonical product page: self-referential canonical resolves the
       ?utm= and ?sort= variants to this one URL. -->
  <link rel="canonical" href="https://example.com/products/42">
  <meta name="robots" content="index,follow">
</head>
```

**Bad Example** — blocked crawl defeats the noindex

```text
# robots.txt
Disallow: /account/          # blocks the crawl of /account/settings
```

```html
<!-- /account/settings -->
<meta name="robots" content="noindex">
<!-- WHY this is wrong: robots.txt stopped the crawler from fetching the page,
     so it never reads this noindex tag. If another site links to
     /account/settings, the URL can still be indexed (as a bare link, no snippet).
     Correct fix: allow the crawl and rely on the noindex, OR require auth so the
     page returns a non-200 to anonymous bots. -->
```

## Common Mistakes

- Combining `Disallow` (robots.txt) with `noindex` on the same URL — the block prevents
  the tag from ever being read.
- Missing or wrong `canonical` tags, letting parameter variants and `http`/`https` or
  `www` duplicates split signals.
- Shipping a global/layout-level `noindex` (often left over from staging) to production.
- Listing `noindex` or canonicalized-away URLs in the sitemap, contradicting the intent.
- Canonicalizing to a URL that is itself `noindex`, `404`, or redirected.
- Assuming `noindex` deletes a page instantly — the engine must re-crawl to see it.

## Production Tips

- Use the **URL Inspection** tool in [Search Console](22-search-console.md) to confirm
  Google's *rendered* view of a page and its indexing verdict — not just the raw HTML.
- Diff staging vs production `robots` meta and `X-Robots-Tag` in CI to catch a
  `noindex` accidentally promoted from a non-prod environment.
- Alert on a sudden drop in "Indexed" pages in the Pages report — it is the earliest
  signal of an accidental deindex.

## AI Review Checklist

- Is any page both `Disallow`ed in robots.txt and `noindex`ed (contradiction)?
- Does every canonical page have a correct self-referential `<link rel="canonical">`?
- Do canonical targets resolve to an indexable, `200`, non-redirecting URL?
- Is there any environment-wide `noindex` that could reach production?
- Does the sitemap contain only canonical, indexable URLs?
- For non-HTML files needing exclusion, is `X-Robots-Tag` used instead of a meta tag?

## Related

- `knowledge/seo/02-crawling.md`
- `knowledge/seo/06-canonicalization.md`
- `knowledge/seo/04-rendering.md`
- `knowledge/seo/08-robots-txt.md`
- `knowledge/seo/22-search-console.md`
