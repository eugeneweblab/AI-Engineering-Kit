---
id: accessibility/20-testing-tools
topic: accessibility
slug: testing-tools
title: "Testing Tools"
type: doc
order: 20
status: ready
tags: [accessibility, testing-tools]
related: [accessibility/21-axe, accessibility/22-lighthouse, accessibility/24-accessibility-testing, accessibility/06-screen-readers, accessibility/23-wcag]
when_to_use: "Read before choosing how to test accessibility, or when deciding what a passing automated scan does and does not prove."
---
# Testing Tools

## Purpose

This document maps the landscape of accessibility testing tools and, more importantly,
what each one can and cannot catch. It exists to prevent the single most common
accessibility mistake in engineering teams: treating a green automated scan as proof
of an accessible product. It orients you to the three complementary layers —
automated engine, manual assistive-tech testing, and keyboard testing — and hands off
to the deep dives on [axe](21-axe.md) and [Lighthouse](22-lighthouse.md).

## Why It Matters

Automated tools reliably detect only **20–40%** of WCAG issues — the machine-checkable
ones: missing `alt`, insufficient contrast, absent form labels, invalid ARIA. The
remaining majority are judgment calls a machine cannot make: is this alt text
*meaningful*? Is the focus order *logical*? Does this custom widget *behave* like a
combobox? A team that ships on "axe passes" ships a product that is technically scanned
and practically unusable. Knowing each tool's blind spot is what separates a checkbox
audit from real coverage.

## Core Principles

- **Automation is a floor, not a ceiling.** A clean scan means "no machine-detectable
  errors," never "accessible." Treat it as the cheapest gate, run first, not the verdict.
- **Three layers, not one.** Automated engine (axe), keyboard-only pass, and screen
  reader testing each catch a different class of defect. Skipping any leaves a gap.
- **Test with real assistive technology.** Nothing substitutes for driving the UI with a
  screen reader (VoiceOver, NVDA, JAWS) and with the keyboard alone.
- **Shift left.** The cheapest defect is caught in the editor or unit test; the most
  expensive is caught by a user in production. Put automation in dev and CI, not just audit.
- **Right tool for the layer.** A browser extension for spot checks, a library
  (`@axe-core/*`) for CI, a manual protocol for judgment — do not force one tool to do all.

## Best Practices

- Run an **axe-based** engine (jest-axe, `@axe-core/playwright`, cypress-axe) in the test
  suite so regressions fail the build. This is the highest-leverage single step.
- Use the **axe DevTools** or **WAVE** browser extension for interactive spot checks
  during development, when you can inspect a specific component in state.
- Use **Lighthouse** for a scored, per-page snapshot in CI and for tracking a trend over
  time — but read its accessibility category as a subset of axe, not a full audit.
- Add a **keyboard-only** pass to every feature's definition of done: Tab, Shift+Tab,
  Enter, Space, Escape, arrows — reach and operate everything, visible focus throughout.
- Add a **screen reader** pass for any custom or interactive component; test at least one
  screen reader per platform you support (VoiceOver/Safari, NVDA/Firefox).
- Check **contrast** with a dedicated checker (axe, WebAIM Contrast Checker) at design
  time, not after build, so it is cheap to fix.
- Record what was tested and how — the tools do not prove human judgment happened; your
  [testing protocol](24-accessibility-testing.md) does.

## Examples

**Good Example** — automation gates CI, humans cover the rest

```tsx
// vitest + jest-axe: catches the machine-detectable 20-40% on every commit
import { axe } from "jest-axe";

test("dialog has no automatically-detectable a11y violations", async () => {
  const { container } = render(<Dialog open />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
// A green result here is the FLOOR. A keyboard pass and a VoiceOver pass
// are still required before this component is "done".
```

**Bad Example** — one scan treated as the whole audit

```ts
// Runs Lighthouse once, sees a 100, declares the page "accessible"
const { lhr } = await lighthouse(url);
if (lhr.categories.accessibility.score === 1) {
  markAccessible(); // FALSE: a 100 ignores focus order, alt quality,
                    // keyboard operability, and screen reader behavior
}
```

## Common Mistakes

- Equating a passing automated scan with an accessible product — it covers a minority of
  criteria.
- Running the scan only against the initial page load, never against opened menus,
  dialogs, error states, or expanded content where most bugs live.
- Never testing with an actual screen reader or the keyboard alone.
- Relying on a Lighthouse score as a compliance metric — it is a weighted subset.
- Testing in only one browser/AT pair; behavior differs across NVDA, JAWS, and VoiceOver.
- Auditing at the end as a gate instead of testing continuously during development.

## Production Tips

- Wire axe into the component test suite and fail the pipeline on new violations; keep a
  reviewed, time-boxed allowlist for known issues rather than disabling the gate.
- Add a lightweight per-PR checklist item: "keyboard pass done, screen reader pass done"
  for interactive changes, so human layers are not silently skipped.
- Track the automated violation count over time as a trend, not a pass/fail, so the
  number does not create false confidence.

## AI Review Checklist

- Is an axe-based engine running in unit or e2e tests and gating CI?
- Are dynamic states (dialogs, menus, errors) scanned, not just initial load?
- Is there evidence of a keyboard-only pass for interactive changes?
- Is there evidence of a screen reader pass for custom widgets?
- Is any automated score being treated as full coverage rather than a floor?
- Is contrast checked at design time with a dedicated tool?

## Related

- `knowledge/accessibility/21-axe.md`
- `knowledge/accessibility/22-lighthouse.md`
- `knowledge/accessibility/24-accessibility-testing.md`
- `knowledge/accessibility/06-screen-readers.md`
- `knowledge/accessibility/23-wcag.md`
