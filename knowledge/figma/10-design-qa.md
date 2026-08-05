---
id: figma/10-design-qa
topic: figma
slug: design-qa
title: "Design QA"
type: doc
order: 10
status: ready
tags: [figma, design-qa]
related: [figma/15-screenshot-comparison, figma/13-visual-regression, figma/20-implementation-definition-of-done]
  - figma/13-visual-regression
  - figma/15-screenshot-comparison
  - figma/14-figma-inspection-checklist
  - figma/16-accessibility-from-figma
  - figma/20-implementation-definition-of-done
  - accessibility/21-axe
  - accessibility/10-color-and-contrast
  - testing/14-visual-regression
  - performance/18-web-vitals
  - engineering/02-code-review
when_to_use: "Read after development, to validate the implementation against the Figma design before code review or acceptance."
---
# Design QA

## Purpose

This document defines the standard process for validating an implementation against a Figma design after development.

The objective is to detect visual, structural, responsive, and accessibility differences before code review or client acceptance.

Design QA is a verification phase.

It is not another implementation phase.

---

## Core Principle

Never assume the implementation matches the design.

Always verify it systematically.

Every completed page must pass a Design QA review before it is considered production-ready.

---

## AI Mindset

When reviewing an implementation, behave like a Senior Frontend QA Engineer rather than the original developer.

Do not defend the implementation.

Look for differences.

Assume mistakes exist until proven otherwise.

---

## Design QA Workflow

Every page should be reviewed in the following order:

```
Overall Layout
        ↓
Page Structure
        ↓
Sections
        ↓
Components
        ↓
Typography
        ↓
Spacing
        ↓
Colors
        ↓
Responsive Layout
        ↓
Interactions
        ↓
Accessibility
        ↓
Performance
```

Never review isolated elements first.

Start from the entire page.

---

## Step 1 — Overall Layout

Compare:

- page width;
- overall proportions;
- visual balance;
- whitespace;
- section ordering;
- content hierarchy.

The first visual impression should closely match the design.

---

## Step 2 — Page Structure

Verify:

- correct section order;
- consistent containers;
- expected layout hierarchy;
- semantic HTML landmarks.

Unexpected structural differences usually indicate implementation problems.

---

## Step 3 — Section Review

Review every section independently.

Verify:

- width;
- spacing;
- alignment;
- padding;
- margins;
- background;
- responsiveness.

Sections should be visually independent.

---

## Step 4 — Component Review

Review every reusable component.

Examples:

- buttons;
- cards;
- forms;
- navigation;
- accordions;
- sliders;
- pricing cards;
- testimonials.

Verify that all instances remain consistent.

---

## Step 5 — Typography

Review:

- font family;
- font size;
- font weight;
- line height;
- letter spacing;
- text alignment;
- heading hierarchy.

Typography inconsistencies are among the most common implementation issues.

Compare computed values, not impressions. Run this in the browser console against the element
under review and check the output against the Figma text style:

```js
// Paste in DevTools console, then click the element you want to inspect.
document.addEventListener("click", (event) => {
  event.preventDefault();
  const s = getComputedStyle(event.target);
  console.table({
    tag: event.target.tagName,
    fontFamily: s.fontFamily,
    fontSize: s.fontSize,
    fontWeight: s.fontWeight,
    lineHeight: s.lineHeight,
    letterSpacing: s.letterSpacing,
    color: s.color,
  });
}, { capture: true, once: true });
```

Figma reports line height in pixels (`lineHeightPx`) while CSS often carries a unitless
ratio — normalize before comparing: `lineHeightPx / fontSize` is the ratio to expect.

Heading hierarchy is checkable in one line, and a skipped level is a defect even when it
looks correct:

```js
console.table(
  [...document.querySelectorAll("h1,h2,h3,h4,h5,h6")]
    .map((h) => ({ level: +h.tagName[1], text: h.textContent.trim().slice(0, 60) }))
);
// Expect exactly one h1, and no jump greater than one level between consecutive entries.
```

---

## Step 6 — Spacing

Review:

- section spacing;
- component spacing;
- grid gaps;
- margins;
- padding.

Spacing should follow the design system.

Avoid visual approximations.

