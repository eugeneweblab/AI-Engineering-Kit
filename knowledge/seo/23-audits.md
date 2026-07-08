---
id: seo/23-audits
topic: seo
slug: audits
title: "Audits"
type: doc
order: 23
status: ready
tags: [seo, audits]
related: [seo/22-search-console, seo/24-monitoring, seo/27-production-checks, seo/29-seo-review]
when_to_use: "Read before running a technical SEO audit, or wiring automated SEO checks into CI or a release gate."
---
# Audits

## Purpose

This document defines how to run a technical SEO audit: a systematic pass over a site (or
a change) to find crawlability, indexability, rendering, and metadata defects before they
cost traffic. It covers what to check, in what order, and how to automate the parts that
should never regress.

An audit is a repeatable inspection against a checklist, producing a prioritized list of
findings. The most valuable audits are not one-off consultancy PDFs but automated checks
wired into CI and monitoring, so regressions are caught the day they ship, not the quarter
they are discovered.

## Why It Matters

Technical SEO decays. A refactor drops a canonical, a template change adds a global
`noindex`, a migration breaks internal links, a new consent banner hides content. Each
change looks fine in the browser and passes functional tests, because none of it affects
the human-visible page. Without a deliberate audit, these defects accumulate silently and
surface as a slow traffic bleed that is expensive to trace back to its cause. An audit —
especially an automated one at the PR gate — converts these silent, cumulative failures
into loud, immediate, attributable ones.

## Core Principles

- **Audit in pipeline order.** Follow the engine's path: can it be crawled → rendered →
  indexed → understood → does it perform. A rendering defect makes downstream metadata
  checks meaningless, so fix upstream first.
- **Automate what should never regress; do manual review for judgment.** Status codes,
  canonicals, `noindex`, broken links, and structured-data validity are machine-checkable.
  Content quality and intent match need a human.
- **Prioritize by blast radius, not by count.** One template-level `noindex` outranks a
  hundred missing alt attributes. Fix site-wide, indexation-blocking issues first.
- **Audit the rendered HTML, not the source.** For JS sites, check what the crawler sees
  (see [Search Console](22-search-console.md) URL Inspection), because source and rendered
  output diverge.
- **An audit finding is a hypothesis until verified in Search Console.** Cross-check
  suspected indexing issues against the engine's actual view before acting.

## Best Practices

- Run a crawler (Screaming Frog, Sitebulb, or a headless-Chrome script) across the site
  and export: status codes, canonical tags, `robots` meta/`X-Robots-Tag`, `hreflang`,
  titles/descriptions, and internal-link graph.
- Check the indexation signals for agreement per URL: HTTP status, `robots`, canonical,
  and sitemap membership must tell one story (the overview's core rule).
- Validate structured data with the Rich Results Test / schema validator, and confirm it
  matches visible content.
- Compare `indexed` count and coverage exclusions in Search Console against your sitemap
  to find pages that should index but do not.
- Automate the non-negotiables in CI: a headless fetch of key routes asserting `200`,
  presence of `<h1>`/`<title>`/canonical, no accidental `noindex`, and valid JSON-LD.
- Re-audit after every migration, redesign, CMS change, or framework upgrade — these are
  when signals break in bulk.
- Prioritize findings as: (1) site-wide indexation blockers, (2) crawl/render failures,
  (3) duplicate/canonical issues, (4) metadata/structured-data gaps, (5) performance and
  polish.

## Examples

**Good Example** — a CI gate that fails on indexation regressions

```js
// Runs in CI against a preview deploy. Fetches rendered HTML for key routes
// and fails the build on any indexation-blocking regression — the day it ships.
import { chromium } from "playwright";

const ROUTES = ["/", "/pricing", "/blog/launch", "/products/widget"];

test("indexable routes stay indexable", async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const route of ROUTES) {
    const res = await page.goto(`${PREVIEW}${route}`);
    expect(res.status()).toBe(200);                              // no soft 404
    const html = await page.content();                          // rendered, not source
    expect(html).not.toMatch(/name="robots"[^>]*noindex/i);     // no stray noindex
    expect(await page.locator("h1").count()).toBeGreaterThan(0); // content present
    const canonical = await page.getAttribute("link[rel=canonical]", "href");
    expect(canonical).toBe(`https://example.com${route}`);       // self-canonical
  }
  await browser.close();
});
```

**Bad Example** — an audit that inspects source, not rendered output

```bash
# Grep the raw HTML for a canonical tag and call it a day.
curl -s https://example.com/products/widget | grep -q 'rel="canonical"' \
  && echo "PASS"

# Why it's wrong:
#  - This SPA injects the canonical AFTER hydration, so the source has none;
#    for a server-rendered route it might have the WRONG canonical and still "PASS".
#  - It never checks the value, the HTTP status, robots meta, or the rendered DOM.
#  - It passes while the page is, in the engine's eyes, non-canonical or noindexed.
```

## Common Mistakes

- Auditing raw source on JS sites instead of the rendered HTML the crawler indexes.
- Reporting findings by count, burying a template `noindex` under cosmetic nits.
- Treating the audit as a one-time deliverable rather than an automated, recurring gate.
- Not re-auditing after migrations and framework upgrades — the highest-risk moments.
- Flagging suspected indexing issues without confirming them in Search Console.
- Auditing production only, so regressions ship before anyone sees them; audit the
  preview deploy in CI too.

## Production Tips

- Keep a versioned audit checklist in the repo (see [production checks](27-production-checks.md))
  and a scheduled full crawl (weekly/monthly) feeding [monitoring](24-monitoring.md).
- Store each crawl's export so you can diff runs and attribute a regression to a specific
  deploy.
- Gate deploys on the automated subset; route the judgment-based findings to a human
  [SEO review](29-seo-review.md).

## AI Review Checklist

- Does the audit follow pipeline order (crawl → render → index → understand → perform)?
- Are indexation blockers prioritized by blast radius over cosmetic issues?
- Is the rendered HTML checked (not just source) for JS-rendered pages?
- Are the non-negotiables (status, canonical, `noindex`, JSON-LD) automated in CI?
- Are suspected indexing issues confirmed against Search Console before action?
- Is the audit re-run after migrations, redesigns, and framework upgrades?

## Related

- `knowledge/seo/22-search-console.md`
- `knowledge/seo/24-monitoring.md`
- `knowledge/seo/27-production-checks.md`
- `knowledge/seo/29-seo-review.md`
