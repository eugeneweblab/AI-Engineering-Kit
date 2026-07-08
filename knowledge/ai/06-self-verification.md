---
id: ai/06-self-verification
topic: ai
slug: self-verification
title: "Self Verification"
type: doc
order: 6
status: ready
tags: [ai, self-verification]
related: []
when_to_use: "Read before marking any AI-assisted task complete to self-verify the implementation."
---
# Self Verification

## Purpose

This document defines the mandatory self-verification process that every AI coding agent should perform before considering any engineering task complete.

Writing code is not the end of a task.

Verification is.

AI should assume that every implementation may contain mistakes until it has been deliberately reviewed.

---

## Core Principle

Never trust the first implementation.

Always verify it.

The first solution is a draft.

Verification turns a draft into an engineering solution.

---

## Verification Is Evidence, Not Assertion

The single failure mode that separates self-verification from the earlier steps
(context, planning, generation) is this: an agent re-reads its own reasoning,
finds it agrees with itself, and declares the task done. That is confirmation,
not verification.

Every claim you make at completion must be backed by an **observation you
produced after writing the code** — a command output, a test result, a diff you
actually inspected. If you cannot point to the observation, the claim is a guess.

| Claim the agent wants to make | Evidence that actually earns it |
| --- | --- |
| "The change is complete." | `git diff --stat` reviewed hunk by hunk |
| "Tests pass." | Test runner output pasted, with the exit code |
| "Nothing else uses this function." | `git grep -n 'oldName('` returns only the definition |
| "No debug code left behind." | `git grep -nE 'console\.log|debugger|TODO: temp|print\(' -- <changed files>` is empty |
| "The old behavior still works." | The pre-existing test suite for that module ran green |
| "Types are correct." | `tsc --noEmit` / `mypy` / build ran clean |

Bad — an assertion with no observation behind it:

> I updated the `calculateTax` function and it now handles the discount case, so
> the task is complete.

Good — the same claim, earned:

> `git diff` shows the discount branch added to `calculateTax` (src/billing/tax.ts:41).
> `git grep -n 'calculateTax(' src` lists 3 callers; I read each — all pass the
> discount arg or rely on its default. `npm test -- billing` ran green (24 passed).
> `git grep -nE 'console\.|debugger' src/billing/tax.ts` is empty.

---

## Verification Workflow

Every completed task should pass through the same workflow.

```
Implementation
        ↓
Requirement Verification
        ↓
Architecture Review
        ↓
Code Review
        ↓
Regression Analysis
        ↓
Documentation Review
        ↓
Risk Assessment
        ↓
Final Approval
```

No step should be skipped.

---

## Step 1 — Verify Requirements

Compare the implementation with the original request.

Confirm:

- every requirement has been implemented;
- no requested functionality is missing;
- no unnecessary functionality was added;
- the expected behavior matches the implementation.

Never assume the task was completed simply because code was written.

The concrete technique is a **traceability check**: re-read the original request,
extract each discrete requirement as a line, and map it to the exact code location
that satisfies it. A requirement with no location is missing; a code change with
no requirement is scope creep.

Original request: *"Add a `/health` endpoint that returns 200 with uptime, and
make sure it is excluded from auth."*

| Requirement | Satisfied at | Verified how |
| --- | --- | --- |
| Endpoint at `/health` | `routes/health.ts:8` | curled it: `200` |
| Returns uptime | `routes/health.ts:11` (`process.uptime()`) | body shows `{ uptimeSeconds: 42 }` |
| Excluded from auth | `middleware/auth.ts:19` (allow-list) | curled with no token: still `200` |
| ~~Rate limiting~~ | not requested | not added — avoided scope creep |

If any row has an empty "Satisfied at" cell, the task is not done.

---

## Step 2 — Review Architecture

Confirm that the implementation follows the existing architecture.

Review:

- folder structure;
- module responsibilities;
- dependency direction;
- naming conventions;
- abstraction level;
- project patterns.

The implementation should fit naturally into the repository.

---

## Step 3 — Review Code Quality

Inspect the generated code as though it were written by another engineer.

Check:

- readability;
- maintainability;
- duplication;
- unnecessary complexity;
- function size;
- variable naming;
- comments.

Good code should require minimal explanation.

---

## Step 4 — Review Dependencies

Confirm:

- no unnecessary dependencies were added;
- existing utilities were reused;
- imports are correct;
- exports remain valid;
- dependency boundaries were respected.

Prefer existing project capabilities over introducing new ones.

---

## Step 5 — Analyze Regression Risk

Ask:

What could this change accidentally break?

Review:

- shared components;
- public APIs;
- database interactions;
- authentication;
- authorization;
- configuration;
- reusable utilities.

Every modification has potential side effects.

The most common self-verification miss is checking only the file you edited. When
you change a shared signature, name, or contract, find its **blast radius** before
declaring done. Do not reason about who might call it — enumerate the callers.

```bash
# You renamed getUser -> getUserById and changed its return shape.
# 1. Confirm no stale references to the old name survive.
git grep -n 'getUser\b' -- 'src/**/*.ts'

# 2. Enumerate every caller of the NEW function and read each one.
git grep -n 'getUserById(' -- 'src/**/*.ts'

# 3. If the return shape changed from `User` to `User | null`,
#    find callers that assume it is always defined.
git grep -n 'getUserById(.*)\.' -- 'src/**/*.ts'   # immediate member access = unguarded
```

