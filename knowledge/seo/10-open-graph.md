---
id: seo/10-open-graph
topic: seo
slug: open-graph
title: "Open Graph"
type: doc
order: 10
status: ready
tags: [seo, open-graph]
related: [seo/11-twitter-cards, seo/05-metadata, seo/09-structured-data, seo/16-images]
when_to_use: "Read before adding social-share preview tags — when a page will be shared on Facebook, LinkedIn, Slack, WhatsApp, iMessage, or Discord."
---
# Open Graph

## Purpose

This document defines how to add Open Graph (OG) meta tags so that when a URL is shared on
social and messaging platforms, it renders a rich preview card with the intended title,
description, and image. It is written so an agent can produce a correct, per-page preview
instead of a blank or wrong-looking link.

Open Graph is a small meta-tag protocol (originally from Facebook) that most platforms —
Facebook, LinkedIn, Slack, Discord, WhatsApp, iMessage, Pinterest — read to build link
previews. It answers "how should this URL look when someone pastes it into a feed or chat?"

## Why It Matters

A shared link with a good preview card gets far more clicks than a bare URL; a broken one
(no image, wrong title, another page's thumbnail) signals low quality and suppresses
engagement. Open Graph is *not* a Google ranking factor, but shares drive real referral
traffic, and the preview is often a user's first impression of the page. The tags are also
cached aggressively by each platform, so a mistake sticks around until the cache is
manually cleared — making it worth getting right the first time.

## Core Principles

- **Every share-worthy page needs its own OG tags.** Preview data must be per-page, not a
  single site-wide default, or every link looks identical.
- **`og:image` must be absolute and publicly reachable.** Crawlers fetch it from the open
  internet with no cookies; a relative path or an auth-gated image renders no thumbnail.
- **Four tags are effectively required:** `og:title`, `og:type`, `og:image`, `og:url`.
  Add `og:description`; without these the platform falls back to guessing (often wrongly).
- **`og:url` should be the canonical URL.** It consolidates shares of tracking-param
  variants onto one address and keeps the preview stable.
- **Platforms cache previews.** Assume the first fetch is what users see for a long time;
  changes require an explicit cache refresh in the platform's debugger.

## Best Practices

- Set an absolute `og:image` (`https://…`) sized around **1200×630** (1.91:1) so it fills
  the large card without cropping; keep it under a few hundred KB in JPEG/PNG/WebP.
- Provide `og:image:width`, `og:image:height`, and `og:image:alt`. Dimensions let
  platforms render the card before the image loads; `alt` aids accessibility.
- Write a distinct `og:title` and `og:description` per page. They can differ from the SEO
  `<title>`/meta description — tune them for the social feed's shorter, punchier context.
- Set `og:type` accurately (`website`, `article`, `product`); `article` unlocks
  `article:published_time`, `article:author`, etc. for richer cards.
- Set `og:url` to the page's canonical URL and `og:site_name` to your brand.
- Keep OG tags in server-rendered HTML `<head>`. Social crawlers do **not** execute
  JavaScript, so client-injected tags are invisible to them.
- Validate every template in the Facebook Sharing Debugger and LinkedIn Post Inspector,
  and use them to force a cache refresh after changes.

## Examples

**Good Example** — per-page, absolute image, canonical URL, sized

```html
<head>
  <!-- Distinct per page; server-rendered so social crawlers (no JS) can read it. -->
  <meta property="og:title" content="Trail Runner 3 — Lightweight Trail Shoe" />
  <meta property="og:description" content="A 220g trail shoe with a 6mm drop and grippy lugs." />
  <meta property="og:type" content="product" />
  <meta property="og:url" content="https://example.com/shoes/trail-runner-3" /> <!-- canonical -->
  <!-- Absolute, public, 1200x630 → renders the large card reliably. -->
  <meta property="og:image" content="https://example.com/img/trail-runner-3-og.jpg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Blue Trail Runner 3 shoe on a rocky path" />
  <meta property="og:site_name" content="Example Outfitters" />
</head>
```

**Bad Example** — relative image, site-wide defaults, JS-injected

```html
<head>
  <!-- Same generic tags on every page → every shared link looks identical. -->
  <meta property="og:title" content="Example Outfitters" />
  <!-- Relative path: social crawler can't resolve it → no thumbnail. -->
  <meta property="og:image" content="/logo.png" />
  <!-- og:url points to the homepage, not this page → shares consolidate wrongly. -->
  <meta property="og:url" content="https://example.com/" />
</head>
<script>
  // Injected client-side: social crawlers don't run JS, so these never apply.
  setOgTag("og:description", product.summary);
</script>
```

## Common Mistakes

- Relative or auth-gated `og:image`, producing a card with no thumbnail.
- One set of default OG tags for the whole site, so every shared page looks the same.
- Injecting OG tags with client-side JavaScript, which social crawlers never execute.
- Omitting image dimensions, causing a slow or wrongly-cropped preview.
- `og:url` set to the homepage or a tracking-param variant instead of the canonical URL.
- Assuming an edit shows up immediately, forgetting each platform caches the old preview.

## Production Tips

- Generate OG tags from the same data as the page and canonical logic so they never drift.
- After changing a template, re-scrape the URL in the Facebook Sharing Debugger to bust the
  cache before users share it.
- Serve a per-page image where possible (product photo, article hero); fall back to a
  branded default only when no specific image exists.

## AI Review Checklist

- Does each share-worthy page emit its own `og:title`, `og:type`, `og:image`, `og:url`?
- Is `og:image` an absolute, publicly reachable URL around 1200×630 with width/height set?
- Is `og:url` the page's canonical URL?
- Are OG tags server-rendered in `<head>`, not injected by client JavaScript?
- Are titles/descriptions tuned per page rather than a single site-wide default?
- Was the template validated (and cache-refreshed) in a sharing debugger?

## Related

- `knowledge/seo/11-twitter-cards.md`
- `knowledge/seo/05-metadata.md`
- `knowledge/seo/09-structured-data.md`
- `knowledge/seo/16-images.md`
