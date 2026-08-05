---
id: accessibility/22-lighthouse
topic: accessibility
slug: lighthouse
title: "Lighthouse"
type: doc
order: 22
status: ready
tags: [accessibility, lighthouse, lighthouse]
related: [accessibility/21-axe, accessibility/20-testing-tools, accessibility/24-accessibility-testing, accessibility/23-wcag, accessibility/06-screen-readers]
when_to_use: "Read before using a Lighthouse accessibility score in CI, reporting, or as an acceptance criterion."
---
# Lighthouse

## Purpose

This document explains Google Lighthouse's accessibility category — what it measures, how
its score is computed, and, critically, how to avoid the trap of treating that score as a
grade of accessibility. Lighthouse runs a **subset of axe-core** rules and rolls the
results into a single 0–100 number. That number is useful for trend-watching and a quick
per-page snapshot; it is dangerous as a compliance target.

The goal here is to let an agent use Lighthouse for what it is good at — a fast, scored,
CI-friendly page audit — while never inferring "accessible" from a high score.

## Why It Matters

Lighthouse is built into Chrome DevTools, PageSpeed Insights, and `lighthouse-ci`, so it
is often the first (and sometimes only) accessibility signal a team sees. Its single
score is seductive: managers ask for "100 on accessibility." But the score is a
**weighted average of a subset of axe checks**, and a page can score 100 while being
completely unusable by keyboard or screen reader — because focus order, alt-text quality,
and custom-widget behavior are not in the audit at all. Worse, the score is
**not linear**: fixing one high-weight audit can swing it more than fixing five real but
low-weight problems. Understanding this prevents a false sense of compliance.

## Core Principles

- **The score is a subset, not a verdict.** Lighthouse runs fewer rules than a full
  axe-core scan and none of the manual criteria. 100 ≠ accessible.
- **Use it for trend and snapshot, not as a pass/fail gate on its own.** It is excellent
  for "did this PR make a page worse," poor as "this page is compliant."
- **Read the individual audits, not the number.** The value is in the itemized failures
  and the "Additional items to manually check" list — not the aggregate.
- **Audit the state you care about.** Lighthouse scans the loaded page. Menus, modals,
  and authenticated views need explicit navigation or user-flow mode.
- **Prefer axe directly for depth.** If you need thorough automated coverage, run
  axe-core with your full ruleset; Lighthouse is the convenient, lighter view.

## Best Practices

- Run Lighthouse in CI with **`lighthouse-ci`** and assert against the itemized audits or
  a floor score to catch *regressions*, not to certify compliance.
- Always read the **"Additional items to manually check"** section Lighthouse prints — it
  is Lighthouse itself telling you the machine part is incomplete.
- Test meaningful states: use Lighthouse **user flows** (timespan/snapshot mode) to audit
  after opening a dialog or logging in, not just the cold landing page.
- Combine with a direct **axe** run in tests (see [axe](21-axe.md)); let axe be the
  detailed gate and Lighthouse the scored overview, so you are not relying on the subset.
- Track the score **over time as a trend line**, and pair any target with an explicit
  note that manual testing is still required for sign-off.
- Run on a consistent environment (throttling, viewport, headless flags) so score
  movement reflects code changes, not machine noise.

## Examples

**Good Example** — Lighthouse for regression trend, audits read, manual work still required

```js
// lighthouserc.js — treat accessibility as a regression guard, not a compliance stamp
module.exports = {
  ci: {
    collect: { url: ["http://localhost:3000/checkout"], numberOfRuns: 3 },
    assert: {
      assertions: {
        // Fail on specific real regressions rather than certifying via the aggregate
        "categories:accessibility": ["warn", { minScore: 0.9 }],
        "color-contrast": "error",
        "label": "error",
      },
    },
  },
};
// Sign-off still requires the keyboard and screen reader passes Lighthouse cannot do.
```

**Bad Example** — the score as a compliance gate

```js
const { lhr } = await lighthouse("https://app.example.com");
if (lhr.categories.accessibility.score >= 0.95) {
  certifyWcagCompliant(); // FALSE: the score is a weighted subset of axe rules
                          // and ignores focus order, alt quality, and keyboard use
}
// Only the landing page was audited; the app behind login was never scanned.
```

## Common Mistakes

- Reporting the Lighthouse accessibility score as WCAG compliance.
- Chasing 100 by fixing high-weight audits while real, low-weight barriers remain.
- Auditing only the public landing page, never authenticated or interactive states.
- Ignoring the "manually check" list Lighthouse explicitly surfaces.
- Comparing scores across inconsistent runs (different throttling/viewport) and reading
  noise as progress or regression.
- Using Lighthouse as the *only* automated tool when axe-core offers deeper coverage.

## Production Tips

- Wire `lighthouse-ci` to post per-PR reports and assert on named audits; keep the
  aggregate score as a soft `warn`, not the merge blocker.
- Store historical LHRs to plot the accessibility trend and spot slow regressions that a
  single-run threshold would miss.
- Document, next to any score target, that a high score is necessary-not-sufficient and
  does not replace the manual [testing protocol](24-accessibility-testing.md).

## AI Review Checklist

- Is the Lighthouse score used for regression/trend, not as a compliance verdict?
- Are individual audits and the "manually check" list read, not just the number?
- Are interactive and authenticated states audited via user flows?
- Is a direct axe run providing deeper automated coverage alongside Lighthouse?
- Are runs configured consistently so score changes are meaningful?
- Is manual keyboard and screen reader testing still required for sign-off?

## Related

- `knowledge/accessibility/21-axe.md`
- `knowledge/accessibility/20-testing-tools.md`
- `knowledge/accessibility/24-accessibility-testing.md`
- `knowledge/accessibility/23-wcag.md`
- `knowledge/accessibility/06-screen-readers.md`
