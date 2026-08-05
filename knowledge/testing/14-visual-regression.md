---
id: testing/14-visual-regression
topic: testing
slug: visual-regression
title: "Testing Visual Regression"
type: doc
order: 14
status: ready
tags: [testing, visual-regression]
related: [testing/13-ui-testing, testing/04-e2e-testing, testing/22-flaky-tests, testing/18-accessibility-testing, testing/20-test-maintenance]
when_to_use: "Read before adding screenshot-based tests that guard the rendered appearance of a component or page."
---
# Testing Visual Regression

## Purpose

This document defines how to guard the *rendered appearance* of a UI against unintended
change by comparing screenshots to an approved baseline. It complements
[UI testing](13-ui-testing.md), which checks behavior: visual regression checks that a
component still *looks* right — layout, spacing, color, overflow, and the bugs a DOM
assertion cannot see.

A visual test renders a component or page, captures an image, and diffs it pixel-by-pixel
(or perceptually) against a stored baseline. A difference beyond a threshold fails the
test and a human decides whether it is a bug or an intended change to re-baseline.

## Why It Matters

Whole classes of regressions are invisible to functional tests: a `z-index` that hides a
button, text that overflows its container, a broken dark-mode color, a shifted layout on
a narrow viewport. The DOM is correct; the pixels are wrong. Visual tests are the only
economical way to catch these across many components and states. They are also the
easiest tests to make flaky — a single unstable font, animation, or timestamp turns the
whole suite into noise the team learns to click past. Stability *is* the feature here.

## Core Principles

- **A baseline is a reviewed artifact, not a byproduct.** Every baseline image must be
  reviewed and committed like code. An unreviewed baseline blesses whatever bug was on
  screen when it was captured.
- **Eliminate every non-deterministic pixel before comparing.** Fonts, animations, dates,
  random data, and caret blinks must be frozen. A flaky visual test is worthless.
- **Diff perceptually, with an intentional threshold.** Anti-aliasing and sub-pixel
  rendering differ across machines; a tiny tolerance prevents false failures without
  hiding real ones.
- **A failure means "look," not "broken."** The test flags a pixel change; a human
  decides bug vs. intended. Never auto-accept new baselines in CI.
- **Test states, not just pages.** Empty, loading, error, long-text, and RTL states are
  where visual bugs hide — capture them as separate stories.

## Best Practices

- Render at a fixed viewport and device-pixel-ratio, and pin the exact browser version.
  Screenshots taken on different engines will never match.
- Disable animations and transitions and freeze time and randomness before capture, so
  the same input always produces the same pixels.
- Load fonts from local files and wait for `document.fonts.ready`; a late web font shifts
  every glyph and fails the whole page.
- Mask or exclude genuinely dynamic regions (avatars, ad slots, live clocks) rather than
  letting them flap the diff.
- Capture small, isolated components (Storybook stories, Playwright component snapshots)
  rather than giant full-page shots — small diffs are reviewable; huge ones get
  rubber-stamped.
- Generate baselines in the same environment CI runs (a pinned container), so local and
  CI pixels agree. Never commit baselines captured on a developer laptop.
- Review visual diffs like code: the PR must show before/after/diff, and re-baselining is
  an explicit, reviewed act.

## Examples

**Good Example** — deterministic render, scoped snapshot, intentional threshold

```ts
import { test, expect } from "@playwright/test";

test("pricing card — dark mode", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await page.goto("/iframe.html?id=pricing-card--pro"); // isolated story, not full app

  // Freeze the sources of non-determinism, then wait for fonts before capturing.
  await page.addStyleTag({ content: `*,*::before,*::after{
    animation:none!important; transition:none!important; caret-color:transparent!important;}` });
  await page.evaluate(() => document.fonts.ready);

  await expect(page.getByTestId("pricing-card")).toHaveScreenshot("pricing-pro-dark.png", {
    maxDiffPixelRatio: 0.01, // small perceptual tolerance for anti-aliasing, not a blank check
  });
});
```

**Bad Example** — full-page shot with live data, no stabilization, auto-approve

```ts
test("home page looks right", async ({ page }) => {
  await page.goto("/"); // real page: live "posted 2m ago" timestamps, lazy avatars, ads

  // No animation/font/time freezing, zero tolerance, and CI writes a new baseline
  // whenever it fails — so the test both flakes constantly and rubber-stamps regressions.
  await expect(page).toHaveScreenshot("home.png");
});
```

## Common Mistakes

- Committing a baseline no one reviewed, freezing an existing bug as "correct."
- Leaving animations, timestamps, or random data live, so the diff flaps and gets ignored.
- Zero tolerance, causing anti-aliasing noise to fail builds on a different machine.
- Screenshotting whole pages, producing diffs too large to review honestly.
- Running captures across mismatched browser versions or viewports between local and CI.
- Configuring CI to auto-update baselines on failure, which silently accepts every change.

## Production Tips

- Run visual tests in a pinned Docker image so font rendering is byte-stable between
  contributors and CI. Font antialiasing is the number-one source of cross-machine noise.
- Gate re-baselining behind a required review and store baselines with LFS or an external
  snapshot service to keep the repo lean.
- Keep the visual suite small and high-signal; it guards appearance, not logic. Behavior
  belongs in [UI](13-ui-testing.md) and [E2E](04-e2e-testing.md) tests.

## AI Review Checklist

- Is every baseline image reviewed and committed, never auto-generated in CI on failure?
- Are animations, time, randomness, and fonts frozen before capture?
- Is the viewport, color scheme, and browser version pinned and matched between local and CI?
- Is the diff scoped to a component or masked region rather than a whole live page?
- Is there an intentional perceptual threshold instead of exact-pixel matching?
- Does re-baselining require an explicit, human-reviewed step?

## Related

- `knowledge/testing/13-ui-testing.md`
- `knowledge/testing/04-e2e-testing.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/18-accessibility-testing.md`
- `knowledge/testing/20-test-maintenance.md`
