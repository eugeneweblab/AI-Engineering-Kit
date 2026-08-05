---
id: react/21-testing
topic: react
slug: testing
title: "React Testing"
type: doc
order: 21
status: ready
tags: [react, testing]
related: ["react/09-custom-hooks", "react/15-forms", "react/16-data-fetching", "react/20-accessibility"]
when_to_use: "Read before writing or reviewing tests for React components and hooks."
---
# React Testing

## Purpose

This document defines the engineering standards for testing React applications.

The objective is to build applications that are reliable, maintainable, and safe to refactor by establishing consistent testing practices across the project.

Testing should increase confidence in the software rather than simply increase code coverage.

---

## Core Principle

Test behavior.

Not implementation.

A good test verifies what the user observes, not how the component is internally implemented.

Bad (couples the test to internal state and structure):

```tsx
// ❌ Asserts on implementation, not behavior.
const { container } = render(<Counter />);
// Reaches into DOM structure and internal class names.
fireEvent.click(container.querySelector(".increment-btn"));
expect(container.querySelector(".count").textContent).toBe("1");
```

Good (asserts on what the user sees and does):

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

test("increments the visible count", async () => {
    const user = userEvent.setup();
    render(<Counter />);

    await user.click(screen.getByRole("button", { name: /increment/i }));

    expect(screen.getByText("Count: 1")).toBeInTheDocument();
});
```

The Good test survives a refactor from `useState` to `useReducer`, a class-name
change, or a re-structured DOM. The Bad test breaks on all three even though the
user-facing behavior never changed.

---

## Testing Strategy

Every feature should follow the testing pyramid.

```
                E2E

         Integration Tests

          Component Tests

             Unit Tests
```

The majority of tests should exist at the unit and integration levels.

---

## What Should Be Tested

Prioritize testing:

- user interactions;
- business rules;
- conditional rendering;
- state changes;
- error handling;
- form validation;
- accessibility;
- API integration.

Avoid testing implementation details.

---

## Unit Testing

Unit tests verify isolated logic.

Examples:

- utility functions;
- formatters;
- validators;
- custom hooks;
- reducers.

Unit tests should execute quickly and deterministically.

---

## Component Testing

Component tests verify UI behavior.

Examples:

- rendering;
- props;
- callbacks;
- conditional states;
- accessibility;
- loading states;
- error states.

Render components as users would interact with them.

A component test renders a single component in isolation, drives it through
`userEvent`, and asserts on accessible output. Always call `userEvent.setup()`
once per test and `await` every interaction — `userEvent` is asynchronous and
advances React state and effects between events.

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PasswordField } from "./PasswordField";

test("toggles password visibility", async () => {
    const user = userEvent.setup();
    render(<PasswordField label="Password" />);

    const input = screen.getByLabelText(/password/i);
    expect(input).toHaveAttribute("type", "password");

    await user.click(screen.getByRole("button", { name: /show password/i }));

    expect(input).toHaveAttribute("type", "text");
});
```

Verify callback props with a spy, and assert on the arguments the parent
actually receives — not on internal handler names.

```tsx
test("calls onSubmit with the entered value", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn(); // jest.fn() under Jest.
    render(<SearchBox onSubmit={onSubmit} />);

    await user.type(screen.getByRole("searchbox"), "react");
    await user.click(screen.getByRole("button", { name: /search/i }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit).toHaveBeenCalledWith("react");
});
```

---

## Integration Testing

Integration tests verify multiple parts working together.

Examples:

- forms with validation;
- API requests;
- authentication flows;
- routing;
- state management;
- complex user interactions.

Integration tests provide the highest confidence for most frontend features.

Mock the network at the boundary with MSW, not the components in between. This
exercises real data fetching, loading, and error paths while keeping the test
deterministic. MSW 2.x uses the `http` + `HttpResponse` API.

```tsx
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { render, screen } from "@testing-library/react";
import { UserList } from "./UserList";

const server = setupServer(
    http.get("/api/users", () =>
        HttpResponse.json([{ id: 1, name: "Ada Lovelace" }])
    )
);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test("renders users fetched from the API", async () => {
    render(<UserList />);

    // Loading state is observable first.
    expect(screen.getByRole("status")).toHaveTextContent(/loading/i);

    // findBy* retries until the async result appears.
    expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
});

test("shows an error message when the request fails", async () => {
    // Override the handler for this test only.
    server.use(
        http.get("/api/users", () => new HttpResponse(null, { status: 500 }))
    );
    render(<UserList />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/couldn.t load/i);
});
```

`onUnhandledRequest: "error"` fails the test if the component hits an endpoint
you forgot to mock — a cheap safeguard against silent, flaky network calls.

