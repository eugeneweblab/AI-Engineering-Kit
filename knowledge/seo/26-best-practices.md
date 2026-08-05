---
id: seo/26-best-practices
topic: seo
slug: best-practices
title: "SEO Best Practices"
type: doc
order: 26
status: ready
tags: [seo, best-practices, noindex, onClick, robots, Disallow, aspect-ratio, height]
related: [seo/01-seo-fundamentals, seo/03-indexing, seo/06-canonicalization, seo/27-production-checks, seo/29-seo-review]
when_to_use: "Read before shipping any user-facing page or route change, as the cross-cutting SEO checklist that ties the topic together."
---
# SEO Best Practices

## Purpose

This document collects the cross-cutting rules that apply to almost every page, pulling
together the specifics covered in the rest of this topic — [indexing](03-indexing.md),
[canonicalization](06-canonicalization.md), [metadata](05-metadata.md),
[performance](12-performance.md), and [content quality](25-content-quality.md) — into one
default-correct baseline.

It is written so an agent building or reviewing a page can apply the high-value 20% of
SEO that prevents 80% of the damage, without reading every sibling doc first.

## Why It Matters

Most SEO failures are not exotic — they are the same handful of mistakes repeated:
a page that is accidentally `noindex`, a wrong canonical, a missing or duplicate title,
content that only exists after client-side JavaScript, or a slow page. Each is cheap to
prevent at build time and expensive to detect and reverse in production.

Getting the baseline right on every page is worth far more than advanced tactics on a few
pages. A site where every page is crawlable, canonical, uniquely titled, fast, and
server-rendered will out-rank a site with clever tactics layered over a broken
foundation.

## Core Principles

- **Default to indexable and canonical-to-self.** A normal content page should serve
  `200`, `index,follow`, and a self-referential canonical. Deviations must be deliberate.
- **Render the content server-side.** The primary content, links, and meta must be in the
  initial HTML — do not depend on client JS to render what the crawler needs.
- **One URL per piece of content.** Pick a canonical URL scheme (host, trailing slash,
  casing, params) and redirect every variant to it.
- **Make the important content and links reachable without interaction.** Crawlers do not
  click, scroll infinitely, hover, or fill forms.
- **Fast is a ranking factor.** [Core Web Vitals](13-core-web-vitals.md) are part of
  ranking; performance is an SEO requirement, not a nicety.

## Best Practices

- Serve a unique `<title>` and [meta description](05-metadata.md) on every page; a
  self-referential `<link rel="canonical">`; and correct `robots` directives.
- Ensure the initial HTML contains the main content and internal links. If you use a SPA
  framework, use SSR/SSG so crawlers see rendered output.
- Keep URLs stable, lowercase, and descriptive. When a URL must change, `301`-redirect the
  old one; never let content silently move.
- Use real `<a href>` links for navigation — not `onClick` handlers or buttons — so
  crawlers can follow them.
- Maintain an accurate XML [sitemap](07-sitemaps.md) of canonical, indexable URLs and keep
  [robots.txt](08-robots-txt.md) from blocking anything you want indexed (including CSS/JS).
- Set explicit `width`/`height` (or `aspect-ratio`) on [images](16-images.md) and
  descriptive `alt` text to avoid layout shift and gain image search traffic.
- Add relevant [structured data](09-structured-data.md) that matches visible content.
- Verify changes against a bot user-agent before shipping, and monitor after
  ([monitoring](24-monitoring.md)).

## Examples

**Good Example** — a default-correct page head

```html
<!-- Indexable, self-canonical, uniquely described, and crawlable by default.
     WHY: this is the baseline a normal content page should meet; anything less
     needs a deliberate reason. -->
<head>
  <title>Argon2id password hashing: a practical guide</title>
  <meta name="description" content="How Argon2id works, how to tune it, and safe defaults." />
  <link rel="canonical" href="https://example.com/guides/argon2id" />
  <meta name="robots" content="index,follow" />
</head>
<body>
  <h1>Argon2id password hashing</h1>
  <!-- Real anchor so the crawler can follow it -->
  <a href="/guides/password-storage">See the password storage overview</a>
</body>
```

**Bad Example** — content and links hidden behind client JS

```html
<!-- The crawler receives an empty shell; content appears only after JS runs.
     WHY THIS FAILS: no title/canonical/content in the initial HTML, and the
     "link" is a click handler the crawler cannot follow → the page is invisible. -->
<head>
  <title>Loading…</title>            <!-- non-unique, placeholder title -->
  <!-- no canonical, no meta description, no robots -->
</head>
<body>
  <div id="root"></div>              <!-- content injected client-side only -->
  <span onClick="go('/guides')">Guides</span> <!-- not an <a href>: uncrawlable -->
</body>
```

## Common Mistakes

- Shipping a SPA that renders content client-side only, leaving crawlers an empty shell.
- A stray global `noindex` or `Disallow` from staging config that reaches production.
- Duplicate or placeholder titles/descriptions across many pages.
- Missing or non-self-referential canonical tags, splitting duplicate URL variants.
- Navigation via `onClick`/buttons instead of `<a href>`, so links are not followed.
- Blocking CSS/JS in robots.txt, so Google cannot render the page it needs to rank.
- Treating performance as separate from SEO instead of a ranking input.

## Production Tips

- Encode this baseline as CI assertions (title present, canonical self-referential,
  `robots` not `noindex`, status 200) so regressions fail the build.
- Keep a single source of truth for the canonical URL scheme and derive redirects from it.
- Test with the URL Inspection tool in [Search Console](22-search-console.md) after major
  template changes to see the actual rendered, indexed version.

## AI Review Checklist

- Does the page serve `200`, `index,follow`, and a self-referential canonical by default?
- Is the main content and are internal links present in the initial server-rendered HTML?
- Is the `<title>` unique and is a meta description present?
- Is navigation done with real `<a href>` links crawlers can follow?
- Are CSS/JS unblocked in robots.txt and the sitemap limited to canonical URLs?
- Do URL changes ship with `301` redirects from the old paths?
- Are Core Web Vitals within target on the affected templates?

## Related

- `knowledge/seo/01-seo-fundamentals.md`
- `knowledge/seo/03-indexing.md`
- `knowledge/seo/06-canonicalization.md`
- `knowledge/seo/27-production-checks.md`
- `knowledge/seo/29-seo-review.md`
