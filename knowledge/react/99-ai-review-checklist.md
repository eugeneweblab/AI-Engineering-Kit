---
id: react/99-ai-review-checklist
topic: react
slug: ai-review-checklist
title: "React Definition of Done"
type: checklist
order: 99
status: ready
tags: [react, ai-review-checklist, useEffect, done, confirm, ai-generated]
related: [react/98-production-checklist, react/100-common-antipatterns, react/26-best-practices]
when_to_use: "Read before reviewing a React pull request or AI-generated React, or to confirm an implementation is done."
---
# React Definition of Done

## Purpose

This document defines the minimum quality requirements that every React implementation must satisfy before it can be considered complete.

The Definition of Done (DoD) ensures consistent engineering quality across the project and provides a standardized checklist for developers, reviewers, and AI coding assistants.

Completing a task means more than making it work—it means delivering production-ready code.

---

## Core Principle

Working code is not necessarily finished code.

A feature is complete only when it satisfies functional, architectural, performance, accessibility, testing, and maintainability requirements.

---

## Functional Requirements

Verify that:

☐ The implementation satisfies all acceptance criteria.

☐ All expected user scenarios work correctly.

☐ Edge cases have been considered.

☐ Invalid input is handled gracefully.

☐ No known regressions have been introduced.

---

## Architecture

**Rules:** [Component Architecture](02-component-architecture.md) · [Component Composition](13-component-composition.md)

Verify that:

☐ Component responsibilities are clearly separated.

☐ Business logic is isolated from presentation.

☐ Custom Hooks are used appropriately.

☐ API communication is separated from UI.

☐ Shared logic has not been duplicated.

☐ State ownership is well defined.

---

## React Best Practices

**Rules:** [Best Practices](26-best-practices.md) · [Hooks](08-hooks.md)

Verify that:

☐ Components have a single responsibility.

☐ Props are minimal and clearly named.

☐ Derived values are not stored in state.

☐ Rendering remains pure.

☐ Hooks follow the Rules of Hooks.

☐ Effects synchronize with external systems only.

☐ Stable keys are used for lists.

☐ Component APIs remain consistent.

---

## TypeScript

Verify that:

☐ No unnecessary use of `any`.

☐ Types are explicit.

☐ Public APIs are well typed.

☐ Shared types are reused.

☐ Type definitions remain readable.

---

## Performance

**Rules:** [Performance](12-performance.md) · [Rendering Patterns](11-rendering.md)

Verify that:

☐ No unnecessary rendering.

☐ Memoization is justified.

☐ Expensive calculations are optimized when necessary.

☐ Bundle growth has been considered.

☐ Large collections use appropriate rendering strategies.

---

## Accessibility

**Rules:** [Accessibility](20-accessibility.md)

Verify that:

☐ Semantic HTML is used.

☐ Keyboard navigation works.

☐ Focus management is correct.

☐ Forms are accessible.

☐ Images provide appropriate alternative text.

☐ Error messages are accessible.

☐ Color is not the only source of information.

---

## Error Handling

**Rules:** [Error Handling](19-error-handling.md)

Verify that:

☐ Expected errors are handled.

☐ Loading states exist.

☐ Error states exist.

☐ Retry mechanisms are available where appropriate.

☐ Unexpected failures are logged.

---

## Testing

**Rules:** [Testing](21-testing.md)

Verify that:

☐ Critical user behavior is tested.

☐ Business logic is tested.

☐ Error scenarios are covered.

☐ Accessibility has been verified.

☐ Existing tests pass.

---

## Code Quality

**Rules:** [Code Style](23-code-style.md) · [Folder Structure](22-folder-structure.md)

Verify that:

☐ Naming is consistent.

☐ Files remain appropriately sized.

☐ Dead code has been removed.

☐ Comments explain intent rather than implementation.

☐ Magic values have been eliminated.

☐ Code formatting is consistent.

---

## Documentation

Verify that:

☐ Public APIs are documented.

☐ Complex decisions are explained.

☐ README updates have been made when necessary.

☐ Breaking changes have been documented.

---

## Security

**Rules:** [Security](25-security.md)

Verify that:

☐ User input is validated.

☐ Sensitive information is protected.

☐ Authorization rules are respected.

☐ Client-side validation is not trusted.

☐ External input is handled safely.

---

## Review Readiness

Before requesting review, verify that:

☐ The implementation is understandable without verbal explanation.

☐ The solution follows project conventions.

☐ Unnecessary complexity has been removed.

☐ The implementation is production-ready.

---

## AI Execution Checklist

## Investigation

☐ Requirements reviewed.

☐ Existing architecture understood.

☐ Dependencies identified.

☐ Potential risks evaluated.

---

## Planning

☐ Define implementation strategy.

☐ Identify reusable code.

☐ Plan testing.

☐ Plan accessibility.

---

## Verification

☐ All Definition of Done items satisfied.

☐ No React anti-patterns introduced.

☐ Code remains maintainable.

☐ Solution is scalable.

☐ Documentation updated.

---

## Common Reasons for Rejection

Implementations should not be considered complete when:

- business logic is mixed with UI;
- duplicated state exists;
- unnecessary `useEffect` or memoization has been introduced;
- accessibility has been ignored;
- loading or error states are missing;
- testing has been skipped;
- public APIs are inconsistent;
- the solution introduces avoidable technical debt.

---

## Completion Criteria

A React task is considered complete only when:

- functional requirements are satisfied;
- engineering standards are followed;
- testing has been completed;
- accessibility has been verified;
- documentation is updated when required;
- the implementation is ready for production deployment without additional engineering work.

---

## Summary

The Definition of Done is the final quality gate for every React task.

Following this checklist ensures that completed work is not only functional, but also maintainable, scalable, accessible, testable, and aligned with the engineering standards of the project.

## Related

- `knowledge/react/98-production-checklist.md`
- `knowledge/react/100-common-antipatterns.md`
- `knowledge/react/26-best-practices.md`
