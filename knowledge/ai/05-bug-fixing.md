# Bug Fixing

## Purpose

This document defines the standard process AI coding agents should follow when fixing software defects.

Bug fixing is an engineering investigation, not a code generation task.

The objective is to identify the root cause, implement the smallest safe fix, verify the solution, and avoid introducing regressions.

---

# Core Principle

Never fix a symptom.

Always identify and fix the underlying cause.

A bug that appears solved but whose root cause remains is likely to return.

---

# Bug Fix Workflow

Every bug investigation should follow the same sequence.

```
Receive Report
       ↓
Understand Expected Behavior
       ↓
Reproduce
       ↓
Gather Evidence
       ↓
Identify Root Cause
       ↓
Design Smallest Safe Fix
       ↓
Implement
       ↓
Verify
       ↓
Prevent Regression
```

Skipping investigation usually produces unstable fixes.

---

# Step 1 — Understand the Bug Report

Before reading code, determine:

- what the user expected;
- what actually happened;
- when the problem occurs;
- when it does not occur;
- whether the issue is reproducible.

Clarify ambiguous reports before continuing.

---

# Step 2 — Reproduce the Problem

Never implement a fix without reproducing the issue whenever possible.

Identify:

- browser;
- operating system;
- device;
- permissions;
- feature flags;
- user role;
- application state;
- input data.

The shortest reliable reproduction is the best starting point.

---

# Step 3 — Gather Evidence

Collect evidence before changing code.

Possible sources:

- logs;
- stack traces;
- network requests;
- API responses;
- database records;
- browser console;
- screenshots;
- recordings.

Evidence should explain the observed behavior.

---

# Step 4 — Inspect Existing Code

Read the complete implementation.

Review:

- related services;
- helper functions;
- validation;
- dependencies;
- surrounding modules;
- similar implementations.

Never assume the first suspicious line is the cause.

---

# Step 5 — Identify the Root Cause

Continue investigating until the underlying reason is known.

Examples:

Symptom

```
Save button does nothing.
```

Cause

```
Validation always fails.
```

Root Cause

```
The validation schema expects a field that is never populated.
```

Only the root cause should be fixed.

---

# Step 6 — Design the Fix

Before editing code determine:

- the smallest required change;
- affected files;
- possible side effects;
- reusable utilities;
- verification strategy.

Prefer extending existing logic over replacing it.

---

# Step 7 — Implement Carefully

During implementation:

- preserve architecture;
- preserve naming;
- preserve existing behavior;
- modify only required files;
- avoid unrelated refactoring.

Every changed line should have a clear reason.

---

# Step 8 — Verify the Fix

Confirm:

- the original bug no longer exists;
- existing functionality still works;
- edge cases behave correctly;
- related features remain unaffected.

Never assume a successful compilation means the bug is fixed.

---

# Step 9 — Prevent Regression

Whenever appropriate:

- add a test;
- improve validation;
- improve logging;
- improve documentation;
- simplify the implementation.

A good bug fix reduces the probability of the same defect returning.

---

# AI Execution Checklist

## Investigation

☐ Understand the bug report.

☐ Reproduce the issue.

☐ Collect evidence.

☐ Read all related code.

☐ Search for similar implementations.

☐ Identify the root cause.

---

## Implementation

☐ Modify the smallest possible area.

☐ Reuse existing utilities.

☐ Preserve architecture.

☐ Avoid unrelated refactoring.

☐ Keep public behavior unchanged unless required.

---

## Verification

☐ Reproduce the original scenario.

☐ Verify related scenarios.

☐ Review side effects.

☐ Remove debug code.

☐ Verify tests.

☐ Update documentation if required.

---

# Risk Assessment

Before implementing, estimate the impact.

Low Risk

- UI text
- Styling
- Documentation

Medium Risk

- Validation
- Component logic
- API behavior

High Risk

- Authentication
- Authorization
- Database schema
- Payments
- Shared infrastructure
- Public APIs

Higher-risk fixes require additional verification.

---

# Common Anti-patterns

Avoid:

Fixing symptoms instead of causes.

Making multiple unrelated changes.

Guessing instead of investigating.

Suppressing errors.

Replacing large implementations unnecessarily.

Deleting code without understanding why it exists.

Declaring the issue fixed without verification.

---

# AI Responsibilities

When proposing a bug fix, AI should explain:

- the observed behavior;
- the expected behavior;
- the suspected root cause;
- supporting evidence;
- why the proposed solution is appropriate;
- possible risks;
- how the fix should be verified.

Engineering decisions should always be transparent.

---

# Definition of Success

A bug fix is successful when:

- the root cause has been eliminated;
- the smallest reasonable change was made;
- existing functionality remains intact;
- regression risk is minimized;
- the implementation follows project conventions;
- verification confirms the issue is resolved.

---

# Summary

Professional bug fixing is a structured investigation process.

The quality of a bug fix is determined not by how quickly code was changed, but by how confidently the underlying problem was understood and resolved.