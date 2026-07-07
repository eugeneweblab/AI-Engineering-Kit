---
id: react/21-testing
topic: react
slug: testing
title: "React Testing"
type: doc
order: 21
status: ready
tags: [react, testing]
related: []
when_to_use: ""
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

---

## Async Testing

Wait for observable behavior.

Avoid arbitrary delays.

Prefer waiting for:

- rendered content;
- loading completion;
- state changes;
- user-visible results.

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