---
id: seo/18-pagination
topic: seo
slug: pagination
title: "Pagination"
type: doc
order: 18
status: ready
tags: [seo, pagination]
related: [seo/03-indexing, seo/06-canonicalization, seo/17-links, seo/02-crawling]
when_to_use: "Read before building or reviewing any paginated list, archive, category, or infinite-scroll page."
---
# Pagination

## Purpose

This document defines how to structure multi-page sequences — search results, category
listings, blog archives, comment threads — so search engines can crawl the whole set,
attribute content to the right URL, and avoid wasting crawl budget on near-duplicates.

Pagination is where a single logical collection is split across many URLs. Done wrong,
it either buries content the crawler never reaches or floods the index with thin,
overlapping pages. Done right, every item in the collection is discoverable through a
crawlable path, and each page URL is a distinct, self-canonical thing.

## Why It Matters

Deep content lives behind pagination. If page 2 onward is only reachable by JavaScript
click handlers or a `#anchor`, the crawler stops at page 1 and the rest of the catalog
never gets indexed — silently. The failure looks like "our old products don't rank"
months later, with no error anywhere. Conversely, sloppy pagination generates hundreds
of thin URLs (`?page=2`, `?sort=price&page=2`, `?page=2&ref=x`) that compete with each
other and drain the crawl budget you needed for real pages. Both failure modes are
invisible in the browser and only show up in index-coverage reports.

## Core Principles

- **Each page in a sequence is its own indexable URL.** Google retired `rel="next"` /
  `rel="prev"` as an indexing signal in 2019. Do not rely on them to consolidate a
  series; treat page 2 as a first-class page that self-canonicalizes to itself.
- **Every paginated page must be reachable by a crawlable `<a href>`.** A button that
  loads more via `fetch` with no underlying link is invisible to a crawler that does not
  execute it. Discoverability is the whole point.
- **Do not canonicalize page N to page 1.** That tells the engine pages 2+ are
  duplicates of page 1, so their unique content (items 11–20) is dropped from the index.
- **Use stable, canonical URL parameters.** One collection, one parameter scheme. Order
  parameters consistently and drop tracking noise, so `?page=2` is one URL, not twenty.
- **Prefer one signal per intent.** If you offer a "view all" page, canonicalize the
  paginated pages to it *only* when the all-in-one page is genuinely usable and fast.

## Best Practices

- Render pagination as real anchors: `<a href="/blog?page=2">2</a>`. Server-render the
  links so they exist in the initial HTML, not after hydration.
- Keep page URLs self-referential in their canonical tag: `/blog?page=2` canonicals to
  `/blog?page=2`. See [canonicalization](06-canonicalization.md).
- Return `200 OK` for valid pages and `404` for out-of-range pages (`?page=9999` on a
  three-page list). Never return `200` with an empty list — that is a soft 404.
- For infinite scroll, back it with paginated, crawlable URLs (progressive enhancement):
  the scroll is a UX layer over real `/page/2` routes the crawler can follow.
- Put unique, page-specific `<title>`/description context on deep pages when it helps
  users, but do not spam "Page 2 of 9" as the whole title — keep the primary title.
- List only page 1 of a sequence in your [sitemap](07-sitemaps.md); let crawling
  discover the rest through links. Deep pages rarely need direct sitemap inclusion.
- Faceted filters (color, size, sort) that create pagination variants should be
  `noindex` or canonicalized to the base collection unless a facet has real search
  demand — otherwise they explode crawl budget.

## Examples

**Good Example** — crawlable links, self-canonical pages, honest status codes

```html
<!-- Server-rendered pagination: real anchors present in initial HTML -->
<nav aria-label="Pagination">
  <a href="/products?page=1">1</a>
  <a href="/products?page=2" aria-current="page">2</a>
  <a href="/products?page=3">3</a>
  <a href="/products?page=3" rel="next">Next</a>
</nav>

<!-- On /products?page=2, the canonical points to itself, not page 1.
     Page 2's unique items stay eligible for indexing. -->
<link rel="canonical" href="https://example.com/products?page=2" />
```

```js
// Out-of-range pages must 404, not 200-with-empty-list (a soft 404).
app.get("/products", async (req, res) => {
  const page = Number(req.query.page ?? 1);
  const { items, totalPages } = await getProducts(page);
  if (page < 1 || page > totalPages) return res.status(404).render("not-found");
  res.status(200).render("products", { items, page });
});
```

**Bad Example** — JS-only "load more", page N canonicalized to page 1

```html
<!-- No href: a crawler that does not run JS never reaches page 2+.
     Deep content becomes undiscoverable. -->
<button onclick="loadMore()">Load more</button>

<!-- On /products?page=2, canonical points to page 1.
     Engine treats page 2 as a duplicate and drops items 11–20 from the index. -->
<link rel="canonical" href="https://example.com/products" />
```

## Common Mistakes

- Canonicalizing every paginated page to page 1, deindexing all deep content.
- Relying on `rel="next"`/`rel="prev"` to consolidate a series — they are ignored for
  indexing since 2019.
- Infinite scroll with no underlying paginated URLs, so the crawler sees only the first
  batch.
- Returning `200 OK` with an empty result set for out-of-range pages (soft 404).
- Letting faceted/sort parameters multiply pagination into thousands of thin URLs that
  burn [crawl budget](02-crawling.md).
- `noindex` on paginated pages combined with links only reachable *through* those pages —
  the engine drops the page and may stop following its links, orphaning deeper content.

## Production Tips

- Watch Search Console's "Crawled – currently not indexed" and "Discovered – currently
  not indexed" buckets; a spike there often traces to pagination or facet explosion.
- Log crawler hits per URL pattern. If bots spend most requests on `?sort=` variants,
  tighten parameter handling before it starves your real pages.
- When migrating pagination schemes, `301` old page URLs to new ones so deep-link equity
  and existing crawl paths survive.

## AI Review Checklist

- Is every paginated page reachable via a server-rendered `<a href>`, not JS-only?
- Does each page N canonicalize to itself, not to page 1?
- Do out-of-range pages return `404` rather than `200` with an empty list?
- Is infinite scroll backed by real, crawlable paginated URLs?
- Are faceted/sort parameter variants `noindex` or canonicalized unless they have demand?
- Do the paginated URLs use a stable, minimal parameter scheme (no tracking noise)?

## Related

- `knowledge/seo/03-indexing.md`
- `knowledge/seo/06-canonicalization.md`
- `knowledge/seo/17-links.md`
- `knowledge/seo/02-crawling.md`
