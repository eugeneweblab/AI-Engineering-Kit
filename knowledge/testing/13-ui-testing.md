---
id: testing/13-ui-testing
topic: testing
slug: ui-testing
title: "UI Testing"
type: doc
order: 13
status: ready
tags: [testing, ui-testing]
related: [testing/04-e2e-testing, testing/14-visual-regression, testing/18-accessibility-testing, testing/02-unit-testing, testing/22-flaky-tests]
when_to_use: "Read before writing or reviewing tests for a component or page rendered in a browser or a DOM environment."
---
# UI Testing

## Purpose

This document defines how to test user-interface code — components and pages — by driving
them the way a user does: rendering, interacting, and asserting on what the user can
observe. It covers component tests (one component in a DOM) and stops where full
[E2E tests](04-e2e-testing.md) begin (the whole app through a real browser).

A UI test proves that when a user does something, the interface responds correctly. It
does not test that a specific prop was passed or a specific hook fired — those are
implementation details a refactor should be free to change.

## Why It Matters

UI is where correctness meets the user. A component that computes the right value but
renders it in a disabled button, behind a broken conditional, or with an inaccessible
label is still broken. Yet UI is also the most tempting place to write brittle tests:
tests coupled to CSS classes, DOM structure, or internal state break on every harmless
refactor, so teams stop trusting them and delete them. Tests written around *user-visible
behavior* survive redesigns and catch the regressions that actually reach users.

## Core Principles

- **Query the way a user perceives the UI.** Find elements by role, label, and visible
  text — not by CSS selector, test-id-of-last-resort, or DOM position. If a user finds a
  button by its label, so should the test.
- **Interact, do not inspect internals.** Click, type, and submit. Never reach into
  component state or call internal methods; assert on the rendered result instead.
- **Assert what the user sees.** The error message appears, the button becomes disabled,
  the row is removed. Not "state.loading is true."
- **Accessibility and testability are the same thing.** Role- and label-based queries only
  work if the UI is accessible. A hard-to-test UI is usually a hard-to-use one.
- **Determinism over speed hacks.** Wait for the UI to reach the expected state; never
  wait on a fixed timer. See [flaky tests](22-flaky-tests.md).

## Best Practices

- Use a user-centric library (Testing Library family, Playwright's role locators). Prefer
  `getByRole`, `getByLabelText`, `getByText`; fall back to `data-testid` only for
  elements with no accessible identity.
- Render the real component with its real children; mock only external boundaries
  (network, time, navigation), not the component's own logic.
- Drive interactions through the high-level user API (`userEvent`), which fires the full
  event sequence a real user triggers — not a bare `fireEvent.click`.
- Assert asynchronous outcomes with `findBy*` / `waitFor`, which retry until the condition
  holds or times out. Never assert immediately after an async action.
- Stub the network at the transport (MSW, route interception) so the component runs its
  real fetch-and-render path against controlled responses.
- Keep component tests for logic and interaction; delegate cross-browser rendering and
  pixel fidelity to [visual regression](14-visual-regression.md).
- Run an accessibility assertion (`axe`) inside the component test to catch missing labels
  and roles at the cheapest possible point.

## Examples

**Good Example** — user-facing queries, real interaction, awaited result

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginForm } from "./LoginForm";

it("shows an error when the password is empty", async () => {
  render(<LoginForm />);

  // Found the way a user finds them: by their accessible label and role.
  await userEvent.type(screen.getByLabelText(/email/i), "ada@example.com");
  await userEvent.click(screen.getByRole("button", { name: /log in/i }));

  // Waits for the UI to reach the expected state instead of asserting on internals.
  expect(await screen.findByText(/password is required/i)).toBeVisible();
  expect(screen.getByRole("button", { name: /log in/i })).toBeDisabled();
});
```

**Bad Example** — couples to structure and internal state, races the render

```tsx
it("shows an error when the password is empty", () => {
  const { container } = render(<LoginForm />);

  container.querySelector(".login-btn").click();      // brittle CSS selector
  // Reads component internals a refactor is free to change, and asserts synchronously
  // before React has re-rendered, so it flakes or checks the wrong thing.
  expect(container.querySelector(".error").textContent).toBe("Password is required");
});
```

## Common Mistakes

- Selecting elements by CSS class, tag, or DOM index, so a harmless markup change breaks
  the test.
- Asserting on component state, props, or hook calls instead of rendered output.
- Using fixed `setTimeout`/`sleep` waits instead of `findBy`/`waitFor`, producing flakes.
- Over-mocking: replacing the component's own children or logic so the test proves nothing
  about real behavior.
- Firing low-level events (`fireEvent`) that skip focus, key, and input events a real user
  generates, hiding bugs in real interactions.
- Pushing whole user journeys into component tests when they belong in
  [E2E](04-e2e-testing.md); component tests should stay fast and focused.

## Production Tips

- Keep `data-testid` as a deliberate, documented escape hatch, not the default query —
  its overuse is a sign the UI lacks accessible structure.
- Snapshot only small, stable subtrees, if at all; large auto-snapshots rot into
  rubber-stamped diffs no one reviews.
- Run component tests in a real browser engine (Playwright/Vitest browser mode) when
  layout or native input behavior matters; jsdom approximates the DOM but not the browser.

## AI Review Checklist

- Are elements queried by role, label, or visible text rather than CSS/DOM structure?
- Do assertions check user-visible output, not component state or props?
- Are async results awaited with `findBy`/`waitFor`, never a fixed timer?
- Is the network stubbed at the boundary so the real fetch-render path runs deterministically?
- Are interactions driven through `userEvent` so the full event sequence fires?
- Is at least one accessibility check present for forms and interactive components?

## Related

- `knowledge/testing/04-e2e-testing.md`
- `knowledge/testing/14-visual-regression.md`
- `knowledge/testing/18-accessibility-testing.md`
- `knowledge/testing/02-unit-testing.md`
- `knowledge/testing/22-flaky-tests.md`