---

## End-to-End Testing

End-to-end tests verify complete user journeys.

Examples:

- login;
- checkout;
- registration;
- payment;
- account management.

Keep E2E tests focused on critical business workflows.

---

## Recommended Tools

Preferred tools:

## Test Runner

- Vitest
- Jest

## Component Testing

- React Testing Library

## API Mocking

- MSW (Mock Service Worker)

## End-to-End

- Playwright
- Cypress

Choose the smallest toolset that satisfies project requirements.

The examples in this document assume a standard setup: `@testing-library/react`
for rendering, `@testing-library/user-event` for interaction, and
`@testing-library/jest-dom` for DOM matchers (`toBeInTheDocument`,
`toHaveFocus`, `toBeDisabled`). Register the matchers once in a shared setup
file so every test inherits them.

```ts
// vitest.setup.ts — referenced from vitest config `setupFiles`.
import "@testing-library/jest-dom/vitest";
```

Under Jest, import `"@testing-library/jest-dom"` from `setupFilesAfterEnv` and
replace `vi.fn()` with `jest.fn()` in the examples below. Everything else is
identical.

---

## React Testing Library Principles

Prefer queries that reflect user behavior.

Recommended order:

1. `getByRole`
2. `getByLabelText`
3. `getByPlaceholderText`
4. `getByText`
5. `getByDisplayValue`
6. `getByTestId` (last resort)

Tests should resemble real user interactions.

Choose the query variant by intent:

- `getBy*` — element must already be present; throws if missing.
- `queryBy*` — asserting absence; returns `null` instead of throwing.
- `findBy*` — element appears asynchronously; returns a promise and retries.

Bad (querying by test id and asserting on absence with `getBy`):

```tsx
// ❌ getByTestId ignores the accessible role/name a user relies on.
expect(screen.getByTestId("submit")).toBeDisabled();
// ❌ getBy throws before you can assert absence — the test errors, not fails.
expect(screen.getByText("Error")).not.toBeInTheDocument();
```

Good (role/name queries; `queryBy` for absence):

```tsx
expect(screen.getByRole("button", { name: /submit/i })).toBeDisabled();
expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
```

Reach for `getByRole` first: it forces the markup to expose an accessible role
and name, so a passing query is also a small accessibility assertion.

---

## Mocking

Mock only external dependencies.

Examples:

- API requests;
- browser APIs;
- timers;
- third-party services.

Avoid mocking the component under test.

Over-mocking reduces test value.

---

## Custom Hooks

Test hooks independently.

Verify:

- returned values;
- state changes;
- loading states;
- error handling;
- side effects.

Hooks should remain testable without rendering the entire application.

Use `renderHook` from React Testing Library (no separate package since RTL
13.1). Wrap any state update that happens outside a React event — a direct call
to a returned function — in `act`.

```tsx
import { renderHook, act } from "@testing-library/react";
import { useCounter } from "./useCounter";

test("increments and resets", () => {
    const { result } = renderHook(() => useCounter({ initial: 5 }));

    expect(result.current.count).toBe(5);

    act(() => result.current.increment());
    expect(result.current.count).toBe(6);

    act(() => result.current.reset());
    expect(result.current.count).toBe(5);
});
```

For hooks that need context or a client, pass a `wrapper`:

```tsx
const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={new QueryClient()}>
        {children}
    </QueryClientProvider>
);

const { result } = renderHook(() => useUsers(), { wrapper });

// Wait for async state to settle.
await waitFor(() => expect(result.current.isSuccess).toBe(true));
```

Prefer testing a hook through a small component when its value only surfaces via
rendered output. Reserve `renderHook` for reusable, logic-heavy hooks.

---

## Forms

Verify:

- validation;
- submission;
- error messages;
- success states;
- disabled buttons;
- keyboard interaction.

Test realistic user behavior.

Drive the form the way a user would — fill fields by label, submit by clicking
the button — and assert on validation output and the payload sent to the server.
This applies equally to React 19 forms built on Actions and `useActionState`,
which run an async action on submit and expose `isPending` for the disabled/busy
state.

```tsx
// SignupForm uses: const [state, formAction, isPending] =
//   useActionState(signupAction, { error: null });
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../test/server";
import { SignupForm } from "./SignupForm";

test("shows a validation error for an invalid email", async () => {
    const user = userEvent.setup();
    render(<SignupForm />);

    await user.type(screen.getByLabelText(/email/i), "not-an-email");
    await user.click(screen.getByRole("button", { name: /sign up/i }));

    // The action returns an error that renders in an alert region.
    expect(await screen.findByRole("alert")).toHaveTextContent(/valid email/i);
});

test("disables the button while the action is pending", async () => {
    const user = userEvent.setup();
    server.use(
        http.post("/api/signup", () => HttpResponse.json({ ok: true }))
    );
    render(<SignupForm />);

    await user.type(screen.getByLabelText(/email/i), "ada@example.com");
    const submit = screen.getByRole("button", { name: /sign up/i });
    await user.click(submit);

    // isPending flips the button to a disabled/busy state during the action.
    await waitFor(() => expect(submit).toBeDisabled());
    expect(await screen.findByText(/welcome/i)).toBeInTheDocument();
});
```

