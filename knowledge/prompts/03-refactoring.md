---
id: prompts/03-refactoring
topic: prompts
slug: refactoring
title: "Prompt — Refactoring"
type: doc
order: 3
status: ready
tags: [prompts, refactoring]
related: [prompts/01-code-review, prompts/02-bug-investigation, workflows/04-refactor-existing-code, engineering/00-engineering-principles, testing/20-test-maintenance]
when_to_use: "Copy when asking an assistant to restructure code without changing its behavior."
---
# Prompt — Refactoring

## Purpose

A prompt for restructuring code while keeping behavior identical. The hard part is not the
restructuring — it is stopping there.

---

## The Prompt

```markdown
Refactor this code. Behavior must not change.

## Goal
<the specific problem: this function does three things / this logic is duplicated in four
places / this module cannot be tested without a database>

## Constraints
- Public API stays the same: <the signatures or endpoints callers depend on>
- Behavior stays identical, including error cases, edge cases, and ordering
- Existing tests must pass unchanged — if a test needs editing, stop and tell me why
- Follow the conventions in the surrounding code

## Do not
- Add features, options, or configuration that nothing asks for
- Add abstractions for hypothetical future requirements
- Add error handling for cases that cannot occur
- Rename things beyond what the refactor requires
- Touch files outside the stated scope

## What I want back
The refactored code, plus a short note on what changed structurally and why — enough that a
reviewer can check behavior is preserved without re-deriving your reasoning.
```

---

## Why It Is Shaped This Way

**The "do not" section is the important half.** Unprompted, an assistant asked to refactor
tends to improve — extra abstractions, defensive checks, options nobody needs. Each addition
is plausible on its own, and collectively they turn a reviewable refactor into a rewrite.

**"Existing tests must pass unchanged" is the behavior contract.** A refactor that requires
editing tests has changed behavior, changed the interface, or the tests were coupled to
implementation details. All three are worth stopping for — see
[Testing — Test Maintenance](../testing/20-test-maintenance.md).

**Naming the goal prevents aimless tidying.** "This function does three things" produces a
focused change; "clean this up" produces whatever the model finds untidy.

---

## Before You Start

A refactor without a safety net is a rewrite with extra steps:

☐ Tests exist and pass for the current behavior. If not, write characterization tests first —
tests that capture what the code *does*, not what it should do.

☐ The current behavior is understood, including the parts that look like bugs. Some of them
are load-bearing.

☐ The refactor is separate from any behavior change. Never both in one commit.

---

## Variants

**Characterization tests first** — when coverage is missing:

```markdown
Before refactoring, write tests that capture the current behavior of this code — including
behavior that looks incorrect. Do not fix anything. The point is a net that will catch a
change in behavior.

Cover: the normal path, each branch, the edge cases the code explicitly handles, and the
error paths. Where behavior looks wrong, note it in a comment but preserve it in the test.
```

**Extracting a testable core:**

```markdown
This logic can only be tested with a live <database / HTTP client / framework context>.
Separate the decision-making from the I/O: pure functions that take data and return
decisions, and a thin layer that fetches and persists. Keep the existing entry point's
signature so callers are unaffected.
```

**Splitting a large module:**

```markdown
This file has grown to <N> lines and mixes <concerns>. Propose a split — which pieces move
where, and what each new module owns — before writing any code. I want to agree the shape
first.
```

Asking for the plan before the diff is worth a round trip on anything structural.

---

## Reviewing the Result

- **Read the diff as behavior, not as structure.** For each moved block, ask what changed
  besides its location.
- **Watch for silently altered defaults** — a parameter that gained a default value, an early
  return that changed order, an error swallowed where it used to propagate.
- **Check the tests were not weakened** to accommodate the new shape.
- **Verify the scope held.** Files outside the stated scope in the diff are a finding.

---

## Examples

**Good Example** — the goal, the invariant, and the stopping condition

```text
Refactor src/pricing/discount.ts.

Goal
  Replace the 6-branch switch on plan type with a lookup, so adding a plan does
  not mean editing this function.

Must not change
  - Observable behaviour, including the half-up rounding at line 31. There is a
    pinning test for it (test/pricing/rounding.test.ts); it must still pass.
  - The public signature of applyDiscount.

Constraints
  - No new dependencies.
  - Keep it in this file; do not reorganise the module.
  - Behaviour changes, if you think one is warranted, go in a SEPARATE commit
    with its own test — do not fold them into the refactor.

Done when
  npm run verify passes and `git diff` shows no change outside this file.
```

**Bad Example** — an open invitation

```text
This file is messy, please clean it up and modernise it.
```

"Modernise" invites a new dependency, a rename that breaks callers, and a rounding change made
in passing — all in one diff, with no way to tell which part caused the invoices to come out a
penny short next month.

---

## Related


- `knowledge/prompts/01-code-review.md`
- `knowledge/prompts/02-bug-investigation.md`
- `knowledge/workflows/04-refactor-existing-code.md`
- `knowledge/engineering/00-engineering-principles.md`
- `knowledge/testing/20-test-maintenance.md`
