---
id: checklists/01-pre-launch
topic: checklists
slug: pre-launch
title: "Pre-Launch Checklist"
type: doc
order: 1
status: ready
tags: [checklists, pre-launch]
related: [checklists/03-new-project-setup, seo/98-production-checklist, accessibility/98-production-checklist, security/98-production-checklist, performance/98-production-checklist]
when_to_use: "Run a week before putting a site or application in front of real users, and again on launch day."
---
# Pre-Launch Checklist

## Purpose

The cross-cutting checks that decide whether a launch goes quietly. Every item is verifiable
against the real production environment — not against staging, and not against intent.

Run this **a week before launch**, not the morning of. Its value is finding the things that
take days to fix.

---

## Availability

☐ The production domain resolves, over HTTPS, without a certificate warning.

☐ The certificate has more than 30 days remaining, with automated renewal configured and
tested.

☐ `www` and apex both work, with one redirecting to the other consistently.

☐ Uptime monitoring checks a real page, not just the server root.

☐ Someone receives the alerts, and that path has been tested with a real notification.

---

## Correctness

☐ The primary conversion flow has been completed end to end in production — a real signup,
a real order, a real form submission.

☐ Transactional email arrives, from the production sender, and is not marked as spam.

☐ Payment processing works in live mode, with a real charge and a real refund.

☐ Forms validate, reject bad input, and report errors that a user can act on.

☐ 404 and 500 pages exist, are styled, and offer a way back.

---

## Security

☐ No credentials, keys, or `.env` files are in version control.

☐ Production secrets differ from every non-production environment.

☐ Admin interfaces are not reachable with default credentials.

☐ Security headers are set (CSP, HSTS, `X-Content-Type-Options`, `Referrer-Policy`).

☐ Debug output is disabled, and error pages leak no stack traces or paths.

☐ Rate limiting protects authentication and any expensive public endpoint.

☐ Dependency audit is clean at high severity, or exceptions are documented.

See [Security — Production Checklist](../security/98-production-checklist.md).

---

## Data

☐ Automated backups run, cover both database and uploads, and are stored off-site.

☐ A restore has been performed and timed — not merely configured.

☐ The database user holds only the privileges the application needs.

☐ Personal data collection matches the privacy policy, and retention is defined.

☐ Any test or seed data is gone from production.

---

## Performance

☐ Core Web Vitals measured on production, on a mid-range device over a real network.

☐ Images are correctly sized, in a modern format, with dimensions set to prevent layout
shift.

☐ Caching is configured at the layers that apply, with an invalidation path.

☐ The site has been exercised at expected launch traffic, not just single-user.

See [Performance — Production Checklist](../performance/98-production-checklist.md).

---

## Findability

☐ `robots.txt` allows what should be crawled — and check this twice; a staging `Disallow: /`
reaching production is the most common launch defect there is.

☐ No stray `noindex` on pages that should rank.

☐ Canonical URLs point at production, not staging.

☐ A sitemap exists and is submitted.

☐ Titles and meta descriptions are unique and descriptive.

☐ Open Graph and Twitter Card previews render correctly when a link is pasted.

☐ Redirects exist for every URL that changed, if this replaces an existing site.

See [SEO — Production Checklist](../seo/98-production-checklist.md).

---

## Accessibility

☐ Automated scan (axe or equivalent) reports zero violations on primary pages.

☐ Every interactive element is reachable by keyboard, with a visible focus indicator.

☐ Contrast meets AA for text and interactive states.

☐ Images have appropriate alternative text; decorative images have empty `alt`.

☐ Forms have persistent labels and error messages that are announced.

See [Accessibility — Production Checklist](../accessibility/98-production-checklist.md).

---

## Operations

☐ Rollback is a single command, and someone has run it this quarter.

☐ Error tracking is live, with sourcemaps and a release marker.

☐ Analytics is installed and recording, with consent handling if required.

☐ Scheduled jobs run on a real scheduler, verified by observing one fire.

☐ Someone is available after launch, and everyone knows who.

☐ The status page and its update path exist before they are needed.

---

## Launch Day

☐ Deploy at a time when people are available — not Friday evening.

☐ Watch error rates and conversion for a full traffic cycle.

☐ Re-verify the primary flow immediately after the DNS or deploy cutover.

☐ Re-check `robots.txt` and canonical tags on the live site.

☐ Confirm backups ran successfully after go-live.

---

## Sign-off

The launch is ready when someone has completed the primary user flow on production, a
restore has been tested, alerts reach a person, and rollback has been rehearsed. Everything
else on this list is a defect you would rather find now than at 2am.

## Examples

**Good Example** — items that can be answered by running something

```markdown
- [ ] `curl -sI https://example.com` returns `200` and `strict-transport-security`.
- [ ] A restore of last night's backup into a scratch database returns a non-zero
      row count for `orders` (proving the dump is real, not just present).
- [ ] Lighthouse on `/` scores LCP < 2.5 s on Slow 4G throttling.
- [ ] `axe` reports zero violations on the four highest-traffic templates.
- [ ] `robots.txt` allows `/` and the staging site's `Disallow: /` did not ship.
- [ ] A 404 returns HTTP 404, not 200 with a "not found" page.
```

Each line names the check and the passing condition, so two people running the list reach the
same verdict.

**Bad Example** — items that cannot fail

```markdown
- [ ] Site is fast
- [ ] SEO is set up
- [ ] Security reviewed
- [ ] Backups working
- [ ] Accessibility checked
```

"Backups working" is ticked by seeing a file in a bucket. The file may be a 0-byte dump from a
cron job that has been failing for a month; the checklist cannot tell the difference, which is
exactly the situation it exists to prevent.

---

## Related

- `knowledge/checklists/03-new-project-setup.md`
- `knowledge/security/98-production-checklist.md`
- `knowledge/seo/98-production-checklist.md`
- `knowledge/playbooks/01-site-down.md`
