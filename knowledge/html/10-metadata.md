---
id: html/10-metadata
topic: html
slug: metadata
title: "HTML Metadata"
type: doc
order: 10
status: ready
tags: [html, metadata, "og:image", charset, "og:title", "og:type", nofollow, "og:url"]
related: [html/01-document-structure, html/12-seo, html/13-structured-data, html/11-accessibility]
when_to_use: "Read before setting up a page's <head>, social previews, or viewport behaviour."
---
# HTML Metadata

## Purpose

This document defines what belongs in the document `<head>`: the character encoding,
viewport, page title and description, canonical URL, and social-share (Open Graph /
Twitter) tags. Metadata is information *about* the page that users never see directly but
that browsers, search engines, and social platforms depend on to render, index, and
share it correctly.

## Why It Matters

The `<head>` is parsed before anything renders, so mistakes here have outsized effects.
A missing `charset` can garble every non-ASCII character; a missing viewport makes the
whole site unusable on phones; a wrong or absent `<title>` sinks search ranking and
confuses users with a dozen identical browser tabs. Social tags decide whether a shared
link shows a rich card or a bare URL — a link with no Open Graph image gets far fewer
clicks. This is cheap to get right and expensive to get wrong, because it is invisible
until someone reports the symptom.

## Core Principles

- **`charset` must be UTF-8 and come first.** Put `<meta charset="utf-8">` within the
  first 1024 bytes of `<head>`, before any content, so the parser decodes text correctly.
- **Set the viewport for responsive layout.** Include
  `<meta name="viewport" content="width=device-width, initial-scale=1">` or mobile
  browsers render at a fake 980px width and zoom out.
- **Every page has a unique, descriptive `<title>`.** It names the tab, the bookmark,
  and the search result. Front-load the distinctive part; keep it under ~60 characters.
- **Declare a canonical URL** with `<link rel="canonical">` when the same content is
  reachable at multiple URLs, to consolidate ranking and avoid duplicate-content issues.
- **Metadata belongs in `<head>`, content in `<body>`.** Only metadata elements
  (`<meta>`, `<title>`, `<link>`, `<base>`, `<style>`, `<script>`) go in `<head>`.

## Best Practices

- Provide a `<meta name="description">` (~150 characters) — search engines often use it
  as the snippet. Make it a genuine summary, not keyword stuffing.
- Add Open Graph tags (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`)
  and Twitter Card tags for rich link previews; use an absolute `og:image` URL and a
  ~1200x630 image.
- Do **not** disable zoom: avoid `maximum-scale=1` or `user-scalable=no` in the viewport
  — it blocks users who need to pinch-zoom and fails accessibility guidelines.
- Set `<html lang="…">` (document language) — technically on `<html>`, but it is core
  page metadata for screen readers and translation. Use `dir` for RTL languages.
- Add `<link rel="icon">` (and `apple-touch-icon`) for a favicon; reference a web app
  manifest with `<link rel="manifest">` for installable PWAs.
- Use `<meta name="robots">` deliberately (`noindex`, `nofollow`) only when you truly
  want a page excluded; the default is index/follow.

## Examples

**Good Example** — complete, accessible, share-ready head

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">                                   <!-- first: decodes text -->
  <meta name="viewport" content="width=device-width, initial-scale=1"> <!-- responsive -->
  <title>Pricing — Acme Analytics</title>                  <!-- unique, front-loaded -->
  <meta name="description" content="Simple per-seat pricing for Acme Analytics, with a free tier.">
  <link rel="canonical" href="https://acme.example/pricing">
  <!-- Rich social preview -->
  <meta property="og:title" content="Pricing — Acme Analytics">
  <meta property="og:image" content="https://acme.example/og/pricing.png">
  <meta property="og:url" content="https://acme.example/pricing">
</head>
```

**Bad Example** — garbled text, unusable on mobile, zoom disabled

```html
<head>
  <!-- No charset near the top: non-ASCII characters may render as mojibake.
       Zoom is disabled, failing accessibility. Title is generic and shared
       across every page, hurting SEO and tab identification. -->
  <meta name="viewport" content="width=device-width, user-scalable=no">
  <title>Home</title>
  <meta charset="utf-8"> <!-- too late; belongs first -->
</head>
```

## Common Mistakes

- Placing `<meta charset>` late (or omitting it), causing encoding corruption.
- No viewport meta, so the site renders zoomed-out and unusable on phones.
- Disabling pinch-zoom with `user-scalable=no`/`maximum-scale=1` (accessibility failure).
- Reusing one generic `<title>` across all pages.
- Absent or duplicate content served without a `rel="canonical"`.
- Open Graph `og:image` using a relative URL (crawlers require absolute).
- Missing `<html lang>`, degrading screen-reader pronunciation and translation.

## Production Tips

- Generate `<title>`/description/OG tags per route so each page is unique and shareable.
- Validate share cards with the platform debuggers before launch; cached bad previews
  are hard to purge.
- Keep a single source of truth for the site name and base URL to avoid drift between
  `<title>`, `og:title`, and canonical.
- Serve the correct `Content-Type: text/html; charset=utf-8` header too — headers win
  over the meta tag.

## AI Review Checklist

- Is `<meta charset="utf-8">` the first thing in `<head>`?
- Is a responsive viewport meta present *without* disabling zoom?
- Does the page have a unique, descriptive `<title>` under ~60 characters?
- Is a `<meta name="description">` present and genuinely summarising the page?
- Are Open Graph/Twitter tags set with an absolute `og:image` URL?
- Is `<link rel="canonical">` declared where duplicate URLs exist?
- Is `<html lang>` set (and `dir` for RTL)?

## Related

- `knowledge/html/01-document-structure.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/12-seo.md`
- `knowledge/html/13-structured-data.md`
