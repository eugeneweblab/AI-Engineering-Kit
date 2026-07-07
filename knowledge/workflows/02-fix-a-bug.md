---
id: workflows/02-fix-a-bug
topic: workflows
slug: fix-a-bug
title: "Workflow — Fix a Bug"
type: doc
order: 2
status: ready
tags: [workflows, fix-a-bug]
related: []
when_to_use: ""
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

---

## Step 9 — Prevent Regression

When appropriate:

- add automated tests;
- improve validation;
- improve logging;
- update documentation;
- simplify fragile logic.

The same defect should become less likely to occur again.

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

## Summary

A professional bug fix is the result of investigation, not intuition.

The safest fix is the one that changes only what is necessary, preserves the project's architecture, and eliminates the root cause rather than masking the symptom.