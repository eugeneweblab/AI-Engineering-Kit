---
id: seo/29-seo-review
topic: seo
slug: seo-review
title: "SEO Review"
type: doc
order: 29
status: ready
tags: [seo, seo-review]
related: [seo/99-ai-review-checklist, seo/26-best-practices, seo/27-production-checks, seo/23-audits, seo/100-common-antipatterns]
when_to_use: "Read before reviewing a pull request or change that touches routing, rendering, metadata, redirects, or page content."
---
# SEO Review

## Purpose

This document defines how to *review* a change for SEO impact: what to look for in a diff,
how to prioritize findings, and how to decide whether a change is safe to ship. It is the
reviewer's counterpart to [best practices](26-best-practices.md) (what to build) and
[production checks](27-production-checks.md) (what to gate automatically).

It is written so an agent reviewing a pull request can catch SEO regressions that
automated checks miss — the ones that require reading intent, not just asserting values.

## Why It Matters

Most SEO damage enters through changes that were never framed as "SEO work": a routing
refactor, a rename, a caching tweak, a component that now loads content client-side. The
author was not thinking about crawlers, and neither was the reviewer, so a `noindex`, a
broken canonical, or a removed redirect slips through.

A reviewer who knows the small set of SEO-sensitive diffs — and treats them with the same
scrutiny as a security or data-migration change — prevents these regressions at the last
human checkpoint before they reach automated gates and, failing that, production.

## Core Principles

- **Review intent, not just correctness.** A `noindex` may be right or catastrophic — the
  diff alone does not say which. Confirm the author *meant* the SEO-visible effect.
- **Flag the SEO-sensitive surfaces every time.** Changes to routing, rendering strategy,
  meta/head, canonicals, redirects, robots/sitemap, and pagination always warrant a look.
- **Prioritize by blast radius.** A change to a shared layout or middleware affects every
  page; weight it far above a one-page tweak.
- **Verify as the crawler, not the author.** Ask for evidence from a bot-user-agent fetch
  or the URL Inspection tool, not a screenshot of the browser.
- **Prefer reversible and gated changes.** If a risky SEO change ships, ensure it is
  covered by a production check and monitored so it can be caught and rolled back.

## Best Practices

- On any diff, scan for these red flags: added `noindex`/`Disallow`, changed or removed
  `canonical`, deleted or altered redirects, a move from SSR/SSG to client rendering,
  changed URL structure, and `<title>`/meta changes on shared templates.
- When a URL changes, require the matching `301` redirect and updated internal links in the
  same PR — never approve a rename that orphans the old URL.
- When rendering moves client-side, require proof the content is in the server HTML (or an
  SSR/prerender path) before approving.
- For new indexable pages generated at scale, require the [content-quality](25-content-quality.md)
  gate (unique value, `noindex` fallback) to be present.
- Confirm structured-data and metadata changes still match visible content and are unique.
- Ask whether the change is covered by a [production check](27-production-checks.md); if
  not, request one for anything touching a critical template.

## Examples

**Good Example** — a review that questions intent and asks for crawler evidence

```diff
# PR: "Speed up category pages by rendering the product grid on the client"
- <ProductGrid products={products} />           # was server-rendered
+ <ProductGrid lazy clientOnly />               # now fetched after hydration

# Reviewer comment (WHY: the grid is the page's primary content and internal
# link source; client-only rendering can make products and their links invisible
# to crawlers):
# "This moves the main content + product links out of the server HTML. Please
#  confirm via a Googlebot fetch / URL Inspection that products still render for
#  the crawler, or keep SSR for the grid. Blocking until verified."
```

**Bad Example** — rubber-stamping an SEO-sensitive diff

```diff
# PR: "Clean up staging config"
- ROBOTS_DEFAULT = "index,follow"
+ ROBOTS_DEFAULT = "noindex,nofollow"   # meant for staging, applied globally

# Review: "LGTM 👍"
# WHY THIS FAILS: this one-line default flips the ENTIRE site to noindex. The
# reviewer treated a config cleanup as low-risk and never asked which
# environments consume ROBOTS_DEFAULT → site-wide deindexing on next deploy.
```

## Common Mistakes

- Treating routing, rendering, or config diffs as low-risk because they are not "SEO PRs".
- Approving a URL change without the paired `301` and internal-link updates.
- Accepting a browser screenshot as proof content is crawlable, instead of a bot fetch.
- Not weighting changes to shared layouts, middleware, or defaults by their blast radius.
- Missing added `noindex`/`Disallow` because the diff line looks innocuous.
- Approving mass page generation without a content-quality gate.
- Failing to request a production check for a risky change to a critical template.

## Production Tips

- Add a PR template checkbox: "Does this change routing, rendering, meta, canonicals,
  redirects, or robots/sitemap? If yes, attach crawler-fetch evidence."
- Use a CODEOWNERS rule so changes to head/meta components, redirect maps, robots.txt, and
  sitemap generation require an SEO-aware reviewer.
- Link the [common anti-patterns](100-common-antipatterns.md) list in the review template
  so reviewers scan against a concrete catalog.

## AI Review Checklist

- Does the diff add `noindex`/`Disallow`, and if so, is that intentional and scoped?
- Are canonical, redirect, and URL changes deliberate, with `301`s and link updates paired?
- If rendering moved client-side, is there proof the content is in the server HTML?
- Are changes to shared layouts, middleware, or defaults reviewed for site-wide impact?
- Do metadata/structured-data changes remain unique and match visible content?
- Are mass-generated indexable pages gated on content quality?
- Is the change covered by a production check and monitoring, or is one requested?

## Related

- `knowledge/seo/99-ai-review-checklist.md`
- `knowledge/seo/26-best-practices.md`
- `knowledge/seo/27-production-checks.md`
- `knowledge/seo/23-audits.md`
- `knowledge/seo/100-common-antipatterns.md`
