---
id: workflows/02-fix-a-bug
topic: workflows
slug: fix-a-bug
title: "Workflow — Fix a Bug"
type: doc
order: 2
status: ready
tags: [workflows, fix-a-bug]
related: [engineering/03-debugging-methodology, ai/05-bug-fixing, workflows/06-investigate-production-bug]
  - engineering/03-debugging-methodology
  - engineering/02-code-review
  - testing/02-unit-testing
  - testing/03-integration-testing
  - testing/23-debugging-tests
  - testing/98-production-checklist
  - testing/99-ai-review-checklist
  - testing/100-common-antipatterns
  - react/19-error-handling
  - git/18-history
  - security/09-input-validation
when_to_use: "Follow this workflow when investigating and fixing a bug end-to-end."
---
# Workflow — Fix a Bug

## Purpose

This workflow defines the standard process for investigating, fixing, and verifying software defects.

Bug fixing is an investigation process. The goal is to eliminate the root cause of a defect while minimizing changes to the existing system and preventing regressions.

This workflow applies to all technologies and frameworks.

---

## Goal

Produce a fix that:

- resolves the root cause;
- preserves existing behavior;
- follows the project's architecture;
- minimizes regression risk;
- is easy to review.

---

## Workflow Overview

```
Receive Bug Report
        ↓
Understand the Problem
        ↓
Reproduce the Bug
        ↓
Collect Evidence
        ↓
Identify Root Cause
        ↓
Inspect Existing Code
        ↓
Plan the Fix
        ↓
Implement
        ↓
Verify
        ↓
Prevent Regression
        ↓
Complete
```

---

## Step 1 — Receive the Bug Report

Read the report carefully.

Determine:

- expected behavior;
- actual behavior;
- affected users;
- affected environments;
- severity;
- frequency.

If information is missing, request clarification before proceeding.

---

## Step 2 — Reproduce the Bug

Reproduce the issue before modifying code.

Record:

- operating system;
- browser;
- device;
- user role;
- application state;
- feature flags;
- input values;
- exact reproduction steps.

If the issue cannot be reproduced, continue investigating before implementing changes.

For a structured approach to reproduction and hypothesis testing, see [Engineering — Debugging Methodology](../engineering/03-debugging-methodology.md).

---

## Step 3 — Collect Evidence

Gather objective evidence.

Possible sources:

- application logs;
- browser console;
- server logs;
- stack traces;
- API responses;
- database records;
- screenshots;
- video recordings.

Avoid making assumptions without evidence.

Relevant knowledge:

- [Testing — Observability](../testing/26-observability.md) — reading logs, metrics, and traces to locate the failure.
- [Git — History](../git/18-history.md) and [Git — Reflog](../git/19-reflog.md) — correlate the regression with recent commits and deployments (`git bisect`, `git log`).

---

## Step 4 — Identify the Root Cause

Determine why the defect occurs.

Continue asking:

> Why?

until the underlying cause becomes clear.

Example:

```
User cannot save profile.

↓

API returns validation error.

↓

Validation expects "phoneNumber".

↓

Frontend sends "phone".

↓

Field names are inconsistent.
```

Fix the inconsistency—not the symptom.

Relevant knowledge:

- [Engineering — Debugging Methodology](../engineering/03-debugging-methodology.md) — a disciplined root-cause process.
- [React — Debugging](../react/27-debugging.md) and [Git — Debugging](../git/26-debugging.md) — technology-specific techniques for narrowing down the cause.

---

## Step 5 — Inspect Existing Code

Read all related code before editing.

Inspect:

- similar implementations;
- shared services;
- helper functions;
- validation;
- API contracts;
- tests;
- configuration.

Look for an existing solution before creating a new one.

Relevant knowledge:

- [Architecture — Clean Architecture](../architecture/03-clean-architecture.md) — understand which layer owns the defect before editing.
- [Git — History](../git/18-history.md) — use `git blame` and `git log -p` to learn why the current code exists.
- [Engineering — Code Review](../engineering/02-code-review.md) — the same lens a reviewer will apply to your fix.

---

## Step 6 — Plan the Fix

Document:

Files to modify

Files that must remain unchanged

Existing code to reuse

Potential risks

Verification strategy

Rollback considerations

Planning reduces accidental changes.

---

## Step 7 — Implement

During implementation:

- modify the smallest possible area;
- preserve architecture;
- preserve naming conventions;
- avoid unrelated refactoring;
- reuse existing utilities;
- maintain backward compatibility when appropriate.

