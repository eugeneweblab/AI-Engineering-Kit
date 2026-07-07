---
id: workflows/04-refactor-existing-code
topic: workflows
slug: refactor-existing-code
title: "Workflow — Refactor Existing Code"
type: doc
order: 4
status: ready
tags: [workflows, refactor-existing-code]
related: []
when_to_use: ""
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

Never refactor code you do not understand.

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

Shared code requires additional caution.

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

Do not expand the scope during implementation.

---

## Step 5 — Create a Safety Net

Before refactoring, verify existing behavior.

Whenever possible:

- review existing tests;
- add missing tests;
- document current behavior;
- identify critical user flows.

Behavior should be protected before implementation begins.

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

Avoid large rewrites.

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

Refactoring should not introduce behavioral differences.

---

## Step 8 — Review Code Quality

Review the final implementation.

Confirm:

- improved readability;
- lower complexity;
- consistent naming;
- reusable abstractions;
- clear responsibilities.

Every refactoring should leave the codebase in a better state.

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

## Summary

Refactoring is the disciplined process of improving code without changing what it does.

A successful refactoring is often invisible to users but highly valuable to future engineers because it makes the system easier to understand, maintain, and extend.