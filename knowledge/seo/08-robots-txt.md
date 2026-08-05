---
id: seo/08-robots-txt
topic: seo
slug: robots-txt
title: "Robots Txt"
type: doc
order: 8
status: ready
tags: [seo, robots-txt, robots.txt, noindex, Disallow, "Sitemap:", Allow, X-Robots-Tag]
related: [seo/02-crawling, seo/03-indexing, seo/07-sitemaps, seo/04-rendering]
when_to_use: "Read before editing robots.txt or trying to keep a URL out of Google — the wrong tool here removes pages from the index or leaks private ones."
---
# Robots Txt

## Purpose

This document defines how to use `robots.txt` correctly: what it controls, what it does
*not*, and how to avoid the classic mistake of using it to hide pages. It is written so an
agent can configure crawler access without accidentally deindexing the site or exposing it.

`robots.txt` is a plain-text file at the domain root (`https://example.com/robots.txt`)
that tells crawlers which URLs they may **request**. It governs *crawling*, not
*indexing*, and not *access control*. Confusing those three is the root of nearly every
robots.txt bug.

## Why It Matters

`robots.txt` is the first file a crawler fetches, and a single wrong line has site-wide
blast radius. `Disallow: /` on a production deploy stops all crawling and, over weeks,
drops the whole site from search. Worse, blocking a page does **not** remove it from the
index — a blocked URL that others link to can still appear in results as a bare, snippet-
less link. And because the file is public, listing "secret" paths in it advertises exactly
where to look. The failure mode is silent and delayed: rankings decay days after the
mistake ships.

## Core Principles

- **`Disallow` blocks crawling, not indexing.** To keep a page out of the index, let it be
  crawled and serve `noindex` (meta tag or `X-Robots-Tag`). If it is blocked, the crawler
  never sees the `noindex` and may index the URL anyway.
- **It is a public file and not a security boundary.** Anyone can read it. Never rely on it
  to protect private URLs — use authentication for that.
- **It is advisory.** Reputable engines obey it; malicious bots ignore it. It is a
  politeness protocol, not enforcement.
- **Blocking removes the tool that fixes duplicates.** A crawler that cannot fetch a page
  cannot see its `rel=canonical` or `noindex`. Block only truly worthless URLs.
- **Rules are longest-match, per user-agent.** The most specific matching `Allow`/`Disallow`
  wins; a broad `Disallow` can be re-opened by a longer `Allow`.

## Best Practices

- Keep the file minimal. Block only crawler traps and infinite spaces (faceted search,
  calendars, internal search results), not content you want to rank.
- To *deindex*, use `noindex` on a crawlable page — never `Disallow`. Remove the page from
  `robots.txt` if it is currently blocked so the crawler can read the `noindex`.
- List your sitemap(s) with an absolute `Sitemap:` line; it is the one indexing-adjacent
  directive that belongs here.
- Do not use `robots.txt` to hide staging, admin, or private areas — those need HTTP auth
  or IP restriction; naming them here is a roadmap for attackers.
- Never block CSS, JS, or image assets the page needs to render — the engine renders pages
  and will misjudge a page it cannot fully load.
- Test every change in the Search Console robots.txt tester before shipping; verify the
  live file returns `200` with `text/plain`.
- Prefer explicit `User-agent: *` rules; add engine-specific groups only when you truly
  need different behavior per bot.

## Examples

**Good Example** — blocks a crawler trap, exposes the sitemap, leaves assets open

```
# https://example.com/robots.txt
User-agent: *
Disallow: /search        # internal search results = infinite low-value space
Disallow: /cart          # transactional, nothing to index
Allow: /search/help      # longer match re-opens one useful subpath

# Assets stay crawlable so the page renders correctly for indexing.
Sitemap: https://example.com/sitemap-index.xml
```

```html
<!-- To DEINDEX /promo: leave it crawlable and serve noindex, NOT Disallow. -->
<meta name="robots" content="noindex, follow" />
```

**Bad Example** — blocks to "hide", breaks rendering, deploys a kill switch

```
User-agent: *
Disallow: /                 # ships from staging → whole site deindexed over time
Disallow: /admin            # public file now advertises the admin path
Disallow: /assets/          # blocks CSS/JS → engine renders a broken page
Disallow: /old-page         # blocked, so the noindex on it is NEVER seen → stays indexed
```

## Common Mistakes

- Using `Disallow` to remove a page from Google; the URL stays indexed as a snippet-less
  link because the `noindex` is never crawled.
- Shipping a staging `Disallow: /` to production, silently deindexing the site.
- Blocking CSS/JS/image assets, so the rendered page looks broken to the crawler.
- Treating `robots.txt` as access control and listing private/admin paths in a public file.
- Assuming `Disallow` also hides the page from link-based discovery — it does not.
- Serving the file with the wrong content type, a redirect, or a non-`200` status, so
  crawlers ignore it.

## Production Tips

- Guard the file per environment: staging serves `Disallow: /`, production must serve the
  permissive file. Make the swap part of the deploy, not a manual step.
- Alert if `robots.txt` returns anything but `200 text/plain`, or if its byte size changes
  unexpectedly — a broken file can block the whole site.
- For at-scale removals, combine `noindex` with the Search Console Removals tool for speed,
  then let the `noindex` hold it out permanently.

## AI Review Checklist

- Is deindexing done with `noindex` on a *crawlable* page, never with `Disallow`?
- Are CSS, JS, and image assets left crawlable so pages render correctly?
- Does production serve a permissive file (no accidental `Disallow: /` from staging)?
- Are private/admin areas protected by auth, not merely listed in `robots.txt`?
- Is the sitemap declared with an absolute `Sitemap:` URL?
- Does `robots.txt` return `200` with `text/plain` at the domain root?

## Related

- `knowledge/seo/02-crawling.md`
- `knowledge/seo/03-indexing.md`
- `knowledge/seo/07-sitemaps.md`
- `knowledge/seo/04-rendering.md`
