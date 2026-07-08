---
id: seo/24-monitoring
topic: seo
slug: monitoring
title: "Monitoring"
type: doc
order: 24
status: ready
tags: [seo, monitoring]
related: [seo/22-search-console, seo/21-analytics, seo/23-audits, seo/27-production-checks, seo/13-core-web-vitals]
when_to_use: "Read before setting up ongoing SEO health checks or alerting on organic traffic, indexing, or crawl regressions."
---
# Monitoring

## Purpose

This document defines how to continuously watch the SEO health of a site so that
regressions are caught in hours, not weeks. An [audit](23-audits.md) is a point-in-time
snapshot; monitoring is the standing alarm system that runs between audits and tells you
the moment something breaks.

Monitoring answers "did anything just get worse?" — for indexing, crawlability,
rankings, Core Web Vitals, and organic traffic. It is the difference between noticing a
`noindex` deploy the day it ships versus a month later when traffic has already
collapsed.

## Why It Matters

SEO regressions are silent and delayed. A bad deploy can add `noindex`, break a
canonical, orphan a section of the site, or block a JS bundle — and the page renders
perfectly to humans. Google may take days or weeks to drop the pages, and revenue drops
with them. By the time a human notices "traffic is down," the cause is buried under a
dozen unrelated changes.

Because the feedback loop from cause to symptom is so long, the only defense is
automated, continuous measurement with alerting on the *leading* indicators (indexed
count, crawl errors, meta directives) rather than the *lagging* one (traffic). Catch it
at deploy, not at the invoice.

## Core Principles

- **Alert on leading indicators, not just traffic.** Indexed-page count, `noindex`
  coverage, canonical targets, and crawl errors change before traffic does. Watch them.
- **Baseline, then diff.** Store a known-good snapshot of critical signals and alert on
  deviation, not on absolute values. "Sitemap dropped from 12,000 to 400 URLs" is
  actionable; "400 URLs" alone is not.
- **Monitor from the crawler's perspective.** Fetch pages with a bot user-agent and no
  cookies. What a logged-in human sees is not what Googlebot indexes.
- **Fail the deploy, not the audit.** The cheapest place to catch an SEO regression is CI,
  before it reaches production. Push checks left.
- **One signal, one owner, one threshold.** Every alert must be actionable and routed to
  someone who can fix it, or it will be ignored.

## Best Practices

- Track these signals on a schedule (at least daily): indexed URL count, `robots` meta
  and `X-Robots-Tag` on key templates, canonical targets, HTTP status of top URLs,
  sitemap URL count and freshness, and Core Web Vitals field data.
- Pull [Search Console](22-search-console.md) data via the API into your own store so you
  can alert and retain history beyond Google's 16-month window.
- Add synthetic checks that fetch each critical template with a Googlebot user-agent and
  assert on `<title>`, `<meta name="robots">`, canonical, and status 200.
- Set relative thresholds: alert if indexed count, sitemap size, or organic sessions move
  more than a set percentage versus the trailing baseline.
- Monitor Core Web Vitals from field data (CrUX / RUM), not only lab tools — lab numbers
  do not reflect real users and will not match what Google ranks on.
- Route alerts to the deploy channel and annotate dashboards with deploy timestamps so a
  regression can be tied to the change that caused it.

## Examples

**Good Example** — CI check that fails the build on an accidental `noindex`

```ts
// Runs against a preview deploy before promoting to production.
// WHY: catching a noindex here costs one red build; catching it in prod
// costs weeks of lost indexing and traffic.
const CRITICAL_PATHS = ["/", "/products", "/blog", "/pricing"];

for (const path of CRITICAL_PATHS) {
  const res = await fetch(`${PREVIEW_URL}${path}`, {
    headers: { "User-Agent": "Googlebot" }, // fetch as the crawler, not a browser
  });
  const html = await res.text();
  const robots = html.match(/<meta name="robots" content="([^"]*)"/i)?.[1] ?? "";

  if (res.status !== 200) throw new Error(`${path} returned ${res.status}`);
  if (/noindex/i.test(robots)) throw new Error(`${path} is noindex — blocking deploy`);
}
```

**Bad Example** — a dashboard nobody watches, alerting only on traffic

```yaml
# The only alert fires when organic sessions drop 50% week over week.
# WHY THIS FAILS: traffic is a lagging signal. By the time sessions halve,
# Google has already deindexed the pages days ago and the cause is unknown.
alert:
  metric: organic_sessions
  condition: drop > 50%
  window: 7d          # too slow: the damage is already done and untraceable
  # no indexing, canonical, or crawl-error checks → the actual cause is invisible
```

## Common Mistakes

- Alerting only on organic traffic — the slowest possible signal to move.
- Checking pages as a logged-in browser instead of as a bot, hiding SSR/`robots` issues.
- Absolute thresholds that fire constantly or never; use deltas against a baseline.
- Relying on Search Console's UI, then losing history when the 16-month window rolls off.
- Treating lab Core Web Vitals as the truth Google ranks on instead of field data.
- No deploy annotations, so a regression cannot be traced to the change that caused it.
- Alerts with no owner, which train the team to ignore the channel.

## Production Tips

- Store daily snapshots (indexed count, sitemap size, CWV, top-URL status) in a small
  table so you can chart trends and back-test thresholds.
- Alert on *rate of change* for indexed pages — a sudden drop is a deploy bug; a slow
  decline is a content or quality issue and needs a different response.
- Keep an "SEO smoke test" in the same pipeline as your app tests so it runs on every
  release, not on a separate cron nobody maintains.

## AI Review Checklist

- Are leading indicators (indexed count, `robots` meta, canonicals, crawl errors)
  monitored, not just traffic?
- Do synthetic checks fetch pages with a bot user-agent and assert on status and meta
  directives?
- Are thresholds relative to a baseline rather than absolute values?
- Is Core Web Vitals data sourced from the field (CrUX/RUM), not only lab tools?
- Do critical templates have a CI check that blocks deploys on `noindex` or non-200?
- Is Search Console history exported and retained beyond 16 months?
- Does every alert have an owner and a clear remediation path?

## Related

- `knowledge/seo/22-search-console.md`
- `knowledge/seo/21-analytics.md`
- `knowledge/seo/23-audits.md`
- `knowledge/seo/27-production-checks.md`
- `knowledge/seo/13-core-web-vitals.md`