---

## Step 7 — Colors

Verify:

- backgrounds;
- text colors;
- borders;
- buttons;
- links;
- icons;
- shadows.

Compare against design tokens rather than screenshots whenever possible.

---

## Step 8 — Responsive Review

Review:

Desktop

↓

Laptop

↓

Tablet

↓

Mobile

Verify:

- layout changes;
- stacking;
- typography;
- spacing;
- navigation;
- touch targets.

Responsive behavior should be intentional.

Script the sweep so every breakpoint is reviewed the same way each time, instead of dragging
the window until something looks wrong:

```js
// qa/breakpoints.spec.ts — Playwright
import { test, expect } from "@playwright/test";

const VIEWPORTS = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "laptop", width: 1280, height: 800 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "mobile", width: 390, height: 844 },
];

for (const vp of VIEWPORTS) {
  test(`pricing page at ${vp.name}`, async ({ page }) => {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    await page.goto("/pricing");

    // No horizontal overflow: the most common responsive defect.
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(overflow, `horizontal scrollbar at ${vp.name}`).toBe(false);

    await expect(page).toHaveScreenshot(`pricing-${vp.name}.png`, { maxDiffPixelRatio: 0.01 });
  });
}
```

See [Visual Regression](13-visual-regression.md) for turning these snapshots into a gate, and
[Screenshot Comparison](15-screenshot-comparison.md) for comparing against the Figma export
rather than a previous build.

---

## Step 9 — Interaction Review

Verify every interactive element.

Examples:

- hover;
- focus;
- active;
- disabled;
- loading;
- expanded;
- collapsed.

Review keyboard navigation in addition to pointer interactions.

---

## Step 10 — Accessibility Review

Verify:

- heading hierarchy;
- semantic HTML;
- image alt text;
- focus indicators;
- keyboard navigation;
- labels;
- contrast.

Accessibility is part of design quality.

Automate what can be automated before reviewing by hand — the manual pass is for what the
scanner cannot see (focus order, meaningful alt text, sensible labels):

```js
// qa/a11y.spec.ts — Playwright + axe-core
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("pricing page has no detectable a11y violations", async ({ page }) => {
  await page.goto("/pricing");
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();

  expect(results.violations.map((v) => `${v.id}: ${v.nodes.length} node(s)`)).toEqual([]);
});
```

An automated scan catches roughly a third of real accessibility defects — treat a clean run
as the floor, not the verdict. See [Accessibility — Axe](../accessibility/21-axe.md),
[Accessibility — Color and Contrast](../accessibility/10-color-and-contrast.md), and
[Accessibility from Figma](16-accessibility-from-figma.md) for the checks that stay manual.

---

## Step 11 — Performance Review

Verify:

- image optimization;
- lazy loading;
- asset size;
- unnecessary JavaScript;
- unnecessary CSS;
- layout shifts.

Visual quality should not compromise performance.

---

## Severity Levels

Every issue should receive a severity.

## Critical

Examples:

- broken layout;
- inaccessible functionality;
- missing content;
- unusable navigation.

Must be fixed before approval.

---

## Major

Examples:

- incorrect responsive layout;
- missing section;
- incorrect typography;
- incorrect spacing affecting usability.

Should be fixed before approval.

---

## Minor

Examples:

- inconsistent padding;
- small alignment differences;
- incorrect icon size;
- minor border-radius differences.

Should be corrected if practical.

---

## Cosmetic

Examples:

- tiny visual differences;
- insignificant spacing variations;
- decorative inconsistencies.

May be addressed later.

---

## QA Report Format

Every review should include:

## Overall Assessment

Examples:

- Matches Figma closely.
- Minor visual differences detected.
- Significant differences require revision.

---

## Findings

For every issue include:

- severity;
- location;
- description;
- expected result;
- recommended fix.

Write findings as data so they can be counted, filtered, and turned into tickets:

