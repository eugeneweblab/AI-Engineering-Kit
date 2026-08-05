---
id: testing/19-test-coverage
topic: testing
slug: test-coverage
title: "Test Coverage"
type: doc
order: 19
status: ready
tags: [testing, test-coverage, applyDiscount, toBe, toThrow, describe]
related: [testing/02-unit-testing, testing/27-quality-gates, testing/24-best-practices, testing/28-testing-strategy, testing/09-assertions]
when_to_use: "Read before setting a coverage threshold, interpreting a coverage report, or reviewing a change that adds tests to hit a number."
---
# Test Coverage

## Purpose

This document defines what code coverage does and does not measure, how to use it
as a signal rather than a target, and how to configure coverage gates that catch
untested behavior without inviting metric-gaming. It is written so an agent can
set thresholds and read reports without drawing false conclusions.

Coverage is a *proxy*: it tells you which lines and branches executed during the
test run. It never tells you whether the assertions were meaningful. Treat it as
a map of what is definitely untested, not a certificate of what is well tested.

## Why It Matters

Coverage is the most misused metric in testing. A high number feels like safety,
so teams chase it — and get tests that execute code but assert nothing, or delete
hard-to-cover branches to make the bar. The result is a false sense of security:
the number is green while real behavior is unverified. Conversely, coverage does
one thing extremely well — it *proves a line never ran in any test*. Used for
that, it reliably surfaces dead paths, forgotten error handling, and whole
modules with no tests at all. The value is in the zeros, not the nineties.

## Core Principles

- **Coverage measures execution, not verification.** A line can be 100% covered
  and completely wrong if no assertion checks its output. High coverage is
  necessary-ish, never sufficient.
- **Prefer branch coverage over line coverage.** Line coverage marks an
  `if`/`else` "covered" when only one side ran. Branch (and condition) coverage
  forces both paths, which is where bugs hide.
- **Goodhart's law applies.** The moment coverage becomes the target, it stops
  measuring test quality. Gate on *not regressing*, not on hitting a vanity peak.
- **Coverage of critical paths matters more than the average.** 95% overall with
  0% on the payment module is worse than 80% evenly distributed. Weight by risk.
- **Uncovered code is a question, not a defect.** Each red line asks "should this
  be tested?" Sometimes the answer is "delete it" or "it's trivial glue."

## Best Practices

- Set a realistic floor (e.g. 80% branch coverage) and enforce **no regression**
  on pull requests, so new code must be tested but legacy gaps do not block work.
- Measure coverage on the **diff**, not the whole repo, for PR gates — this
  targets exactly the lines the author changed and avoids punishing untouched code.
- Exclude generated code, config, migrations, and type-only files from the
  denominator so the number reflects logic you actually own.
- Review coverage reports for *branch* and *function* gaps, not just the top-line
  percentage; open the report and look at what is red on changed files.
- Pair coverage with **mutation testing** (Stryker, PIT) on critical modules to
  detect assertions that execute code but verify nothing.
- Never write a test whose only purpose is to raise the number. If a line is not
  worth asserting on, either it needs a real test or it should not exist.
- Fail the build on a coverage *drop*, and require an explicit, reviewed
  ignore-comment (with a reason) for any deliberately uncovered branch.

## Examples

**Good Example** — a test that both covers and verifies both branches

```ts
// Exercises both branches AND asserts the observable outcome of each.
describe("applyDiscount", () => {
  test("applies percentage when code is valid", () => {
    expect(applyDiscount(100, "SAVE10")).toBe(90); // real assertion on the result
  });

  test("rejects an unknown code", () => {
    // The error path is covered *and* verified — not just executed.
    expect(() => applyDiscount(100, "NOPE")).toThrow(/invalid code/i);
  });
});
```

```jsonc
// vitest.config coverage: gate on branches, exclude non-logic, fail on regression.
{
  "coverage": {
    "provider": "v8",
    "reporter": ["text", "lcov"],
    "exclude": ["**/*.d.ts", "**/migrations/**", "**/*.config.*"],
    "thresholds": { "branches": 80, "functions": 80, "autoUpdate": false }
  }
}
```

**Bad Example** — coverage theater: executes the code, verifies nothing

```ts
test("applyDiscount covers everything", () => {
  // Calls every branch to light up the report, but asserts nothing meaningful.
  applyDiscount(100, "SAVE10");
  try { applyDiscount(100, "NOPE"); } catch {}
  expect(true).toBe(true); // 100% line coverage, 0% verification — pure theater
});
```

## Common Mistakes

- Treating a coverage percentage as a quality score instead of a
  "what's definitely untested" signal.
- Gating on **line** coverage only, letting half-tested branches count as covered.
- Chasing 100% and writing assertion-free tests that inflate the number.
- Measuring whole-repo coverage on PRs, so a large untouched legacy area masks
  that the new code has none.
- Excluding hard-to-test error paths from the report to make the bar, hiding the
  exact code most likely to fail in production.
- Assuming high coverage means the tests would catch a regression — only mutation
  testing verifies that.

## Production Tips

- Report coverage as a non-blocking comment on every PR (diff coverage plus the
  changed-file report) so reviewers see gaps in context.
- Keep a small allowlist of files exempt from the threshold, each with a comment
  and a tracking ticket, and review it periodically — exemptions should shrink.
- Run mutation testing on a nightly schedule for core domains; it is too slow for
  every PR but invaluable for finding fake assertions.

## AI Review Checklist

- Is the gate on **branch** (or condition) coverage, not just line coverage?
- Does the PR gate measure the **diff**, and enforce no-regression rather than a
  vanity 100%?
- Do new tests contain real assertions on outcomes, not calls that only execute
  code?
- Are generated files, migrations, and config excluded from the denominator?
- Are deliberately uncovered branches marked with a reviewed reason, not silently
  excluded?
- For critical modules, is coverage backed by mutation testing to catch empty
  assertions?

## Related

- `knowledge/testing/02-unit-testing.md`
- `knowledge/testing/27-quality-gates.md`
- `knowledge/testing/24-best-practices.md`
- `knowledge/testing/28-testing-strategy.md`
- `knowledge/testing/09-assertions.md`
