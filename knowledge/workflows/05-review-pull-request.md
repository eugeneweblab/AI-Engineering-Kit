---
id: workflows/05-review-pull-request
topic: workflows
slug: review-pull-request
title: "Workflow — Review a Pull Request"
type: doc
order: 5
status: ready
tags: [workflows, review-pull-request]
related: []
when_to_use: ""
---
# Workflow — Review a Pull Request

## Purpose

This workflow defines the standard process for reviewing a pull request (PR) to ensure code quality, maintainability, consistency, and safety before merging.

The objective of a review is not to find as many issues as possible.

The objective is to improve the quality of the software while helping the author produce better code.

A good review is objective, constructive, and evidence-based.

---

## Goal

Approve only pull requests that:

- satisfy the requirements;
- preserve project architecture;
- follow coding standards;
- introduce minimal regression risk;
- remain maintainable;
- are ready for production.

---

## Workflow Overview

```
Read Pull Request
        ↓
Understand the Goal
        ↓
Review Architecture
        ↓
Review Code
        ↓
Review Testing
        ↓
Review Risks
        ↓
Provide Feedback
        ↓
Approve or Request Changes
```

---

## Step 1 — Read the Entire Pull Request

Before reviewing code:

Read:

- title;
- description;
- linked issue;
- acceptance criteria;
- screenshots;
- testing notes.

Understand what problem the PR is intended to solve.

Never review code without understanding its purpose.

---

## Step 2 — Review the Scope

Determine whether the scope is appropriate.

Questions:

- Does the PR solve a single problem?
- Does it include unrelated changes?
- Is the size reasonable?
- Can it be reviewed effectively?

Large pull requests are harder to review and more likely to introduce defects.

---

## Step 3 — Verify Requirements

Confirm that the implementation satisfies the requested behavior.

Review:

- acceptance criteria;
- business requirements;
- edge cases;
- error handling;
- permissions.

Code should solve the intended problem—not a different one.

---

## Step 4 — Review Architecture

Verify that the implementation respects the existing architecture.

Review:

- folder structure;
- module responsibilities;
- dependency direction;
- abstraction level;
- reusable components;
- project conventions.

Reject architectural drift unless intentionally approved.

---

## Step 5 — Review Code Quality

Evaluate:

- readability;
- naming;
- complexity;
- duplication;
- maintainability;
- consistency;
- comments;
- formatting.

Every line should have a clear purpose.

---

## Step 6 — Review Reusability

Determine whether existing code could have been reused.

Look for:

- duplicate components;
- duplicate services;
- duplicate utilities;
- duplicate validation;
- duplicate API logic.

Reuse should always be preferred over duplication.

---

## Step 7 — Review Safety

Inspect:

- null handling;
- validation;
- exception handling;
- authentication;
- authorization;
- input sanitization;
- configuration changes.

Security and stability are mandatory review topics.

---

## Step 8 — Review Performance

Evaluate whether the implementation introduces:

- unnecessary rendering;
- unnecessary API calls;
- repeated calculations;
- inefficient loops;
- duplicate queries;
- unnecessary memory allocations.

Performance issues should be identified before merge.

---

## Step 9 — Review Testing

Verify:

- existing tests still pass;
- new functionality is tested;
- edge cases are covered;
- regression risk is acceptable.

Testing should match the importance of the change.

---

## Step 10 — Review Documentation

Determine whether updates are required for:

- README;
- API documentation;
- architecture documents;
- configuration;
- environment variables;
- migration guides.

Documentation should evolve with the codebase.

---

## AI Execution Checklist

## Understanding

☐ Read the complete PR.

☐ Read the linked issue.

☐ Understand business requirements.

☐ Understand acceptance criteria.

---

## Architecture

☐ Verify project conventions.

☐ Verify module boundaries.

☐ Verify dependency direction.

☐ Verify reusable code usage.

---

## Code Review

☐ Review naming.

☐ Review readability.

☐ Review complexity.

☐ Review duplication.

☐ Review comments.

☐ Review formatting.

---

## Safety

☐ Review validation.

☐ Review permissions.

☐ Review error handling.

☐ Review security.

☐ Review performance.

---

## Verification

☐ Review tests.

☐ Review documentation.

☐ Estimate regression risk.

☐ Confirm production readiness.

---

## Review Feedback Guidelines

Feedback should be:

Specific

Explain exactly what should change.

---

Objective

Reference architecture, standards, or evidence rather than personal preference.

---

Constructive

Suggest improvements instead of only identifying problems.

---

Prioritized

Classify findings.

### Critical

Must be resolved before merge.

Examples:

- security issue;
- broken functionality;
- data corruption risk.

---

### Major

Should be resolved before merge.

Examples:

- architectural violations;
- missing validation;
- incorrect business logic.

---

### Minor

Improvement recommendations.

Examples:

- naming;
- readability;
- simplification;
- documentation.

---

### Suggestion

Optional improvements that are not required for correctness.

---

## Common Mistakes

Avoid:

Reviewing only changed lines.

Ignoring business requirements.

Focusing only on formatting.

Approving code without understanding it.

Requesting unnecessary refactoring.

Blocking a merge for personal preferences.

Ignoring regression risks.

---

## Completion Criteria

A pull request is ready for approval only if:

- requirements are satisfied;
- architecture is respected;
- code quality is acceptable;
- testing is sufficient;
- documentation is current;
- regression risk is acceptable;
- no critical issues remain.

---

## Expected AI Output

After completing the review, the AI should provide:

Summary

A concise overview of the implementation.

Strengths

Positive observations about the solution.

Findings

Categorized by Critical, Major, Minor, and Suggestion.

Risks

Any remaining concerns after review.

Decision

Approve

Approve with Minor Suggestions

Request Changes

---

## Summary

A pull request review is an engineering quality gate.

Its purpose is to improve software quality, reduce future maintenance costs, and help engineers produce reliable, maintainable, and production-ready code.