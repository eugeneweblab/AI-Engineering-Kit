---
id: workflows/04-refactor-existing-code
topic: workflows
slug: refactor-existing-code
title: "Workflow — Refactor Existing Code"
type: workflow
order: 4
status: ready
tags: [workflows, refactor-existing-code, toBe, refactoring, behavior, workflow]
related: [engineering/02-code-review, engineering/03-debugging-methodology, engineering/05-context-first-development, testing/98-production-checklist, testing/99-ai-review-checklist, testing/100-common-antipatterns, architecture/27-architecture-review, ai/04-code-modification, testing/20-test-maintenance]
when_to_use: "Follow this workflow when refactoring existing code without changing its behavior."
---
# Workflow — Refactor Existing Code

## Purpose

This workflow defines the standard process for refactoring existing code without changing its external behavior.

The objective of refactoring is to improve the internal quality of the code while preserving functionality, reducing technical debt, and making future development easier.

Refactoring is not feature development.

---

## Goal

Produce cleaner code that:

- preserves existing behavior;
- improves readability;
- improves maintainability;
- reduces duplication;
- follows the project's architecture;
- introduces no functional regressions.

---

## Workflow Overview

```
Identify Refactoring Target
        ↓
Understand Existing Behavior
        ↓
Analyze Dependencies
        ↓
Define Refactoring Scope
        ↓
Create Safety Net
        ↓
Refactor Incrementally
        ↓
Verify Behavior
        ↓
Review
        ↓
Complete
```

---

## Step 1 — Identify the Refactoring Target

Determine why the refactoring is needed.

Possible reasons:

- duplicate logic;
- oversized functions;
- poor naming;
- high complexity;
- outdated patterns;
- difficult testing;
- low readability.

Every refactoring should have a clear objective.

Use a decision framework to confirm the change is worth doing now rather than
deferring it, and name the specific code smell you are targeting. See
[../engineering/01-decision-framework.md](../engineering/01-decision-framework.md)
for prioritizing the work and [../testing/100-common-antipatterns.md](../testing/100-common-antipatterns.md)
and [../architecture/100-common-antipatterns.md](../architecture/100-common-antipatterns.md)
for cataloguing the smell you intend to remove.

---

## Step 2 — Understand Existing Behavior

Before changing anything, understand exactly how the current implementation works.

Review:

- inputs;
- outputs;
- side effects;
- dependencies;
- edge cases;
- business rules.

Never refactor code you do not understand. Gather the surrounding context and
reproduce the current behavior before touching anything — the same discipline
used when diagnosing a defect. See
[../engineering/05-context-first-development.md](../engineering/05-context-first-development.md)
for building that understanding and
[../engineering/03-debugging-methodology.md](../engineering/03-debugging-methodology.md)
for characterizing behavior systematically.

---

## Step 3 — Analyze Dependencies

Determine what depends on the code.

Inspect:

- imports;
- exports;
- API consumers;
- shared utilities;
- components;
- services;
- tests.

Shared code requires additional caution. Respect the existing dependency
direction and module boundaries so the refactoring does not couple layers that
were intentionally kept separate. See
[../architecture/03-clean-architecture.md](../architecture/03-clean-architecture.md)
for reasoning about dependency direction and
[../architecture/100-common-antipatterns.md](../architecture/100-common-antipatterns.md)
for the coupling traps to avoid.

---

## Step 4 — Define the Scope

Clearly define what is included.

Examples:

Included

- improve naming;
- extract reusable functions;
- reduce duplication;
- simplify logic.

Not included

- new features;
- UI redesign;
- dependency upgrades;
- architecture changes.

Do not expand the scope during implementation. Break the refactoring into a small,
ordered set of tasks and hold the line on the boundary. See
[../engineering/04-task-execution.md](../engineering/04-task-execution.md) for
sequencing the work into safe increments.

---

## Step 5 — Create a Safety Net

Before refactoring, verify existing behavior.

Whenever possible:

- review existing tests;
- add missing tests;
- document current behavior;
- identify critical user flows.

Behavior should be protected before implementation begins. Characterization tests
that pin the current outputs are the safety net that makes an aggressive
refactoring safe. See [../testing/02-unit-testing.md](../testing/02-unit-testing.md)
and [../testing/03-integration-testing.md](../testing/03-integration-testing.md)
for building the net, and [../testing/19-test-coverage.md](../testing/19-test-coverage.md)
for confirming the critical paths are actually exercised.

---

## Step 6 — Refactor Incrementally

Perform small, isolated changes.

Examples:

- rename variables;
- extract helper functions;
- simplify conditions;
- reduce nesting;
- remove duplication.

Verify after every logical step.

Avoid large rewrites. Keep each behavior-preserving step in its own small,
descriptive commit so the history stays bisectable and any regression is easy to
isolate or revert. See [../git/04-commits.md](../git/04-commits.md) for structuring
commits and [../git/23-trunk-based-development.md](../git/23-trunk-based-development.md)
for keeping increments small and continuously integrated.

---

## Step 7 — Verify Behavior

Confirm that functionality remains unchanged.

Verify:

- user flows;
- API responses;
- business rules;
- edge cases;
- error handling;
- performance.

