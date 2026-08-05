---
id: figma/13-visual-regression
topic: figma
slug: visual-regression
title: "Visual Regression"
type: doc
order: 13
status: ready
tags: [figma, visual-regression]
related:
  - figma/10-design-qa
  - figma/15-screenshot-comparison
  - figma/20-implementation-definition-of-done
  - testing/14-visual-regression
  - testing/22-flaky-tests
  - testing/21-cicd
  - testing/27-quality-gates
  - accessibility/24-accessibility-testing
  - performance/18-web-vitals
when_to_use: "Read before approving frontend changes, to check that new work has not visually regressed existing pages."
---
# Visual Regression

## Purpose

This document defines the standard process for identifying visual regressions after implementing a Figma design.

The objective is to ensure that new changes do not unintentionally alter the appearance, layout, responsiveness, or usability of existing pages.

Visual regression testing is a mandatory verification step before approving frontend changes.

---

## Core Principle

Every visual change must be intentional.

Unexpected differences are defects until proven otherwise.

That principle only holds if the comparison is deterministic. A suite that reports diffs from
animation frames, blinking carets, or today's date trains everyone to approve diffs without
reading them — which is worse than having no suite at all.

```ts
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/visual",
  // Snapshots are OS- and browser-version-specific. Generate and compare them in the
  // same container that CI uses, or every local run will produce false failures.
  snapshotPathTemplate: "{testDir}/__screenshots__/{projectName}/{arg}{ext}",
  expect: {
    toHaveScreenshot: {
      // Allow sub-pixel antialiasing noise; fail on anything structural.
      maxDiffPixelRatio: 0.01,
      animations: "disabled",
      caret: "hide",
      scale: "css",
    },
  },
  use: { baseURL: process.env.BASE_URL ?? "http://localhost:3000" },
  projects: [
    { name: "chromium-desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } } },
    { name: "chromium-mobile", use: { ...devices["Pixel 7"] } },
  ],
});
```

---

## Verification Workflow

Every implementation should be verified in the following order:

```
Baseline Design
        ↓
Current Implementation
        ↓
Desktop Comparison
        ↓
Tablet Comparison
        ↓
Mobile Comparison
        ↓
Component Comparison
        ↓
Interaction Comparison
        ↓
Approval
```

---

## Step 1 — Compare Overall Layout

Verify:

- page width;
- section order;
- visual hierarchy;
- whitespace;
- content alignment;
- container consistency.

---

## Step 2 — Compare Components

Review every reusable component.

Examples:

- buttons;
- cards;
- forms;
- navigation;
- sliders;
- accordions;
- pricing cards;
- testimonials.

All instances should remain visually consistent.

Snapshot components in isolation, including their states — a page-level shot hides a broken
`:disabled` style that a component-level shot catches:

```ts
// tests/visual/button.spec.ts
import { test, expect } from "@playwright/test";

const STATES = ["default", "hover", "focus", "disabled", "loading"] as const;

for (const state of STATES) {
  test(`Button — ${state}`, async ({ page }) => {
    await page.goto(`/__components/button?state=${state}`);
    const button = page.getByRole("button", { name: "Continue" });

    if (state === "hover") await button.hover();
    if (state === "focus") await button.focus();

    await expect(button).toHaveScreenshot(`button-${state}.png`);
  });
}
```

**Bad Example** — a whole-page snapshot with live data

```ts
// Fails every day at midnight, on every new order, and after every CMS edit.
// The failure is real, but it is not a regression — and nobody will read the diff.
await expect(page).toHaveScreenshot("dashboard.png");
```

**Good Example** — mask the volatile regions, keep the layout under test

```ts
await expect(page).toHaveScreenshot("dashboard.png", {
  mask: [
    page.getByTestId("order-count"),   // changes with real data
    page.getByTestId("last-updated"),  // changes with the clock
    page.locator("img.avatar"),        // user-uploaded, arbitrary
  ],
  maskColor: "#FF00FF",
});
```

Masking keeps the geometry under test while removing the content that legitimately varies.
See [Testing — Flaky Tests](../testing/22-flaky-tests.md).

---

## Step 3 — Compare Typography

Verify:

- font family;
- font size;
- font weight;
- line height;
- letter spacing;
- text alignment;
- heading hierarchy.

---

## Step 4 — Compare Spacing

Review:

- margins;
- padding;
- gaps;
- section spacing;
- grid spacing.

