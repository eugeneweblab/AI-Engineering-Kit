---
id: accessibility/21-axe
topic: accessibility
slug: axe
title: "Axe"
type: doc
order: 21
status: ready
tags: [accessibility, axe, AxeBuilder, analyze, toBeLessThan, withTags, "@axe-core", toEqual]
related: [accessibility/20-testing-tools, accessibility/22-lighthouse, accessibility/24-accessibility-testing, accessibility/07-aria, accessibility/23-wcag]
when_to_use: "Read before wiring accessibility checks into tests or CI, or when interpreting axe-core results."
---
# Axe

## Purpose

This document describes axe-core — the open-source accessibility rules engine from Deque
that underpins most automated a11y testing (including the axe DevTools extension,
Lighthouse's accessibility audits, and the CI integrations jest-axe, cypress-axe, and
`@axe-core/playwright`). It explains how to run it correctly, how to read its output, and
where its authors deliberately drew the line on what it will report.

axe-core's defining virtue is its **near-zero false-positive rate**: if it reports a
violation, that is a real WCAG failure, by design. The corollary — which teams forget —
is that silence is not success. This document exists to make agents use axe as a precise
gate without mistaking its pass for a full audit.

## Why It Matters

axe is the highest-leverage automated tool you can add: a handful of lines wires it into
an existing test suite and it catches the entire machine-detectable class of defects —
missing labels, bad contrast, invalid ARIA, duplicate ids, missing `lang` — on every
commit, before they reach users. Because its false-positive rate is engineered to be
essentially zero, every finding is actionable and worth fixing, which means it can safely
**fail the build**. But axe checks roughly 20–40% of WCAG; the judgment criteria are out
of scope on purpose. Treating a clean axe run as compliance is the classic error.

## Core Principles

- **A violation is real; fix it.** axe is tuned to avoid false alarms, so its "violations"
  are not noise. Do not suppress them without a documented, reviewed reason.
- **A pass is a floor, not a verdict.** No violations means "nothing machine-detectable,"
  not "accessible." Keyboard and screen reader passes remain mandatory.
- **Scan the rendered, interactive state.** axe analyzes the DOM at the moment you call
  it. Open the menu, trigger the error, expand the panel — then scan that state.
- **Configure the ruleset to your target.** Enable the WCAG 2.2 AA tags you are held to;
  `best-practice` rules go beyond WCAG and are optional.
- **Understand the four buckets.** Results split into `violations`, `incomplete` (needs
  human review — do not ignore), `passes`, and `inapplicable`.

## Best Practices

- Integrate axe into the test layer you already run: `jest-axe`/`vitest-axe` for
  component tests, `@axe-core/playwright` or `cypress-axe` for e2e. Fail CI on new
  violations so accessibility cannot regress silently.
- Scope scans to the component or region under test (`axe.run(container)`) so failures
  point at an owner and run fast, instead of scanning the whole page every time.
- Configure `runOnly` with the tags you enforce, e.g. `wcag2a`, `wcag2aa`, `wcag21aa`,
  `wcag22aa`. Add `best-practice` if you want the stricter, non-normative advice.
- Treat **`incomplete`** results as work, not as passes — they are cases axe could not
  decide (e.g. contrast over a background image) and a human must confirm.
- When you must exclude a known issue, use a **narrow, commented allowlist** (specific
  rule + selector) with a tracking ticket — never disable a rule globally.
- Scan multiple UI states in one flow: initial render, opened overlays, post-submit error
  state. Most violations hide in states the default snapshot never reaches.

## Examples

**Good Example** — scoped, tagged, gating, states covered

```ts
import { AxeBuilder } from "@axe-core/playwright";

test("checkout page is free of WCAG 2.2 AA violations", async ({ page }) => {
  await page.goto("/checkout");
  await page.getByRole("button", { name: "Add coupon" }).click(); // open the dynamic UI

  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"]) // enforce our target level
    .analyze();

  expect(results.violations).toEqual([]); // real failures block the merge
  // Note: results.incomplete may still hold items a human must review.
});
```

**Bad Example** — global scan, rule disabled to force green

```ts
const results = await new AxeBuilder({ page })
  .disableRules(["color-contrast"]) // silences a REAL failure instead of fixing it
  .analyze();
// Only the initial page load is scanned; menus and modals are never opened,
// so their violations are invisible. "No violations" here is meaningless.
expect(results.violations.length).toBeLessThan(5); // tolerating known failures
```

## Common Mistakes

- Reading "0 violations" as "accessible" and skipping manual testing.
- Ignoring `incomplete` results, which are unresolved checks, not passes.
- Disabling a rule (commonly `color-contrast`) to make the suite green instead of fixing
  the underlying defect.
- Scanning only the initial DOM, never the opened/expanded/error states.
- Scanning the entire document so failures have no clear owner and tests slow down.
- Not aligning `runOnly` tags with the WCAG level the product is actually held to.
- Assuming the axe extension and axe in CI report identically — configuration differs;
  pin the ruleset explicitly.

## Production Tips

- Keep an allowlist file of accepted violations with rule id, selector, ticket, and
  expiry date; review it in each release so it does not become a graveyard.
- Run axe against a component library / Storybook in CI so shared components are gated
  once, upstream of every consumer.
- Pin the `axe-core` version and note it in test output — rule additions between versions
  can introduce new (real) failures, which is desirable but should be an intentional bump.

## AI Review Checklist

- Is axe run in CI and does a new violation fail the build?
- Are the enforced WCAG tags (`wcag2aa`, `wcag22aa`, …) explicitly configured?
- Are dynamic states scanned, not just the initial render?
- Are `incomplete` results reviewed rather than treated as passes?
- Are any disabled rules justified, narrowly scoped, and tracked?
- Is the pass understood as a floor, with keyboard and screen reader testing still done?

## Related

- `knowledge/accessibility/20-testing-tools.md`
- `knowledge/accessibility/22-lighthouse.md`
- `knowledge/accessibility/24-accessibility-testing.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/23-wcag.md`