Test the form and its action together. Do not mock `useActionState` or the
action itself — mock only the network at the MSW boundary, so the real
validation and pending logic are exercised.

---

## Async Testing

Wait for observable behavior.

Avoid arbitrary delays.

Prefer waiting for:

- rendered content;
- loading completion;
- state changes;
- user-visible results.

Bad (arbitrary sleeps and manual `act` around async work):

```tsx
// ❌ Fixed delay: flaky on slow CI, wasteful on fast machines.
render(<UserList />);
await new Promise((r) => setTimeout(r, 1000));
expect(screen.getByText("Ada Lovelace")).toBeInTheDocument();
```

Good (retry until the observable result appears):

```tsx
render(<UserList />);
// findBy* polls the DOM and resolves as soon as the node exists.
expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
```

Use `waitFor` when the thing you are waiting on is an assertion rather than an
element — for example, that a spinner has disappeared:

```tsx
await waitFor(() =>
    expect(screen.queryByRole("status")).not.toBeInTheDocument()
);
```

Keep a single expectation inside `waitFor`. Multiple assertions there can retry
after the first already passed and mask the real failure.

React 19 components that read a promise with `use()` suspend, so render them
under a `Suspense` boundary and wait for the resolved content:

```tsx
import { Suspense } from "react";

test("renders data resolved through use()", async () => {
    const userPromise = Promise.resolve({ name: "Ada Lovelace" });
    render(
        <Suspense fallback={<p>Loading…</p>}>
            <Profile userPromise={userPromise} />
        </Suspense>
    );

    expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
});
```

---

## Accessibility Testing

Verify:

- semantic roles;
- accessible names;
- keyboard navigation;
- focus management;
- form labels;
- error announcements.

Accessibility should be part of every testing strategy.

Role and label queries already assert accessibility as a side effect: if
`getByRole("button", { name: /save/i })` passes, the control has the right role
and an accessible name. Add `jest-axe` for automated rule coverage on rendered
output.

```tsx
import { render } from "@testing-library/react";
import { axe } from "jest-axe";

test("has no detectable accessibility violations", async () => {
    const { container } = render(<SignupForm />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
});
```

Assert focus management directly through `document.activeElement` or the
`toHaveFocus` matcher — for example, that focus moves to the first invalid field
after a failed submit:

```tsx
await user.click(screen.getByRole("button", { name: /sign up/i }));
expect(screen.getByLabelText(/email/i)).toHaveFocus();
```

Automated checks catch structural issues; they do not replace verifying
keyboard flows and screen-reader announcements as described above.

---

## Test Quality

Every test should be:

- deterministic;
- isolated;
- readable;
- maintainable;
- independent.

A failing test should clearly identify the problem.

---

## Code Coverage

Coverage is an indicator.

It is not the goal.

High coverage with poor assertions provides little value.

Prioritize meaningful scenarios over percentage targets.

---

## AI Execution Checklist

## Investigation

☐ Identify critical behaviors.

☐ Identify business rules.

☐ Review user interactions.

☐ Review edge cases.

---

## Planning

☐ Select appropriate test type.

☐ Mock external dependencies.

☐ Plan accessibility verification.

☐ Plan error scenarios.

---

## Verification

☐ Tests verify behavior.

☐ Tests remain independent.

☐ Accessibility verified.

☐ Async behavior verified.

☐ Error scenarios covered.

☐ Tests remain readable.

---

## Common Mistakes

Avoid:

Testing implementation details.

Overusing mocks.

Testing private component state.

Using `getByTestId` unnecessarily.

Ignoring accessibility.

Ignoring error scenarios.

Writing brittle tests tied to DOM structure.

Optimizing only for code coverage.

---

## Completion Criteria

Testing is complete when:

- critical user behaviors are verified;
- business logic is covered;
- accessibility has been validated;
- asynchronous behavior has been tested;
- error scenarios have been verified;
- tests are readable, deterministic, and maintainable.

---

## Summary

Effective React testing focuses on user behavior, business outcomes, and confidence during refactoring.

By combining unit, component, integration, and end-to-end testing with accessible testing practices, applications become more reliable and significantly easier to maintain over time.