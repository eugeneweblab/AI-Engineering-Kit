---
id: figma/15-screenshot-comparison
topic: figma
slug: screenshot-comparison
title: "Screenshot Comparison"
type: doc
order: 15
status: ready
tags: [figma, screenshot-comparison, goto, toHaveScreenshot, evaluate, readFileSync, FIGMA_FILE_KEY]
related:
  - figma/13-visual-regression
  - figma/10-design-qa
  - testing/14-visual-regression
  - figma/05-responsive-analysis
  - figma/20-implementation-definition-of-done
  - testing/13-ui-testing
  - performance/12-fonts
  - accessibility/10-color-and-contrast
when_to_use: "Read when comparing an implemented page against its Figma design using screenshots to detect visual differences."
---
# Screenshot Comparison

## Purpose

This document defines the standard process for comparing implemented pages with approved Figma designs using screenshots.

The objective is to detect visual differences objectively and consistently before code review, QA, or production deployment.

Screenshot comparison should validate the final implementation rather than replace manual review.

---

## Core Principle

Compare the rendered result, not assumptions.

A page should be evaluated using identical conditions so that only implementation differences remain.

"Identical conditions" is concrete work: same width, same device pixel ratio, same fonts
loaded, same content. Capture both sides mechanically instead of cropping by hand:

```js
// scripts/capture-pair.mjs — Figma frame + rendered page at the same width
import { writeFile } from "node:fs/promises";
import { chromium } from "playwright";

const { FIGMA_TOKEN, FIGMA_FILE_KEY } = process.env;
const FRAME_ID = "2:10";     // desktop frame
const WIDTH = 1440;          // must equal the frame width in Figma
const URL = "http://localhost:3000/pricing";

// 1. Export the design frame. scale:1 keeps it at its native width.
const meta = await fetch(
  `https://api.figma.com/v1/images/${FIGMA_FILE_KEY}?ids=${FRAME_ID}&format=png&scale=1`,
  { headers: { "X-Figma-Token": FIGMA_TOKEN } }
).then((r) => r.json());

const design = await fetch(meta.images[FRAME_ID]).then((r) => r.arrayBuffer());
await writeFile("out/design.png", Buffer.from(design));

// 2. Render the implementation at the same width and pixel ratio.
const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: WIDTH, height: 900 },
  deviceScaleFactor: 1,          // Figma exported at 1x, so the browser must match
});
await page.goto(URL, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);   // web fonts change every metric
await page.screenshot({ path: "out/implementation.png", fullPage: true });
await browser.close();
```

A `deviceScaleFactor` mismatch is the most common source of phantom differences: a 2x browser
capture against a 1x export makes every edge look wrong while the implementation is correct.

---

## Comparison Workflow

Every comparison should follow this sequence.

```
Open Approved Figma
        ↓
Open Implemented Page
        ↓
Match Viewport
        ↓
Match Zoom Level
        ↓
Capture Screenshots
        ↓
Compare Layout
        ↓
Compare Components
        ↓
Document Differences
        ↓
Fix Issues
        ↓
Repeat Verification
```

---

## Step 1 — Prepare the Environment

Verify:

- correct branch is running;
- latest implementation is loaded;
- browser cache is cleared if necessary;
- required fonts are loaded;
- correct theme is active;
- required content exists.

The implementation should be reviewed in its intended environment.

---

## Step 2 — Match Viewport

Use the same viewport dimensions as the design whenever possible.

Typical breakpoints:

- Desktop
- Laptop
- Tablet
- Mobile

A mismatch in viewport size may produce misleading differences.

---

## Step 3 — Match Zoom

Verify:

- browser zoom is 100%;
- operating system scaling is understood;
- Figma zoom is appropriate for inspection.

Do not compare screenshots captured at different scales.

---

## Step 4 — Compare Page Structure

Review:

- section order;
- page hierarchy;
- containers;
- alignment;
- whitespace.

Large structural differences should be investigated before reviewing smaller details.

A pixel diff finds *where* to look; it does not decide what is wrong. Generate one, then read
it:

```js
// scripts/diff.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { PNG } from "pngjs";
import pixelmatch from "pixelmatch";

