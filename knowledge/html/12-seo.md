---
id: html/12-seo
topic: html
slug: seo
title: "HTML SEO"
type: doc
order: 12
status: ready
tags: [html, seo]
related: [html/10-metadata, html/13-structured-data, html/02-semantic-html, html/11-accessibility, html/05-images, html/18-performance]
when_to_use: "Read before shipping any public page that should rank in search or preview correctly when shared."
---
# HTML SEO

## Purpose

This document defines the HTML an agent must emit so a page is *discoverable*,
*indexable*, and *correctly summarized* by search engines and social crawlers. It
covers titles, meta descriptions, canonical URLs, crawl directives, headings, and
link semantics — the markup crawlers read, not the ranking algorithm you cannot see.

SEO here means the on-page HTML contract. Off-page factors (backlinks, page speed,
authority) live elsewhere; see [performance](18-performance.md) for Core Web Vitals.
This doc is about the tags that decide whether a page is indexed at all and how it
appears in results.

## Why It Matters

A crawler is a machine reader with no human judgment. If your HTML is ambiguous, it
guesses — and the guess is usually wrong. A missing `<title>` gives you a URL as your
headline. A missing canonical splits ranking signals across duplicate URLs. A stray
`noindex` silently removes a page from the index and no error is ever thrown. These
mistakes are invisible in the browser: the page looks perfect while it ranks nowhere.
Because the failure is silent and the cost is lost traffic over weeks, SEO markup is
worth getting right the first time.

## Core Principles

- **One page, one indexable identity.** Each page needs exactly one `<title>`, one
  `<h1>`, and one canonical URL. Duplicate identities dilute or confuse ranking.
- **Say what you mean to the crawler explicitly.** `robots`, `canonical`, and
  `hreflang` are directives, not hints. If you do not set them, the crawler decides.
- **Content must be in the HTML, not only in JavaScript.** Crawlers index what the
  server renders. Client-only content may be seen late, partially, or never.
- **Semantics carry meaning.** A heading outline, real `<a href>` links, and
  descriptive `alt` text tell the crawler what the page is about. Divs tell it nothing.
- **Never block what you want indexed.** A single misconfigured `robots` rule or
  `robots.txt` entry can deindex an entire section.

## Best Practices

- Give every page a unique, descriptive `<title>` (roughly 50–60 characters) with the
  primary keyword near the front. It is the clickable headline in results.
- Write a unique `<meta name="description">` (~150–160 characters). It is not a ranking
  factor but it is the snippet users decide to click.
- Set a self-referencing `<link rel="canonical" href="…">` with an absolute URL on
  every page to consolidate duplicate URLs (tracking params, trailing slashes).
- Use exactly one `<h1>` and a logical `<h2>`/`<h3>` outline that mirrors the content
  structure — do not pick heading levels for their font size.
- Make internal links real `<a href="…">` with descriptive anchor text. Crawlers follow
  `href`; they do not click `onClick` handlers or `<span role="link">`.
- Add Open Graph (`og:title`, `og:description`, `og:image`, `og:url`) and
  `twitter:card` tags so shared links render a rich preview.
- Use `<meta name="robots">` deliberately: `index,follow` for public pages,
  `noindex,follow` for thin/duplicate pages you still want crawled.
- For multilingual sites, declare `<link rel="alternate" hreflang="…">` for every
  language variant, including a self-reference and `x-default`.
- Give images meaningful `alt` text and descriptive filenames; this feeds image search.

## Examples

**Good Example** — explicit identity, self-canonical, real semantics

```html
<head>
  <title>Argon2 vs bcrypt: Choosing a Password Hash (2026)</title>
  <!-- Unique, front-loaded keyword, under 60 chars -->
  <meta name="description" content="A practical comparison of Argon2id and bcrypt for password hashing, with tuning guidance and migration steps.">
  <link rel="canonical" href="https://example.com/blog/argon2-vs-bcrypt">
  <!-- Absolute self-canonical: collapses ?utm_* duplicates into one URL -->
  <meta name="robots" content="index,follow">
  <meta property="og:title" content="Argon2 vs bcrypt: Choosing a Password Hash">
  <meta property="og:image" content="https://example.com/img/argon2-cover.png">
</head>
<body>
  <h1>Argon2 vs bcrypt</h1>        <!-- exactly one h1, describes the page -->
  <a href="/blog/password-tuning">Read the tuning guide</a>  <!-- crawlable link -->
</body>
```

**Bad Example** — no identity, JS-only content, fake links

```html
<head>
  <title>Home</title>                 <!-- generic; every page is "Home" -->
  <!-- no meta description → search snippet is scraped at random -->
  <!-- no canonical → ?utm=... variants ranked as separate duplicate pages -->
</head>
<body>
  <div id="root"></div>               <!-- content injected by JS after load -->
  <h1>Blog</h1><h1>Latest Posts</h1>  <!-- two h1s, no clear topic -->
  <span onclick="go('/post/1')">Read more</span> <!-- not an <a href>; uncrawlable -->
</body>
```

## Common Mistakes

- Reusing one `<title>`/description across many pages, so results look identical.
- Shipping content only client-side and assuming the crawler runs your JavaScript fully.
- Forgetting `rel="canonical"`, letting tracking parameters create duplicate URLs.
- Leaving a `noindex` from staging in production, silently deindexing the page.
- Blocking CSS/JS in `robots.txt`, so the crawler cannot render the page as users see it.
- Using multiple `<h1>` tags or skipping heading levels, breaking the topical outline.
- Anchor text like "click here" that describes nothing to the crawler.

## Production Tips

- Verify each template in Google Search Console's URL Inspection and check the *rendered*
  HTML, not just the source — confirm your content survived rendering.
- Generate and submit an XML sitemap; keep it in sync with published, indexable URLs.
- After a launch, grep the built HTML for accidental `noindex` and for missing
  `canonical` before deploy — both fail silently in the browser.
- Redirect (301) old URLs on any slug change; never let two live URLs serve the same page.

## AI Review Checklist

- Does every page have a unique, descriptive `<title>` and `<meta name="description">`?
- Is there exactly one `<h1>` and a logical heading outline?
- Does each page carry a self-referencing absolute `rel="canonical"`?
- Is primary content present in server-rendered HTML, not only injected by JS?
- Are internal links real `<a href>` with descriptive anchor text?
- Are `robots` directives intentional, with no stray `noindex` in production?
- Are Open Graph / Twitter card tags present for share previews?

## Related


- `knowledge/html/10-metadata.md`
- `knowledge/html/13-structured-data.md`
- `knowledge/html/02-semantic-html.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/05-images.md`
- `knowledge/html/18-performance.md`
