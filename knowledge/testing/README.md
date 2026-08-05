---
id: testing/readme
topic: testing
slug: readme
title: "Testing Engineering Standards"
type: index
order: -1
status: ready
tags: [testing, readme]
related: []
when_to_use: "Read first when starting testing work, to see how this section's docs fit together and which level of test fits the problem."
---
# Testing Engineering Standards

## Purpose

This section defines the engineering standards for testing: which level of test answers which
question, how to write tests that survive refactoring, and how to keep a suite fast and
trustworthy enough that people actually run it.

The failure mode this section exists to prevent is not the absence of tests. It is a suite
that takes twenty minutes, fails intermittently, and breaks whenever an implementation detail
changes — because that suite gets ignored, and an ignored suite is worse than none: it costs
maintenance and provides no confidence.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Fundamentals and test strategy
- Levels: unit, integration, end-to-end, contract
- Test doubles, mocking, fixtures, and test data
- Specialized testing: API, UI, visual, performance, load, security, accessibility
- Coverage, flakiness, and maintenance
- CI/CD integration and quality gates
- Production testing and observability
- Review practice and antipatterns

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. [Overview](00-overview.md)
- 01. [Testing Fundamentals](01-testing-fundamentals.md)
- 28. [Testing Strategy](28-testing-strategy.md)
- 30. [Engineering Principles](30-engineering-principles.md)

## Levels of Testing

- 02. [Unit Testing](02-unit-testing.md)
- 03. [Integration Testing](03-integration-testing.md)
- 04. [E2E Testing](04-e2e-testing.md)
- 11. [Contract Testing](11-contract-testing.md)

## Writing Good Tests

- 05. [Test Doubles](05-test-doubles.md)
- 06. [Mocking](06-mocking.md)
- 07. [Test Data](07-test-data.md)
- 08. [Test Organization](08-test-organization.md)
- 09. [Assertions](09-assertions.md)
- 10. [Fixtures](10-fixtures.md)

## Specialized Testing

- 12. [API Testing](12-api-testing.md)
- 13. [UI Testing](13-ui-testing.md)
- 14. [Visual Regression](14-visual-regression.md)
- 15. [Performance Testing](15-performance-testing.md)
- 16. [Load Testing](16-load-testing.md)
- 17. [Security Testing](17-security-testing.md)
- 18. [Accessibility Testing](18-accessibility-testing.md)

## Keeping the Suite Healthy

- 19. [Test Coverage](19-test-coverage.md)
- 20. [Test Maintenance](20-test-maintenance.md)
- 22. [Flaky Tests](22-flaky-tests.md)
- 23. [Debugging Tests](23-debugging-tests.md)

## Running Tests in Practice

- 21. [CI/CD](21-cicd.md)
- 27. [Quality Gates](27-quality-gates.md)
- 25. [Production Testing](25-production-testing.md)
- 26. [Observability](26-observability.md)

## Applied Guidance

- 24. [Best Practices](24-best-practices.md)
- 29. [Test Review](29-test-review.md)

## Verification

- 98. [Production Checklist](98-production-checklist.md)
- 99. [AI Review Checklist](99-ai-review-checklist.md)
- 100. [Common Antipatterns](100-common-antipatterns.md)

---

## Engineering Principles

Every test should satisfy the following principles:

- Test behavior through the public interface, not implementation details — otherwise every
  refactor breaks the suite.
- Pick the cheapest level that can answer the question; reach for E2E only for flows that
  cross real boundaries.
- A test must fail for exactly one reason, and its name should state that reason.
- Determinism is non-negotiable: no real clocks, no network, no shared mutable state, no
  order dependence.
- Mock what you own and what is slow; do not mock what you are trying to verify.
- A regression test that does not fail on the old code proves nothing.
- Coverage is a diagnostic, not a target — 100% coverage of trivial code says nothing about
  the untested edge case.
- Test data should be explicit at the point of use; a fixture nobody can read is a test
  nobody can trust.
- A flaky test is a defect. Fix it or delete it, but never retry it into passing.
- Fast feedback beats exhaustive coverage: a suite people wait for is a suite people skip.

---

## Intended Audience

These standards are intended for:

- Backend and Frontend Engineers
- QA and Test Engineers
- DevOps and Platform Engineers
- Tech Leads
- AI Coding Assistants
- Code Reviewers

---

## Summary

A good suite is fast, deterministic, and coupled to behavior rather than implementation. Pick
the cheapest level that answers the question, make every failure mean one thing, and treat
flakiness as a defect rather than a nuisance.
