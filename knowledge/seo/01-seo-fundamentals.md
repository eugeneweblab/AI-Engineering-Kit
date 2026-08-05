---
id: seo/01-seo-fundamentals
topic: seo
slug: seo-fundamentals
title: "SEO Fundamentals"
type: doc
order: 1
status: ready
tags: [seo, seo-fundamentals, noindex]
related: [seo/02-crawling, seo/03-indexing, seo/04-rendering, seo/05-metadata, seo/00-overview]
when_to_use: "Read before any SEO task, to ground decisions in the crawl-render-index-rank pipeline."
---
# SEO Fundamentals

## Purpose

This document gives you the mental model every other `seo` doc builds on: the pipeline a
search engine runs to turn a URL into a ranked result, and where an engineer actually has
leverage. Read it so you can reason about *why* a technical change helps or hurts, rather
than copying tactics blindly.

The pipeline has four stages — **crawl → render → index → rank**. Engineers own the first
three almost entirely. Ranking is an engine's judgment call influenced by content and
authority; you cannot command it, but you can stop yourself from being disqualified before
it happens.

## Why It Matters

Most "SEO problems" engineers are asked to fix are really pipeline failures: a page that
was never crawled, rendered blank, got deduplicated away, or shipped with a broken title.
Without the model you treat symptoms — adding keywords to a page the crawler never
fetched. With the model you find the stage that failed and fix the cause. It also stops
the opposite error: chasing ranking magic when the real job is boring correctness that
either works or does not.

## Core Principles

- **You control eligibility, not ranking.** Your job is to make a page *qualify* —
  crawlable, renderable, indexable, correctly described. The engine decides position.
- **The pipeline is sequential; an early failure hides later work.** A page blocked at
  [crawl](02-crawling.md) never reaches [indexing](03-indexing.md). Diagnose in order.
- **Robots and users must see the same content.** Parity is the baseline; divergence
  (cloaking) is both a policy violation and a source of "works for me" bugs.
- **Ranking rewards genuine usefulness, not tricks.** Modern engines discount keyword
  density, hidden text, and link schemes. Optimize for the reader; make it legible to
  the machine.

## Best Practices

- Map any SEO issue to a pipeline stage before proposing a fix. "Not showing in Google"
  → is it crawled? rendered? indexed? Check in that order using Search Console.
- Give every important page a unique, descriptive `<title>` and meta description (see
  [Metadata](05-metadata.md)); these are the highest-leverage per-page signals.
- Ensure primary content is present in server-rendered HTML, not injected only by
  client JavaScript (see [Rendering](04-rendering.md)).
- Keep information architecture flat and linked: important pages within a few clicks of
  the homepage, reachable by crawlable `<a href>` links (see [Links](17-links.md)).
- Understand the audience-facing distinction between on-page technical SEO (your domain)
  and off-page authority signals like backlinks (mostly not code).

## Examples

**Good Example** — diagnosing a page missing from search, in pipeline order

```text
# 1. CRAWL: is the URL fetchable and allowed?
$ curl -sI https://example.com/product/42
HTTP/2 200                     # 200, not 4xx/5xx → crawlable
$ curl -s https://example.com/robots.txt | grep -i product
                               # no Disallow rule → allowed

# 2. RENDER: does fetched HTML contain the real content?
$ curl -s https://example.com/product/42 | grep -c "Add to cart"
1                              # content in HTML, not JS-only → renderable

# 3. INDEX: does the page invite indexing?
$ curl -s https://example.com/product/42 | grep -i 'name="robots"'
<meta name="robots" content="index,follow">   # not noindex → indexable
# Only after all three pass does ranking even apply.
```

**Bad Example** — jumping to ranking tactics before checking the pipeline

```html
<!-- Page isn't in Google, so someone stuffs keywords into hidden text. -->
<div style="display:none">
  cheap shoes buy shoes best shoes shoes online discount shoes
</div>
<!-- WHY this is wrong: the page returns 404 to the crawler, so it was never
     eligible to rank. The hidden text fixes nothing and, if the page were
     crawled, would be flagged as manipulative spam. Diagnose the stage first. -->
```

## Common Mistakes

- Treating SEO as keyword density instead of pipeline correctness plus useful content.
- Skipping stages: optimizing content on a page that is blocked, broken, or `noindex`.
- Assuming the crawler runs JavaScript exactly like a modern browser (see
  [JavaScript SEO](19-javascript-seo.md)); it renders later, and sometimes not at all.
- Confusing what you control (technical eligibility) with what you request (ranking).

## AI Review Checklist

- Does the proposed change target the pipeline stage that is actually failing?
- Is the primary content present in the server response, not only client-injected?
- Do robots and users receive the same content (no cloaking)?
- Does every important page have a unique title and description?
- Are important pages reachable via crawlable links within a few clicks of the homepage?

## Related

- `knowledge/seo/02-crawling.md`
- `knowledge/seo/03-indexing.md`
- `knowledge/seo/04-rendering.md`
- `knowledge/seo/05-metadata.md`
- `knowledge/seo/00-overview.md`