```json
{
  "page": "/pricing",
  "reviewedAt": "2026-07-14",
  "figmaFrames": { "desktop": "2:10", "mobile": "2:12" },
  "findings": [
    {
      "severity": "major",
      "area": "responsive",
      "location": "PlanGrid — mobile (390px)",
      "observed": "Three columns remain side by side; the card content overflows horizontally.",
      "expected": "Single column, cards stacked with spacing-lg between them (Figma 2:12).",
      "fix": "Change the grid to `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`.",
      "evidence": "qa/screens/pricing-mobile.png"
    },
    {
      "severity": "minor",
      "area": "typography",
      "location": "PlanCard — price label",
      "observed": "font-size 18px / line-height 28px",
      "expected": "font-size 20px / line-height 28px (text-heading-sm)",
      "fix": "Use the `text-heading-sm` token instead of a literal size."
    }
  ],
  "positive": ["Reused the existing Button component", "Correct heading hierarchy"],
  "recommendation": "request-changes"
}
```

`observed` and `expected` must both be concrete values. "Spacing looks off" is not a finding
a developer can act on; "32px instead of the 24px `spacing-lg` token" is.

---

## Positive Findings

List areas implemented correctly.

Examples:

- Excellent responsive behavior.
- Consistent typography.
- Proper semantic HTML.
- Good accessibility.
- Reused existing components.

Good implementations deserve recognition.

---

## Final Recommendation

Choose one:

- Approve
- Approve with minor comments
- Request changes
- Reject implementation

---

## AI Execution Checklist

## Investigation

☐ Compare page structure.

☐ Compare sections.

☐ Compare typography.

☐ Compare spacing.

☐ Compare colors.

☐ Compare responsiveness.

☐ Compare interactions.

☐ Compare accessibility.

---

## Verification

☐ Every difference is documented.

☐ Severity is assigned.

☐ Recommendations are actionable.

☐ Positive findings are included.

☐ Final recommendation is justified.

---

## Common Mistakes

Avoid:

Checking only desktop.

Ignoring spacing.

Ignoring accessibility.

Ignoring hover states.

Ignoring keyboard navigation.

Ignoring responsive layouts.

Accepting visual approximations.

Reviewing implementation without the Figma design.

---

## Examples

**Good Example** — a finding states the node, the measurement, and the decision

```text
QA — Checkout / Desktop 1440   build 4a91c2e

FAIL  Button/Primary (node 12:88)
      design 44×44, built 36×32 — below the 44×44 minimum touch target
      → fix in code

FAIL  Card gap (node 44:12)
      design 24, built 16 — the card grid uses --space-md instead of --space-lg
      → fix in code

DIFF  Heading line-height
      design 1.2, built 1.35 — the built value comes from the type scale and is
      more readable at this size
      → accepted, design updated to 1.35 (agreed with designer, 2026-08-04)

PASS  Colour, spacing scale, focus ring, empty state
```

**Bad Example** — a screenshot with circles drawn on it

```text
"Some spacing looks off on the checkout page, see attached."
```

Nobody can act on this. There is no node id, so the reference cannot be found; no measurement,
so "off" cannot be verified; no distinction between a defect and a deliberate improvement; and
no record of what was accepted, so the same difference is reported again next release.

---

## Completion Criteria

A Design QA review is complete when:

- every section has been reviewed;
- responsive layouts have been verified;
- accessibility has been evaluated;
- issues are categorized by severity;
- a final recommendation is provided;
- the implementation is considered ready for production or returned for revision.

---

## Related Knowledge

- [Figma Inspection Checklist](14-figma-inspection-checklist.md) — the pre-implementation counterpart of this review.
- [Screenshot Comparison](15-screenshot-comparison.md) and [Visual Regression](13-visual-regression.md) — mechanized comparison and the CI gate.
- [Implementation Definition of Done](20-implementation-definition-of-done.md) — the criteria this review is measured against.
- [Testing — Visual Regression](../testing/14-visual-regression.md) and [Testing — Accessibility Testing](../testing/18-accessibility-testing.md) — the wider testing practice.
- [Performance — Web Vitals](../performance/18-web-vitals.md) — layout shift and loading metrics for the performance step.
- [Engineering — Code Review](../engineering/02-code-review.md) — how these findings enter the review process.

---

## Summary

Design QA is the final engineering safeguard between implementation and production.

A disciplined review process catches visual, structural, responsive, and accessibility issues before they reach users, reducing costly revisions and increasing confidence in every release.