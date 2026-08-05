---
id: testing/100-common-antipatterns
topic: testing
slug: common-antipatterns
title: "Testing Common Antipatterns"
type: antipatterns
order: 100
status: ready
tags: [testing, common-antipatterns]
related: [testing/22-flaky-tests, testing/05-test-doubles, testing/06-mocking, testing/19-test-coverage, testing/24-best-practices]
when_to_use: "Read when writing or reviewing tests to recognize and avoid the failure patterns below."
---
# Testing Common Antipatterns

## Purpose

This document catalogs the test patterns that look productive but actively harm a suite.
Each entry names the anti-pattern, explains *why it is wrong*, and gives *the fix*. An
agent should recognize these on sight and refuse to generate them, because every one of
them passes review and CI while providing little or no protection.

## Why It Matters

The danger of a bad test is not that it fails — a failing test gets fixed. The danger is
that it passes, forever, while catching nothing. These anti-patterns produce green builds
that lie: they inflate coverage, mirror the implementation, or depend on timing luck. The
team ships on that false signal until a real defect slips through. Eliminating these
patterns is what separates a suite that protects the system from one that merely decorates it.

## Anti-Patterns

### 1. The Assertion-Free Test

**Why it is wrong.** A test that calls the code but asserts nothing — or only that it did
not throw — passes no matter what the code returns. It inflates coverage while catching
zero defects, and it teaches reviewers that "covered" means "verified."

**The fix.** Every test asserts a specific expected outcome. If there is genuinely nothing
to assert, there is nothing to test — delete it. See [test coverage](19-test-coverage.md).

### 2. Testing the Mock

**Why it is wrong.** The test configures a mock to return `X`, calls code that returns the
mock's value, and asserts it got `X`. It verifies the test's own setup, not the production
code, so it stays green even if the real logic is deleted.

**The fix.** Mock only at true boundaries and assert on the code's own behavior. Prefer
real objects or fakes over mocks. See [test doubles](05-test-doubles.md) and
[mocking](06-mocking.md).

### 3. The Change-Detector Test

**Why it is wrong.** The test mirrors the implementation line for line — asserting private
fields, call order, and internal method calls. Any refactor breaks it even when behavior is
unchanged, so it punishes improvement and trains the team to ignore red.

**The fix.** Assert observable behavior a caller or user can see. A test should survive any
refactor that preserves behavior. See [best practices](24-best-practices.md).

### 4. Sleeping to Fix Flakiness

**Why it is wrong.** `sleep(2)` to wait for async work is both slow and unreliable: it is
too long on fast machines and too short on slow ones, so the test flakes under load and
wastes time otherwise.

**The fix.** Wait on a condition (poll until state is reached) with an explicit timeout, or
use the framework's async assertions. Control time with an injected clock. See
[flaky tests](22-flaky-tests.md).

### 5. Coverage-Driven Testing

**Why it is wrong.** Writing tests to hit a coverage percentage optimizes the wrong metric.
It produces tests that execute lines without asserting meaning, and it skips high-value edge
cases in already-"covered" code.

**The fix.** Target confidence, not a number. Cover critical paths and error cases
deliberately; treat coverage as a floor that finds untested code, never as the goal.

### 6. The Ice-Cream Cone (Inverted Pyramid)

**Why it is wrong.** A suite dominated by slow, brittle E2E tests with few unit tests is
slow to run, flaky, and hard to diagnose — a failure could be anywhere. Feedback arrives
minutes late instead of seconds.

**The fix.** Push confidence down to the cheapest level that provides it: many unit tests,
fewer integration, fewest E2E. See the [testing pyramid](01-testing-fundamentals.md).

### 7. Shared Mutable Fixtures

**Why it is wrong.** Tests that share and mutate the same fixture or database rows become
order-dependent and interfere with each other, causing failures that vanish when a test is
run alone and reappear in CI.

**The fix.** Each test builds its own data with factories/builders and cleans up after
itself. No global mutable state. See [test data](07-test-data.md).

### 8. The Slow Test in the Inner Loop

**Why it is wrong.** A "unit" test that hits the real network, database, or filesystem is
slow and non-deterministic. Enough of them and developers stop running tests locally, so
defects reach CI or later.

**The fix.** Keep unit tests in-memory and fast; move real-boundary tests to a clearly
labeled integration suite that runs separately. See [integration testing](03-integration-testing.md).

### 9. Overly-Specified Assertions

**Why it is wrong.** Asserting on an entire serialized object or exact log string couples
the test to incidental details (field order, formatting), so unrelated changes break it and
its intent is buried.

**The fix.** Assert on the specific fields the behavior guarantees. Match the minimum that
proves the contract. See [assertions](09-assertions.md).

### 10. Conditional Logic in Tests

**Why it is wrong.** `if`/`for`/`try` branches inside a test mean some assertions may never
run, and the test can silently pass by skipping its checks. The test now needs its own tests.

**The fix.** Keep tests linear and straight-line. Use parameterized/table-driven tests for
multiple cases instead of loops and branches.

### 11. Retry-Until-Green

**Why it is wrong.** Wrapping a flaky test in automatic retries hides a real defect —
usually a race condition or shared state — and the underlying bug can hit users in production
where there is no retry.

**The fix.** Treat every flake as a bug to root-cause and fix. Quarantine it out of the
blocking suite while you fix it, not behind a permanent retry. See [flaky tests](22-flaky-tests.md).

## AI Review Checklist

- Does every test assert something a failure in production code would break?
- Do assertions target observable behavior, not internals or a mock's own return value?
- Is the suite free of `sleep`-based waits, retries-until-green, and order dependence?
- Is the pyramid upright — fast unit tests dominate, E2E is minimal?
- Are tests linear (no branching) and asserting the minimum that proves the contract?

## Related

- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/05-test-doubles.md`
- `knowledge/testing/06-mocking.md`
- `knowledge/testing/19-test-coverage.md`
- `knowledge/testing/24-best-practices.md`
