---
id: frontend/22-testing
topic: frontend
slug: testing
title: "Frontend Testing"
type: doc
order: 22
status: ready
tags: [frontend, testing]
related: [frontend/02-component-driven-development, frontend/09-accessibility, frontend/13-error-handling, frontend/19-build-tools]
when_to_use: "Read before writing or reviewing tests for frontend components, hooks, pages, or user flows."
---
# Frontend Testing

## Purpose

This document defines how to test frontend code — components, hooks, and user flows —
so tests catch real regressions and survive refactors. It is written so an agent can
add or review tests without producing brittle, implementation-coupled, or falsely-green
suites.

Frontend testing has a specific goal: prove the UI does what a *user* can observe, not
that internals are shaped a certain way. Tests that assert on internal state and DOM
structure break on every refactor and pass while the feature is broken. This connects to
[component-driven development](02-component-driven-development.md) and
[accessibility](09-accessibility.md), since querying by role is both robust and a11y-aware.

## Why It Matters

A test suite is only valuable if a green run means the app works and a red run means it
doesn't. Tests that couple to implementation details fail that bar in both directions:
they go red on harmless refactors (training the team to ignore failures) and stay green
when behavior regresses (because they never exercised behavior). The result is worse
than no tests — false confidence plus maintenance drag. Getting the *level* and *query
strategy* right is what makes a suite a safety net instead of a liability.

## Core Principles

- **Test behavior, not implementation.** Assert what the user sees and can do. Never
  assert on component state, private methods, or CSS-class internals.
- **Query the way users perceive the UI.** Prefer accessible-role and text queries over
  test IDs and DOM traversal; this also verifies accessibility for free.
- **Follow the testing trophy.** Most value is in integration/component tests; add a
  thin layer of unit tests for pure logic and a few end-to-end tests for critical flows.
- **Deterministic, isolated, fast.** No shared state, no real network, no reliance on
  timers or order. A flaky test is a broken test.
- **Test the states that break in production.** Loading, empty, error, and edge cases —
  not just the happy path.

## Best Practices

- Use a modern fast runner — **Vitest** (or Jest) — with **Testing Library** for
  components and **Playwright**/**Cypress** for end-to-end flows.
- Query by role and accessible name (`getByRole("button", { name: /save/i })`); fall
  back to `getByLabelText`/`getByText`; use `getByTestId` only as a last resort.
- Simulate real interaction with `user-event` (which fires the full event sequence),
  not raw `fireEvent`, so tests match how users actually interact.
- Await async UI with `findBy*` / `waitFor`; never assert immediately after an action
  that triggers async work.
- Mock the network at the boundary with **MSW** (request interception), not by stubbing
  your own fetch functions — this keeps tests honest about real request/response shapes.
- Write one clear assertion of intent per test; name tests by the behavior under test.
- Run tests in CI on every PR, collect coverage as a signal (not a target to game), and
  fail the build on failures and unhandled console errors.
- Add accessibility assertions (`axe`) to component tests to catch regressions early.

## Examples

**Good Example** — behavior-focused, role queries, real interaction

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginForm } from "./LoginForm";

test("shows an error when login fails", async () => {
  const user = userEvent.setup();
  render(<LoginForm />); // network mocked with MSW to return 401

  // Query as a user would: by label and role, not by class or test id.
  await user.type(screen.getByLabelText(/email/i), "a@b.com");
  await user.type(screen.getByLabelText(/password/i), "wrong");
  await user.click(screen.getByRole("button", { name: /log in/i }));

  // Assert the observable outcome, and await the async UI update.
  expect(await screen.findByRole("alert")).toHaveTextContent(/invalid/i);
});
```

**Bad Example** — couples to internals, brittle and false-green

```tsx
test("login", () => {
  const wrapper = shallow(<LoginForm />);
  // WHY BAD: asserts on internal state — breaks on any refactor, tests nothing a user sees.
  wrapper.instance().setState({ email: "a@b.com", password: "wrong" });
  wrapper.find(".submit-btn").simulate("click"); // brittle CSS-class selector

  // WHY BAD: no await on async work → assertion runs before the error renders,
  // so this passes even when the error message never appears.
  expect(wrapper.state("error")).toBe(true);
});
```

## Common Mistakes

- Asserting on component state, props, or CSS classes instead of user-visible output.
- Querying by test ID or DOM path when a role/label query would be robust and a11y-aware.
- Missing `await` on async UI, producing tests that pass before the DOM updates.
- Mocking your own data-fetching functions instead of the network boundary, so tests
  never verify real request/response contracts.
- Testing only the happy path; no loading, empty, or error-state coverage.
- Chasing a coverage percentage, writing tests that execute lines without asserting behavior.
- Tolerating flaky tests with retries instead of fixing the nondeterminism.

## Production Tips

- Run end-to-end tests against a production-like build, not the dev server, so bundling
  and hydration bugs surface.
- Gate merges on the suite; quarantine (don't ignore) a flaky test and fix it fast.
- Add visual regression tests for design-system components where pixel changes matter.
- Fail tests on unexpected `console.error`/`console.warn` to catch React warnings early.

## AI Review Checklist

- Do tests assert user-observable behavior rather than internal state or CSS classes?
- Are elements queried by role/label/text, with `getByTestId` only as a fallback?
- Is async UI awaited with `findBy*`/`waitFor` before assertions?
- Is the network mocked at the boundary (MSW) rather than by stubbing app functions?
- Are loading, empty, and error states covered, not just the happy path?
- Are tests deterministic and isolated, with no flaky-retry masking?

## Related

- `knowledge/frontend/02-component-driven-development.md`
- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/13-error-handling.md`
- `knowledge/frontend/19-build-tools.md`
