---
id: testing/23-debugging-tests
topic: testing
slug: debugging-tests
title: "Debugging Tests"
type: doc
order: 23
status: ready
tags: [testing, debugging-tests]
related: [testing/22-flaky-tests, testing/09-assertions, testing/06-mocking, testing/20-test-maintenance, testing/04-e2e-testing]
when_to_use: "Read when a test fails and the cause is not obvious, or a test passes locally but fails in CI."
---
# Debugging Tests

## Purpose

This document defines a systematic method for diagnosing failing tests — whether
the failure is a real regression, a flaky test, or a broken test — and for making
tests debuggable in the first place. It is written so an agent can find the root
cause of a failure efficiently instead of guessing or blindly re-running.

Debugging a test failure is a fork in the road: either the **code** is wrong (the
test did its job), the **test** is wrong (it asserts the wrong thing), or the test
is **flaky** (non-deterministic). Identifying which, quickly, is the whole skill.

## Why It Matters

A confusing test failure taxes every developer who hits it, and the temptation
under deadline pressure is to "fix" it by deleting the assertion, adding a wait, or
re-running until green — each of which destroys the test's value. Time spent making
failures readable and diagnosable is repaid every time the suite goes red for the
next several years. Conversely, a test that fails with a bare `expected true, got
false` and no context is a test the team will neuter rather than understand. Good
debugging discipline is what keeps failures leading to fixes instead of to
deletions.

## Core Principles

- **Reproduce deterministically before changing anything.** Run the single failing
  test in isolation, then in the full suite, then in random order. A failure that
  only appears in one of these tells you the cause (isolation vs. ordering vs.
  [flakiness](22-flaky-tests.md)).
- **Read the failure, not your assumptions.** The assertion message, the diff, and
  the stack trace usually name the cause. Improve the message before you improve
  your guess.
- **Isolate the variable.** Change one thing at a time — one test, one input, one
  mock. Bisect the setup until the failure appears or vanishes.
- **Trust the test until proven otherwise.** A green-to-red transition on
  unchanged test code is a real regression by default. Assume the code broke, not
  the test, until you have evidence.
- **"Passes locally, fails in CI" is an environment diff.** The delta is almost
  always time zone, locale, parallelism, ordering, resource limits, or an
  uncommitted local file. Diff the environments, do not blame the CI.

## Best Practices

- Run one test in watch/inspect mode with a real debugger and breakpoints
  (`node --inspect-brk`, `--runInBand`, IDE test debugging) rather than scattering
  `console.log`; you can inspect the full state at the failure point.
- Make assertions self-explanatory: assert on whole objects so the diff shows
  exactly what differs, and add a message argument stating the expected behavior.
- Reproduce CI conditions locally — run in band vs. parallel, set the CI time zone
  and locale (`TZ=UTC LANG=…`), and run in random order — to surface environment
  and ordering bugs.
- For async failures, log or await the actual state and use the framework's
  find/waitFor with a bounded timeout so you see *what* the UI/data was, not just
  that it timed out.
- Use test framework artifacts on failure — Playwright traces, screenshots, DOM
  dumps, retained containers — to inspect the exact state without re-running.
- Bisect with `git bisect` when a previously green test starts failing after a
  range of commits; it finds the offending change far faster than reading diffs.
- When you conclude the test (not the code) was wrong, fix the assertion *and*
  note why, so the next person does not re-introduce the bad expectation.

## Examples

**Good Example** — object diff + message make the failure self-diagnosing

```ts
test("normalizes a user record", () => {
  const result = normalize(rawUser);

  // Asserting the whole object: the failure diff shows *exactly* which field is
  // wrong (e.g. `role: "admin"` vs `"member"`) — no re-run or logging needed.
  expect(result).toEqual({
    id: "u1",
    email: "a@b.com",
    role: "member",
  });
});

test("rejects a negative balance", () => {
  // The message states the intended behavior, so a failure explains itself.
  expect(() => applyDebit(acct, -5)).toThrow(/amount must be positive/i);
});
```

**Bad Example** — opaque assertion; failure tells you nothing

```ts
test("normalizes a user record", () => {
  const result = normalize(rawUser);

  // Boolean assertion: on failure you get `expected true, received false` with no
  // hint which field is wrong. The only way to debug is to add logging and re-run.
  expect(result.role === "member" && result.email === "a@b.com").toBe(true);

  // "Fixing" a mystery failure by loosening the assertion hides the regression:
  // expect(result).toBeTruthy();  // ← never do this to make red go green
});
```

## Common Mistakes

- Re-running until green instead of reproducing the failure deterministically —
  this hides both regressions and flakiness.
- Asserting on booleans or single fields, so the failure message names nothing and
  forces print-debugging.
- "Fixing" a failing test by loosening or deleting the assertion, converting a real
  signal into silence.
- Blaming CI for a "passes locally" failure without diffing the environment (time
  zone, locale, ordering, parallelism).
- Adding `console.log` everywhere instead of attaching a debugger and inspecting
  state at the breakpoint.
- Changing test and code together in one step, so you cannot tell which fix
  actually resolved the failure.

## Production Tips

- Configure the framework to retain traces/screenshots/videos on failure in CI so
  a red build is diagnosable from artifacts alone, without reproduction.
- Standardize a `TZ=UTC` and fixed-locale CI environment and document it, so
  "works on my machine" gaps shrink to real code differences.
- Keep a short runbook of the reproduce-in-isolation → run-in-suite →
  random-order → bisect sequence; it turns ad-hoc debugging into a repeatable
  procedure.

## AI Review Checklist

- Was the failure reproduced deterministically (isolation, full suite, random
  order) before any change?
- Do assertions produce a meaningful diff/message rather than a bare boolean?
- For "passes locally, fails in CI," was the environment (TZ, locale, ordering,
  parallelism) actually diffed?
- Was the root cause classified as code-bug vs. test-bug vs. flake before fixing?
- Is the failure diagnosable from CI artifacts (traces/screenshots) without a
  local re-run?
- Does the fix address the cause rather than loosen or delete the assertion?

## Related

- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/09-assertions.md`
- `knowledge/testing/06-mocking.md`
- `knowledge/testing/20-test-maintenance.md`
- `knowledge/testing/04-e2e-testing.md`
