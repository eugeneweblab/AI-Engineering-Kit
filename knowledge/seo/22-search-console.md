---
id: seo/22-search-console
topic: seo
slug: search-console
title: "Search Console"
type: doc
order: 22
status: ready
tags: [seo, search-console, noindex, alert, list, execute]
related: [seo/03-indexing, seo/07-sitemaps, seo/24-monitoring, seo/23-audits]
when_to_use: "Read before verifying a property, diagnosing an indexing problem, or wiring Search Console data into monitoring."
---
# Search Console

## Purpose

This document defines how to use Google Search Console (GSC) — and its Bing equivalent,
Webmaster Tools — as the source of truth for how a search engine actually sees your site.
It covers property setup, the reports that matter, and how to turn GSC into a feedback
loop rather than a dashboard nobody reads.

Search Console is the only place that shows the engine's real view: which URLs are
indexed, why others are excluded, how pages render, what queries they appear for, and
what is broken. When your assumptions and GSC disagree, GSC is right.

## Why It Matters

Everything else in this topic is a hypothesis about how the engine will treat your pages.
Search Console is the measurement that confirms or refutes it. Without it you are flying
blind: a stray `noindex`, a canonical pointing at the wrong URL, or a render failure can
quietly deindex pages, and you find out from a traffic chart weeks later. GSC surfaces
these as concrete, per-URL reasons ("Excluded by 'noindex' tag", "Duplicate, Google chose
different canonical") with the rendered HTML the engine used. It is also how you request
recrawls, submit sitemaps, and get alerted to manual actions and Core Web Vitals
regressions. Treated as a habit, it turns silent SEO failures into visible ones.

## Core Principles

- **GSC reflects the engine's view, not yours.** Use "URL Inspection → View crawled page"
  to see the rendered HTML Google indexed, especially for JS-heavy pages. Debug against
  that, not your local browser.
- **Verify at the right scope.** A Domain property (DNS-verified) covers every subdomain
  and protocol; a URL-prefix property covers only one. Prefer Domain to avoid blind spots.
- **Index Coverage reasons are actionable diagnoses.** Each exclusion bucket names a
  cause. Read the bucket, fix the cause, then validate — do not just resubmit.
- **Requesting indexing is a nudge, not a fix.** "Request indexing" does not override
  `noindex`, a bad canonical, or a render error. Fix the signal first.
- **GSC data is delayed and sampled.** Coverage lags days; Performance data is capped and
  rounded. Use it for trends and diagnosis, not for precise real-time counts.

## Best Practices

- Verify a **Domain property** via DNS so all subdomains, `www`/non-`www`, and
  `http`/`https` are covered under one view.
- Submit XML [sitemaps](07-sitemaps.md) in the Sitemaps report and watch the
  discovered-vs-indexed gap; a widening gap signals an indexing problem.
- Use **URL Inspection** on any page you doubt: check indexed status, the chosen
  canonical (user-declared vs Google-selected), coverage state, and the rendered HTML.
- Work the **Page indexing (Index Coverage)** report by exclusion reason. Prioritize
  "Excluded by 'noindex'", "Duplicate without user-selected canonical", "Crawled –
  currently not indexed", and "Soft 404".
- Read the **Performance** report by query and page to see what actually drives clicks;
  filter to a page after a change to confirm it kept its rankings.
- Monitor **Core Web Vitals** and **Manual actions / Security issues** — a manual action
  requires a fix plus a reconsideration request.
- Export GSC data via the API/BigQuery bulk export into your own [monitoring](24-monitoring.md)
  so you can alert on drops instead of checking manually.

## Examples

**Good Example** — automate coverage checks with the API

```python
# Pull indexed-vs-submitted per sitemap and alert when the gap widens.
# Runs on a schedule; turns a silent indexing drop into a notification.
from googleapiclient.discovery import build

svc = build("searchconsole", "v1", credentials=creds)
site = "sc-domain:example.com"  # Domain property covers all subdomains

sitemaps = svc.sitemaps().list(siteUrl=site).execute().get("sitemap", [])
for sm in sitemaps:
    submitted = int(sm["contents"][0]["submitted"])
    indexed = int(sm["contents"][0]["indexed"])
    if indexed < submitted * 0.9:  # >10% of submitted URLs unindexed
        alert(f"{sm['path']}: {indexed}/{submitted} indexed — investigate coverage")
```

**Bad Example** — treating "Request indexing" as the fix

```text
Symptom:  A product page is missing from Google.
Action:   Open URL Inspection → click "Request indexing" → repeat daily.
Result:   Nothing changes. The page still won't index.

Why it's wrong:
  URL Inspection showed "Excluded by 'noindex' tag" — the page carries
  <meta name="robots" content="noindex"> from a stale template flag.
  "Request indexing" cannot override that signal. The fix is to remove the
  noindex tag, then validate the fix in the Page indexing report — not to
  keep re-requesting a crawl of a page that tells the engine to stay out.
```

## Common Mistakes

- Debugging JS pages against the local browser instead of GSC's rendered HTML.
- Verifying only a URL-prefix property, missing issues on other subdomains/protocols.
- Spamming "Request indexing" instead of fixing the underlying exclusion reason.
- Ignoring the sitemap discovered-vs-indexed gap until traffic drops.
- Reading Performance click counts as exact truth (they are sampled and capped).
- Never exporting the data, so nobody notices a coverage drop until it is severe.
- Missing a manual-action notice because no one checks GSC on a schedule.

## Production Tips

- Grant team access with appropriate roles and add GSC verification to your
  infrastructure-as-code so a redeploy never loses it.
- Schedule the bulk BigQuery export and build alerts on: indexed-URL count drop, spike in
  a coverage-exclusion bucket, new manual action, and Core Web Vitals status change.
- After any indexation-affecting deploy (robots, canonicals, `noindex`), inspect a sample
  of affected URLs in GSC within a week to confirm the intended effect.

## AI Review Checklist

- Is the property Domain-verified (DNS) so all subdomains and protocols are covered?
- Are XML sitemaps submitted, with the indexed-vs-submitted gap monitored?
- When diagnosing a page, was URL Inspection's rendered HTML and chosen canonical checked?
- Are Index Coverage exclusions triaged by reason, then validated after a fix?
- Is GSC data exported into monitoring with alerts on coverage/CWV/manual-action changes?
- Is "Request indexing" used only after the underlying signal is fixed?

## Related

- `knowledge/seo/03-indexing.md`
- `knowledge/seo/07-sitemaps.md`
- `knowledge/seo/24-monitoring.md`
- `knowledge/seo/23-audits.md`
