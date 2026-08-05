---
id: performance/23-performance-budget
topic: performance
slug: performance-budget
title: "Performance Budget"
type: doc
order: 23
status: ready
tags: [performance, performance-budget]
related: [performance/18-web-vitals, performance/02-metrics, performance/10-code-splitting, performance/11-images, performance/29-performance-review]
when_to_use: "Read before setting or enforcing a performance target, so 'fast enough' becomes a number CI can check."
---
# Performance Budget

## Purpose

This document defines how to set an explicit, enforced limit on performance — a bundle
size, a latency threshold, a Web Vitals target — and gate CI on it. It exists so an agent
knows when a change is *too slow to merge*, turning performance from a vague aspiration
into a build-breaking check.

A budget is the stopping rule for optimization and the guardrail against regression. It
gives the numbers in [metrics](02-metrics.md) and [Web Vitals](18-web-vitals.md) teeth: a
target no one enforces is a wish.

## Why It Matters

Performance dies by a thousand cuts, not one bad commit. Each feature adds a few
kilobytes, one more request, ten more milliseconds — individually reasonable, collectively
a page that takes six seconds to load a year later. No single author is at fault, and no
one notices until it is a rewrite. A budget catches each cut at the moment it is made,
when it is one small diff to fix, instead of an unattributable mess to untangle later. It
also settles arguments: "is this fast enough?" has an answer, not an opinion.

## Core Principles

- **A budget is a number plus enforcement.** A target with no CI gate is decoration.
  Budgets must fail the build (or block the merge) or they will be ignored under deadline.
- **Budget what users feel and what causes it.** Set *outcome* budgets (LCP, INP, p99
  latency) and *proxy* budgets (JS bytes, request count, image weight) — proxies are
  cheaper to check per-commit and catch regressions earlier.
- **Set budgets from a baseline, not a wish.** Measure current performance, set the budget
  slightly tighter, and ratchet down over time. An unreachable budget gets muted; a
  slack one does nothing.
- **Fail the build, then attribute.** A crossed budget should name what grew (which bundle,
  which route) so the author fixes their own diff.
- **Budget for the target device and network.** A budget only means something at p75 real
  conditions (mid-range mobile, 4G) — the same field truth as Web Vitals.

## Best Practices

- Set **size budgets** on JavaScript, CSS, images, and total transfer per route (e.g.
  "≤ 170 KB compressed JS on the landing route"); enforce with a bundler budget or a tool
  like `bundlesize`/Lighthouse CI.
- Set **metric budgets** on the Core Web Vitals (LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1) and
  on backend p99 latency, checked in CI against a lab run and in production against RUM.
- Gate the CI pipeline: a pull request that exceeds a budget **fails**, with the offending
  number in the output, so the regression cannot merge silently.
- Ratchet: when you beat a budget durably, tighten it, so the system trends faster instead
  of drifting back to the ceiling.
- Attribute regressions with per-route/per-bundle budgets rather than one global number,
  so the fix lands on the responsible change.
- Review budgets during [performance review](29-performance-review.md); update them when
  requirements or the baseline genuinely change — not to paper over a regression.

## Examples

**Good Example** — enforced size budget that fails the build

```json
// bundlesize / bundler budget: CI FAILS if the compressed bundle exceeds the limit.
{
  "budgets": [
    { "path": "dist/landing.*.js", "maxSize": "170 kB", "compression": "gzip" },
    { "path": "dist/**/*.css",     "maxSize": "50 kB",  "compression": "gzip" }
  ]
}
// A PR adding a 40 KB dependency to the landing route breaks the build here,
// while it is one small, attributable diff — not a mystery six months later.
```

**Bad Example** — a target with no enforcement

```markdown
<!-- In the team wiki: -->
## Performance goals
- Keep the app fast (aim for a good Lighthouse score).
- Try not to add too much JavaScript.

<!-- No number, no CI gate, no owner. Every PR is individually "not too much,"
     and the bundle triples over a year with no single commit to blame. -->
```

## Common Mistakes

- A budget that exists only in a doc, with nothing in CI to enforce it.
- Budgeting a lab score on fast hardware while real users on mobile blow past it.
- One global budget that hides which route or bundle regressed, so no one owns the fix.
- Setting the budget so loose it never fires, or so tight it fires constantly and gets
  muted.
- Raising the budget to make a red build green instead of fixing the regression.
- Budgeting bytes but not the user-facing metric (or vice versa) — track both.

## Production Tips

- Run Lighthouse CI (or an equivalent) on every PR against the budget, and also monitor
  the same metrics in production RUM so field regressions that lab tests miss still alert.
- Keep the budget config in the repo next to the code so it versions with the app and
  changes go through review.
- Publish the current headroom ("landing route: 148 / 170 KB") so authors see the cost of
  their change before they spend the budget.

## AI Review Checklist

- Is there an explicit numeric budget (size and/or metric), not a vague goal?
- Is the budget enforced in CI so a violating change fails the build?
- Are both a user-facing metric (LCP/INP/p99) and a proxy (bytes/requests) budgeted?
- Is the budget attributable to a route/bundle so regressions name their cause?
- Is the target set for real p75 conditions (mobile, 4G), not fast lab hardware?
- Was a crossed budget fixed at the source, not raised to silence the check?

## Related

- `knowledge/performance/18-web-vitals.md`
- `knowledge/performance/02-metrics.md`
- `knowledge/performance/10-code-splitting.md`
- `knowledge/performance/11-images.md`
- `knowledge/performance/29-performance-review.md`
