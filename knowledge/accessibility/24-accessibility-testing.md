---
id: accessibility/24-accessibility-testing
topic: accessibility
slug: accessibility-testing
title: "Accessibility Testing"
type: doc
order: 24
status: ready
tags: [accessibility, accessibility-testing, toHaveNoViolations, cypress-axe, jest-axe, toBe]
related: [accessibility/20-testing-tools, accessibility/21-axe, accessibility/22-lighthouse, accessibility/04-keyboard-navigation, accessibility/06-screen-readers]
when_to_use: "Read before adding accessibility checks to a test suite or a CI pipeline, or when deciding what to test manually versus automatically."
---
# Accessibility Testing

## Purpose

This document defines a testing strategy that catches accessibility defects before
users do. It covers what automated tools can and cannot verify, how to layer manual
checks on top, and how to wire both into CI so regressions fail the build. The goal is
a repeatable process an agent can implement, not a one-time audit.

Testing is how [WCAG](23-wcag.md) conformance stops being an aspiration and becomes a
gate. See [testing tools](20-testing-tools.md) for the tool landscape and
[axe](21-axe.md) / [Lighthouse](22-lighthouse.md) for the two engines used below.

## Why It Matters

Accessibility bugs are invisible to the developer who introduced them: the page looks
fine on screen, so nothing signals a broken screen-reader flow or an unreachable button.
Without an explicit test, the only "detector" is a disabled user hitting a wall in
production — the most expensive and least fair place to find the defect. Automated tests
turn a silent, subjective quality into a hard, reproducible signal that blocks merges.

The catch: automation covers only part of the problem. Studies of real audits put
automated coverage at roughly 30–40% of WCAG success criteria. The rest — whether alt
text is *meaningful*, whether focus order is *logical*, whether a control is *operable*
— needs a human. A team that ships on a green axe run alone has a false sense of safety.

## Core Principles

- **Automate the mechanical, verify the meaningful by hand.** Tools catch missing
  attributes and contrast math; humans judge intent, order, and usability.
- **Shift left.** A failing unit test on a component costs minutes; a legal complaint on
  a shipped flow costs months. Run checks in the editor, in CI, and in review.
- **Test the rendered output, not the source.** Accessibility lives in the final DOM
  after JavaScript runs, so drive a real browser or a real DOM, not static markup.
- **Fail the build on new violations.** A warning that scrolls past in a log changes
  nothing. Conformance you do not enforce, you do not have.
- **Test with the assistive tech, not just about it.** Nothing substitutes for a
  keyboard run and a screen-reader pass on the primary user flows.

## Best Practices

- Run **axe-core** (via `@axe-core/playwright`, `jest-axe`, or `cypress-axe`) against key
  pages and component states. Assert **zero** violations; do not soft-fail.
- Test **dynamic states**, not just first paint: open menus, expanded accordions,
  validation errors, loading and empty states. Bugs hide in the states automation skips.
- Add a **keyboard-only walkthrough** to your manual checklist: Tab, Shift+Tab, Enter,
  Space, Escape, and arrow keys through every interactive element. See
  [keyboard navigation](04-keyboard-navigation.md).
- Do at least one **screen-reader pass** per release on core flows — NVDA + Firefox or
  VoiceOver + Safari. Automation cannot hear what the user hears.
- Test at **200% zoom** and **400% reflow** (320 CSS px width) to catch content that is
  clipped or requires two-dimensional scrolling.
- Include users with disabilities in usability testing when the stakes justify it; their
  feedback finds problems no checklist enumerates.
- Track results over time so you can prove the trend is down, not just that today is green.

## Examples

**Good Example** — component test that fails CI on a real violation

```tsx
import { render } from "@testing-library/react";
import { axe } from "jest-axe"; // runs axe-core against the rendered DOM

test("Dialog has no detectable a11y violations when open", async () => {
  // Render the OPEN state — the interactive state is where violations live.
  const { container } = render(<Dialog open title="Delete file?" />);

  const results = await axe(container);
  // Assert zero violations; a soft console.warn would let regressions merge.
  expect(results).toHaveNoViolations();
});
```

**Bad Example** — checks static markup and swallows failures

```tsx
test("page is accessible", async () => {
  const html = renderToStaticMarkup(<Page />); // no JS, no dynamic states
  const results = await axe(html);

  if (results.violations.length) {
    console.warn(results.violations); // logged, never enforced → regressions ship
  }
  expect(true).toBe(true); // always passes; the test asserts nothing
});
```

## Common Mistakes

- Treating a green automated run as full conformance; ~60% of criteria are never checked.
- Testing only the initial render, missing violations in menus, dialogs, and error states.
- Logging violations as warnings instead of failing the test, so nothing is enforced.
- Running axe on server-rendered HTML before hydration, missing JS-injected ARIA.
- Skipping the keyboard and screen-reader passes because "the tool was green."
- Auditing once at launch and never again, so every later change silently regresses.
- Suppressing rules wholesale to get to green instead of fixing the underlying markup.

## Production Tips

- Gate merges with a CI job that runs axe on critical pages; publish the report as an
  artifact so reviewers can see exactly what failed and where.
- Keep a short, versioned manual test script (keyboard, zoom, screen reader) in the repo
  so every release runs the same checks the same way.
- Snapshot the accessibility tree in tests for complex widgets; a diff surfaces broken
  name/role/value regressions that a rule-based scan can miss.

## AI Review Checklist

- Do automated a11y tests run in CI and **fail the build** on new violations?
- Are tests run against the **rendered DOM** with dynamic states exercised, not static HTML?
- Is there a documented **keyboard-only** and **screen-reader** manual pass for core flows?
- Are **zoom (200%)** and **reflow (320px)** covered for primary layouts?
- Does the team understand automation covers only part of WCAG, with the rest verified by hand?
- Are suppressed rules justified in code, or are they hiding real defects?

## Related

- `knowledge/accessibility/20-testing-tools.md`
- `knowledge/accessibility/21-axe.md`
- `knowledge/accessibility/22-lighthouse.md`
- `knowledge/accessibility/04-keyboard-navigation.md`
- `knowledge/accessibility/06-screen-readers.md`
