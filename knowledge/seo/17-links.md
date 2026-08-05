---
id: seo/17-links
topic: seo
slug: links
title: "SEO Links"
type: doc
order: 17
status: ready
tags: [seo, links]
related: [seo/06-canonicalization, seo/02-crawling, seo/18-pagination, seo/03-indexing, seo/09-structured-data]
when_to_use: "Read before building navigation, internal linking, anchor markup, or handling outbound/user-generated links."
---
# SEO Links

## Purpose

This document defines how to author links so search engines can discover, crawl, and
weigh a site's pages correctly. It covers internal linking and site structure, anchor
markup, the `rel` attributes (`nofollow`, `sponsored`, `ugc`, `noopener`), and outbound
link hygiene. Links are how crawlers travel and how ranking signal (PageRank) flows, so
getting them right is foundational to everything downstream.

Links are the substrate of [Crawling](02-crawling.md): a URL with no internal link
pointing to it is effectively invisible, no matter how good its content or how correct its
[canonical](06-canonicalization.md).

## Why It Matters

Search engines discover pages by following links, and they distribute ranking signal
along them. A page that nothing links to (an "orphan") may never be crawled or indexed;
an important page buried ten clicks deep gets crawled rarely and ranks weakly. The way you
link internally is one of the few ranking levers entirely under engineering control — it
shapes both what gets found and what gets prioritized. Meanwhile, the wrong link markup
does quiet damage: a JavaScript `onClick` that looks like a link but has no `href` is
uncrawlable, and un-attributed paid or user-generated links can trigger a manual penalty.
None of this errors at runtime; it shows up as pages that never rank.

## Core Principles

- **A crawlable link is `<a href="…">` with a real URL.** Engines follow `href` on anchor
  elements. `<span onClick>`, `<button>` routing, or JS-only navigation without an `href`
  is not a link the crawler can follow. This is the single most common link SEO bug.
- **Every indexable page needs at least one internal link.** No orphans. Important pages
  should be reachable within a few clicks of the homepage — flatter is easier to crawl.
- **Anchor text describes the destination.** Descriptive anchors ("2026 pricing guide")
  are a relevance signal for the target; "click here" and bare URLs waste it.
- **Attribute untrusted and paid links.** Use `rel="sponsored"` for paid/affiliate links,
  `rel="ugc"` for user-generated content, and `rel="nofollow"` where you do not vouch for
  the target. Omitting these on paid links is a policy violation.
- **Link signals must agree with the rest.** Do not internally link with tracking-param
  URLs that conflict with canonicals, and do not link to `noindex`/redirecting URLs when
  the clean one exists (see [Canonicalization](06-canonicalization.md)).

## Best Practices

- Build primary navigation and pagination as real `<a href>` links so the whole site is
  crawlable without executing JavaScript (see [Pagination](18-pagination.md) for
  paginated sets).
- Link internally to **clean, canonical URLs** — no session IDs, no tracking params, no
  redirect chains. Every internal link should resolve in one hop to a `200`.
- Use descriptive, varied anchor text that reflects the target page's topic; avoid
  linking many pages to one target with the identical over-optimized phrase.
- Add `rel="noopener"` (and `noreferrer` if desired) to `target="_blank"` links for
  security; it does not affect SEO but is correct hygiene.
- Keep a crawlable HTML sitemap or well-structured footer/hub pages so deep content is
  reachable; surface new content from relevant existing pages.
- Fix broken internal links promptly — a link to a 404 wastes crawl budget and drops the
  signal that would have flowed to the intended page.
- For outbound links to untrusted destinations, decide the `rel` deliberately; default to
  `nofollow` for anything you cannot vouch for.

## Examples

**Good Example** — crawlable anchor, descriptive text, correct rel

```html
<!-- Real href → crawlable; descriptive anchor → relevance signal to the target -->
<a href="/guides/2026-pricing">Read the 2026 pricing guide</a>

<!-- Paid placement correctly attributed so it does not pass endorsement -->
<a href="https://partner.example" rel="sponsored noopener" target="_blank">Our sponsor</a>

<!-- User-submitted link in a comment, marked ugc -->
<a href="https://user-site.example" rel="ugc nofollow">their blog</a>
```

**Bad Example** — uncrawlable navigation, wasted anchors, un-attributed paid link

```html
<!-- No href: the crawler cannot follow this; the target page may be orphaned -->
<span class="nav-link" onclick="router.go('/products')">Products</span>

<!-- Bare "click here" gives the target no descriptive signal -->
<a href="/guides/2026-pricing">click here</a>

<!-- Paid affiliate link with no rel → passes endorsement, a policy violation -->
<a href="https://affiliate.example?ref=123" target="_blank">Buy now</a>
```

## Common Mistakes

- Navigation built from `<span>`/`<div>` + `onClick` instead of `<a href>`, leaving pages
  uncrawlable.
- Orphan pages with no internal links pointing to them.
- Internal links to tracking-param or redirecting URLs that fight the canonical.
- Generic anchor text ("click here", "read more", raw URLs) that carries no relevance.
- Paid or affiliate links without `rel="sponsored"` (or user links without `ugc`).
- Deep, important content buried many clicks from any hub, so it is crawled rarely.
- Broken internal links to 404s, wasting crawl budget and leaking signal.

## Production Tips

- Run a link crawler (or a CI check) that flags orphan pages, internal links to non-200
  URLs, and redirect chains before release.
- Audit that all navigational elements render as `<a href>` in the raw, pre-JS HTML —
  view source, not the DevTools DOM, since the crawler's first pass sees the former.
- Watch the internal-links and crawl reports in [Search Console](22-search-console.md);
  a suddenly under-linked template signals a navigation regression.

## AI Review Checklist

- Is every navigational/internal link a real `<a href>` with a crawlable URL?
- Does every indexable page have at least one internal link (no orphans)?
- Do internal links point to clean, canonical, `200`-returning URLs (no param/redirect
  noise)?
- Is anchor text descriptive of the destination rather than "click here"?
- Are paid links `rel="sponsored"`, user-generated links `rel="ugc"`, and untrusted links
  `nofollow`?
- Do `target="_blank"` links include `rel="noopener"`?

## Related

- `knowledge/seo/06-canonicalization.md`
- `knowledge/seo/02-crawling.md`
- `knowledge/seo/18-pagination.md`
- `knowledge/seo/03-indexing.md`
- `knowledge/seo/09-structured-data.md`
