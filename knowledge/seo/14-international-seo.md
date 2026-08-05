---
id: seo/14-international-seo
topic: seo
slug: international-seo
title: "International SEO"
type: doc
order: 14
status: ready
tags: [seo, international-seo, hreflang, x-default, Link, lang]
related: [seo/06-canonicalization, seo/05-metadata, seo/07-sitemaps, seo/03-indexing, seo/15-local-seo]
when_to_use: "Read before adding languages or country variants of a site, or when duplicate/wrong-language pages appear in results."
---
# International SEO

## Purpose

This document defines how to serve a site in multiple languages or regions so search
engines index each variant, show the right one to each user, and do not treat the
variants as duplicates. It covers URL structure, `hreflang` annotations, and the signals
that keep a `en-US` page from cannibalizing its `en-GB` twin.

International SEO is where [canonicalization](06-canonicalization.md) meets localization:
each variant is unique content that must not be collapsed into one canonical, yet the
engine must understand they are alternates of each other.

## Why It Matters

Multi-region sites fail in predictable, silent ways. Without correct annotations, Google
sees `/en/` and `/en-gb/` as near-duplicates and indexes only one — so half your market
gets the wrong currency, spelling, or shipping copy, or no result at all. Worse, an
untranslated page with a `hreflang` pointing to it can send Spanish users to an English
page, tanking engagement in that market. These errors do not throw; they quietly leak
traffic and revenue from exactly the markets you paid to enter. The annotations are cheap
to add at build time and painful to reconcile once thousands of URLs are live.

## Core Principles

- **Pick one URL strategy and keep it consistent.** The options, strongest geo-signal
  first: country-code top-level domains (`example.de`), subdomains (`de.example.com`),
  or subdirectories (`example.com/de/`). Subdirectories on one domain are usually best
  for engineering simplicity and shared domain authority. Never split the same content
  across strategies.
- **`hreflang` is reciprocal and complete.** Every variant must list *every* variant,
  including a self-reference. If A points to B but B does not point back to A, the engine
  ignores the annotation.
- **Language and region are separate.** Use ISO 639-1 language codes optionally with an
  ISO 3166-1 region (`en`, `en-GB`, `es-419`). Region alone is invalid.
- **Provide `x-default`.** A `hreflang="x-default"` entry names the fallback page for
  users whose language/region you do not target — usually a language selector or your
  primary market.
- **Translate the content, not just the tag.** `hreflang` describes reality; it does not
  create it. Pointing a tag at machine-garbled or English-only text hurts the target
  market.

## Best Practices

- Emit `hreflang` in one place — HTML `<head>` link tags, the XML sitemap, or the HTTP
  `Link` header — and keep it consistent. The sitemap approach scales best for large
  sites because it centralizes the reciprocal map.
- Keep each variant self-canonical: the `en-GB` page's canonical points to *itself*, not
  to `en-US`. A cross-language canonical deindexes the variant (see
  [Canonicalization](06-canonicalization.md)).
- Do not auto-redirect by IP or `Accept-Language` in a way that traps crawlers or users.
  Googlebot crawls from the US; a hard geo-redirect can hide your whole non-US site.
  Prefer a dismissible banner suggesting the local version.
- Localize metadata too: translate titles and descriptions (see [Metadata](05-metadata.md))
  and localize structured data (currency, price, availability).
- Use `lang` on the `<html>` element (`<html lang="de">`) so browsers and assistive tech
  render correctly; it also reinforces the language signal.
- For region-specific storefronts, pair with [Local SEO](15-local-seo.md) signals
  (address, currency, local business data) per market.

## Examples

**Good Example** — reciprocal, self-referencing, with x-default

```html
<!-- On every one of these three pages, emit the SAME complete set below. -->
<link rel="alternate" hreflang="en-US" href="https://example.com/us/" />
<link rel="alternate" hreflang="en-GB" href="https://example.com/uk/" />
<link rel="alternate" hreflang="es-ES" href="https://example.com/es/" />
<!-- Fallback for everyone else (e.g. a language picker) -->
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
<!-- Each page canonicals to ITSELF, not to another language -->
<link rel="canonical" href="https://example.com/uk/" />
```

**Bad Example** — non-reciprocal, cross-language canonical

```html
<!-- On /uk/ only, pointing outward but /us/ never points back → tag ignored -->
<link rel="alternate" hreflang="en-us" href="https://example.com/us/" />
<!-- Region-only code "gb" is invalid; must be a language like en-GB -->
<link rel="alternate" hreflang="gb" href="https://example.com/uk/" />
<!-- Canonical points to the US page → the UK page gets deindexed -->
<link rel="canonical" href="https://example.com/us/" />
```

## Common Mistakes

- Non-reciprocal `hreflang`: return links missing, so the whole annotation is discarded.
- Using a region code (`gb`, `us`) where a language code (`en`) is required.
- Pointing each variant's canonical at one "main" language, collapsing the set to one URL.
- Hard IP/`Accept-Language` redirects that hide non-US variants from the US-based crawler.
- Missing `x-default`, leaving untargeted users with no defined fallback.
- Adding `hreflang` to pages that are not actually translated.

## Production Tips

- Validate `hreflang` in CI or with the Search Console International Targeting / coverage
  reports; broken reciprocity shows up as "no return tags" errors.
- Generate the reciprocal map programmatically from a single source of truth (a locale
  registry), never hand-maintained per page — hand-maintenance drifts and breaks
  reciprocity.
- After launching a new locale, submit its URLs in a locale-specific sitemap (see
  [Sitemaps](07-sitemaps.md)) to speed discovery.

## AI Review Checklist

- Does every variant list every other variant plus a self-reference (reciprocal)?
- Are language codes valid ISO 639-1, with region only as an optional suffix?
- Is an `x-default` entry present?
- Does each variant canonical to itself, not to another language/region?
- Is the URL strategy (ccTLD / subdomain / subdirectory) consistent site-wide?
- Are geo-redirects avoided or made non-trapping so the crawler can reach all locales?

## Related

- `knowledge/seo/06-canonicalization.md`
- `knowledge/seo/05-metadata.md`
- `knowledge/seo/07-sitemaps.md`
- `knowledge/seo/03-indexing.md`
- `knowledge/seo/15-local-seo.md`
