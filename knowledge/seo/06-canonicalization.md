---
id: seo/06-canonicalization
topic: seo
slug: canonicalization
title: "Canonicalization"
type: doc
order: 6
status: ready
tags: [seo, canonicalization, https, noindex, robots.txt, http]
related: [seo/03-indexing, seo/07-sitemaps, seo/17-links, seo/18-pagination, seo/14-international-seo]
when_to_use: "Read before shipping any page reachable at more than one URL — filters, tracking params, trailing slashes, pagination, or syndicated content."
---
# Canonicalization

## Purpose

This document defines how to tell a search engine which URL is the *authoritative*
version of a piece of content when the same or near-identical content is reachable at
several URLs. It is written so an agent can add canonicalization to a page without
splitting its ranking signals or hiding it from the index.

Canonicalization answers "which URL should represent this content?". It does not remove
duplicates from your site — it consolidates their signals onto one chosen URL so links,
crawl budget, and ranking accrue to a single address instead of being divided.

## Why It Matters

Modern sites generate duplicate URLs by default: `?utm_source=` tracking params, faceted
filters, session IDs, `http` vs `https`, `www` vs apex, trailing slashes, uppercase paths,
and print views all point at the same content. To a crawler these are distinct URLs. Left
unmanaged, they dilute link equity across copies, waste crawl budget on redundant pages,
and let the engine pick a canonical for you — often the wrong one. The failure is silent:
the page still loads, but it ranks below where it should because its signals are scattered.

## Core Principles

- **One canonical per piece of content.** Every indexable URL must declare exactly one
  canonical, even if it points to itself. Ambiguity forces the engine to guess.
- **The canonical is a strong hint, not a directive.** Google may ignore a canonical it
  distrusts (e.g. it contradicts your sitemap or redirects). Keep every signal consistent.
- **Use absolute, final URLs.** The canonical must be the exact `https` URL that returns
  `200` — no relative paths, no redirect chains, no parameters you strip elsewhere.
- **Redirect when a URL should not exist; canonicalize when it must.** A 301 removes the
  duplicate outright; `rel=canonical` keeps it reachable but consolidates its signals.
- **Never canonicalize to a `noindex`, redirected, or blocked URL.** These are conflicting
  signals; the engine will distrust all of them and canonicalize on its own.

## Best Practices

- Put `<link rel="canonical" href="https://example.com/page">` in `<head>` on every page,
  self-referencing when the page is its own canonical. Self-canonicals absorb stray
  parameter variants automatically.
- Pick one host and one scheme (`https://www.` or `https://` apex) and 301 all others to
  it. Enforce it in the router or edge, not just in markup.
- Normalize trailing slashes and case at the server with a 301 to the canonical form.
  Decide the rule once and apply it everywhere.
- For paginated series, self-canonicalize each page (`?page=2` → `?page=2`). Do **not**
  canonicalize page 2 to page 1 — it hides page 2's items from the index.
- For syndicated or cross-posted content, set the canonical to the original publisher's
  URL so the source, not the copy, ranks.
- Keep the canonical consistent with the sitemap, internal links, and hreflang. Every
  cluster (canonical + alternates) must agree.
- Send the canonical via `Link:` HTTP header for non-HTML resources (PDFs, images) where
  you cannot add a `<link>` tag.

## Examples

**Good Example** — absolute, self-referencing, points to the indexable `200` URL

```html
<!-- On https://example.com/shoes?color=red&utm_source=news -->
<!-- Strips tracking + filter noise; consolidates signals onto the clean canonical. -->
<link rel="canonical" href="https://example.com/shoes" />

<!-- Page 2 of a series canonicalizes to ITSELF, not to page 1, -->
<!-- so its unique product listings stay eligible for indexing. -->
<link rel="canonical" href="https://example.com/shoes?page=2" />
```

**Bad Example** — relative, cross-signal contradictions

```html
<!-- Relative URL: ambiguous, and resolves differently across environments. -->
<link rel="canonical" href="/shoes/" />

<!-- Canonical target is itself noindexed elsewhere → contradictory signals, -->
<!-- so Google ignores the canonical and picks its own winner. -->
<link rel="canonical" href="https://example.com/shoes-print" />
<meta name="robots" content="noindex" />   <!-- on /shoes-print -->

<!-- Every paginated page points at page 1 → pages 2..n vanish from the index. -->
<link rel="canonical" href="https://example.com/shoes?page=1" />
```

## Common Mistakes

- Canonicalizing every paginated page to page 1, dropping deep items from the index.
- Using a relative or non-`https` canonical, or one that 301-redirects before reaching a
  `200`.
- A canonical that points to a `noindex` or robots-blocked URL — the engine cannot verify
  it and distrusts the whole cluster.
- Multiple `<link rel="canonical">` tags on one page; engines ignore all but treat it as
  a quality problem.
- Contradicting the canonical with the sitemap or internal links (linking to the non-
  canonical variant everywhere).
- Leaving no canonical at all on filter/parameter URLs, letting the engine split signals
  across every combination.

## Production Tips

- Audit canonicals in [Search Console](22-search-console.md): the "Page indexing" report
  shows "Duplicate, Google chose different canonical" when your hint was overridden — fix
  the contradicting signal.
- Generate the canonical from the same routing logic that builds internal links so the two
  can never drift apart.
- Block low-value parameter URLs from wasting crawl budget with a canonical *plus* clean
  internal linking; do not rely on `robots.txt` to fix duplicates (it hides the canonical
  tag from the crawler).

## AI Review Checklist

- Does every indexable page emit exactly one absolute `https` canonical?
- Is the canonical target a `200` URL (no redirect chain, not `noindex`, not blocked)?
- Do paginated pages self-canonicalize instead of pointing to page 1?
- Do canonical, sitemap, internal links, and hreflang all agree for each cluster?
- Is one host+scheme chosen and are all variants 301-redirected to it at the server?
- For syndicated content, does the canonical point to the original source?

## Related

- `knowledge/seo/03-indexing.md`
- `knowledge/seo/07-sitemaps.md`
- `knowledge/seo/17-links.md`
- `knowledge/seo/18-pagination.md`
- `knowledge/seo/14-international-seo.md`
