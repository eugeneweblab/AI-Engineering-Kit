---
id: ai/02-task-planning
topic: ai
slug: task-planning
title: "Task Planning"
type: doc
order: 2
status: ready
tags: [ai, task-planning]
related: []
when_to_use: "Read before planning an AI-assisted task and prior to making any code changes."
---
# Task Planning

## Purpose

This document defines how an AI coding agent should plan work before making any modifications to a project.

Planning reduces unnecessary changes, improves implementation quality, and minimizes the risk of regressions.

Implementation should always be the result of a plan—not the beginning of one.

---

## Core Principle

Think first.

Code second.

Every engineering task should have an implementation plan before any file is modified.

The larger the task, the more detailed the plan should be.

---

## Planning Workflow

Always follow the same planning sequence.

```
Receive Task
      ↓
Understand Requirements
      ↓
Gather Context
      ↓
Identify Impact
      ↓
Design Solution
      ↓
Validate Plan
      ↓
Implement
```

Never skip planning because a task appears simple.

---

## Step 1 — Understand the Goal

Determine exactly what needs to be accomplished.

Identify:

- business objective;
- expected behavior;
- success criteria;
- technical constraints;
- out-of-scope items.

Do not assume hidden requirements.

---

## Step 2 — Break the Task Into Smaller Problems

Large tasks should never be implemented as one large change.

Instead, divide them into logical units.

Example:

Feature:

```
Implement user profile editing
```

Possible subtasks:

- API endpoint
- Validation
- Database update
- UI form
- Error handling
- Tests
- Documentation

Smaller tasks reduce complexity.

---

## Step 3 — Identify Affected Areas

List every part of the project that may be impacted.

Examples:

- components;
- pages;
- services;
- APIs;
- database;
- authentication;
- configuration;
- tests;
- documentation.

Understanding impact reduces unexpected regressions.

---

## Step 4 — Search Before Creating

For every planned change determine whether existing code can be reused.

Search for:

- components;
- utilities;
- hooks;
- services;
- validation;
- layouts;
- configuration.

The implementation plan should identify reusable code before writing new code.

---

## Step 5 — Evaluate Risks

Every task has potential risks.

Examples:

- breaking existing functionality;
- API compatibility;
- performance regressions;
- security implications;
- accessibility issues;
- deployment risks;
- migration requirements.

Risks should be identified before implementation begins.

---

## Step 6 — Define Implementation Order

Determine the safest order of execution.

Prefer dependencies before consumers.

Example:

1. Database changes
2. Backend logic
3. API
4. Frontend
5. Tests
6. Documentation

Avoid constantly switching between unrelated parts of the project.

---

## Step 7 — Define Verification

Every plan should define how success will be verified.

Verification may include:

- manual testing;
- automated tests;
- visual comparison;
- API verification;
- performance measurement;
- accessibility validation.

A task without a verification plan is incomplete.

---

## Planning Questions

Before implementation answer:

What problem am I solving?

Why does this problem exist?

Which files are affected?

Which files should NOT be modified?

Can existing code be reused?

Which architectural decisions must be respected?

How will I verify the implementation?

What could break?

---

## AI Execution Checklist

## Before Planning

- Read the entire task.
- Identify missing information.
- Clarify ambiguous requirements.
- Understand business goals.

---

## During Planning

- Inspect repository structure.
- Search similar implementations.
- Identify reusable code.
- Determine affected modules.
- Estimate implementation risk.
- Define implementation order.
- Define verification strategy.

---

## Before Implementation

- The task is fully understood.
- Context has been collected.
- Existing architecture is understood.
- Risks are documented.
- A verification strategy exists.
- The smallest possible implementation has been identified.

Only after completing every applicable step should implementation begin.

---

## Anti-patterns

Avoid:

Starting implementation immediately.

Planning while coding.

Creating unnecessary abstractions.

Ignoring existing implementations.

Changing architecture without necessity.

Combining unrelated tasks.

Planning only the happy path.

Ignoring rollback considerations.

---

## AI Responsibilities

During planning AI should:

Explain its reasoning.

Identify uncertainties.

State assumptions explicitly.

Recommend alternative approaches when appropriate.

Highlight potential risks.

Prefer existing project patterns over new ones.

Planning should be transparent.

---

## Example Planning Output

Good:

```
Goal

Add profile image upload.

Affected Areas

- User API
- Storage Service
- Profile Page
- Validation
- Tests

Reusable Code

- Existing file upload utility
- Existing image validator

Risks

- File size limits
- Authentication
- Storage permissions

Verification

- Upload succeeds
- Invalid files rejected
- Existing avatars remain unchanged
```

Poor:

```
I'll add avatar upload.
```

The second example contains no engineering thinking.

---

## Summary

Planning is an engineering activity, not administrative overhead.

A good implementation plan reduces defects, improves consistency, simplifies code review, and enables AI coding agents to make predictable engineering decisions.