Refactoring should not introduce behavioral differences. Re-run the safety net
and compare outputs against the pre-refactoring baseline. See
[../testing/24-best-practices.md](../testing/24-best-practices.md) for reliable
verification practices and [../testing/22-flaky-tests.md](../testing/22-flaky-tests.md)
if a test result becomes nondeterministic during the change.

---

## Step 8 — Review Code Quality

Review the final implementation.

Confirm:

- improved readability;
- lower complexity;
- consistent naming;
- reusable abstractions;
- clear responsibilities.

Every refactoring should leave the codebase in a better state. Apply the same
standards used in a formal review, and confirm the change did not quietly erode
an architectural boundary. See [../engineering/02-code-review.md](../engineering/02-code-review.md)
for the quality bar and [../architecture/27-architecture-review.md](../architecture/27-architecture-review.md)
for checking structural integrity.

---

## AI Execution Checklist

## Investigation

☐ Read the complete implementation.

☐ Understand existing behavior.

☐ Identify dependencies.

☐ Identify duplicated logic.

☐ Review existing tests.

---

## Planning

☐ Define the scope.

☐ Exclude unrelated improvements.

☐ Define verification strategy.

☐ Estimate regression risk.

---

## Refactoring

☐ Keep changes small.

☐ Preserve behavior.

☐ Improve readability.

☐ Reduce duplication.

☐ Preserve architecture.

☐ Avoid unnecessary abstractions.

---

## Verification

☐ Compare behavior before and after.

☐ Verify user flows.

☐ Verify tests.

☐ Review side effects.

☐ Remove obsolete code.

☐ Update documentation if needed.

---

## Manual Verification

Before completing:

- compare old and new behavior;
- verify critical workflows;
- review modified files;
- ensure no new warnings or errors exist;
- ensure formatting and naming are consistent.

---

## Examples

**Good Example** — behaviour pinned first, then changed in reviewable steps

```bash
# 1. Characterise the current behaviour before touching it. These tests describe
#    what the code DOES, including the parts nobody intended.
npm run test -- --coverage src/pricing
# → 34% covered. Add tests for the uncovered branches BEFORE refactoring.
```

```ts
// 2. A pinning test for the behaviour being preserved, quirks included.
it('rounds half up, matching the legacy behaviour', () => {
  expect(priceWithTax(1005, 0.2)).toBe(1206);   // not 1205 — documented quirk
});
```

```text
3. Refactor in separate commits, each one green:
   a1b2c3d  test: pin current pricing behaviour        (no production change)
   b2c3d4e  refactor: extract TaxCalculator            (no behaviour change)
   c3d4e5f  refactor: replace the switch with a map    (no behaviour change)
   d4e5f6a  fix: correct the rounding for 0% tax       (behaviour change, stated)

4. The one behavioural change is its own commit, with its own test, and can be
   reverted without losing the refactor.
```

**Bad Example** — restructure and fix in one pass

```text
One commit, 1,400 lines: extracted four classes, renamed a dozen symbols,
switched from a switch to a strategy map, changed the rounding, upgraded the
money library, and reformatted the file.

Tests: three were deleted "because they tested the old structure".
```

The suite is green, and nobody can say whether the behaviour changed. When invoices come out a
penny off next month, the only way back is reverting all of it — including the parts that were
improvements.

---

## Common Mistakes

Avoid:

Adding new features.

Changing business logic unintentionally.

Combining refactoring with bug fixes.

Moving unrelated code.

Changing public APIs without necessity.

Large rewrites instead of incremental improvements.

Assuming behavior has not changed without verification.

---

## Completion Criteria

The workflow is complete only if:

- behavior is unchanged;
- readability has improved;
- duplication has been reduced;
- architecture remains consistent;
- regression risk is low;
- verification is complete;
- self-review has been performed.

---

## Expected AI Output

After completing this workflow, the AI should be able to explain:

- why refactoring was needed;
- what improvements were made;
- which behaviors were intentionally preserved;
- which files were modified;
- how regression risk was minimized;
- how the result was verified.

---

## Final Checklists

Before marking the refactoring complete, self-verify against the target topic's
standing checklists. For any change touching tested code, close with:

- [../testing/98-production-checklist.md](../testing/98-production-checklist.md) — production-readiness gate;
- [../testing/99-ai-review-checklist.md](../testing/99-ai-review-checklist.md) — AI self-review pass;
- [../testing/100-common-antipatterns.md](../testing/100-common-antipatterns.md) — confirm no antipattern was introduced.

When the refactoring is scoped to a specific stack, also run that topic's
equivalent `98`/`99`/`100` checklists — for example
[../react/98-production-checklist.md](../react/98-production-checklist.md) for a
React component or [../architecture/98-production-checklist.md](../architecture/98-production-checklist.md)
for a structural change.

---

## Summary

Refactoring is the disciplined process of improving code without changing what it does.

A successful refactoring is often invisible to users but highly valuable to future engineers because it makes the system easier to understand, maintain, and extend.

## Related

- `knowledge/engineering/02-code-review.md`
- `knowledge/engineering/03-debugging-methodology.md`
- `knowledge/engineering/05-context-first-development.md`
- `knowledge/testing/98-production-checklist.md`
- `knowledge/testing/99-ai-review-checklist.md`
- `knowledge/testing/100-common-antipatterns.md`
- `knowledge/architecture/27-architecture-review.md`
- `knowledge/ai/04-code-modification.md`
- `knowledge/testing/20-test-maintenance.md`
