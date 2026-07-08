---
id: seo/28-real-world-patterns
topic: seo
slug: real-world-patterns
title: "Real World Patterns"
type: doc
order: 28
status: ready
tags: [seo, real-world-patterns]
related: [seo/19-javascript-seo, seo/20-headless-seo, seo/04-rendering, seo/06-canonicalization, seo/18-pagination]
when_to_use: "Read before implementing a common SEO-sensitive feature — SPA routing, faceted navigation, infinite scroll, pagination, or migrations."
---
# Real World Patterns

## Purpose

This document catalogs recurring, SEO-sensitive implementation patterns and the correct
way to build each one. These are the situations where a reasonable-looking engineering
choice quietly destroys crawlability: single-page apps, faceted navigation, infinite
scroll, tabbed content, and URL migrations.

Each pattern names the trap and the fix, so an agent building the feature reaches for the
crawler-safe approach by default rather than discovering the problem after traffic drops.

## Why It Matters

Every pattern here has a "works for users, invisible to crawlers" failure mode. Infinite
scroll feels great to a human and hides every item past the first screen from Google.
Faceted navigation gives users filters and gives crawlers billions of duplicate URLs to
drown in. A migration that forgets redirects vaporizes years of accumulated ranking
signal overnight.

These are not edge cases — they are the most common features on commerce and content
sites. Getting the pattern right once, at implementation time, is trivial; retrofitting
it after launch means lost traffic and a painful re-crawl.

## Core Principles

- **Content must exist without interaction.** Anything that appears only after scroll,
  click, or hover is at risk of never being indexed. Provide a crawlable path to it.
- **Control the URL space you expose.** Every crawlable URL is crawl budget spent.
  Faceted and parameterized URLs must be deliberately allowed or blocked, never accidental.
- **Preserve identity across change.** URL migrations, A/B tests, and re-platforming must
  carry canonical and redirect signals so equity transfers.
- **Render for the bot, enhance for the human.** Server-render the content and links;
  layer JS interactivity on top ([progressive enhancement](19-javascript-seo.md)).

## Best Practices

- **SPA / client routing:** use SSR or SSG so each route returns full HTML with its own
  `<title>`, canonical, and content. Use real `<a href>` routes, not `onClick` navigation.
- **Infinite scroll:** back it with real [paginated](18-pagination.md) URLs
  (`?page=2`) that render server-side, and link them so a crawler can walk the set even
  though humans scroll.
- **Faceted navigation:** pick a small set of valuable filter combinations to index
  (self-canonical), and `noindex` or canonicalize the long tail; block infinite parameter
  permutations from crawling via robots rules or `rel="canonical"`.
- **Tabs / accordions:** keep hidden-tab content in the initial DOM (just visually
  hidden), not loaded on click, so it is indexed.
- **URL migration / re-platform:** map every old URL to its new target and serve `301`s;
  keep the old sitemap live until the new URLs are recrawled; update internal links.
- **A/B tests and variants:** canonicalize variant URLs to the original; never `noindex`
  the control or serve different content to Googlebot than to users (cloaking).

## Examples

**Good Example** — infinite scroll backed by crawlable pagination

```html
<!-- Users scroll; JS fetches the next page and appends it. But the paginated
     URLs are real, server-rendered, and linked, so a crawler can reach every item.
     WHY: content that exists only after a scroll event is invisible to crawlers;
     the underlying paginated URLs give them a walkable path. -->
<ul id="results"><!-- page 1 items server-rendered here --></ul>

<!-- Real, followable link the crawler uses even though humans never click it -->
<a rel="next" href="/products?page=2">Next page</a>

<script>
  // Progressive enhancement: intercept the link for humans, fall back to the URL.
  document.querySelector('[rel=next]').addEventListener('click', (e) => {
    e.preventDefault();
    loadAndAppend('/products?page=2'); // enhances UX; does not replace the crawlable URL
  });
</script>
```

**Bad Example** — faceted navigation with an uncontrolled URL space

```html
<!-- Every filter combination is a unique, indexable, self-canonical URL, and
     filters combine freely. WHY THIS FAILS: color × size × brand × price × sort
     explodes into millions of near-duplicate crawlable URLs that exhaust crawl
     budget and bury the pages that matter. -->
<a href="/shoes?color=red&size=9&brand=x&sort=price&page=3">Red · 9 · X · price</a>
<!-- ...thousands more permutations, all index,follow, none canonicalized... -->
<meta name="robots" content="index,follow" />
<!-- no canonical to a base facet, no crawl controls on parameters -->
```

## Common Mistakes

- SPA routes that share one `<title>`/canonical and render content only client-side.
- Infinite scroll or "load more" with no underlying crawlable paginated URLs.
- Faceted filters that generate unbounded indexable URL permutations.
- Tab/accordion content injected on click, so it never enters the indexable DOM.
- Migrations that drop `301`s or change URLs without updating internal links.
- Serving Googlebot different content than users (cloaking) — a manual-action risk.
- `noindex` on a canonical target, or canonicals pointing across differing content.

## Production Tips

- For faceted pages, decide the indexable set from search demand data, not from what is
  technically possible; everything else gets canonicalized or `noindex`ed.
- During a migration, keep a redirect map in version control and add a check that every
  old URL resolves to a `200` via a single `301`.
- Validate SPA routes with the [Search Console](22-search-console.md) URL Inspection tool
  to confirm Google renders the content, not just the shell.

## AI Review Checklist

- Does each SPA route return full server-rendered HTML with its own title and canonical?
- Is infinite scroll / "load more" backed by crawlable, linked paginated URLs?
- Is the faceted URL space bounded, with the long tail canonicalized or `noindex`ed?
- Is tab/accordion content in the initial DOM rather than click-loaded?
- Does every migrated URL serve a single `301` to the correct target?
- Are internal links updated to the new URLs after a migration?
- Is the same content served to crawlers and users (no cloaking)?

## Related

- `knowledge/seo/19-javascript-seo.md`
- `knowledge/seo/20-headless-seo.md`
- `knowledge/seo/04-rendering.md`
- `knowledge/seo/06-canonicalization.md`
- `knowledge/seo/18-pagination.md`
