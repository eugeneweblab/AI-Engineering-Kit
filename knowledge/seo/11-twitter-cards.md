---
id: seo/11-twitter-cards
topic: seo
slug: twitter-cards
title: "Twitter Cards"
type: doc
order: 11
status: ready
tags: [seo, twitter-cards]
related: [seo/10-open-graph, seo/05-metadata, seo/09-structured-data, seo/16-images]
when_to_use: "Read before shipping share-preview markup for links posted on X/Twitter, when you need a large-image card instead of a plain link."
---
# Twitter Cards

## Purpose

This document defines how to add Twitter Card meta tags so a URL shared on X (Twitter)
renders a rich preview card with a title, description, and image. It is written so an agent
can produce the right card type without duplicating everything Open Graph already provides.

Twitter Cards are a small set of `<meta name="twitter:*">` tags that X reads to build link
previews. They layer on top of Open Graph: X falls back to OG tags for anything a
`twitter:` tag does not override, so the two are designed to work together, not compete.

## Why It Matters

On X, a `summary_large_image` card turns a bare link into a full-width image preview that
draws far more clicks than plain text. Getting the card type or image wrong yields a tiny
thumbnail or no card at all, wasting the visual real estate at the moment of sharing. Like
Open Graph, this is not a Google ranking factor, but it directly affects referral traffic
from X. And because X caches the card, a mistake persists until the URL is re-scraped.

## Core Principles

- **Twitter Cards extend Open Graph; do not duplicate what OG covers.** If `og:title`,
  `og:description`, and `og:image` are present, X uses them. Add `twitter:` tags only for
  what OG cannot express — chiefly `twitter:card`.
- **`twitter:card` selects the layout.** `summary_large_image` gives the big-image card;
  `summary` gives a small square thumbnail. Choosing the wrong one is the most common
  visible error.
- **The image must be absolute, public, and correctly proportioned.** X fetches it
  anonymously; a relative or gated URL renders no image.
- **Tags must be server-rendered.** The X crawler does not execute JavaScript; client-
  injected tags are invisible to it.
- **X caches cards.** The first successful scrape is what users see until you force a
  refresh in the Card Validator.

## Best Practices

- Set `twitter:card` to `summary_large_image` for content with a strong image (articles,
  products); use `summary` only for text-first pages without a good hero image.
- Rely on Open Graph for `title`, `description`, and `image`; add `twitter:title`/
  `twitter:description`/`twitter:image` **only** when you want X to show something different
  from the OG values.
- For `summary_large_image`, use an image at least **1200×628** (roughly 1.91:1), under
  5 MB, in JPG/PNG/WebP/GIF. Provide `twitter:image:alt` for accessibility.
- Add `twitter:site` (the site's `@handle`) and `twitter:creator` (the author's handle)
  so the card attributes correctly and can drive follows.
- Keep all tags in server-rendered `<head>` alongside the OG tags, generated from the same
  page data.
- Validate with the X/Twitter Card Validator on template changes; it also re-scrapes and
  refreshes the cached card.

## Examples

**Good Example** — large-image card, reuses OG, adds only what OG lacks

```html
<head>
  <!-- Open Graph carries title/description/image; X reads these as fallbacks. -->
  <meta property="og:title" content="Trail Runner 3 — Lightweight Trail Shoe" />
  <meta property="og:description" content="A 220g trail shoe with a 6mm drop." />
  <meta property="og:image" content="https://example.com/img/trail-runner-3-og.jpg" />

  <!-- twitter:card is the one thing OG can't express → the only required addition. -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:site" content="@ExampleOutfit" />
  <meta name="twitter:creator" content="@jane_writes" />
  <meta name="twitter:image:alt" content="Blue Trail Runner 3 shoe on a rocky path" />
</head>
```

**Bad Example** — wrong card type, relative image, redundant + JS-injected

```html
<head>
  <!-- No twitter:card → X defaults to a tiny "summary" thumbnail, wasting the hero. -->
  <!-- Relative image: the crawler can't resolve it → no picture at all. -->
  <meta name="twitter:image" content="/img/hero.jpg" />
  <!-- Duplicates OG title exactly → pointless extra tag to maintain. -->
  <meta name="twitter:title" content="Trail Runner 3 — Lightweight Trail Shoe" />
</head>
<script>
  // Injected client-side: the X crawler doesn't run JS, so this never applies.
  setMeta("twitter:card", "summary_large_image");
</script>
```

## Common Mistakes

- Omitting `twitter:card`, so X renders the small `summary` thumbnail instead of the large
  image.
- Duplicating every OG value with a `twitter:` equivalent, doubling maintenance for no gain.
- Relative or auth-gated `twitter:image`, producing a card with no image.
- Injecting card tags via JavaScript, which the X crawler never executes.
- Using `summary_large_image` with an image far off the ~1.91:1 ratio, causing heavy
  cropping.
- Expecting edits to appear instantly, forgetting X caches the card until re-scraped.

## Production Tips

- Emit `twitter:card` (and site/creator handles) once from a shared template, and let
  everything else fall through to Open Graph, so the two never drift.
- Re-run the Card Validator after template changes to bust X's cache before users share.
- Keep the same image pipeline as Open Graph — one well-sized social image satisfies both
  systems.

## AI Review Checklist

- Is `twitter:card` set (usually `summary_large_image`) so the intended layout renders?
- Do title/description/image come from Open Graph, with `twitter:` overrides only where
  they must differ?
- Is the card image absolute, public, and near 1.91:1 for large cards, with `image:alt`?
- Are `twitter:site` and, where relevant, `twitter:creator` handles present?
- Are the tags server-rendered in `<head>`, not injected by client JavaScript?
- Was the template checked in the Card Validator (which also refreshes the cache)?

## Related

- `knowledge/seo/10-open-graph.md`
- `knowledge/seo/05-metadata.md`
- `knowledge/seo/09-structured-data.md`
- `knowledge/seo/16-images.md`