const design = PNG.sync.read(readFileSync("out/design.png"));
const impl = PNG.sync.read(readFileSync("out/implementation.png"));

// Compare the shared region: a taller page is not itself a defect.
const width = Math.min(design.width, impl.width);
const height = Math.min(design.height, impl.height);
const diff = new PNG({ width, height });

const changed = pixelmatch(design.data, impl.data, diff.data, width, height, {
  threshold: 0.15,   // tolerate antialiasing; catch real color and position shifts
  includeAA: false,
});

writeFileSync("out/diff.png", PNG.sync.write(diff));
console.log(`${changed} px differ (${((changed / (width * height)) * 100).toFixed(2)}%)`);
if (design.height !== impl.height) {
  console.log(`height: design ${design.height} vs implementation ${impl.height}`);
}
```

Interpret the output structurally rather than numerically:

| What the diff shows | Usual cause |
|---|---|
| One block shifted, everything below it offset | A wrong spacing value near the top — fix that, and most of the diff disappears |
| Thin outlines around all text | Font not loaded, wrong weight, or a line-height ratio mismatch |
| Solid regions of difference | Wrong background token, or an image that failed to load |
| Diff only past a certain height | Real content is longer than the placeholder content in the design |

Never target zero. Real copy, real images, and browser text rendering all differ from a static
export — a 1–2% diff concentrated in text is normal, while a 0.3% diff shaped like a shifted
section is a defect.

---

## Step 5 — Compare Components

Review every reusable component.

Examples:

- buttons;
- cards;
- navigation;
- forms;
- accordions;
- tabs;
- sliders;
- pricing tables;
- testimonials.

Every instance should remain visually consistent.

---

## Step 6 — Compare Typography

Verify:

- font family;
- font size;
- font weight;
- line height;
- letter spacing;
- text alignment;
- heading hierarchy.

Typography differences often indicate incorrect design token usage.

For a difference you can see but not name, overlay the design on the live page instead of
switching between two windows:

```js
// Paste in the DevTools console on the implemented page.
const overlay = document.createElement("img");
overlay.src = "/out/design.png";          // or a pasted data: URL
Object.assign(overlay.style, {
  position: "absolute", top: "0", left: "50%", transform: "translateX(-50%)",
  width: "1440px", opacity: "0.5", zIndex: "99999", pointerEvents: "none",
  mixBlendMode: "difference",             // identical pixels turn black
});
document.body.append(overlay);

// Toggle: 'd' cycles difference/normal blending, 'x' removes the overlay.
addEventListener("keydown", (e) => {
  if (e.key === "d") overlay.style.mixBlendMode =
    overlay.style.mixBlendMode === "difference" ? "normal" : "difference";
  if (e.key === "x") overlay.remove();
});
```

With `mix-blend-mode: difference`, anything still visible is a discrepancy — this locates a
2px baseline shift far faster than reading two screenshots side by side. Web font loading is a
frequent culprit; see [Performance — Fonts](../performance/12-fonts.md).

---

## Step 7 — Compare Spacing

Review:

- section spacing;
- component spacing;
- margins;
- padding;
- grid gaps.

Spacing should follow the approved design system.

---

## Step 8 — Compare Colors

Verify:

- backgrounds;
- text colors;
- borders;
- buttons;
- icons;
- shadows.

Always compare against approved design tokens rather than subjective visual impressions.

---

## Step 9 — Compare Responsive Layouts

Repeat the comparison for:

- Desktop
- Laptop
- Tablet
- Mobile

Review:

- stacking behavior;
- navigation;
- spacing;
- typography;
- image scaling.

Every breakpoint should be verified independently.

---

## Step 10 — Compare Interactions

Review interactive elements.

Examples:

- hover;
- focus;
- active;
- disabled;
- expanded;
- collapsed;
- loading.

Static screenshots alone are not sufficient for interaction verification.

---

## Recording Differences

Every identified issue should include:

- location;
- description;
- expected result;
- actual result;
- severity;
- recommended fix.

Clear documentation reduces unnecessary review cycles.

---

## Severity Levels

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

- alignment differences;
- inconsistent padding;
- incorrect icon size;
- small border-radius differences.

Fix whenever practical.

---

## Cosmetic

Examples:

- insignificant visual differences;
- decorative inconsistencies.

May be deferred if they do not affect usability or design consistency.

---

## AI Execution Checklist

## Investigation

☐ Compare overall layout.

☐ Compare sections.

☐ Compare components.

☐ Compare typography.

☐ Compare spacing.

☐ Compare colors.

☐ Compare responsiveness.

☐ Compare interactions.

---

## Verification

☐ Every difference has been documented.

☐ Severity has been assigned.

☐ Recommended fixes are clear.

☐ Final comparison confirms design accuracy.

---

## Common Mistakes

Avoid:

Comparing different viewport sizes.

Comparing different zoom levels.

Ignoring typography.

Ignoring spacing.

Ignoring responsive layouts.

Ignoring interaction states.

Approving pages without side-by-side comparison.

---

## Examples

**Good Example** — deterministic capture, then a numeric threshold

```ts
// Fix everything that varies between runs, or the diff reports noise.
import { test, expect } from '@playwright/test';

