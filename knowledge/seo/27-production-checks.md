---
id: seo/27-production-checks
topic: seo
slug: production-checks
title: "Production Checks"
type: doc
order: 27
status: ready
tags: [seo, production-checks, noindex, robots.txt, X-Robots-Tag, robots]
related: [seo/98-production-checklist, seo/24-monitoring, seo/23-audits, seo/13-core-web-vitals, seo/03-indexing]
when_to_use: "Read before promoting a build to production or wiring SEO gates into a CI/CD pipeline."
---
# Production Checks

## Purpose

This document defines the automated checks that must pass before a page reaches
production and the verifications that run against production immediately after a deploy.
It turns the [best practices](26-best-practices.md) baseline into machine-verifiable gates
so an SEO regression fails a build instead of quietly shipping.

Where [monitoring](24-monitoring.md) watches production continuously and an
[audit](23-audits.md) is a periodic deep review, production checks are the fast,
deterministic gate at the moment of release — the last place a regression is cheap to fix.

## Why It Matters

The most damaging SEO bugs are configuration mistakes that ship with an otherwise-working
feature: a staging `noindex` that leaks to prod, a `robots.txt` that blocks the whole
site, a canonical pointing at the wrong host, a redirect loop, a 500 on a key template.
Humans do not notice these in review because the page looks fine.

A deterministic check that fetches the page as a crawler and asserts on the exact
directives catches all of these in seconds, on every deploy, with no judgment required.
The cost of the gate is one CI job; the cost of skipping it is weeks of lost indexing.

## Core Principles

- **Assert as the crawler sees it.** Fetch with a bot user-agent, no cookies, following
  redirects, and check the *final* rendered HTML — not the developer's browser view.
- **Fail closed on ambiguity.** If a check cannot confirm a page is safe (unexpected
  status, missing canonical), block the deploy rather than assume it is fine.
- **Gate the templates that matter.** You cannot check every URL; check one representative
  URL per critical template plus the site-wide files (robots.txt, sitemap).
- **Check both pre-deploy and post-deploy.** Preview checks catch template bugs; a
  post-deploy smoke test catches environment and CDN/config differences.
- **Deterministic, not statistical.** Production gates assert exact values; leave
  trend-based judgment to monitoring.

## Best Practices

- Run these assertions against a preview deploy for each critical template: HTTP `200`,
  `robots` meta / `X-Robots-Tag` is not `noindex`, a self-referential canonical exists,
  a unique `<title>`, and the main content is present in the initial HTML.
- Validate `robots.txt`: it exists, returns `200`, and does not `Disallow: /` for
  Googlebot; validate the XML [sitemap](07-sitemaps.md) parses and lists canonical URLs.
- Check redirects: old paths that moved return `301` to the correct target, and there are
  no redirect chains or loops.
- Run [Core Web Vitals](13-core-web-vitals.md) budgets (e.g. Lighthouse CI) on key
  templates and fail on regressions past a threshold.
- After promotion, re-run a slim smoke test against production URLs to catch CDN, edge,
  or environment-only differences (a common source of prod-only `noindex`).
- Keep the gate fast and flake-free; a slow or flaky SEO check gets disabled, which is
  worse than no check.

## Examples

**Good Example** — a pre-deploy gate over critical templates

```ts
// CI step: assert crawler-visible SEO invariants on one URL per template.
// WHY: these five assertions catch the overwhelming majority of shipping SEO bugs
// deterministically, before the build is promoted.
const templates = ["/", "/products/sample-sku", "/blog/sample-post", "/pricing"];

for (const path of templates) {
  const res = await fetch(`${PREVIEW}${path}`, {
    headers: { "User-Agent": "Googlebot" },
    redirect: "follow",
  });
  const html = await res.text();

  assert(res.status === 200, `${path}: expected 200, got ${res.status}`);
  assert(!/noindex/i.test(html.match(/name="robots" content="([^"]*)"/i)?.[1] ?? ""),
    `${path}: unexpected noindex`);
  assert(/<link rel="canonical"/i.test(html), `${path}: missing canonical`);
  assert(/<title>[^<]{10,}<\/title>/i.test(html), `${path}: missing/short title`);
}

// Site-wide file: robots.txt must not block the whole site.
const robots = await (await fetch(`${PREVIEW}/robots.txt`)).text();
assert(!/User-agent:\s*\*[\s\S]*Disallow:\s*\/\s*$/im.test(robots), "robots blocks all");
```

**Bad Example** — a "check" that proves nothing

```ts
// Fetches the homepage in the CI runner's default browser context and only
// checks it loads. WHY THIS FAILS: no bot user-agent, no meta/canonical/status
// assertions, no per-template coverage, no robots/sitemap check → every real
// SEO regression sails straight through.
const ok = (await fetch(PREVIEW)).ok; // 200 OR 3xx both pass; noindex passes; etc.
if (!ok) throw new Error("site down");
// nothing else is verified
```

## Common Mistakes

- Checking pages in a normal browser context instead of as a bot, hiding SSR/robots bugs.
- Only checking the homepage; template-specific bugs (product, blog) slip through.
- Treating a `3xx` as success, masking redirect loops or wrong canonicals.
- Skipping the post-deploy smoke test, so prod-only config differences go undetected.
- No robots.txt / sitemap validation, allowing a site-wide block to ship.
- Flaky or slow checks that the team eventually disables.
- Gating on lab CWV only, with no field-data follow-up in monitoring.

## Production Tips

- Fail the build with a clear message naming the URL and the exact failed assertion, so
  the fix is obvious without re-running locally.
- Store the checked invariants next to the templates so they are updated when a template
  changes intentionally (e.g. a page that is *meant* to be `noindex`).
- Wire the post-deploy smoke test to auto-rollback or page on-call for the highest-value
  templates.

## AI Review Checklist

- Do checks fetch pages as a bot, follow redirects, and assert on the final HTML?
- Is there at least one checked URL per critical template, plus robots.txt and sitemap?
- Are status `200`, non-`noindex`, self-canonical, and unique title all asserted?
- Do moved paths assert a `301` with no chains or loops?
- Is there a post-deploy smoke test against real production URLs?
- Are Core Web Vitals budgets enforced on key templates?
- Does a failure block promotion and name the exact URL and assertion?

## Related

- `knowledge/seo/98-production-checklist.md`
- `knowledge/seo/24-monitoring.md`
- `knowledge/seo/23-audits.md`
- `knowledge/seo/13-core-web-vitals.md`
- `knowledge/seo/03-indexing.md`
