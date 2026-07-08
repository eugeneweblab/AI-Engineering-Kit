---
id: seo/02-crawling
topic: seo
slug: crawling
title: "Crawling"
type: doc
order: 2
status: ready
tags: [seo, crawling]
related: [seo/03-indexing, seo/08-robots-txt, seo/07-sitemaps, seo/17-links, seo/01-seo-fundamentals]
when_to_use: "Read before changing routing, robots.txt, status codes, or how pages link to each other."
---
# Crawling

## Purpose

This document defines how search engine bots **discover and fetch** your URLs — the first
stage of the pipeline. It covers link discoverability, `robots.txt`, HTTP status codes,
redirects, and crawl budget, so an agent can make sure every important page can actually
be reached and every unimportant one is not wasting the crawler's time.

Crawling answers "can the bot get to this URL and fetch it?" — a separate question from
[indexing](03-indexing.md) ("should it be stored?"). A page must be crawled before it can
be indexed, but crawling a page does *not* guarantee indexing. Do not use crawl controls
to try to deindex pages (that is indexing's job — see below).

## Why It Matters

If the crawler cannot discover or fetch a URL, nothing downstream matters — the page is
invisible. Crawl failures are easy to introduce and hard to notice: an orphaned page with
no inbound links, a `Disallow` that is too broad, a 5xx during a deploy, or a redirect
chain that the bot gives up on. On large sites, crawl budget is finite, so wasting it on
junk URLs (faceted filters, session IDs, infinite calendars) starves the pages you care
about. These are silent traffic leaks.

## Core Principles

- **Discoverability is via links and sitemaps.** A URL the bot cannot reach through a
  crawlable `<a href>` or a [sitemap](07-sitemaps.md) is effectively orphaned.
- **HTTP status codes are instructions, and they must be honest.** `200` = here it is;
  `301` = moved permanently; `404`/`410` = gone; `5xx` = try later. Lying (e.g. a "soft
  404" that returns `200` for a missing page) confuses the crawler.
- **`robots.txt` controls fetching, not indexing.** `Disallow` stops the crawl but a
  disallowed URL can still be indexed from external links — with no snippet. To keep a
  page *out of the index*, allow the crawl and use `noindex` (see [Indexing](03-indexing.md)).
- **Crawl budget is finite; spend it on real pages.** Every crawlable low-value URL is
  budget not spent on a valuable one.

## Best Practices

- Link to every important page with a plain `<a href="/path">` — crawlers do not click
  buttons or run `onClick` handlers to discover routes (see [Links](17-links.md)).
- Return the *correct* status code: real `404`/`410` for missing pages, `301` for
  permanent moves, `302`/`307` only for genuinely temporary ones.
- Keep redirects to a single hop. Chains (`A→B→C`) waste budget and lose signals; loops
  break crawling entirely.
- Submit an XML [sitemap](07-sitemaps.md) of canonical, indexable URLs and keep it in
  sync with what actually returns `200`.
- Block crawl-trap URLs (endless filter combinations, search result pages) in
  [robots.txt](08-robots-txt.md) so budget flows to content.
- Keep the server fast and stable; sustained slowness or `5xx` makes the engine crawl
  less often.

## Examples

**Good Example** — honest status codes and crawlable links

```html
<!-- Discoverable: a real anchor with an href the crawler can follow. -->
<a href="/products/wireless-headphones">Wireless Headphones</a>
```

```http
GET /products/discontinued-item HTTP/1.1
→ HTTP/1.1 410 Gone
# WHY: the product is permanently removed, so 410 tells the crawler to drop it.
# A 200 with an "out of stock" page would be a soft 404 and keep the URL crawled.
```

**Bad Example** — orphaned route and a lying status code

```jsx
{/* Not discoverable: the crawler cannot run this click handler to find the URL. */}
<div onClick={() => router.push("/products/42")}>Wireless Headphones</div>
```

```http
GET /this-page-does-not-exist HTTP/1.1
→ HTTP/1.1 200 OK          # soft 404: returns 200 with "Page not found" text
# WHY this is wrong: the crawler thinks the page is real content, wastes budget
# re-crawling it, and may index the error page. Missing pages must return 404/410.
```

## Common Mistakes

- Using `Disallow` in robots.txt to try to remove a page from the index — it blocks the
  crawl but the URL can still appear in results without a snippet.
- Soft 404s: returning `200 OK` for pages that are actually missing or empty.
- Discovering routes only through JavaScript navigation with no crawlable `<a href>`.
- Long redirect chains or loops that exhaust crawl budget and drop signals.
- Blocking CSS/JS in robots.txt, which breaks the engine's ability to render the page
  (see [Rendering](04-rendering.md)).
- Letting infinite URL spaces (filters, sort params, calendars) be crawlable.

## Production Tips

- Watch **Crawl Stats** and the **Pages** report in [Search Console](22-search-console.md)
  for spikes in `5xx`, soft 404s, or "Discovered – currently not indexed."
- Keep server logs and grep for the bot user-agents to see what is actually being
  crawled and how much budget hits junk URLs.
- After a mass URL change, update the sitemap and internal links the same day; do not
  rely on the crawler to re-discover the new structure quickly.

## AI Review Checklist

- Is every important page reachable through a crawlable `<a href>` or the sitemap?
- Do missing pages return `404`/`410` — never a soft 404 with `200`?
- Are permanent moves `301` with a single hop, no chains or loops?
- Is `robots.txt` blocking only crawl-traps, and never CSS/JS needed for rendering?
- Is `Disallow` being misused to attempt deindexing (should be `noindex` instead)?
- Does the sitemap list only canonical, `200`, indexable URLs?

## Related

- `knowledge/seo/03-indexing.md`
- `knowledge/seo/08-robots-txt.md`
- `knowledge/seo/07-sitemaps.md`
- `knowledge/seo/17-links.md`
- `knowledge/seo/01-seo-fundamentals.md`
