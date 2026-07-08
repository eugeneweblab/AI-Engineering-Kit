---
id: php/15-testing
topic: php
slug: testing
title: "Testing"
type: doc
order: 15
status: ready
tags: [php, testing]
related: [php/09-exceptions, php/20-dependency-injection, php/14-performance, php/28-tooling]
when_to_use: "Read before writing or reviewing PHPUnit/Pest tests, or when deciding what and how to test in PHP."
---
# Testing

## Purpose

This document defines how to write PHP tests that catch real regressions and stay
maintainable: how to structure a test, what to assert, when to use a test double, and
how to make code testable in the first place. It targets **PHPUnit** (the de facto
standard) with notes on **Pest**, and assumes tests run in CI on every change.

## Why It Matters

Tests are the only automated proof that code still does what it claimed after the next
change. In a dynamically typed language, they carry extra weight: many mistakes that a
compiler would catch elsewhere only surface at runtime in PHP, so a fast test suite is
the primary safety net. But a bad suite is worse than none — tests that assert
implementation details break on every refactor, and tests that never fail give false
confidence. The value is in tests that fail exactly when behavior breaks, and only then.

## Core Principles

- **Test behavior, not implementation.** Assert on observable outputs and effects, not
  private methods or internal call order. Behavior tests survive refactors.
- **One reason to fail per test.** A focused test names the exact broken behavior; a
  test that asserts ten unrelated things tells you little when it goes red.
- **Arrange–Act–Assert.** Structure every test in three visible phases; it makes intent
  obvious and keeps setup from bleeding into assertions.
- **Isolate the unit; fake the boundary.** Mock external systems (DB, HTTP, clock), not
  the code under test. Over-mocking tests the mocks, not the logic.
- **Tests are code.** Hold them to the same clarity bar; a confusing test is a liability.

## Best Practices

- Name tests for the behavior they verify: `testWithdrawFailsWhenBalanceTooLow`, not
  `testWithdraw2`. The name should read as a specification.
- Use data providers (`#[DataProvider]`) for the same logic across many inputs instead
  of copy-pasting near-identical test methods.
- Assert exceptions with `$this->expectException(...)` before the acting call; assert the
  message or code too when they carry meaning.
- Inject dependencies (clock, random, repositories) so tests can substitute
  deterministic fakes — untestable code is usually undependency-injected code. See DI doc.
- Prefer real objects and in-memory fakes over mocks where cheap; reserve mocks for slow
  or non-deterministic boundaries. A mock that just records calls tests nothing.
- Keep tests independent and order-free: no shared mutable state, fresh fixtures per test.
  A suite that only passes in one order is broken.
- Measure coverage to find *untested* code, but never chase a percentage — 100% coverage
  of trivial getters proves nothing. Cover branches and error paths, not just lines.
- Run the suite in CI on every push; a green suite is a merge precondition, not a courtesy.

## Examples

**Good Example** — isolated, deterministic, behavior-focused

```php
use PHPUnit\Framework\TestCase;
use PHPUnit\Framework\Attributes\Test;

final class WalletTest extends TestCase
{
    #[Test]
    public function withdraw_fails_when_balance_is_insufficient(): void
    {
        // Arrange: a fake gateway so the test never touches a real payment system.
        $wallet = new Wallet(balanceCents: 500, gateway: new FakeGateway());

        // Assert the contract: the failure is signalled by a typed exception.
        $this->expectException(InsufficientFundsException::class);

        // Act: the single behavior under test.
        $wallet->withdraw(1000);
    }
}
```

**Bad Example** — hidden dependency, asserts internals, non-deterministic

```php
final class WalletTest extends TestCase
{
    public function testWithdraw(): void
    {
        $wallet = new Wallet(500); // reaches out to the real gateway and clock internally
        $wallet->withdraw(1000);

        // Asserts a private field via reflection → breaks on any harmless refactor.
        $ref = new ReflectionProperty($wallet, 'lastTxnAt');
        $this->assertEquals(date('Y-m-d'), $ref->getValue($wallet)); // flaky at midnight
    }
}
```

## Common Mistakes

- Testing private methods or internal state (via reflection) instead of public behavior;
  the suite then breaks on refactors that changed nothing observable.
- Depending on the real clock, filesystem, network, or randomness, producing flaky tests
  that fail intermittently and get ignored.
- One giant test with many unrelated assertions, so a failure does not localize the bug.
- Mocking the class under test, or mocking so much that the test only exercises fakes.
- Shared mutable state between tests, causing order-dependent passes.
- Chasing a coverage number while leaving error paths and edge cases untested.
- Asserting on the exact wording of a log line or an exception message that is not part
  of the contract, making the test brittle.

## Production Tips

- Split fast unit tests from slow integration tests so developers run the fast set
  constantly and CI runs the full set.
- Use a real database in a container for integration tests, wrapped in a transaction that
  rolls back per test, rather than mocking the query layer and testing nothing real.
- Seed randomness and inject a fixed clock so failures are reproducible from the seed.
- Track flaky tests as bugs; quarantine and fix them, do not retry-until-green.

## AI Review Checklist

- Does each test assert observable behavior rather than private methods or fields?
- Does each test have a single, clearly named reason to fail?
- Are external boundaries (DB, HTTP, clock, random) faked so the test is deterministic?
- Are error and exception paths tested, not just the happy path?
- Are tests independent of execution order and free of shared mutable state?
- Are data providers used instead of duplicated near-identical test methods?
- Is coverage used to find untested logic rather than as a target to hit?

## Related

- `knowledge/php/09-exceptions.md`
- `knowledge/php/20-dependency-injection.md`
- `knowledge/php/14-performance.md`
- `knowledge/php/28-tooling.md`
