---
id: testing/99-ai-review-checklist
topic: testing
slug: ai-review-checklist
title: "Testing AI Review Checklist"
type: checklist
order: 99
status: ready
tags: [testing, ai-review-checklist, only, skip]
related: [testing/29-test-review, testing/02-unit-testing, testing/05-test-doubles, testing/09-assertions, testing/22-flaky-tests]
when_to_use: "Read before reviewing or generating test code, to check it item by item."
---
# Testing AI Review Checklist

## Purpose

This is the checklist an agent runs against test code — its own or a human's — before
calling it done. Each item is a yes/no an agent can verify by reading the diff. It is the
fast, pre-merge companion to [test review](29-test-review.md): if any answer is "no," the
test needs work before it is trustworthy. Use it on every change that adds or edits tests.

## Why It Matters

Generated tests fail in predictable ways: they assert nothing meaningful, mock the thing
under test, depend on the clock, or merely restate the implementation. Each of these passes
CI and review while providing zero protection, so the failure is invisible until a real
bug ships through a green build. A concrete checklist catches these patterns mechanically,
before they become false confidence baked into the suite.

## Does the Test Actually Test Something

**Rules:** [Assertions](09-assertions.md) · [Test Coverage](19-test-coverage.md)

- [ ] Every test contains at least one meaningful assertion — not just "it ran without throwing."
- [ ] You can name the exact production change that would make each test fail.
- [ ] The assertion checks the real output/behavior, not a value the test itself computed.
- [ ] The test is not asserting on a mock's return value that the test configured.

## Behavior, Not Implementation

**Rules:** [Unit Testing](02-unit-testing.md) · [Mocking](06-mocking.md)

- [ ] Assertions target observable behavior (return values, side effects a caller sees),
      not private fields, call counts, or internal method calls.
- [ ] The test would survive a refactor that preserves behavior. See
      [best practices](24-best-practices.md).
- [ ] Verification of interactions is limited to true boundaries (e.g., an email was sent),
      not internal collaboration. See [test doubles](05-test-doubles.md).

## Determinism

**Rules:** [Flaky Tests](22-flaky-tests.md) · [Test Data](07-test-data.md)

- [ ] No reliance on real time — clocks are injected or frozen.
- [ ] No reliance on network, filesystem, or external services without a controlled double.
- [ ] Randomness is seeded; unordered collections are compared order-insensitively.
- [ ] The test passes in isolation and when the suite runs in parallel or shuffled. See
      [flaky tests](22-flaky-tests.md).

## Structure and Clarity

**Rules:** [Test Organization](08-test-organization.md) · [Fixtures](10-fixtures.md)

- [ ] The test name states the scenario and expected outcome, readable as a spec line.
- [ ] It follows Arrange-Act-Assert with a single logical action.
- [ ] It checks one behavior; unrelated assertions are split into separate tests.
- [ ] Failure output is diagnostic — expected vs. actual is clear without a debugger. See
      [assertions](09-assertions.md).

## Correct Level and Scope

**Rules:** [Strategy](28-testing-strategy.md) · [Integration Testing](03-integration-testing.md)

- [ ] The test is at the cheapest level that gives real confidence (unit before integration
      before E2E). See the [pyramid](01-testing-fundamentals.md).
- [ ] Doubles are used deliberately and honor the real collaborator's contract, not by reflex.
- [ ] Error and edge cases are covered, not just the happy path.
- [ ] Setup uses factories/builders over brittle shared fixtures; no leaked state between tests.

## Red Flags to Reject

**Rules:** [Test Maintenance](20-test-maintenance.md) · [Test Doubles](05-test-doubles.md)

- [ ] No `sleep(n)` or fixed delays used to wait for async work — condition-based waits only.
- [ ] No assertion-free tests written solely to raise a coverage number.
- [ ] No test tightly mirroring the implementation line for line (change-detector tests).
- [ ] No commented-out assertions, no `skip`/`only` left in, no swallowed exceptions.

## Related

- `knowledge/testing/29-test-review.md`
- `knowledge/testing/02-unit-testing.md`
- `knowledge/testing/05-test-doubles.md`
- `knowledge/testing/09-assertions.md`
- `knowledge/testing/22-flaky-tests.md`
