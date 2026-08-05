---
id: seo/99-ai-review-checklist
topic: seo
slug: ai-review-checklist
title: "SEO AI Review Checklist"
type: doc
order: 99
status: ready
tags: [seo, ai-review-checklist]
related: [seo/00-overview, seo/30-engineering-principles, seo/29-seo-review, seo/03-indexing, seo/06-canonicalization]
when_to_use: "Read when reviewing a diff that touches routing, rendering, metadata, or any crawl/index signal."
---
# SEO AI Review Checklist

## Purpose

A focused checklist for reviewing a *code change* for SEO correctness, aimed at an AI
agent reviewing a diff. Unlike the [production checklist](98-production-checklist.md),
which validates a running site, this catches regressions in the pull request — before
they ship and become a slow, hard-to-trace traffic loss. Each item is a yes/no question
answerable from the diff and its context. A "no" is a review blocker unless justified.

## Scope: Does This Change Touch SEO At All?

- [ ] Does the diff change routing, redirects, URL structure, or trailing-slash/casing
  behavior?
- [ ] Does it change rendering strategy (SSR ↔ CSR), hydration, or where content is
  produced?
- [ ] Does it touch `robots.txt`, `noindex`/`X-Robots-Tag`, canonicals, `hreflang`, or
  sitemaps?
- [ ] Does it change `<head>` metadata, structured data, or social tags?
- [ ] If none of the above, SEO review is not required — say so and move on.

## Indexation Signals

**Rules:** [Indexing](03-indexing.md) · [Robots Txt](08-robots-txt.md)

- [ ] Do all signals for each affected URL agree (HTTP status, `robots` meta,
  `X-Robots-Tag`, canonical, sitemap membership)?
- [ ] Is any new or changed `noindex` intentional, and gated so it can never apply to
  production indexable pages?
- [ ] Does the change avoid disallowing a URL in `robots.txt` that also needs a
  `noindex` read (blocked URLs are never fetched)?
- [ ] Is only one indexation signal changed at a time, or is a batched change justified
  and documented?

## URLs and Redirects

**Rules:** [Links](17-links.md) · [Canonicalization](06-canonicalization.md)

- [ ] If a URL changed, is there a permanent `301` from the old URL, with no chain or
  loop introduced?
- [ ] Are internal links updated to point at the final URL rather than through a
  redirect?
- [ ] Are new links real `<a href>` anchors the crawler can follow, not JS-only
  handlers?

## Canonicalization

**Rules:** [Canonicalization](06-canonicalization.md)

- [ ] Does each affected indexable page still emit exactly one absolute canonical?
- [ ] Is the canonical self-referential on canonical pages and correct on
  parameter/duplicate variants?
- [ ] Does the change avoid creating new indexable duplicates (query params, facets,
  sort orders)?

## Rendering and Content Parity

**Rules:** [Rendering](04-rendering.md) · [JavaScript SEO](19-javascript-seo.md)

- [ ] Does indexable content still exist in the server response without relying on
  client hydration?
- [ ] Does the change avoid branching content on user-agent (no cloaking)?
- [ ] Is robot-visible content identical to user-visible content after the change?

## Metadata and Structured Data

**Rules:** [Metadata](05-metadata.md) · [Structured Data](09-structured-data.md)

- [ ] Does every affected page keep a unique, non-empty `<title>` and description?
- [ ] Are `hreflang`, Open Graph, and Twitter tags still present, valid, and reciprocal
  where applicable?
- [ ] Does modified JSON-LD still validate and match the visible on-page content (no
  marked-up content the user cannot see)?

## Safety Net

**Rules:** [Search Console](22-search-console.md) · [Monitoring](24-monitoring.md)

- [ ] Are SEO invariants for the changed routes covered by (or added to) an automated
  test?
- [ ] For a risky indexation change, is there a rollback plan and post-deploy Search
  Console verification step?

## Related

- `knowledge/seo/00-overview.md`
- `knowledge/seo/30-engineering-principles.md`
- `knowledge/seo/29-seo-review.md`
- `knowledge/seo/03-indexing.md`
- `knowledge/seo/06-canonicalization.md`
