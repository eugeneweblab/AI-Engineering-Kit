---
id: nextjs/22-testing
topic: nextjs
slug: testing
title: "Next.js Testing"
type: doc
order: 22
status: ready
tags: [nextjs, testing]
related: []
when_to_use: "Read before setting up or writing automated tests for a Next.js app."
---
# Next.js Testing

## Purpose

This document defines the engineering standards for testing Next.js applications.

The objective is to build reliable, maintainable, and production-ready applications through automated testing at multiple levels.

Testing should verify application behavior rather than implementation details.

---

## Core Principle

Test behavior.

Not implementation.

Tests should give confidence that the application works correctly from a user's perspective.

---

## Testing Goals

Every project should strive for:

- reliable releases;
- regression prevention;
- maintainable test suites;
- fast feedback;
- deterministic results;
- high developer confidence.

Testing is a quality assurance tool, not a coverage competition.

---

## Testing Pyramid

Prefer the following balance.

```
                E2E

          Integration

        Component Tests

          Unit Tests
```

Use each level for the problems it solves best.

---

## Test Types

A production application may contain:

- unit tests;
- component tests;
- integration tests;
- end-to-end tests;
- accessibility tests;
- visual regression tests;
- performance tests.

Not every project requires every test type.

---

## Unit Tests

Unit tests verify isolated logic.

Typical candidates include:

- utility functions;
- validation;
- formatting;
- business rules;
- custom hooks.

Unit tests should execute quickly and independently.

---

## Component Tests

Component tests verify UI behavior.

Review:

- rendering;
- user interactions;
- state changes;
- conditional rendering;
- accessibility.

Test components through their public interface.

---

## Integration Tests

Integration tests verify collaboration between multiple modules.

Examples:

- forms;
- authentication flow;
- database interaction;
- API communication;
- feature workflows.

Integration tests should reflect realistic application behavior.

---

## End-to-End Tests

End-to-end tests verify complete user journeys.

Typical scenarios:

- login;
- registration;
- checkout;
- search;
- profile updates.

Test the application as users experience it.

---

## Server Components

Server Components should be tested by verifying:

- rendered output;
- data loading;
- error handling;
- authorization behavior.

Avoid testing framework internals.

---

## Client Components

Review:

- interactions;
- local state;
- events;
- accessibility;
- loading states.

Focus on observable behavior.

---

## Server Actions

Verify:

- validation;
- authorization;
- database mutations;
- error handling;
- cache invalidation.

Server Actions should remain independently testable.

---

## API Routes

Every API endpoint should verify:

- request validation;
- authentication;
- authorization;
- response structure;
- HTTP status codes;
- error handling.

API tests should remain deterministic.

---

## Mocking

Mock only external dependencies.

Examples:

- payment providers;
- email services;
- cloud storage;
- external APIs.

Avoid mocking application logic unnecessarily.

---

## Test Data

Use predictable test data.

Test data should be:

- isolated;
- repeatable;
- easy to understand.

Avoid shared mutable test state.

---

## Accessibility Testing

Verify:

- keyboard navigation;
- semantic HTML;
- form labels;
- focus management;
- ARIA usage.

Accessibility should be tested continuously.

---

## Performance Testing

Review:

- rendering speed;
- page load time;
- API latency;
- Core Web Vitals.

Performance regressions should be identified before release.

---

## Test Organization

Organize tests consistently.

Example:

```
src/

    features/

        products/

            ProductCard.tsx

            ProductCard.test.tsx

            ProductCard.integration.test.tsx
```

Keep tests close to the code they verify whenever practical.

---

## Continuous Integration

Run automated tests during CI.

Recommended sequence:

```
Lint

↓

Type Check

↓

Unit Tests

↓

Integration Tests

↓

Build

↓

E2E Tests

↓

Deploy
```

Deployment should depend on successful verification.

---

## Error Handling

Tests should verify:

- expected failures;
- invalid input;
- authorization denial;
- unavailable services.

Failure scenarios are as important as successful ones.

---

## Security

Verify:

- authentication;
- authorization;
- protected routes;
- input validation.

Security-sensitive behavior should always be tested.

---

## AI Execution Checklist

## Investigation

☐ Identify feature behavior.

☐ Identify critical workflows.

☐ Review edge cases.

☐ Review security requirements.

---

## Planning

☐ Select appropriate test type.

☐ Isolate external dependencies.

☐ Use deterministic data.

☐ Verify expected behavior.

---

## Verification

☐ Critical paths covered.

☐ Error cases tested.

☐ Accessibility verified.

☐ Security verified.

☐ Tests deterministic.

☐ CI integration complete.

---

## Common Mistakes

Avoid:

Testing implementation details.

Writing brittle tests.

Mocking everything.

Ignoring failure scenarios.

Sharing mutable test data.

Relying on test execution order.

Skipping accessibility tests.

Treating code coverage as the primary objective.

---

## Completion Criteria

A testing strategy is complete when:

- critical workflows are covered;
- behavior is verified at the appropriate testing level;
- failure scenarios are tested;
- security and accessibility are validated;
- tests run reliably in CI;
- developers can refactor with confidence.

---

## Summary

Testing is an essential part of building reliable Next.js applications.

By focusing on observable behavior, selecting the appropriate testing strategy, automating verification, and continuously validating accessibility, security, and critical user workflows, teams can deliver production-ready applications with greater confidence.