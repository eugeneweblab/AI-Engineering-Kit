---
id: typescript/24-testing
topic: typescript
slug: testing
title: "TypeScript Testing"
type: doc
order: 24
status: ready
tags: [typescript, testing, toHaveBeenCalledTimes, toBeDefined, toThrow, mockResolvedValue, describe]
related: [typescript/17-error-handling, typescript/18-asynchronous-programming, typescript/29-tooling, typescript/08-generics]
when_to_use: "Read before writing or reviewing unit, integration, or type-level tests for TypeScript code."
---
# TypeScript Testing

## Purpose

This document defines how to test TypeScript code so that tests verify *behaviour*,
survive refactors, and catch real regressions. It covers runtime tests (unit and
integration) and type-level tests, and the discipline that keeps both trustworthy.

TypeScript's compiler proves that types line up; it does not prove that your logic is
correct. Tests close that gap. A green build with no tests means nothing runs against
real inputs.

## Why It Matters

Tests are the executable specification of your code. Without them, every change is a bet
that nothing downstream broke. In a typed codebase the temptation is to assume the
compiler has your back — but the compiler cannot know that `calculateTax` should round
half-up, or that a retry must stop after three attempts. Those are behaviours, and only
tests pin them down. Poorly written tests are worse than none: they pass while the code
is broken, or fail on every harmless refactor, training the team to ignore red.

## Core Principles

- **Test behaviour, not implementation.** Assert on observable outputs and side effects,
  not on private methods or call counts. Behaviour tests survive refactors; the cost of
  implementation tests is that they break when you change *how* without changing *what*.
- **Type the test as strictly as the code.** Do not use `any` or `as` to force a value
  into a test. If the test needs a cast, the API is probably wrong.
- **One reason to fail per test.** A test that asserts five unrelated things tells you
  little when it goes red. Split by concern.
- **Deterministic or it does not count.** No real clocks, network, randomness, or shared
  state. Flaky tests get muted, and muted tests protect nothing.
- **Test the type surface too.** For libraries and generics, a type that infers wrongly
  is a bug the runtime tests will never see.

## Best Practices

- Use a fast, TypeScript-native runner — **Vitest** (preferred for new projects) or Jest
  with `ts-jest`/`swc`. Run tests in CI on every push; a test suite that only runs
  locally is optional, and optional tests rot.
- Name tests by behaviour: `it("rejects a negative amount")`, not `it("test amount")`.
- Arrange–Act–Assert: set up inputs, call the unit once, assert on the result. Keep the
  three phases visually distinct.
- Prefer real objects over mocks. Mock only at true boundaries (network, filesystem,
  clock) because over-mocking tests your mocks, not your code.
- Assert on rejected promises with `await expect(fn()).rejects.toThrow(...)`; never a
  bare `try/catch` that can pass when nothing throws. See
  [asynchronous programming](18-asynchronous-programming.md).
- Add type-level tests with `expectTypeOf` (Vitest) or `tsd` for generic and utility
  types, so a broken inference fails CI.
- Freeze time with fake timers when logic depends on `Date.now()` or `setTimeout`.
- Track coverage as a signal, not a target. 100% coverage of trivial getters proves
  nothing; cover branches and error paths.

## Examples

**Good Example** — behavioural, deterministic, async handled correctly

```ts
import { describe, it, expect, vi } from "vitest";
import { withRetry } from "./retry";

describe("withRetry", () => {
  it("retries a failing call up to the limit, then rejects", async () => {
    // A stub that fails twice then succeeds — asserts behaviour, not internals.
    const op = vi
      .fn<() => Promise<string>>()
      .mockRejectedValueOnce(new Error("boom"))
      .mockRejectedValueOnce(new Error("boom"))
      .mockResolvedValue("ok");

    const result = await withRetry(op, { attempts: 3 });

    expect(result).toBe("ok");
    expect(op).toHaveBeenCalledTimes(3); // the retry contract, an observable behaviour
  });

  it("rejects when every attempt fails", async () => {
    const op = vi.fn().mockRejectedValue(new Error("down"));
    // rejects.toThrow cannot silently pass if nothing throws.
    await expect(withRetry(op, { attempts: 2 })).rejects.toThrow("down");
  });
});
```

**Bad Example** — casts around the types, async can pass on failure

```ts
it("works", async () => {
  const service = {} as UserService; // `as` hides a missing dependency
  try {
    await service.create({ name: "x" } as any); // `any` disables the type check
    // If create() resolves without throwing, this test still passes — a false green.
  } catch (e) {
    expect(e).toBeDefined(); // asserts nothing meaningful about the failure
  }
});
```

## Common Mistakes

- Using `any` or `as` to satisfy the compiler inside a test, hiding a real API mismatch.
- Testing private methods or asserting exact mock call arguments that the behaviour does
  not require, so every refactor breaks the suite.
- `try/catch` around an async call without asserting a throw actually happened.
- Shared mutable fixtures between tests, creating order-dependent flakiness.
- Snapshot tests over large objects that nobody reads — they get blindly updated.
- Mocking the unit under test instead of its collaborators.

## Production Tips

- Fail CI on new uncovered branches in changed files rather than a global percentage.
- Run type-level tests (`tsd`/`expectTypeOf`) in the same CI job as unit tests.
- Quarantine flaky tests loudly (tracked issue, deadline) instead of deleting or muting
  them silently.

## AI Review Checklist

- Do tests assert on observable behaviour rather than private internals or call order?
- Is every test free of `any` and unjustified `as` casts?
- Are rejected promises asserted with `rejects.toThrow`, not a permissive `try/catch`?
- Are non-determinism sources (clock, network, random) faked or injected?
- Do generic/utility types have type-level tests?
- Does each test have a single clear reason to fail?

## Related

- `knowledge/typescript/17-error-handling.md`
- `knowledge/typescript/18-asynchronous-programming.md`
- `knowledge/typescript/29-tooling.md`
- `knowledge/typescript/08-generics.md`
