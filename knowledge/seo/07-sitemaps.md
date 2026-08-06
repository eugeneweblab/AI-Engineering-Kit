---
id: seo/07-sitemaps
topic: seo
slug: sitemaps
title: "Sitemaps"
type: doc
order: 7
status: ready
tags: [seo, sitemaps, lastmod, robots.txt, noindex, "Sitemap:", priority]
related: [seo/02-crawling, seo/03-indexing, seo/08-robots-txt, seo/06-canonicalization]
when_to_use: "Read before generating or changing an XML sitemap, especially for large, frequently-updated, or JavaScript-rendered sites."
---
# Sitemaps

## Purpose

This document defines how to build an XML sitemap that helps search engines discover and
prioritize your URLs. It is written so an agent can generate a valid, trustworthy sitemap
that accelerates indexing instead of confusing the crawler.

A sitemap is a machine-readable list of the URLs you *want* indexed, plus optional hints
about when each changed. It supplements crawling — it does not replace it, and it is not a
ranking factor. It answers "here are my canonical pages; please crawl them."

## Why It Matters

Crawlers find pages by following links. New, deep, or poorly-linked pages can wait days or
weeks to be discovered. A sitemap gives the engine a direct manifest, which matters most
for large sites (millions of URLs), sites with weak internal linking, fresh content
(news, listings), and JavaScript apps where links are not in the initial HTML. A clean
sitemap also becomes a diagnostic surface: Search Console reports indexing status per
submitted URL, so a wrong or bloated sitemap actively misleads you about coverage.

## Core Principles

- **List only indexable, canonical, `200` URLs.** A sitemap is a statement "index these".
  Including redirects, `noindex`, blocked, or non-canonical URLs is a contradiction the
  engine penalizes as a trust signal.
- **A sitemap is a hint, not a guarantee.** Listing a URL does not force indexing; the
  engine still judges quality. Absence, however, slows discovery.
- **Respect the limits.** One sitemap file holds at most **50,000 URLs** and **50 MB
  uncompressed**. Beyond that, split into multiple sitemaps behind a sitemap index.
- **Keep it fresh and accurate.** `lastmod` must reflect the real last content change.
  Fabricated or always-`now` timestamps get ignored and erode trust in the whole file.
- **Use absolute URLs on one host.** Every URL must be fully qualified and on the same
  host+scheme as the sitemap itself.

## Best Practices

- Generate sitemaps programmatically from the same source of truth as your routes, so they
  never drift from what actually exists.
- Set `lastmod` from the content's real modified timestamp (ISO 8601, e.g.
  `2026-07-07T10:30:00+00:00`). Omit it rather than fake it.
- Treat `changefreq` and `priority` as near-worthless — Google ignores them. Spend effort
  on accurate URL sets and `lastmod`, not these fields.
- Split by content type or section (`sitemap-products.xml`, `sitemap-posts.xml`) and wrap
  them in a `<sitemapindex>`. This isolates problems and speeds regeneration.
- Reference the sitemap from `robots.txt` with a `Sitemap:` line **and** submit it in
  Search Console. Do both; each covers a different discovery path.
- Compress large sitemaps with gzip (`.xml.gz`) to stay under the size limit and cut
  transfer time.
- For images, video, or news, use the dedicated sitemap extensions rather than stuffing
  metadata into the standard schema.

## Examples

**Good Example** — canonical URLs, real `lastmod`, index for scale

`sitemap-index.xml` — one entry per child sitemap, each under 50k URLs. The XML
declaration must be the **first** thing in the file: a comment or a blank line before
it makes the document invalid, and the sitemap is rejected rather than partly read.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap-products.xml</loc>
    <lastmod>2026-07-07</lastmod>   <!-- when this child last changed -->
  </sitemap>
</sitemapindex>
```

`sitemap-products.xml` — only indexable, canonical URLs:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/shoes</loc>          <!-- absolute, canonical -->
    <lastmod>2026-07-06T14:02:00+00:00</lastmod>  <!-- real modified time -->
  </url>
</urlset>
```

**Bad Example** — non-canonical, redirected, and faked timestamps

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>http://example.com/shoes?utm_source=email</loc> <!-- non-canonical + http -->
    <lastmod>2026-07-07T17:00:00Z</lastmod>              <!-- always "now" → ignored -->
  </url>
  <url>
    <loc>https://example.com/old-shoes</loc>  <!-- 301s elsewhere → contradicts sitemap -->
    <priority>1.0</priority>                  <!-- ignored by Google -->
  </url>
</urlset>
```

## Common Mistakes

- Listing `noindex`, redirected, canonicalized-away, or 404 URLs — this contradicts your
  own indexing intent and lowers trust in the sitemap.
- Exceeding 50,000 URLs or 50 MB in a single file instead of using a sitemap index.
- Setting `lastmod` to the generation time on every build, so the engine stops trusting it.
- Mixing hosts or schemes (listing `www` URLs in a sitemap served from the apex domain).
- Relying on the sitemap alone with no internal links — the engine treats orphaned URLs as
  low value regardless of the manifest.
- Forgetting to update the sitemap when URLs are deleted, leaving 404s in the manifest.

## Production Tips

- Regenerate on publish/delete, not on a slow cron, so the sitemap never lags reality.
- Monitor the Search Console Sitemaps report for "Couldn't fetch" and per-URL discovery
  counts; a drop signals a broken generation job.
- For JavaScript-rendered sites where links are not in initial HTML, the sitemap is your
  primary discovery channel — keep it authoritative.

## AI Review Checklist

- Does the sitemap contain only indexable, canonical, `200` URLs on the correct host?
- Are files kept under 50,000 URLs and 50 MB, with a sitemap index above that?
- Is `lastmod` sourced from real content changes (or omitted), never a fixed "now"?
- Is the sitemap referenced in `robots.txt` and submitted to Search Console?
- Is it regenerated on content create/update/delete rather than on a lagging schedule?
- Are redirected, blocked, and 404 URLs excluded?

## Related

- `knowledge/seo/02-crawling.md`
- `knowledge/seo/03-indexing.md`
- `knowledge/seo/08-robots-txt.md`
- `knowledge/seo/06-canonicalization.md`
