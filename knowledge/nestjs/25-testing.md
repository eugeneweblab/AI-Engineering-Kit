# Testing

## Purpose

This document defines the engineering standards for testing NestJS applications.

The objective is to verify correctness, prevent regressions, enable safe refactoring, and provide confidence that the application behaves as expected in production.

Testing is part of software design.

It is not a phase performed after development.

---

# Core Principle

Test behavior.

Not implementation.

Tests should verify what the system does—not how it is implemented internally.

---

# Goals

A testing strategy should provide:

- confidence;
- fast feedback;
- maintainability;
- reproducibility;
- regression protection;
- production reliability.

A passing test suite should increase confidence—not simply improve coverage metrics.

---

# Testing Pyramid

Prefer the classic Testing Pyramid.

```
            E2E

      Integration

          Unit
```

Most tests should be unit tests.

Integration tests verify collaboration.

End-to-end tests validate complete business flows.

---

# Test Types

## Unit Tests

Test one unit in isolation.

Mock external dependencies.

Verify:

- business logic;
- validation;
- edge cases;
- failure scenarios.

Unit tests should execute quickly.

---

## Integration Tests

Verify collaboration between components.

Examples:

- Service + Repository;
- Repository + Database;
- Service + Cache;
- Queue + Worker.

Use real infrastructure whenever practical.

---

## End-to-End Tests

Validate complete user workflows.

Example:

```
HTTP Request

↓

Authentication

↓

Business Logic

↓

Database

↓

Response
```

E2E tests should resemble production behavior.

---

## Contract Tests

Verify compatibility between communicating systems.

Examples:

- REST APIs;
- gRPC;
- Event Contracts;
- Message Queues.

Contracts reduce integration failures.

---

## Performance Tests

Measure:

- response time;
- throughput;
- concurrency;
- resource consumption.

Performance should be validated—not assumed.

---

## Security Tests

Verify:

- authorization;
- authentication;
- input validation;
- privilege escalation;
- common attack vectors.

Security testing belongs in CI/CD.

---

# Test Doubles

Use the correct test double.

## Mock

Verifies interactions.

---

## Stub

Returns predefined values.

---

## Spy

Observes behavior while preserving implementation.

---

## Fake

Provides a lightweight working implementation.

Choose the simplest double that satisfies the test.

---

# Test Independence

Every test should:

- run independently;
- produce identical results;
- avoid shared mutable state.

Tests should execute in any order.

---

# Determinism

Avoid dependence on:

- system time;
- network availability;
- random values;
- execution order.

Deterministic tests build confidence.

---

# Test Data

Generate only the data required for each scenario.

Prefer builders or factories.

Avoid large fixture files.

---

# Database Testing

Prefer isolated databases.

Use:

- disposable databases;
- transactions with rollback;
- Testcontainers when practical.

Avoid shared development databases.

---

# External Dependencies

Mock external services unless integration is explicitly under test.

Examples:

- payment gateways;
- email providers;
- cloud storage;
- third-party APIs.

---

# Snapshot Testing

Use snapshots only for stable output.

Avoid snapshots for:

- business logic;
- dynamic values;
- complex objects.

Snapshots should remain readable.

---

# Property-Based Testing

Useful when validating:

- parsers;
- validators;
- algorithms;
- mathematical logic.

Test properties rather than individual examples.

---

# Mutation Testing

Measure test quality.

Mutation testing verifies whether tests detect intentional defects.

Coverage alone does not guarantee correctness.

---

# Code Coverage

Coverage is a metric.

Not a goal.

Prefer meaningful assertions over high percentages.

A lower-quality suite with 100% coverage is worse than a smaller suite with excellent behavioral verification.

---

# Flaky Tests

Flaky tests must be fixed immediately.

Typical causes:

- race conditions;
- timing assumptions;
- shared state;
- network dependency.

Never ignore flaky tests.

---

# Naming

Test names should describe behavior.

Good:

```
should_return_404_when_user_does_not_exist
```

Bad:

```
test1
```

Names should communicate intent.

---

# Arrange, Act, Assert

Prefer the AAA structure.

```
Arrange

↓

Act

↓

Assert
```

Keep these sections visually distinct.

---

# Error Scenarios

Every critical feature should test:

- valid input;
- invalid input;
- boundary conditions;
- exceptions;
- authorization failures;
- concurrency when applicable.

---

# Continuous Integration

Tests should execute automatically.

CI should block deployment when critical tests fail.

Testing should be part of every pull request.

---

# Performance

Test suites should remain fast.

Review:

- duplicate setup;
- unnecessary E2E tests;
- expensive fixtures.

Slow test suites discourage execution.

---

# AI Test Generation

AI should generate tests that:

- verify observable behavior;
- include edge cases;
- include failure scenarios;
- avoid implementation coupling;
- remain readable.

AI should never generate assertions solely to increase coverage.

---

# AI Decision Matrix

Use Unit Tests for:

✓ Business rules

✓ Validation

✓ Algorithms

✓ Domain logic

Use Integration Tests for:

✓ Database

✓ Cache

✓ Repository

✓ Queue

Use E2E Tests for:

✓ User workflows

✓ Authentication

✓ API behavior

✓ Cross-module interactions

---

# AI Execution Checklist

## Investigation

☐ Identify business behaviors.

☐ Identify edge cases.

☐ Identify failure scenarios.

☐ Review external dependencies.

---

## Planning

☐ Select appropriate test type.

☐ Keep tests independent.

☐ Mock external systems.

☐ Verify observable behavior.

---

## Verification

☐ Tests deterministic.

☐ No shared mutable state.

☐ Edge cases covered.

☐ Failure paths tested.

☐ Test names descriptive.

☐ CI compatible.

---

# Common Mistakes

Avoid:

Testing implementation details.

Mocking everything.

Ignoring integration tests.

Using production databases.

Overusing snapshots.

Writing assertions only for coverage.

Keeping flaky tests.

Sharing state between tests.

---

# Completion Criteria

A testing strategy is complete when:

- business behavior is verified;
- test types are appropriately balanced;
- tests are deterministic;
- external dependencies are isolated where appropriate;
- CI executes the test suite automatically;
- developers can refactor with confidence.

---

# Summary

Testing provides confidence that software behaves correctly under expected and unexpected conditions.

By emphasizing behavioral verification, maintaining a balanced testing strategy, writing deterministic and independent tests, and treating testing as an integral part of software design, engineering teams can deliver reliable, maintainable, and production-ready NestJS applications.