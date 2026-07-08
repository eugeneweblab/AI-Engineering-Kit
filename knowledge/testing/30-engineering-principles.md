---
id: testing/30-engineering-principles
topic: testing
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [testing, engineering-principles]
related: [testing/01-testing-fundamentals, testing/24-best-practices, testing/28-testing-strategy, testing/22-flaky-tests, testing/02-unit-testing]
when_to_use: "Read before designing a test suite, or when deciding what and how much to test."
---
# Engineering Principles

## Purpose

This document states the durable principles behind good testing — the reasoning that
outlives any framework, language, or assertion library. The other docs in this topic
tell you *how* to write a specific kind of test; this one tells you *why* those rules
exist, so you can apply judgment when a situation is not covered by a rule.

A test suite is engineering, not paperwork. It is code with a job: to give a team the
confidence to change the system quickly and safely. Every principle here serves that job.

## Why It Matters

Tests are a cost you pay forever. Each one must be read, run on every commit, and updated
when requirements change. A suite that is written without principles accretes into a slow,
flaky, low-signal mass that the team learns to ignore — at which point it has negative
value: it costs CI minutes and developer attention while catching nothing. The difference
between a suite that accelerates a team and one that drags it down is not tooling; it is a
handful of principles applied consistently. An agent that internalizes them writes tests
that stay valuable for years instead of tests that pass review and rot.

## Core Principles

- **Tests are a confidence instrument, not a coverage metric.** The purpose of a test is
  to make a change safer, not to move a number. A line covered by a test that cannot fail
  buys nothing. Optimize for defects caught per minute of run time and per line of test.
- **Test behavior, not implementation.** Assert what a caller or user observes, never how
  the code achieves it. A test coupled to internals breaks on every refactor and teaches
  the team that green means "unchanged," not "correct."
- **Determinism is non-negotiable.** Same code, same inputs, same result — every run,
  every machine. Non-determinism is a defect in the test, not bad luck. See
  [flaky tests](22-flaky-tests.md).
- **A test must be able to fail for the right reason.** If you cannot describe the change
  to production code that would turn the test red, the test is not testing anything.
- **Fast feedback beats exhaustive feedback.** A test that runs in the inner loop catches
  bugs before they compound. Push confidence down to the cheapest level that still gives
  it — the [testing pyramid](01-testing-fundamentals.md).
- **The test is documentation.** Its name and body are the clearest spec of intended
  behavior. Optimize it to be read, not just to run.

## Best Practices

- **Design for testability, then test.** If a unit is hard to test, that is a design
  signal: hidden dependencies, doing too much, or coupling to globals. Fix the design
  (inject dependencies, split responsibilities) rather than reaching for elaborate mocks.
- **One reason to fail per test.** A test that asserts many unrelated things gives a
  vague signal when it breaks. Prefer several focused tests over one that checks everything.
- **Follow Arrange-Act-Act-Assert with a single Act.** Multiple actions in one test hide
  which step failed and usually means you are testing a workflow that belongs in E2E.
- **Prefer real objects over doubles; prefer fakes over mocks.** Every double is an
  assumption about a collaborator that can drift from reality. Use the lightest double
  that isolates the unit — see [test doubles](05-test-doubles.md).
- **Make failure messages diagnostic.** A good failure tells you what was expected, what
  happened, and enough context to fix it without re-running under a debugger.
- **Treat test code as production code.** It gets reviewed, refactored, and held to the
  same clarity bar. No dead tests, no commented-out assertions, no `sleep` to paper over a
  race.
- **Delete tests that no longer pay rent.** A redundant or obsolete test is maintenance
  cost with no benefit. Removing it is a legitimate, deliberate act.

## Examples

**Good Example** — asserts observable behavior, one reason to fail, deterministic

```python
# Tests the contract "an expired coupon is rejected" — a rule the caller cares about.
# No clock coupling: time is injected, so the test is deterministic and fast.
def test_expired_coupon_is_rejected():
    coupon = Coupon(code="SAVE10", expires_at=datetime(2026, 1, 1))
    now = datetime(2026, 6, 1)  # injected clock, not datetime.now()

    result = apply_coupon(cart, coupon, now=now)

    assert result.rejected_because == "expired"  # behavior, not internals
```

**Bad Example** — couples to implementation, non-deterministic, vague signal

```python
def test_coupon():
    coupon = Coupon(code="SAVE10", expires_at=datetime(2026, 1, 1))
    apply_coupon(cart, coupon)  # uses datetime.now() internally → time-dependent

    # Asserts private state and call counts: breaks on any refactor even when
    # the observable behavior is unchanged. Also checks three unrelated things,
    # so a failure does not say which rule broke.
    assert cart._coupon_cache_size == 1
    assert coupon._validated is True
    assert cart.total == 100
```

## Common Mistakes

- Chasing a coverage percentage instead of chasing confidence — writing tests that
  execute code without asserting anything meaningful.
- Mocking the unit under test's own internals, so the test verifies the mock, not the code.
- Depending on wall-clock time, real network, random seeds, or test-execution order.
- Writing one giant test per feature, so a single failure gives no diagnostic signal.
- Leaving flaky tests in the suite with a retry wrapper instead of fixing the root cause.
- Never deleting tests, so the suite grows monotonically and slows the inner loop.
- Treating test code as second-class — duplicated setup, magic values, no refactoring.

## Production Tips

- Track suite health as an engineering metric: run time, flake rate, and mean time to
  diagnose a failure. A rising flake rate is a leak to fix now, not later.
- Keep the inner-loop suite (unit) under a few seconds so developers run it constantly.
- Quarantine a newly flaky test immediately and file a fix — never let it erode trust in
  the whole suite.

## AI Review Checklist

- Does each test assert observable behavior rather than internal state or call counts?
- Can you name the production change that would make each test fail?
- Is every test deterministic — free of real time, network, randomness, and order?
- Is each test focused on a single reason to fail, with a diagnostic message?
- Was hard-to-test code fixed by better design rather than heavier mocking?
- Is the suite pruned of redundant and obsolete tests?

## Related

- `knowledge/testing/01-testing-fundamentals.md`
- `knowledge/testing/24-best-practices.md`
- `knowledge/testing/28-testing-strategy.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/02-unit-testing.md`