Spacing should follow the project's design system.

---

## Step 5 — Compare Colors

Verify:

- backgrounds;
- borders;
- text;
- icons;
- buttons;
- links;
- shadows.

Use design tokens whenever possible.

---

## Step 6 — Compare Responsive Layouts

Verify:

Desktop

↓

Laptop

↓

Tablet

↓

Mobile

Ensure that layout transitions match the design.

Run the same page across every breakpoint the design defines, and fail the run on horizontal
overflow before comparing pixels — overflow is a definite defect, while a pixel diff needs
judgement:

```ts
// tests/visual/pages.spec.ts
import { test, expect } from "@playwright/test";

const PAGES = ["/", "/pricing", "/blog", "/contact"];
const WIDTHS = [1440, 1280, 768, 390];

for (const path of PAGES) {
  for (const width of WIDTHS) {
    test(`${path} @ ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(path);
      await page.waitForLoadState("networkidle");

      // Fonts must be settled, or the first run and the next disagree on metrics.
      await page.evaluate(() => document.fonts.ready);

      const overflows = await page.evaluate(
        () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
      );
      expect(overflows, `horizontal overflow at ${width}px`).toBe(false);

      await expect(page).toHaveScreenshot(`${path.replace(/\//g, "_")}-${width}.png`, {
        fullPage: true,
      });
    });
  }
}
```

---

## Step 7 — Compare Interactions

Review:

- hover;
- focus;
- active;
- disabled;
- loading;
- animations.

Interactive behavior should remain consistent.

---

## Step 8 — Compare Accessibility

Verify:

- semantic HTML;
- heading order;
- keyboard navigation;
- focus visibility;
- image alt text;
- form labels.

---

## AI Checklist

## Investigation

☐ Compare layouts.

☐ Compare components.

☐ Compare typography.

☐ Compare spacing.

☐ Compare colors.

☐ Compare responsive behavior.

☐ Compare interactions.

---

## Verification

☐ All visual differences documented.

☐ Unintentional regressions identified.

☐ Responsive behavior verified.

☐ Accessibility preserved.

☐ Final implementation approved.

---

## Running It as a Gate

Snapshots must be produced in the same environment that compares them, otherwise font
rendering alone will paint every run red:

```yaml
# .github/workflows/visual.yml
name: visual-regression
on: pull_request

jobs:
  screenshots:
    runs-on: ubuntu-latest
    # Pin the image to the installed Playwright version — a mismatch silently changes rendering.
    container: mcr.microsoft.com/playwright:v1.49.0-jammy
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run build && npm run start &
      - run: npx wait-on http://localhost:3000
      - run: npx playwright test --project=chromium-desktop --project=chromium-mobile
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: visual-diffs
          path: test-results/   # actual, expected, and diff images for review
          retention-days: 7
```

Updating baselines is a deliberate act, never a reflex:

```bash
# Only after confirming each diff is an intended design change.
npx playwright test --update-snapshots
git add tests/visual/__screenshots__ && git commit -m "test(visual): rebaseline pricing page after plan card redesign"
```

The commit message has to say *why* the baseline moved. A rebaseline commit with no reason is
indistinguishable from an accepted regression six months later.

---

## Common Mistakes

Avoid:

Ignoring small spacing differences.

Reviewing only desktop.

Ignoring hover states.

Ignoring accessibility.

Approving visual regressions without investigation.

---

## Completion Criteria

Visual regression review is complete when:

- all layouts have been compared;
- responsive behavior has been verified;
- unexpected differences have been resolved;
- implementation accurately reflects the approved design.

---

## Related Knowledge

- [Screenshot Comparison](15-screenshot-comparison.md) — comparing against the Figma export rather than a previous build.
- [Design QA](10-design-qa.md) — the human review this automation supports but does not replace.
- [Testing — Visual Regression](../testing/14-visual-regression.md) — the general practice and tooling landscape.
- [Testing — Flaky Tests](../testing/22-flaky-tests.md) — keeping the suite trustworthy.
- [Testing — CI/CD](../testing/21-cicd.md) and [Testing — Quality Gates](../testing/27-quality-gates.md) — where this runs and what it blocks.
- [Performance — Web Vitals](../performance/18-web-vitals.md) — layout shift often shows up as an unexplained snapshot diff.

---

## Summary

Visual regression testing protects design consistency and prevents unintended frontend changes from reaching production.