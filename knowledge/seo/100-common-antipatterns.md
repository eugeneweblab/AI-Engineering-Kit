---
id: seo/100-common-antipatterns
topic: seo
slug: common-antipatterns
title: "SEO Common Antipatterns"
type: antipatterns
order: 100
status: ready
tags: [seo, common-antipatterns, noindex, robots.txt, X-Robots-Tag, Disallow, https, http]
related: [seo/00-overview, seo/04-rendering, seo/06-canonicalization, seo/08-robots-txt, seo/19-javascript-seo]
when_to_use: "Read when debugging a traffic drop or reviewing code, to recognize the failure patterns that silently harm search visibility."
---
# SEO Common Antipatterns

## Purpose

A catalog of the technical-SEO mistakes that recur across codebases, each with why it is
wrong and the concrete fix. These are the failures that pass every functional test and
still cut organic traffic. Use this list as a pattern library during review and
incident triage: match the symptom, apply the fix.

## Antipatterns

### 1. Blocking a URL in `robots.txt` to deindex it

- **Why it is wrong:** `Disallow` stops the crawler from *fetching* the URL, so it never
  sees the `noindex` tag on the page. A blocked URL can still be indexed (URL-only, no
  snippet) from external links, and now you cannot remove it because the removal signal
  is unreachable.
- **The fix:** To deindex, allow crawling and serve `noindex` (meta or `X-Robots-Tag`).
  Use `Disallow` only to save crawl budget on URLs you never want fetched — never as a
  deindexing tool. See [robots.txt](08-robots-txt.md).

### 2. Shipping indexable content that only exists after client-side rendering

- **Why it is wrong:** Content injected by JavaScript after load depends on the engine's
  render queue, which is delayed and not guaranteed. The first-wave HTML the crawler
  indexes may be an empty shell, so the page ranks for nothing.
- **The fix:** Server-render or statically generate anything that must rank; reserve
  client rendering for interactivity that need not appear in results. Verify with URL
  Inspection. See [Rendering](04-rendering.md), [JavaScript SEO](19-javascript-seo.md).

### 3. Cloaking — serving different content to bots and users

- **Why it is wrong:** Branching output on user-agent is a search-policy violation and
  untestable: the "SEO" path and the human path drift apart with no test to catch it,
  and the engine may penalize the whole site when it detects the divergence.
- **The fix:** Serve identical content to every client. If bots need rendered HTML, give
  the same server-rendered HTML to users too.

### 4. Missing or non-self-referential canonical

- **Why it is wrong:** Without a canonical, the engine guesses which of several
  duplicate URLs (query params, trailing slash, `http`/`https`) to index and may pick
  the wrong one, splitting ranking signals across variants.
- **The fix:** Emit exactly one absolute canonical per page; make it self-referential on
  the canonical URL and point variants at it. See [Canonicalization](06-canonicalization.md).

### 5. Changing URLs without a `301`

- **Why it is wrong:** The old URL now `404`s, and all accumulated link equity and
  bookmarks are lost. The new URL starts from zero, and external links break
  permanently.
- **The fix:** Add a permanent `301` from every old URL to its new equivalent, keep it
  forever, and update internal links to point at the final destination.

### 6. Soft 404s — returning `200` for missing content

- **Why it is wrong:** A "not found" page that returns `200 OK` gets crawled and indexed
  as real content, wasting crawl budget and polluting the index with empty pages.
- **The fix:** Return a genuine `404` (gone temporarily) or `410` (gone permanently) for
  missing resources; reserve `200` for real content.

### 7. Leaking `noindex` (or `Disallow: /`) from staging to production

- **Why it is wrong:** A `noindex` copied from a staging config, or a wildcard
  `Disallow: /` left in `robots.txt`, deindexes the entire site within days and takes
  weeks to recover — with no error thrown.
- **The fix:** Gate indexation directives on an explicit environment check, default
  production to indexable, and add a CI assertion that production returns
  `index,follow` and a non-blocking `robots.txt`.

### 8. Duplicate or empty titles and descriptions

- **Why it is wrong:** Reused or missing `<title>`/description tags make pages
  indistinguishable in results, suppress click-through, and can cause the engine to
  rewrite or drop your snippet.
- **The fix:** Generate a unique, descriptive `<title>` and meta description per page;
  assert non-empty, unique titles for representative routes in CI. See
  [Metadata](05-metadata.md).

### 9. Contradictory signals across the stack

- **Why it is wrong:** A sitemap listing `noindex` URLs, a canonical pointing at a
  redirected page, or an `X-Robots-Tag` that disagrees with the meta tag forces the
  engine to resolve the conflict arbitrarily — usually not in your favor.
- **The fix:** Derive all signals for a URL from one source of truth so status,
  canonical, robots directives, and sitemap membership cannot disagree.

### 10. Navigation and links that the crawler cannot follow

- **Why it is wrong:** Links implemented as `<button onclick>`, `<div>` handlers, or
  infinite scroll with no paginated URLs are invisible to the crawler, so linked pages
  are never discovered.
- **The fix:** Use real `<a href>` anchors for anything that must be crawlable; back
  infinite scroll with real, linkable paginated URLs. See [Links](17-links.md).

### 11. Blocking CSS/JS in `robots.txt`

- **Why it is wrong:** If the engine cannot fetch the CSS and JS needed to render the
  page, it renders a broken or empty layout and may misjudge mobile-friendliness and
  content.
- **The fix:** Allow the crawler to fetch the render-critical assets; only disallow
  truly private or infinite-space endpoints.

### 12. Marking up structured data that is not on the page

- **Why it is wrong:** JSON-LD describing content, ratings, or prices the user cannot see
  is a guidelines violation that can trigger a manual action and loss of rich results.
- **The fix:** Keep structured data a faithful reflection of visible on-page content;
  validate it and remove any claims the page does not actually display. See
  [Structured Data](09-structured-data.md).

## Related

- `knowledge/seo/00-overview.md`
- `knowledge/seo/04-rendering.md`
- `knowledge/seo/06-canonicalization.md`
- `knowledge/seo/08-robots-txt.md`
- `knowledge/seo/19-javascript-seo.md`
