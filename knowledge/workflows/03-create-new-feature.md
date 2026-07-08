---
id: workflows/03-create-new-feature
topic: workflows
slug: create-new-feature
title: "Workflow — Create a New Feature"
type: doc
order: 3
status: ready
tags: [workflows, create-new-feature]
related: []
when_to_use: "Follow this workflow when implementing a new feature in an existing project."
---
# Workflow — Create a New Feature

## Purpose

This workflow defines the standard engineering process for implementing a new feature in an existing software project.

A new feature should integrate naturally into the existing system without introducing unnecessary complexity, duplication, or architectural inconsistencies.

The objective is to deliver maintainable functionality that follows the project's engineering standards.

---

## Goal

Deliver a feature that:

- satisfies the business requirements;
- follows the existing architecture;
- reuses existing code whenever possible;
- minimizes technical debt;
- is safe to review, test, and maintain.

---

## Workflow Overview

```
Receive Requirements
        ↓
Understand Business Goal
        ↓
Analyze Existing System
        ↓
Identify Reusable Code
        ↓
Design Implementation
        ↓
Estimate Impact
        ↓
Implement Incrementally
        ↓
Verify
        ↓
Document
        ↓
Complete
```

---

## Step 1 — Understand the Requirements

Read the complete specification.

Determine:

- business objective;
- expected user behavior;
- acceptance criteria;
- technical constraints;
- dependencies;
- assumptions.

If any requirement is unclear, resolve it before implementation.

---

## Step 2 — Understand the Existing System

Investigate how similar functionality is implemented.

Review:

- architecture;
- folder structure;
- reusable components;
- services;
- utilities;
- APIs;
- coding conventions;
- testing strategy.

Every feature should feel native to the project.

---

## Step 3 — Search Before Creating

Before creating new code, search for reusable implementations.

Examples:

Components

Services

Utilities

Hooks

Validation

Layout containers

Configuration

Constants

Types

Prefer extension over duplication.

---

## Step 4 — Design the Implementation

Create a technical plan.

Identify:

- affected modules;
- new modules;
- reusable code;
- data flow;
- API changes;
- database changes;
- configuration changes;
- testing requirements.

The implementation plan should be understandable before coding begins.

---

## Step 5 — Estimate Impact

Determine what could be affected.

Review:

- public APIs;
- authentication;
- authorization;
- shared components;
- existing workflows;
- performance;
- accessibility;
- SEO (if applicable);
- analytics;
- caching.

Every feature has consequences beyond its own code.

---

## Step 6 — Implement Incrementally

Implement in small logical steps.

Recommended order:

Infrastructure

↓

Data layer

↓

Business logic

↓

API

↓

UI

↓

Interactions

↓

Validation

↓

Tests

↓

Documentation

Avoid implementing the entire feature in one large change.

---

## Step 7 — Verify Functionality

Verify:

- happy path;
- edge cases;
- invalid input;
- permissions;
- loading states;
- empty states;
- error handling.

The feature is not complete until every important scenario has been reviewed.

---

## Step 8 — Review Integration

Confirm the feature integrates naturally.

Review:

- navigation;
- shared layouts;
- design consistency;
- API compatibility;
- performance impact;
- accessibility;
- responsive behavior.

The feature should feel like part of the product—not an addition.

---

## Step 9 — Update Documentation

When appropriate update:

- README;
- API documentation;
- architecture documentation;
- environment variables;
- configuration guides;
- developer documentation.

Documentation is part of implementation.

---

## AI Execution Checklist

## Investigation

☐ Read the complete requirements.

☐ Understand the business goal.

☐ Review existing architecture.

☐ Search for similar implementations.

☐ Identify reusable code.

☐ Identify affected modules.

---

## Planning

☐ Create an implementation plan.

☐ Estimate risks.

☐ Define implementation order.

☐ Define verification strategy.

---

## Implementation

☐ Modify only required files.

☐ Preserve architecture.

☐ Reuse existing code.

☐ Avoid duplicate functionality.

☐ Keep responsibilities separated.

---

## Verification

☐ Verify all acceptance criteria.

☐ Verify edge cases.

☐ Verify permissions.

☐ Verify responsive behavior.

☐ Verify accessibility.

☐ Verify tests.

☐ Update documentation if necessary.

---

## Manual Verification

Before completing the feature:

- complete every acceptance criterion;
- verify user flows;
- verify navigation;
- verify responsive layouts;
- verify browser console contains no errors;
- verify network requests behave correctly;
- verify logs contain no unexpected warnings.

---

## Common Mistakes

Avoid:

Starting implementation without understanding the business problem.

Creating duplicate components.

Ignoring existing architecture.

Combining feature development with refactoring.

Introducing unnecessary dependencies.

Changing unrelated files.

Skipping verification.

Treating documentation as optional.

---

## Completion Criteria

The workflow is complete only if:

- all requirements are satisfied;
- existing architecture is respected;
- reusable code has been used where appropriate;
- verification is complete;
- documentation is accurate;
- regression risk is acceptable;
- self-review has been completed.

---

## Expected AI Output

After completing this workflow, the AI should be able to explain:

- the business objective;
- the implementation strategy;
- reused components and services;
- newly created modules;
- affected files;
- verification performed;
- remaining risks or assumptions.

---

## Summary

A successful feature is not measured by the amount of new code.

It is measured by how naturally it integrates into the existing product while remaining maintainable, consistent, and easy to extend.