Every hit from step 2 is a location you must open and confirm still compiles and
behaves. A green build on the changed file alone proves nothing about callers in
other packages, dynamic imports, or test fixtures.

For a change to a database column, config key, or public API field, widen the net
beyond code:

```bash
git grep -n 'old_column_name' -- 'migrations/**' 'src/**' '**/*.sql' '**/*.json'
```

---

## Step 6 — Review Error Handling

Verify:

- invalid input;
- empty states;
- null values;
- exceptions;
- network failures;
- unexpected responses.

Failure paths should be as intentional as success paths.

---

## Step 7 — Review Security

Confirm:

- validation exists;
- authorization remains correct;
- authentication flow is preserved;
- secrets are protected;
- unsafe input is handled.

Security verification is mandatory.

---

## Step 8 — Review Performance

Evaluate whether the implementation introduces:

- unnecessary rendering;
- duplicate API requests;
- repeated calculations;
- inefficient loops;
- avoidable database queries;
- unnecessary allocations.

Performance optimization should be evidence-based.

---

## Step 9 — Review Documentation

Determine whether any documentation requires updates.

Examples:

- README
- API documentation
- Architecture documents
- Configuration guides
- Environment variables
- Migration notes

Code and documentation should remain synchronized.

---

## Step 10 — Final Review

Before marking the task complete ask:

Would I approve this pull request?

If the answer is uncertain, continue reviewing.

---

## AI Execution Checklist

## Requirements

☐ Every requested feature is implemented.

☐ Nothing unnecessary was added.

☐ Expected behavior matches implementation.

---

## Architecture

☐ Existing architecture was respected.

☐ Naming conventions were followed.

☐ Existing patterns were preserved.

☐ No competing abstractions were introduced.

---

## Code Quality

☐ Code is readable.

☐ Code is maintainable.

☐ No duplicate logic exists.

☐ Complexity is justified.

☐ Comments explain intent rather than implementation.

---

## Safety

☐ Imports are correct.

☐ Exports are correct.

☐ No temporary debugging code remains.

☐ No commented-out code remains.

☐ No unused variables remain.

☐ No unused imports remain.

---

## Verification

☐ Existing functionality still works.

☐ Edge cases were reviewed.

☐ Side effects were considered.

☐ Regression risk is acceptable.

☐ Documentation is accurate.

☐ Tests pass or were updated.

---

## Confidence Assessment

Before completing the task, estimate confidence.

## High Confidence

- Requirements are clear.
- Context is complete.
- Existing patterns were followed.
- Verification is complete.
- Regression risk is low.

---

## Medium Confidence

- Minor assumptions were required.
- Verification is mostly complete.
- Small uncertainties remain.

These uncertainties should be documented.

---

## Low Confidence

- Important context is missing.
- Requirements are ambiguous.
- Existing architecture is unclear.
- Side effects cannot be evaluated.

AI should clearly communicate low confidence instead of presenting uncertain conclusions as facts.

---

## Completion Criteria

A task should only be marked complete if all of the following are true:

- Requirements have been satisfied.
- Architecture has been respected.
- Existing behavior remains correct.
- No unnecessary changes were introduced.
- Documentation is accurate.
- Verification is complete.
- Self-review has been completed.

Completion is a quality decision, not a coding milestone.

---

## Anti-patterns

Avoid:

Declaring success after compilation.

Skipping manual review.

Ignoring regression risks.

Assuming generated code is correct.

Verifying only the modified file.

Confusing implementation with completion.

---

## AI Responsibilities

Before stating that a task is complete, AI should explain:

- what was changed;
- why the implementation satisfies the requirements;
- what was verified;
- remaining assumptions;
- remaining risks;
- recommended manual verification.

Engineering confidence should always be justified.

Bad — a completion report that is a summary of intent:

> Done. I added the caching layer to the user service, refactored the repository,
> and everything should work now. Let me know if you need anything else.

Good — a completion report that is a record of verification:

> **Changed** — `user.service.ts` now wraps `findById` in a 60s in-memory cache
> (lines 22–48); `user.repository.ts` unchanged.
> **Requirements** — cache hit avoids the DB call (verified: added a temporary
> log, second call produced no query in the test output, then removed the log).
> **Regression** — `git grep 'findById(' src` lists 4 callers; all read-only, none
> mutate through the returned object, so a shared cached instance is safe.
> **Tests** — `npm test -- user` green (18 passed); added one test for the
> eviction path.
> **Assumption** — cache is per-process; if you run multiple instances, reads can
> be up to 60s stale. Flagged because your deploy config was not in context.
> **Recommend** — a human should confirm 60s staleness is acceptable for this data.

The Good version is longer for a reason: every sentence names an observation or an
explicit, surfaced assumption. That is what "engineering confidence should be
justified" means in practice.

---

## Definition of Success

Successful self-verification means:

The implementation satisfies the requested outcome.

The project architecture remains consistent.

The change introduces minimal risk.

Another experienced engineer would be comfortable approving the implementation without requesting significant revisions.

---

## Summary

Self-verification is the final engineering discipline before task completion.

AI should never assume that generated code is correct.

Instead, AI should systematically challenge its own implementation until there is sufficient evidence that the solution is correct, maintainable, and safe to integrate into the project.