Every change should have a clear purpose.

Relevant knowledge:

- [Security — Input Validation](../security/09-input-validation.md) — when the fix touches untrusted input, validate at the boundary rather than patching downstream.
- [React — Error Handling](../react/19-error-handling.md) — surface failures safely instead of swallowing them.

---

## Step 8 — Verify

Verify the original scenario.

Then verify:

- related functionality;
- edge cases;
- negative scenarios;
- user permissions;
- responsive behavior (if applicable);
- API responses (if applicable).

Verification should be broader than the original bug.

Relevant knowledge:

- [Testing — API Testing](../testing/12-api-testing.md) — confirm request/response contracts still hold.
- [Testing — E2E Testing](../testing/04-e2e-testing.md) — exercise the full user flow that reported the bug.

---

## Step 9 — Prevent Regression

When appropriate:

- add automated tests;
- improve validation;
- improve logging;
- update documentation;
- simplify fragile logic.

The same defect should become less likely to occur again.

Write a test that fails on the old code and passes on the fix — this is the regression guard.

Relevant knowledge:

- [Testing — Unit Testing](../testing/02-unit-testing.md) and [Testing — Integration Testing](../testing/03-integration-testing.md) — pin the corrected behavior with an automated test.
- [Testing — Debugging Tests](../testing/23-debugging-tests.md) and [Testing — Flaky Tests](../testing/22-flaky-tests.md) — make sure the new test is deterministic.

---

## AI Execution Checklist

## Investigation

☐ Read the complete bug report.

☐ Reproduce the issue.

☐ Collect logs and evidence.

☐ Read related files completely.

☐ Inspect similar implementations.

☐ Identify the root cause.

---

## Planning

☐ Identify affected files.

☐ Identify reusable code.

☐ Estimate implementation risk.

☐ Define verification strategy.

---

## Implementation

☐ Modify the smallest possible area.

☐ Preserve architecture.

☐ Preserve public interfaces.

☐ Avoid duplicate logic.

☐ Avoid unrelated changes.

---

## Verification

☐ Verify the original bug.

☐ Verify related functionality.

☐ Review edge cases.

☐ Remove debugging code.

☐ Verify tests.

☐ Review documentation.

---

## Manual Verification

Before completing the task:

- repeat the original reproduction steps;
- verify the expected behavior;
- verify similar user flows;
- verify error handling;
- verify affected APIs;
- verify browser console contains no new errors.

---

## Common Mistakes

Avoid:

Implementing before reproducing.

Guessing the cause.

Fixing only the symptom.

Changing multiple unrelated modules.

Ignoring existing architecture.

Leaving temporary debugging code.

Skipping regression testing.

---

## Completion Criteria

The workflow is complete only if:

- the root cause has been eliminated;
- the original issue is resolved;
- no unnecessary files were modified;
- regression risk has been evaluated;
- documentation remains accurate;
- tests have been updated when appropriate;
- the implementation passes self-review.

---

## Expected AI Output

After completing this workflow, the AI should be able to explain:

- what the bug was;
- what caused it;
- what evidence supported the diagnosis;
- which files were modified;
- why those changes were sufficient;
- what was verified;
- what risks remain, if any.

---

## Close With the Topic Checklists

Before marking the fix complete, run it through the checklists of the topic you changed. For most defects the testing topic is the closest fit:

- [Testing — Production Checklist](../testing/98-production-checklist.md) — confirm the fix and its regression test are production-ready.
- [Testing — AI Review Checklist](../testing/99-ai-review-checklist.md) — self-review the change the way a reviewer would.
- [Testing — Common Antipatterns](../testing/100-common-antipatterns.md) — verify the fix did not introduce a known antipattern.

If the fix lives in a specific stack, use that topic's equivalent `98`/`99`/`100` checklists instead — for example [React — Production Checklist](../react/98-production-checklist.md) / [React — AI Review Checklist](../react/99-ai-review-checklist.md) / [React — Common Antipatterns](../react/100-common-antipatterns.md), or the matching files under [`../security/`](../security/) for security-sensitive changes.

---

## Summary

A professional bug fix is the result of investigation, not intuition.

The safest fix is the one that changes only what is necessary, preserves the project's architecture, and eliminates the root cause rather than masking the symptom.

## Related

- `knowledge/engineering/03-debugging-methodology.md`
- `knowledge/ai/05-bug-fixing.md`
- `knowledge/workflows/06-investigate-production-bug.md`
