---
id: seo/00-overview
topic: seo
slug: overview
title: "Overview"
type: doc
order: 0
status: ready
tags: [seo, overview]
related: [seo/01-seo-fundamentals, seo/02-crawling, seo/03-indexing, seo/04-rendering, seo/05-metadata]
when_to_use: "Read first when starting any SEO work, to see how the topic's docs fit together."
---
# Overview

## Purpose

This document orients you to the `seo` topic: what search engine optimization means
for an engineer, and how the individual docs in this folder connect. It is a map, not a
concept doc — read it first, then jump to the specific doc for the task in front of you.

SEO here means **technical SEO**: making a site's pages discoverable, crawlable,
renderable, and correctly represented to search engines and social platforms. It does
*not* mean keyword-stuffing, link schemes, or gaming ranking signals. An agent that
follows these docs produces markup and infrastructure that search engines can consume
without ambiguity — which is the only part of ranking an engineer actually controls.

## Why It Matters

A page that a search engine cannot crawl, render, or interpret does not exist to that
engine, no matter how good its content is. Technical SEO failures are silent: the app
works perfectly for humans while robots see a blank page, a duplicate, or a `noindex`
tag committed by accident. These bugs surface weeks later as a traffic collapse that is
hard to trace. Getting the machine-readable layer right — status codes, canonicals,
metadata, structured data — is cheap up front and expensive to retrofit.

## Core Principles

- **Serve robots the same content you serve users.** Cloaking (different content by
  user-agent) is a policy violation and a maintenance trap. Parity is the default.
- **Every indexable URL returns one canonical, `200 OK`, self-consistent response.**
  One piece of content, one URL, one canonical signal.
- **Signals must agree.** The HTTP status, `robots` meta, `X-Robots-Tag`, canonical
  link, and sitemap entry for a URL must tell the same story. Contradictions get
  resolved unpredictably by the engine.
- **Make intent explicit in markup, not in hope.** Say `noindex` when you mean it; set
  `hreflang` when you have translations. Do not rely on the engine to guess.

## How These Docs Fit Together

The topic follows the search engine pipeline — the journey from a URL to a ranked result:

- **[SEO Fundamentals](01-seo-fundamentals.md)** — the mental model: crawl → render →
  index → rank, and where engineers have leverage. Start here for concepts.
- **[Crawling](02-crawling.md)** — how bots discover and fetch URLs; robots.txt, crawl
  budget, status codes, and link discoverability.
- **[Indexing](03-indexing.md)** — how fetched pages enter (or are excluded from) the
  index; `noindex`, canonicals, duplicate handling.
- **[Rendering](04-rendering.md)** — how JavaScript pages become HTML the engine can
  index; SSR, hydration, and the two-wave rendering trap.
- **[Metadata](05-metadata.md)** — titles, descriptions, and the `<head>` tags that
  control how a page appears in results.

Supporting docs go deeper on specific surfaces:
[Canonicalization](06-canonicalization.md), [Sitemaps](07-sitemaps.md),
[robots.txt](08-robots-txt.md), [Structured Data](09-structured-data.md),
[Open Graph](10-open-graph.md), [JavaScript SEO](19-javascript-seo.md),
[Core Web Vitals](13-core-web-vitals.md), and [Search Console](22-search-console.md).

## Best Practices

- Treat SEO as a code concern reviewed in PRs, not a marketing task done after launch.
  A broken canonical is a bug like any other.
- Verify rendered output with the tool the engine uses (Search Console URL Inspection),
  not the raw HTML you authored — they can differ when JavaScript is involved.
- Change indexation signals deliberately and one at a time. A stray `Disallow: /` or
  global `noindex` can deindex a site in days and take weeks to recover.

## Common Mistakes

- Reading these docs as ranking hacks. They cover the mechanics engines rely on; they
  do not promise position one.
- Shipping a client-only SPA and assuming the crawler runs your JavaScript reliably
  (see [Rendering](04-rendering.md)).
- Contradicting yourself across signals — e.g., a sitemap listing URLs marked
  `noindex`.

## AI Review Checklist

- Does the change touch a URL's crawlability, indexability, rendering, or metadata? If
  so, was the matching doc in this folder consulted?
- Do all indexation signals for the affected URLs agree?
- Is robot-visible content the same as user-visible content?
- Are indexation-affecting changes (robots.txt, `noindex`, canonicals) reviewed as
  deliberately as security changes?

## Related

- `knowledge/seo/01-seo-fundamentals.md`
- `knowledge/seo/02-crawling.md`
- `knowledge/seo/03-indexing.md`
- `knowledge/seo/04-rendering.md`
- `knowledge/seo/05-metadata.md`
