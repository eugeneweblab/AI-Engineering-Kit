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
when_to_use: ""
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