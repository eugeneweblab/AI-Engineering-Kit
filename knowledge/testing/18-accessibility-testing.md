---
id: testing/18-accessibility-testing
topic: testing
slug: accessibility-testing
title: "Testing Accessibility Testing"
type: doc
order: 18
status: ready
tags: [testing, accessibility-testing, toHaveFocus, aria-live, click, querySelector, getByRole, data-testid]
related: [testing/13-ui-testing, testing/04-e2e-testing, testing/14-visual-regression, testing/09-assertions, testing/27-quality-gates]
when_to_use: "Read before writing or reviewing tests for any user-facing UI that must be usable with a keyboard or screen reader."
---
# Testing Accessibility Testing

## Purpose

This document defines how to test that a UI is usable by people who rely on
assistive technology — screen readers, keyboard-only navigation, magnification,
and reduced motion. It is written so an agent can add or review accessibility
(a11y) tests that catch real barriers, not just lint-level noise.

Accessibility testing verifies conformance to **WCAG 2.2** success criteria and,
just as importantly, that the interface *works* when driven without a mouse or
without sight. It complements [UI testing](13-ui-testing.md) — you are asserting
on the accessibility tree, not only the visual DOM.

## Why It Matters

Accessibility defects are silent to sighted, mouse-using developers: the app
looks perfect while an entire class of users cannot complete the flow. Unlike a
visual bug, no screenshot reveals a missing form label or a focus trap. These
defects also carry legal exposure (ADA, Section 508, the European Accessibility
Act) and they compound — an un-labelled icon button ships once and breaks every
screen-reader user forever. Automated a11y tests turn an invisible, subjective
concern into a concrete, regression-guarded assertion in CI.

## Core Principles

- **Automated tools find ~30-40% of issues.** Axe, Lighthouse, and Pa11y catch
  contrast, missing labels, and bad ARIA, but they cannot judge whether focus
  order makes sense or whether an announcement is meaningful. Automate the
  mechanical checks; keep a manual keyboard/screen-reader pass for the rest.
- **Query by role and accessible name.** Test the way assistive tech sees the
  page (`getByRole('button', { name: /save/i })`), not by CSS class or test id.
  A test that passes only via `data-testid` proves nothing about accessibility.
- **Keyboard is the baseline.** Every interactive element must be reachable and
  operable with Tab, Shift+Tab, Enter, Space, and arrow keys. If the keyboard
  path works, most assistive tech works.
- **Assert on the accessibility tree, not the pixels.** Names, roles, states
  (`aria-expanded`, `aria-invalid`), and focus are the contract. Color and
  position are not.
- **Zero critical violations is a gate, not a goal.** Fail the build on serious
  and critical violations; do not merely report them.

## Best Practices

- Run `axe-core` (via `jest-axe`, `@axe-core/playwright`, or `cypress-axe`) on
  every meaningful UI state — including modals open, menus expanded, and error
  states — because violations often appear only after interaction.
- Test keyboard flows explicitly: tab through the component, assert focus lands
  where expected, and confirm `Escape` closes overlays and restores focus.
- Verify focus management on route changes and after async actions — focus must
  never be lost to `<body>` or trapped inside a closed dialog.
- Assert accessible names for icon-only controls and images, and `aria-live`
  regions announce async updates (toasts, validation, loading).
- Check color contrast programmatically (axe covers WCAG 1.4.3), and test that
  the UI still functions with `prefers-reduced-motion` and at 200% zoom.
- Scope automated scans to the component under test to keep failures actionable;
  a page-wide scan reports third-party noise you cannot fix.
- Include a screen-reader smoke test in QA for critical flows (VoiceOver, NVDA);
  document expected announcements so regressions are catchable.

## Examples

**Good Example** — role-based queries, axe scan, and a real keyboard assertion

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";

test("dialog is accessible and keyboard-operable", async () => {
  const user = userEvent.setup();
  const { container } = render(<SettingsDialog />);

  // Query by role + accessible name — exactly what a screen reader exposes.
  const open = screen.getByRole("button", { name: /open settings/i });
  await user.click(open);

  const dialog = screen.getByRole("dialog", { name: /settings/i });
  expect(dialog).toHaveFocus(); // focus must move into the dialog, not stay behind

  // Axe scans the DOM in its *current* state (dialog open), where real bugs live.
  expect(await axe(container)).toHaveNoViolations();

  await user.keyboard("{Escape}");
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  expect(open).toHaveFocus(); // focus returns to the trigger — no lost focus
});
```

**Bad Example** — tests the DOM by class, never exercises assistive-tech surface

```tsx
test("settings dialog works", async () => {
  const user = userEvent.setup();
  render(<SettingsDialog />);

  // Selecting by class/testid proves nothing about the accessible name or role.
  await user.click(document.querySelector(".gear-icon")!);

  // Asserts a visual class, not that the element is exposed as a dialog.
  expect(document.querySelector(".modal.is-open")).toBeTruthy();
  // No axe scan, no keyboard operation, no focus assertion → screen-reader users
  // and keyboard users are entirely untested. This passes while a11y is broken.
});
```

## Common Mistakes

- Running axe only on the initial page and missing violations in modals, menus,
  and error states that appear after interaction.
- Selecting elements by `data-testid` or CSS class, which bypasses the very
  role/name contract accessibility depends on.
- Treating a passing axe scan as full coverage — it never validates focus order,
  keyboard traps, or whether an announcement makes sense.
- Not asserting focus management, so focus silently escapes to `<body>` after a
  dialog closes or a route changes.
- Ignoring `aria-live` regions, so async success/error messages are never
  announced to screen-reader users.
- Reporting violations without failing the build, so they accumulate forever.

## Production Tips

- Add an axe scan to component and E2E suites and fail CI on `serious`/`critical`
  impact; downgrade `moderate`/`minor` to warnings to avoid blocking on noise.
- Track a per-page violation baseline so new violations fail even when legacy
  ones are temporarily allowlisted (with a ticket, not silently).
- Pair automated checks with a periodic manual screen-reader audit of the top
  user journeys; automation alone will never reach WCAG conformance.

## AI Review Checklist

- Does every interactive element have a test asserting its role and accessible
  name (not a class or test id)?
- Is axe (or equivalent) run in each meaningful UI state, including modals and
  error states — not just the initial render?
- Are keyboard flows tested: Tab reachability, Enter/Space activation, Escape to
  close, and focus restoration?
- Is focus management asserted on open/close and route changes?
- Are `aria-live` announcements for async updates verified?
- Does CI fail on serious/critical violations rather than only reporting them?

## Related

- `knowledge/testing/13-ui-testing.md`
- `knowledge/testing/04-e2e-testing.md`
- `knowledge/testing/14-visual-regression.md`
- `knowledge/testing/09-assertions.md`
- `knowledge/testing/27-quality-gates.md`