test('product card matches the reference', async ({ page }) => {
  await page.goto('/products/lamp');

  // Freeze animations and blinking carets.
  await page.addStyleTag({
    content: `*, *::before, *::after {
      animation: none !important;
      transition: none !important;
      caret-color: transparent !important;
    }`,
  });

  // Wait for the actual condition, not for a fixed duration.
  await page.getByRole('img', { name: /ceramic table lamp/i }).waitFor({ state: 'visible' });
  await page.evaluate(() => document.fonts.ready);

  await expect(page.getByTestId('product-card')).toHaveScreenshot('product-card.png', {
    maxDiffPixelRatio: 0.01,      // a stated tolerance, not "looks the same"
    animations: 'disabled',
  });
});
```

```bash
# The comparison runs in the same container as CI, so the font rendering matches.
docker run --rm -v "$PWD:/work" -w /work mcr.microsoft.com/playwright:v1.50.0-noble \
  npx playwright test --update-snapshots
```

**Bad Example** — eyeballing two screenshots side by side

```ts
test('product card looks right', async ({ page }) => {
  await page.goto('/products/lamp');

  // An arbitrary sleep instead of a condition: too short under load, wasted
  // time otherwise, and the fonts may still be swapping when the shot is taken.
  await page.waitForTimeout(2000);

  // No threshold: a single antialiased pixel fails the test, so the suite is
  // marked flaky and eventually skipped.
  await expect(page).toHaveScreenshot();
});
```

Baselines generated on a developer's macOS machine and compared on a Linux runner differ in
font rasterisation on every glyph. The comparison is not wrong — the environment is.

---

## Completion Criteria

Screenshot comparison is complete when:

- every supported breakpoint has been reviewed;
- visual differences have been documented;
- significant issues have been resolved;
- the implementation accurately reflects the approved design.

---

## Related Knowledge

- [Design QA](10-design-qa.md) — the review this comparison feeds; findings go into its report format.
- [Visual Regression](13-visual-regression.md) — comparing against the previous build instead of the design, and running it in CI.
- [Responsive Analysis](05-responsive-analysis.md) — which viewports must be compared and why.
- [Testing — Visual Regression](../testing/14-visual-regression.md) and [Testing — UI Testing](../testing/13-ui-testing.md) — the surrounding testing practice.
- [Performance — Fonts](../performance/12-fonts.md) — font loading behavior behind most typography differences.
- [Implementation Definition of Done](20-implementation-definition-of-done.md) — the acceptance bar this evidence supports.

---

## Summary

Screenshot comparison provides an objective method for validating frontend implementations against approved designs.

When performed consistently, it improves design accuracy, reduces review iterations, and increases confidence before production deployment.